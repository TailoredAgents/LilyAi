import hmac
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import structlog

from app.core.config import settings
from app.integrations.twilio_client import TwilioClient
from app.integrations.google_calendar_client import GoogleCalendarClient

logger = structlog.get_logger()
router = APIRouter()

@router.post("/calcom")
async def calcom_webhook(request: Request):
    """
    Handle Cal.com webhook events for booking automation
    
    Processes:
    - booking.created: Create internal booking record, send SMS confirmation, create Google Calendar event
    - booking.cancelled: Handle cancellation
    - booking.rescheduled: Handle rescheduling
    """
    try:
        payload = await request.body()
        signature = request.headers.get("X-Cal-Signature", "")
        
        # Validate webhook signature if secret is configured
        if settings.CALCOM_WEBHOOK_SECRET:
            if not validate_calcom_signature(payload, signature):
                logger.warning("Invalid Cal.com webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        try:
            import json
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Cal.com webhook")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        event_type = data.get("triggerEvent")
        booking_data = data.get("payload", {})
        
        logger.info(
            "Received Cal.com webhook",
            event_type=event_type,
            booking_id=booking_data.get("id")
        )
        
        if event_type == "BOOKING_CREATED":
            await handle_booking_created(booking_data)
        elif event_type == "BOOKING_CANCELLED":
            await handle_booking_cancelled(booking_data)
        elif event_type == "BOOKING_RESCHEDULED":
            await handle_booking_rescheduled(booking_data)
        else:
            logger.info(f"Unhandled Cal.com event: {event_type}")
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing Cal.com webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_booking_created(booking_data: Dict[str, Any]):
    """Handle new booking creation"""
    try:
        # Extract booking details
        booking_id = booking_data.get("id")
        booking_uid = booking_data.get("uid")
        title = booking_data.get("title", "Pressure Washing Appointment")
        start_time = booking_data.get("startTime")
        end_time = booking_data.get("endTime")
        
        # Customer details
        attendees = booking_data.get("attendees", [])
        if not attendees:
            logger.warning("No attendees found in booking", booking_id=booking_id)
            return
        
        customer = attendees[0]  # Primary attendee
        customer_name = customer.get("name", "Customer")
        customer_email = customer.get("email")
        customer_phone = customer.get("phoneNumber") or customer.get("phone")
        
        # Location and notes
        location = booking_data.get("location", {}).get("value", "")
        notes = booking_data.get("description", "")
        
        logger.info(
            "Processing booking creation",
            booking_id=booking_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            start_time=start_time
        )
        
        # TODO: Create internal Booking record in database
        # This would typically involve:
        # 1. Parse start_time and end_time to datetime objects
        # 2. Create Booking model instance
        # 3. Associate with Lead/Tenant
        # 4. Save to database
        
        # Send SMS confirmation
        if customer_phone:
            await send_booking_confirmation_sms(
                phone=customer_phone,
                customer_name=customer_name,
                appointment_time=start_time,
                location=location
            )
        
        # Create Google Calendar event
        if start_time and end_time:
            try:
                # For now, use default tenant - in production, determine from booking
                tenant_id = "default-tenant"
                
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                await GoogleCalendarClient.create_booking_event(
                    tenant_id=tenant_id,
                    customer_name=customer_name,
                    customer_email=customer_email or "",
                    customer_phone=customer_phone or "",
                    service_type="Pressure Washing",
                    start_time=start_dt,
                    duration_minutes=int((end_dt - start_dt).total_seconds() / 60),
                    location=location
                )
                
            except Exception as e:
                logger.error("Failed to create Google Calendar event", error=str(e))
        
        logger.info("Booking creation handled successfully", booking_id=booking_id)
        
    except Exception as e:
        logger.error("Error handling booking creation", error=str(e), booking_data=booking_data)

async def handle_booking_cancelled(booking_data: Dict[str, Any]):
    """Handle booking cancellation"""
    try:
        booking_id = booking_data.get("id")
        attendees = booking_data.get("attendees", [])
        
        if attendees:
            customer = attendees[0]
            customer_name = customer.get("name", "Customer")
            customer_phone = customer.get("phoneNumber") or customer.get("phone")
            
            # Send cancellation confirmation SMS
            if customer_phone:
                await send_cancellation_sms(
                    phone=customer_phone,
                    customer_name=customer_name
                )
        
        # TODO: Update internal booking status to cancelled
        # TODO: Delete or update Google Calendar event
        
        logger.info("Booking cancellation handled", booking_id=booking_id)
        
    except Exception as e:
        logger.error("Error handling booking cancellation", error=str(e))

async def handle_booking_rescheduled(booking_data: Dict[str, Any]):
    """Handle booking reschedule"""
    try:
        booking_id = booking_data.get("id")
        new_start_time = booking_data.get("startTime")
        attendees = booking_data.get("attendees", [])
        
        if attendees:
            customer = attendees[0]
            customer_name = customer.get("name", "Customer")
            customer_phone = customer.get("phoneNumber") or customer.get("phone")
            
            # Send reschedule confirmation SMS
            if customer_phone and new_start_time:
                await send_reschedule_sms(
                    phone=customer_phone,
                    customer_name=customer_name,
                    new_appointment_time=new_start_time
                )
        
        # TODO: Update internal booking record
        # TODO: Update Google Calendar event
        
        logger.info("Booking reschedule handled", booking_id=booking_id)
        
    except Exception as e:
        logger.error("Error handling booking reschedule", error=str(e))

async def send_booking_confirmation_sms(
    phone: str,
    customer_name: str,
    appointment_time: str,
    location: str = ""
):
    """Send booking confirmation SMS"""
    try:
        # Parse and format appointment time
        appointment_dt = datetime.fromisoformat(appointment_time.replace('Z', '+00:00'))
        formatted_time = appointment_dt.strftime("%A, %B %d at %I:%M %p")
        
        message = f"Hi {customer_name}! 📅 Your pressure washing appointment is confirmed for {formatted_time}."
        
        if location:
            message += f" Location: {location}."
        
        message += " We'll text you when we're on our way. Thanks for choosing us!"
        
        twilio_client = TwilioClient()
        success = await twilio_client.send_sms(phone, message)
        
        if success:
            logger.info("Booking confirmation SMS sent", phone=phone, customer_name=customer_name)
        
    except Exception as e:
        logger.error("Error sending booking confirmation SMS", error=str(e), phone=phone)

async def send_cancellation_sms(phone: str, customer_name: str):
    """Send booking cancellation SMS"""
    try:
        message = (
            f"Hi {customer_name}, your appointment has been cancelled. "
            "If you'd like to reschedule, just reply or call us anytime!"
        )
        
        twilio_client = TwilioClient()
        await twilio_client.send_sms(phone, message)
        
        logger.info("Cancellation SMS sent", phone=phone, customer_name=customer_name)
        
    except Exception as e:
        logger.error("Error sending cancellation SMS", error=str(e), phone=phone)

async def send_reschedule_sms(phone: str, customer_name: str, new_appointment_time: str):
    """Send booking reschedule SMS"""
    try:
        # Parse and format new appointment time
        appointment_dt = datetime.fromisoformat(new_appointment_time.replace('Z', '+00:00'))
        formatted_time = appointment_dt.strftime("%A, %B %d at %I:%M %p")
        
        message = (
            f"Hi {customer_name}! Your appointment has been rescheduled to "
            f"{formatted_time}. Thanks for your flexibility!"
        )
        
        twilio_client = TwilioClient()
        await twilio_client.send_sms(phone, message)
        
        logger.info("Reschedule SMS sent", phone=phone, customer_name=customer_name)
        
    except Exception as e:
        logger.error("Error sending reschedule SMS", error=str(e), phone=phone)

def validate_calcom_signature(payload: bytes, signature: str) -> bool:
    """
    Validate Cal.com webhook signature
    
    Args:
        payload: Raw request payload
        signature: Signature from X-Cal-Signature header
    
    Returns:
        True if signature is valid
    """
    if not settings.CALCOM_WEBHOOK_SECRET or not signature:
        return True  # Skip validation if not configured
    
    try:
        # Cal.com uses HMAC SHA256
        expected_signature = hmac.new(
            settings.CALCOM_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare with provided signature
        return hmac.compare_digest(expected_signature, signature)
        
    except Exception as e:
        logger.error("Error validating Cal.com signature", error=str(e))
        return False