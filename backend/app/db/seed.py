import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import *
from app.models.enums import *
from app.core.security import get_password_hash

def seed_database():
    db = SessionLocal()
    
    try:
        # Create demo tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Demo Pressure Washing Co",
            company_name="Demo Pressure Washing Co",
            email="demo@pressurewash.com",
            phone="+1234567890",
            website="https://demo.pressurewash.com",
            address_line1="123 Demo Street",
            city="Miami",
            state="FL",
            zip_code="33101",
            country="US",
            timezone="America/New_York",
            subscription_plan=SubscriptionPlan.TRIAL,
            subscription_status=SubscriptionStatus.TRIALING,
            trial_ends_at=datetime.utcnow() + timedelta(days=14),
            is_active=True,
            quiet_hours_start=21,
            quiet_hours_end=9,
            auto_reply_enabled=True,
            review_delay_hours=24,
        )
        db.add(tenant)
        
        # Create tenant settings
        settings = TenantSettings(
            tenant_id=tenant.id,
            calcom_embed_url="https://cal.com/demo-pressure-wash",
            welcome_message="Hi! Thanks for reaching out to Demo Pressure Washing. How can we help you today?",
            quote_request_message="I'd be happy to provide a quote! Please share photos of the area and your address.",
            booking_confirmation_message="Your appointment is confirmed for {date} at {time}. We'll see you then!",
            review_request_message="Thank you for choosing Demo Pressure Washing! We'd love to hear about your experience: {review_link}",
            ai_tone="friendly",
            auto_reply_delay_seconds=30,
            max_auto_replies_per_conversation=5,
            review_request_delay_hours=24,
        )
        db.add(settings)
        
        # Create demo user (owner)
        owner = User(
            id=uuid.uuid4(),
            email="owner@demo.com",
            hashed_password=get_password_hash("demo123"),
            first_name="John",
            last_name="Owner",
            phone="+1234567890",
            role=UserRole.OWNER,
            is_active=True,
            is_verified=True,
            tenant_id=tenant.id,
        )
        db.add(owner)
        
        # Create operator user
        operator = User(
            id=uuid.uuid4(),
            email="operator@demo.com",
            hashed_password=get_password_hash("demo123"),
            first_name="Jane",
            last_name="Operator",
            phone="+1234567891",
            role=UserRole.OPERATOR,
            is_active=True,
            is_verified=True,
            tenant_id=tenant.id,
        )
        db.add(operator)
        
        # Create price book entries
        house_wash = PriceBook(
            tenant_id=tenant.id,
            name="House Wash",
            service_type=ServiceType.HOUSE_WASH,
            description="Complete exterior house washing",
            base_price=199.00,
            price_per_sqft=0.10,
            minimum_charge=199.00,
            material_multipliers={
                "vinyl": 1.0,
                "brick": 1.2,
                "stucco": 1.3,
                "wood": 1.4,
            },
            severity_multipliers={
                "light": 0.8,
                "moderate": 1.0,
                "heavy": 1.3,
            },
            is_active=True,
        )
        db.add(house_wash)
        
        driveway = PriceBook(
            tenant_id=tenant.id,
            name="Driveway Cleaning",
            service_type=ServiceType.DRIVEWAY,
            description="Driveway and sidewalk pressure washing",
            base_price=99.00,
            price_per_sqft=0.08,
            minimum_charge=99.00,
            material_multipliers={
                "concrete": 1.0,
                "asphalt": 1.1,
                "pavers": 1.3,
            },
            severity_multipliers={
                "light": 0.8,
                "moderate": 1.0,
                "heavy": 1.5,
            },
            is_active=True,
        )
        db.add(driveway)
        
        roof_wash = PriceBook(
            tenant_id=tenant.id,
            name="Roof Soft Wash",
            service_type=ServiceType.ROOF_WASH,
            description="Gentle roof cleaning to remove algae and stains",
            base_price=349.00,
            price_per_sqft=0.15,
            minimum_charge=349.00,
            material_multipliers={
                "shingle": 1.0,
                "tile": 1.2,
                "metal": 0.9,
            },
            severity_multipliers={
                "light": 0.9,
                "moderate": 1.0,
                "heavy": 1.4,
            },
            is_active=True,
            requires_in_person=True,
        )
        db.add(roof_wash)
        
        # Create sample leads
        lead1 = Lead(
            tenant_id=tenant.id,
            first_name="Sarah",
            last_name="Johnson",
            email="sarah.johnson@example.com",
            phone="+13055551234",
            address_line1="456 Palm Avenue",
            city="Miami",
            state="FL",
            zip_code="33130",
            status=LeadStatus.NEW,
            source=AttributionSource.ORGANIC,
            lead_score=75.0,
        )
        db.add(lead1)
        
        lead2 = Lead(
            tenant_id=tenant.id,
            first_name="Mike",
            last_name="Williams",
            email="mike.williams@example.com",
            phone="+13055555678",
            address_line1="789 Beach Road",
            city="Miami Beach",
            state="FL",
            zip_code="33139",
            status=LeadStatus.QUALIFIED,
            source=AttributionSource.GOOGLE_ADS,
            campaign_id="summer-special-2024",
            lead_score=85.0,
        )
        db.add(lead2)
        
        # Create channel accounts
        sms_channel = ChannelAccount(
            tenant_id=tenant.id,
            channel_type=ChannelType.SMS,
            name="Primary SMS",
            account_id="+1234567890",
            account_name="Demo Pressure Washing",
            is_active=True,
            is_verified=True,
        )
        db.add(sms_channel)
        
        # Commit all changes
        db.commit()
        
        print("✅ Database seeded successfully!")
        print("\nDemo accounts created:")
        print("  Owner: owner@demo.com / demo123")
        print("  Operator: operator@demo.com / demo123")
        print("\nTenant: Demo Pressure Washing Co")
        print("  - 14-day trial active")
        print("  - 3 price book entries")
        print("  - 2 sample leads")
        print("  - SMS channel configured")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    seed_database()