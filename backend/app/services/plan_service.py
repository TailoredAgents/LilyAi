from typing import Optional, List
from sqlalchemy.orm import Session
import structlog

from app.models.tenant import Tenant
from app.models.enums import SubscriptionPlan, SubscriptionStatus
from app.core.feature_flags import feature_flags, Feature

logger = structlog.get_logger()

class PlanService:
    def __init__(self, db: Session):
        self.db = db
        
        self.plan_hierarchy = {
            SubscriptionPlan.TRIAL: 0,
            SubscriptionPlan.STARTER: 1,
            SubscriptionPlan.PRO: 2,
            SubscriptionPlan.GROWTH: 3,
        }
        
        self.plan_limits = {
            SubscriptionPlan.TRIAL: {
                "max_users": 2,
                "max_conversations_per_month": 50,
                "max_sms_per_month": 100,
                "max_leads": 100,
            },
            SubscriptionPlan.STARTER: {
                "max_users": 3,
                "max_conversations_per_month": 100,
                "max_sms_per_month": 500,
                "max_leads": 500,
            },
            SubscriptionPlan.PRO: {
                "max_users": 10,
                "max_conversations_per_month": 500,
                "max_sms_per_month": 2000,
                "max_leads": 2000,
            },
            SubscriptionPlan.GROWTH: {
                "max_users": -1,  # Unlimited
                "max_conversations_per_month": -1,
                "max_sms_per_month": -1,
                "max_leads": -1,
            },
        }
    
    def has_access(self, tenant: Tenant, required_plan: str) -> bool:
        """Check if tenant has access to a feature based on plan"""
        if tenant.subscription_status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
            return False
        
        required_plan_enum = SubscriptionPlan(required_plan.lower())
        tenant_plan_level = self.plan_hierarchy.get(tenant.subscription_plan, 0)
        required_plan_level = self.plan_hierarchy.get(required_plan_enum, 0)
        
        return tenant_plan_level >= required_plan_level
    
    def check_limit(self, tenant: Tenant, limit_type: str, current_usage: int = 0) -> tuple[bool, int]:
        """Check if tenant is within plan limits"""
        limits = self.plan_limits.get(tenant.subscription_plan, {})
        limit = limits.get(limit_type, 0)
        
        if limit == -1:  # Unlimited
            return True, -1
        
        remaining = limit - current_usage
        return current_usage < limit, remaining
    
    def get_available_features(self, tenant: Tenant) -> List[Feature]:
        """Get list of features available for tenant's plan"""
        return feature_flags.get_plan_features(tenant.subscription_plan.value)
    
    def can_use_feature(self, tenant: Tenant, feature: Feature) -> bool:
        """Check if tenant can use a specific feature"""
        return feature_flags.is_enabled(feature, tenant.subscription_plan.value)
    
    def update_usage(self, tenant: Tenant, usage_type: str, increment: int = 1):
        """Update tenant usage counters"""
        if usage_type == "conversations":
            tenant.current_month_conversations += increment
        elif usage_type == "sms":
            tenant.current_month_sms += increment
        
        self.db.commit()
        
        # Check if over limit
        if usage_type == "conversations":
            within_limit, remaining = self.check_limit(
                tenant, 
                "max_conversations_per_month", 
                tenant.current_month_conversations
            )
            if not within_limit:
                logger.warning("Tenant over conversation limit", 
                             tenant_id=str(tenant.id),
                             limit=self.plan_limits[tenant.subscription_plan]["max_conversations_per_month"],
                             usage=tenant.current_month_conversations)
        
        elif usage_type == "sms":
            within_limit, remaining = self.check_limit(
                tenant,
                "max_sms_per_month",
                tenant.current_month_sms
            )
            if not within_limit:
                logger.warning("Tenant over SMS limit",
                             tenant_id=str(tenant.id),
                             limit=self.plan_limits[tenant.subscription_plan]["max_sms_per_month"],
                             usage=tenant.current_month_sms)
    
    def reset_monthly_usage(self, tenant: Tenant):
        """Reset monthly usage counters"""
        tenant.current_month_conversations = 0
        tenant.current_month_sms = 0
        self.db.commit()
        
        logger.info("Monthly usage reset", tenant_id=str(tenant.id))
    
    def get_plan_details(self, plan: SubscriptionPlan) -> dict:
        """Get detailed information about a plan"""
        limits = self.plan_limits.get(plan, {})
        features = feature_flags.get_plan_features(plan.value)
        
        prices = {
            SubscriptionPlan.TRIAL: 0,
            SubscriptionPlan.STARTER: 149,
            SubscriptionPlan.PRO: 299,
            SubscriptionPlan.GROWTH: 499,
        }
        
        return {
            "name": plan.value.title(),
            "price": prices.get(plan, 0),
            "limits": limits,
            "features": [f.value for f in features],
        }