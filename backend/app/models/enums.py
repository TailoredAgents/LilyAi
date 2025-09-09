from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class SubscriptionPlan(str, Enum):
    TRIAL = "trial"
    STARTER = "starter"
    PRO = "pro"
    GROWTH = "growth"

class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    QUOTED = "quoted"
    BOOKED = "booked"
    LOST = "lost"
    CUSTOMER = "customer"

class ConversationStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    SNOOZED = "snoozed"

class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class MessageStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class QuoteStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    CANCELED = "canceled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class JobStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"

class ReviewStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    RECEIVED = "received"
    RESPONDED = "responded"

class ChannelType(str, Enum):
    SMS = "sms"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    VOICE = "voice"
    WEB = "web"

class ServiceType(str, Enum):
    HOUSE_WASH = "house_wash"
    ROOF_WASH = "roof_wash"
    DRIVEWAY = "driveway"
    DECK = "deck"
    FENCE = "fence"
    CONCRETE = "concrete"
    GUTTER_CLEANING = "gutter_cleaning"
    WINDOW_CLEANING = "window_cleaning"
    COMMERCIAL = "commercial"
    OTHER = "other"

class MaterialType(str, Enum):
    VINYL = "vinyl"
    BRICK = "brick"
    STUCCO = "stucco"
    WOOD = "wood"
    CONCRETE = "concrete"
    ASPHALT = "asphalt"
    METAL = "metal"
    COMPOSITE = "composite"
    OTHER = "other"

class Severity(str, Enum):
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"

class AttributionSource(str, Enum):
    ORGANIC = "organic"
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    REFERRAL = "referral"
    DIRECT = "direct"
    SMS = "sms"
    SOCIAL = "social"
    OTHER = "other"