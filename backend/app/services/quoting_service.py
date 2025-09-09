from typing import Dict, Any, Optional, Tuple
import structlog
from enum import Enum

logger = structlog.get_logger()

class ServiceType(Enum):
    DRIVEWAY = "driveway"
    ROOF = "roof"
    HOUSE = "house"
    DECK = "deck"
    WALKWAY = "walkway"
    WINDOWS = "windows"
    OTHER = "other"

class SeverityLevel(Enum):
    LIGHT = "light"      # 1.0x multiplier
    MODERATE = "moderate" # 1.3x multiplier
    HEAVY = "heavy"      # 1.6x multiplier
    EXTREME = "extreme"   # 2.0x multiplier

class MaterialType(Enum):
    CONCRETE = "concrete"      # 1.0x multiplier
    ASPHALT = "asphalt"       # 0.9x multiplier
    BRICK = "brick"           # 1.2x multiplier
    VINYL = "vinyl"           # 0.8x multiplier
    WOOD = "wood"             # 1.1x multiplier
    METAL = "metal"           # 1.0x multiplier
    OTHER = "other"           # 1.0x multiplier

class QuotingService:
    """Service for generating ballpark quotes based on PriceBook rules"""
    
    # Base pricing per service type (minimum prices)
    BASE_PRICES = {
        ServiceType.DRIVEWAY: 150,
        ServiceType.ROOF: 300,
        ServiceType.HOUSE: 400,
        ServiceType.DECK: 200,
        ServiceType.WALKWAY: 100,
        ServiceType.WINDOWS: 80,
        ServiceType.OTHER: 200,
    }
    
    # Per-unit rates (price per square foot)
    PER_SQFT_RATES = {
        ServiceType.DRIVEWAY: 0.25,
        ServiceType.ROOF: 0.40,
        ServiceType.HOUSE: 0.35,
        ServiceType.DECK: 0.30,
        ServiceType.WALKWAY: 0.20,
        ServiceType.WINDOWS: 2.00,  # per window, not sqft
        ServiceType.OTHER: 0.30,
    }
    
    # Severity multipliers
    SEVERITY_MULTIPLIERS = {
        SeverityLevel.LIGHT: 1.0,
        SeverityLevel.MODERATE: 1.3,
        SeverityLevel.HEAVY: 1.6,
        SeverityLevel.EXTREME: 2.0,
    }
    
    # Material multipliers
    MATERIAL_MULTIPLIERS = {
        MaterialType.CONCRETE: 1.0,
        MaterialType.ASPHALT: 0.9,
        MaterialType.BRICK: 1.2,
        MaterialType.VINYL: 0.8,
        MaterialType.WOOD: 1.1,
        MaterialType.METAL: 1.0,
        MaterialType.OTHER: 1.0,
    }
    
    @classmethod
    def calculate_quote(
        cls,
        tenant_id: str,
        service_type: ServiceType,
        severity: SeverityLevel,
        sqft: Optional[int] = None,
        material: Optional[MaterialType] = None,
        unit_count: Optional[int] = None  # For windows, doors, etc.
    ) -> Dict[str, Any]:
        """
        Calculate a ballpark quote based on PriceBook rules
        
        Args:
            tenant_id: Tenant ID (for future per-tenant pricing)
            service_type: Type of service
            severity: Severity/condition level
            sqft: Square footage (optional)
            material: Surface material type
            unit_count: Count of units (for windows, etc.)
        
        Returns:
            Dictionary with quote details
        """
        try:
            base_price = cls.BASE_PRICES[service_type]
            per_unit_rate = cls.PER_SQFT_RATES[service_type]
            
            # Calculate base cost
            if sqft:
                area_cost = sqft * per_unit_rate
            elif unit_count and service_type == ServiceType.WINDOWS:
                area_cost = unit_count * per_unit_rate
            else:
                # No square footage provided, use estimation
                area_cost = 0
                sqft = None  # Mark as estimated
            
            subtotal = base_price + area_cost
            
            # Apply severity multiplier
            severity_multiplier = cls.SEVERITY_MULTIPLIERS[severity]
            subtotal *= severity_multiplier
            
            # Apply material multiplier
            if material:
                material_multiplier = cls.MATERIAL_MULTIPLIERS[material]
                subtotal *= material_multiplier
            else:
                material_multiplier = 1.0
            
            # Round to nearest $25
            final_price = round(subtotal / 25) * 25
            
            # If no square footage, provide range estimate
            if sqft is None:
                confidence = "low"
                price_range = {
                    "min": int(final_price),
                    "max": int(final_price * 1.5)  # 50% higher for range
                }
                estimated_sqft = cls._estimate_sqft_for_service(service_type)
            else:
                confidence = "medium" if sqft < 500 else "high"
                price_range = {
                    "min": int(final_price * 0.85),  # 15% lower
                    "max": int(final_price * 1.15)   # 15% higher
                }
                estimated_sqft = None
            
            result = {
                "service_type": service_type.value,
                "base_price": base_price,
                "area_cost": int(area_cost) if area_cost else 0,
                "severity_level": severity.value,
                "severity_multiplier": severity_multiplier,
                "material_type": material.value if material else None,
                "material_multiplier": material_multiplier,
                "subtotal": int(subtotal),
                "final_price": int(final_price),
                "price_range": price_range,
                "confidence": confidence,
                "sqft_provided": sqft,
                "estimated_sqft": estimated_sqft,
                "unit_count": unit_count,
                "tenant_id": tenant_id
            }
            
            logger.info(
                "Quote calculated",
                tenant_id=tenant_id,
                service_type=service_type.value,
                final_price=final_price,
                confidence=confidence
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Error calculating quote",
                error=str(e),
                tenant_id=tenant_id,
                service_type=service_type.value if service_type else None
            )
            return {
                "error": "Failed to calculate quote",
                "service_type": service_type.value if service_type else None,
                "tenant_id": tenant_id
            }
    
    @classmethod
    def _estimate_sqft_for_service(cls, service_type: ServiceType) -> int:
        """Provide rough square footage estimates for common service types"""
        estimates = {
            ServiceType.DRIVEWAY: 400,      # Typical 20x20 driveway
            ServiceType.ROOF: 1200,         # Small house roof
            ServiceType.HOUSE: 1500,        # Single story house exterior
            ServiceType.DECK: 300,          # Typical deck size
            ServiceType.WALKWAY: 100,       # Front walkway
            ServiceType.WINDOWS: 15,        # Number of windows
            ServiceType.OTHER: 500,         # General estimate
        }
        return estimates.get(service_type, 500)
    
    @classmethod
    def generate_quote_message(cls, quote_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable quote message for SMS/chat
        
        Args:
            quote_data: Quote calculation result
        
        Returns:
            Formatted quote message
        """
        try:
            if "error" in quote_data:
                return (
                    "Sorry, I couldn't calculate a quote right now. "
                    "Please call us for a personalized estimate!"
                )
            
            service_type = quote_data["service_type"].replace("_", " ").title()
            price_range = quote_data["price_range"]
            confidence = quote_data["confidence"]
            
            if confidence == "low":
                message = (
                    f"Great! For {service_type} cleaning, our ballpark range is "
                    f"${price_range['min']}-${price_range['max']}. 💰\n\n"
                    "For a more precise quote, we'd need the square footage or "
                    "a quick in-person assessment. Would you like to schedule "
                    "a free estimate? 📅"
                )
            else:
                avg_price = (price_range['min'] + price_range['max']) // 2
                message = (
                    f"Perfect! Based on your details, {service_type} cleaning "
                    f"would be approximately ${avg_price} "
                    f"(range: ${price_range['min']}-${price_range['max']}). 💰\n\n"
                    "This includes our standard cleaning process. "
                    "Ready to schedule? 📅"
                )
            
            return message
            
        except Exception as e:
            logger.error("Error generating quote message", error=str(e))
            return (
                "Thanks for your interest! Please call us for a personalized "
                "quote - we'd love to help with your cleaning needs!"
            )
    
    @classmethod
    def parse_service_from_text(cls, text: str) -> ServiceType:
        """
        Parse service type from customer message text
        
        Args:
            text: Customer message
        
        Returns:
            Detected service type
        """
        text_lower = text.lower()
        
        keywords = {
            ServiceType.DRIVEWAY: ["driveway", "drive", "garage", "parking"],
            ServiceType.ROOF: ["roof", "roofing", "shingle", "gutter"],
            ServiceType.HOUSE: ["house", "home", "siding", "exterior", "building"],
            ServiceType.DECK: ["deck", "patio", "porch", "balcony"],
            ServiceType.WALKWAY: ["walkway", "sidewalk", "path", "steps", "stairs"],
            ServiceType.WINDOWS: ["window", "glass", "pane"],
        }
        
        for service_type, service_keywords in keywords.items():
            if any(keyword in text_lower for keyword in service_keywords):
                return service_type
        
        return ServiceType.OTHER
    
    @classmethod
    def parse_severity_from_text(cls, text: str) -> SeverityLevel:
        """
        Parse severity level from customer message text
        
        Args:
            text: Customer message
        
        Returns:
            Detected severity level
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["extreme", "terrible", "awful", "disaster", "gross"]):
            return SeverityLevel.EXTREME
        elif any(word in text_lower for word in ["heavy", "bad", "dirty", "stained", "moldy"]):
            return SeverityLevel.HEAVY
        elif any(word in text_lower for word in ["moderate", "some", "bit", "little"]):
            return SeverityLevel.MODERATE
        else:
            return SeverityLevel.LIGHT