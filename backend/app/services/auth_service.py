from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import structlog

from app.models.user import User
from app.models.tenant import Tenant
from app.models.enums import UserRole, SubscriptionPlan, SubscriptionStatus
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.schemas.auth import UserCreate, UserLogin

logger = structlog.get_logger()

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate, tenant_id: Optional[str] = None) -> User:
        # Check if user exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_data.role or UserRole.OPERATOR,
            tenant_id=tenant_id,
            is_active=True,
            is_verified=False,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info("User registered", user_id=str(user.id), email=user.email)
        return user
    
    def register_tenant_with_owner(self, tenant_data: dict, owner_data: UserCreate) -> tuple[Tenant, User]:
        # Check if tenant exists
        existing_tenant = self.db.query(Tenant).filter(Tenant.email == tenant_data["email"]).first()
        if existing_tenant:
            raise ValueError("Tenant with this email already exists")
        
        # Create tenant with trial
        tenant = Tenant(
            name=tenant_data["name"],
            company_name=tenant_data["company_name"],
            email=tenant_data["email"],
            phone=tenant_data.get("phone"),
            website=tenant_data.get("website"),
            address_line1=tenant_data.get("address_line1"),
            city=tenant_data.get("city"),
            state=tenant_data.get("state"),
            zip_code=tenant_data.get("zip_code"),
            country=tenant_data.get("country", "US"),
            timezone=tenant_data.get("timezone", "America/New_York"),
            subscription_plan=SubscriptionPlan.TRIAL,
            subscription_status=SubscriptionStatus.TRIALING,
            trial_ends_at=datetime.utcnow() + timedelta(days=14),
            is_active=True,
        )
        
        self.db.add(tenant)
        self.db.flush()  # Get tenant ID without committing
        
        # Create owner user
        owner = self.register_user(owner_data, tenant.id)
        owner.role = UserRole.OWNER
        owner.is_verified = True  # Auto-verify owner
        
        self.db.commit()
        self.db.refresh(tenant)
        self.db.refresh(owner)
        
        logger.info("Tenant registered with owner", 
                   tenant_id=str(tenant.id), 
                   owner_id=str(owner.id))
        
        return tenant, owner
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning("Authentication failed - user not found", email=email)
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning("Authentication failed - invalid password", user_id=str(user.id))
            return None
        
        if not user.is_active:
            logger.warning("Authentication failed - inactive user", user_id=str(user.id))
            return None
        
        logger.info("User authenticated", user_id=str(user.id))
        return user
    
    def create_tokens(self, user: User) -> dict:
        access_token = create_access_token(
            subject=str(user.id),
            tenant_id=str(user.tenant_id) if user.tenant_id else None
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            tenant_id=str(user.tenant_id) if user.tenant_id else None
        )
        
        # Store refresh token
        user.refresh_token = refresh_token
        self.db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        from app.core.security import decode_token
        
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or user.refresh_token != refresh_token:
                return None
            
            new_access_token = create_access_token(
                subject=str(user.id),
                tenant_id=str(user.tenant_id) if user.tenant_id else None
            )
            
            return new_access_token
        except Exception as e:
            logger.error("Token refresh failed", error=str(e))
            return None
    
    def logout_user(self, user: User):
        user.refresh_token = None
        self.db.commit()
        logger.info("User logged out", user_id=str(user.id))