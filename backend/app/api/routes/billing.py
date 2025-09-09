from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import structlog
from app.services.stripe_service import StripeService

logger = structlog.get_logger()
router = APIRouter()

class CheckoutRequest(BaseModel):
    plan_code: str  # 'starter', 'pro', 'growth'
    tenant_id: str
    customer_email: str
    success_url: str
    cancel_url: str
    trial_days: int = 14

class PortalRequest(BaseModel):
    customer_id: str
    return_url: str

@router.post("/checkout")
async def create_checkout_session(request: CheckoutRequest):
    """Create a Stripe checkout session for subscription"""
    try:
        session = StripeService.create_checkout_session(
            plan_code=request.plan_code,
            customer_email=request.customer_email,
            tenant_id=request.tenant_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            trial_days=request.trial_days
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create checkout session"
            )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        logger.error("Error in checkout endpoint", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/portal")
async def create_portal_session(request: PortalRequest):
    """Create a Stripe customer portal session"""
    try:
        session = StripeService.create_portal_session(
            customer_id=request.customer_id,
            return_url=request.return_url
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create portal session"
            )
        
        return {
            "portal_url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        logger.error("Error in portal endpoint", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )