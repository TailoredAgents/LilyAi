import asyncio
import time
from typing import Optional
import structlog
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from app.core.config import settings

logger = structlog.get_logger()

class TwilioClient:
    """Twilio integration client with retry logic and error handling"""
    
    def __init__(self):
        self.client = None
        self.validator = None
        
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        else:
            logger.warning("Twilio not configured - SMS functionality disabled")
    
    async def send_sms(
        self, 
        to: str, 
        body: str, 
        from_number: Optional[str] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Send SMS with retry logic and exponential backoff
        
        Args:
            to: Destination phone number
            body: Message body
            from_number: Sender phone number (defaults to configured number)
            max_retries: Maximum retry attempts
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Twilio client not configured")
            return False
        
        if not from_number:
            from_number = settings.TWILIO_FROM_NUMBER
        
        if not from_number:
            logger.error("No Twilio from number configured")
            return False
        
        for attempt in range(max_retries):
            try:
                # Run in thread pool since Twilio SDK is sync
                loop = asyncio.get_event_loop()
                message = await loop.run_in_executor(
                    None,
                    lambda: self.client.messages.create(
                        body=body,
                        from_=from_number,
                        to=to
                    )
                )
                
                logger.info(
                    "SMS sent successfully",
                    message_sid=message.sid,
                    to=to,
                    status=message.status
                )
                return True
                
            except Exception as e:
                logger.warning(
                    "SMS send attempt failed",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                    to=to
                )
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(
                        "SMS send failed after all retries",
                        to=to,
                        error=str(e)
                    )
        
        return False
    
    def validate_webhook(self, url: str, params: dict, signature: str) -> bool:
        """
        Validate Twilio webhook signature
        
        Args:
            url: Full webhook URL
            params: POST parameters
            signature: X-Twilio-Signature header value
        
        Returns:
            True if signature is valid
        """
        if not self.validator:
            logger.warning("Twilio validator not configured - skipping validation")
            return True  # Allow in development
        
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            logger.error("Error validating Twilio webhook", error=str(e))
            return False
    
    @staticmethod
    def is_stop_command(body: str) -> bool:
        """Check if message is a STOP command for SMS opt-out"""
        if not body:
            return False
        
        stop_keywords = {
            'stop', 'stopall', 'unsubscribe', 'cancel', 'end', 'quit'
        }
        
        return body.lower().strip() in stop_keywords
    
    @staticmethod
    def is_help_command(body: str) -> bool:
        """Check if message is a HELP command"""
        if not body:
            return False
        
        help_keywords = {'help', 'info'}
        return body.lower().strip() in help_keywords
    
    async def send_missed_call_followup(self, to: str, caller_name: str = None) -> bool:
        """
        Send missed call follow-up SMS
        
        Args:
            to: Phone number that called
            caller_name: Optional caller name
        
        Returns:
            True if successful
        """
        if caller_name:
            body = (
                f"Hi {caller_name}! Sorry we missed your call. 📞 "
                "Text us 2-3 photos of what needs cleaning + your ZIP code "
                "and we'll send a ballpark quote in minutes!"
            )
        else:
            body = (
                "Sorry we missed your call! 📞 Text us 2-3 photos of what "
                "needs cleaning + your ZIP code and we'll send a ballpark "
                "quote in minutes!"
            )
        
        return await self.send_sms(to, body)
    
    async def send_review_request(self, to: str, customer_name: str = None) -> bool:
        """
        Send review request SMS
        
        Args:
            to: Customer phone number
            customer_name: Optional customer name
        
        Returns:
            True if successful
        """
        if customer_name:
            body = (
                f"Hi {customer_name}! 🌟 How did we do with your cleaning? "
                "We'd love a quick review to help other customers find us!"
            )
        else:
            body = (
                "Hi! 🌟 How did we do with your cleaning? "
                "We'd love a quick review to help other customers find us!"
            )
        
        return await self.send_sms(to, body)
    
    async def send_help_response(self, to: str) -> bool:
        """Send HELP command response"""
        body = (
            "This is Lily AI automated messaging. "
            "Text photos + ZIP for quotes, or call us directly. "
            "Reply STOP to unsubscribe."
        )
        return await self.send_sms(to, body)
    
    async def send_stop_confirmation(self, to: str) -> bool:
        """Send STOP command confirmation"""
        body = (
            "You've been unsubscribed from SMS messages. "
            "Reply START to resubscribe or call us anytime."
        )
        return await self.send_sms(to, body)