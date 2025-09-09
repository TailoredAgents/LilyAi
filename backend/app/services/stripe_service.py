import stripe
import structlog
from typing import Optional, Dict, Any
from app.core.config import settings

logger = structlog.get_logger()
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    """Service for Stripe operations"""
    
    @staticmethod
    def create_checkout_session(
        plan_code: str,
        customer_email: str,
        tenant_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: Optional[int] = 14
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe checkout session for subscription
        
        Args:
            plan_code: 'starter', 'pro', or 'growth'
            customer_email: Customer's email
            tenant_id: Tenant ID for metadata
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if canceled
            trial_days: Trial period in days
        
        Returns:
            Checkout session data or None if error
        """
        try:
            # Map plan codes to Stripe price IDs
            price_map = {
                'starter': settings.STRIPE_PRICE_STARTER,
                'pro': settings.STRIPE_PRICE_PRO,
                'growth': settings.STRIPE_PRICE_GROWTH
            }
            
            price_id = price_map.get(plan_code)
            if not price_id:
                logger.error("Invalid plan code", plan_code=plan_code)
                return None
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                mode='subscription',
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                customer_email=customer_email,
                metadata={
                    'tenant_id': tenant_id,
                    'plan_code': plan_code,
                },
                subscription_data={
                    'trial_period_days': trial_days,
                    'metadata': {
                        'tenant_id': tenant_id,
                        'plan_code': plan_code,
                    }
                },
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            logger.info(
                "Created checkout session",
                session_id=session.id,
                plan_code=plan_code,
                tenant_id=tenant_id
            )
            
            return session
            
        except Exception as e:
            logger.error("Error creating checkout session", error=str(e), plan_code=plan_code)
            return None
    
    @staticmethod
    def create_portal_session(
        customer_id: str,
        return_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe customer portal session
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session
        
        Returns:
            Portal session data or None if error
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            
            logger.info("Created portal session", session_id=session.id, customer_id=customer_id)
            return session
            
        except Exception as e:
            logger.error("Error creating portal session", error=str(e), customer_id=customer_id)
            return None
    
    @staticmethod
    def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer details"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except Exception as e:
            logger.error("Error retrieving customer", error=str(e), customer_id=customer_id)
            return None
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except Exception as e:
            logger.error("Error retrieving subscription", error=str(e), subscription_id=subscription_id)
            return None