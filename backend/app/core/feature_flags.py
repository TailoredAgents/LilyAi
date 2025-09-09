from typing import Dict, Any, Optional
from enum import Enum
from app.core.config import settings

class Feature(str, Enum):
    META_ADS = "meta_ads"
    GOOGLE_ADS = "google_ads"
    JOBBER_SYNC = "jobber_sync"
    HCP_SYNC = "hcp_sync"
    AI_QUOTING = "ai_quoting"
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_BRANDING = "custom_branding"
    API_ACCESS = "api_access"
    BULK_SMS = "bulk_sms"
    REVIEW_AUTOMATION = "review_automation"

class FeatureFlags:
    def __init__(self):
        self.flags = {
            Feature.META_ADS: settings.ENABLE_META_ADS,
            Feature.GOOGLE_ADS: settings.ENABLE_GOOGLE_ADS,
            Feature.JOBBER_SYNC: settings.ENABLE_JOBBER_SYNC,
            Feature.HCP_SYNC: settings.ENABLE_HCP_SYNC,
            Feature.AI_QUOTING: True,
            Feature.ADVANCED_ANALYTICS: True,
            Feature.CUSTOM_BRANDING: False,
            Feature.API_ACCESS: True,
            Feature.BULK_SMS: True,
            Feature.REVIEW_AUTOMATION: True,
        }
        
        self.plan_features = {
            "starter": [
                Feature.AI_QUOTING,
                Feature.REVIEW_AUTOMATION,
            ],
            "pro": [
                Feature.AI_QUOTING,
                Feature.REVIEW_AUTOMATION,
                Feature.ADVANCED_ANALYTICS,
                Feature.BULK_SMS,
            ],
            "growth": [
                Feature.AI_QUOTING,
                Feature.REVIEW_AUTOMATION,
                Feature.ADVANCED_ANALYTICS,
                Feature.BULK_SMS,
                Feature.API_ACCESS,
                Feature.CUSTOM_BRANDING,
                Feature.META_ADS,
                Feature.GOOGLE_ADS,
                Feature.JOBBER_SYNC,
                Feature.HCP_SYNC,
            ],
        }
    
    def is_enabled(self, feature: Feature, tenant_plan: Optional[str] = None) -> bool:
        # Check if feature is globally enabled
        if not self.flags.get(feature, False):
            return False
        
        # Check if tenant plan has access
        if tenant_plan:
            plan_features = self.plan_features.get(tenant_plan.lower(), [])
            return feature in plan_features
        
        return True
    
    def get_plan_features(self, plan: str) -> list[Feature]:
        return self.plan_features.get(plan.lower(), [])
    
    def get_all_features(self) -> Dict[str, bool]:
        return {k.value: v for k, v in self.flags.items()}

feature_flags = FeatureFlags()