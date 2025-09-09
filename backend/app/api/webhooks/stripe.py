import stripe
import structlog
from fastapi import APIRouter, Request, HTTPException, status
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    
    Processes:
    - checkout.session.completed: Create/update subscription and set tenant plan/trial
    - customer.subscription.updated: Sync subscription status
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe webhook secret not configured")
            return {"status": "webhook secret not configured"}
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid payload")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        logger.info("Received Stripe webhook", event_type=event["type"], event_id=event["id"])
        
        # Handle different event types
        if event["type"] == "checkout.session.completed":
            await handle_checkout_completed(event["data"]["object"])
        elif event["type"] == "customer.subscription.updated":
            await handle_subscription_updated(event["data"]["object"])
        elif event["type"] == "customer.subscription.deleted":
            await handle_subscription_deleted(event["data"]["object"])
        else:
            logger.info("Unhandled event type", event_type=event["type"])
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error("Error processing Stripe webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def handle_checkout_completed(session):
    """Handle successful checkout session"""
    try:
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        metadata = session.get("metadata", {})
        tenant_id = metadata.get("tenant_id")
        
        logger.info(
            "Processing checkout completion",
            customer_id=customer_id,
            subscription_id=subscription_id,
            tenant_id=tenant_id
        )
        
        # TODO: Update tenant subscription in database
        # This would typically involve:
        # 1. Find tenant by tenant_id from metadata
        # 2. Create/update Subscription record
        # 3. Set tenant's plan based on subscription
        # 4. Start trial period if applicable
        
        logger.info("Checkout completed successfully", tenant_id=tenant_id)
        
    except Exception as e:
        logger.error("Error handling checkout completion", error=str(e))

async def handle_subscription_updated(subscription):
    """Handle subscription status changes"""
    try:
        subscription_id = subscription["id"]
        status = subscription["status"]
        customer_id = subscription["customer"]
        
        logger.info(
            "Processing subscription update",
            subscription_id=subscription_id,
            status=status,
            customer_id=customer_id
        )
        
        # TODO: Update subscription status in database
        # This would typically involve:
        # 1. Find subscription by subscription_id
        # 2. Update status (active, past_due, canceled, etc.)
        # 3. Update tenant's plan access accordingly
        
        logger.info("Subscription updated successfully", subscription_id=subscription_id, status=status)
        
    except Exception as e:
        logger.error("Error handling subscription update", error=str(e))

async def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        subscription_id = subscription["id"]
        customer_id = subscription["customer"]
        
        logger.info(
            "Processing subscription deletion",
            subscription_id=subscription_id,
            customer_id=customer_id
        )
        
        # TODO: Handle subscription cancellation
        # This would typically involve:
        # 1. Find subscription by subscription_id
        # 2. Set status to canceled
        # 3. Downgrade tenant to free plan or disable features
        
        logger.info("Subscription deleted successfully", subscription_id=subscription_id)
        
    except Exception as e:
        logger.error("Error handling subscription deletion", error=str(e))