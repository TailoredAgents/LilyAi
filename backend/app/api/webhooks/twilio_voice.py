from fastapi import APIRouter, Request, Form, HTTPException, Response
from typing import Optional
import structlog
import random

from app.core.config import settings
from app.integrations.twilio_client import TwilioClient
from app.services.jitter_queue import JitterQueue

logger = structlog.get_logger()
router = APIRouter()

@router.post("/twilio/voice")
async def twilio_voice_webhook(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Direction: Optional[str] = Form(None),
    CallerName: Optional[str] = Form(None),
):
    """
    Handle Twilio voice webhook for missed call automation
    
    Triggers SMS follow-up when calls are not answered, busy, or failed
    """
    try:
        # Validate webhook signature
        twilio_client = TwilioClient()
        signature = request.headers.get("X-Twilio-Signature", "")
        url = str(request.url)
        
        # Get form data for validation
        form_data = await request.form()
        params = dict(form_data)
        
        if not twilio_client.validate_webhook(url, params, signature):
            logger.warning("Invalid Twilio webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        logger.info(
            "Received Twilio voice webhook",
            call_sid=CallSid,
            call_status=CallStatus,
            from_number=From,
            to_number=To,
            direction=Direction,
            caller_name=CallerName
        )
        
        # Check if this is a missed call (inbound call that wasn't answered)
        missed_statuses = {"no-answer", "busy", "failed", "canceled"}
        is_inbound = Direction == "inbound" or From != settings.TWILIO_FROM_NUMBER
        
        if CallStatus in missed_statuses and is_inbound:
            await handle_missed_call(From, To, CallSid, CallerName)
        
        # Return empty TwiML response
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing Twilio voice webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_missed_call(
    from_number: str, 
    to_number: str, 
    call_sid: str, 
    caller_name: Optional[str] = None
):
    """Handle missed call by queuing follow-up SMS"""
    try:
        # Generate jitter delay (10-45 seconds as specified)
        jitter_delay = random.randint(
            settings.JITTER_MIN_SECONDS,
            settings.JITTER_MAX_SECONDS
        )
        
        task_payload = {
            "to_number": from_number,
            "caller_name": caller_name,
            "call_sid": call_sid,
            "original_to": to_number
        }
        
        # For now, use a default tenant_id
        # In production, you'd look up the tenant by the business phone number (to_number)
        tenant_id = "default-tenant"  # TODO: Implement tenant lookup by phone number
        
        # Enqueue missed call SMS task
        task_id = JitterQueue.enqueue_delayed(
            task_type="MISSED_CALL_SMS",
            payload=task_payload,
            delay_seconds=jitter_delay,
            tenant_id=tenant_id,
            idempotency_key=f"missed_call_{call_sid}"
        )
        
        logger.info(
            "Queued missed call SMS",
            task_id=task_id,
            from_number=from_number,
            call_sid=call_sid,
            delay_seconds=jitter_delay,
            caller_name=caller_name
        )
        
    except Exception as e:
        logger.error(
            "Error handling missed call",
            error=str(e),
            from_number=from_number,
            call_sid=call_sid
        )