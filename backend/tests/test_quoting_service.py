import pytest
from app.services.quoting_service import QuotingService, ServiceType, SeverityLevel, MaterialType

def test_basic_driveway_quote():
    """Test basic driveway quote calculation"""
    result = QuotingService.calculate_quote(
        tenant_id="test_tenant",
        service_type=ServiceType.DRIVEWAY,
        severity=SeverityLevel.LIGHT,
        sqft=400
    )
    
    assert result["service_type"] == "driveway"
    assert result["base_price"] == 150
    assert result["area_cost"] == 100  # 400 sqft * $0.25
    assert result["final_price"] == 250  # 150 + 100, rounded
    assert result["confidence"] == "medium"
    assert result["sqft_provided"] == 400

def test_heavy_cleaning_multiplier():
    """Test severity multiplier application"""
    result = QuotingService.calculate_quote(
        tenant_id="test_tenant",
        service_type=ServiceType.DRIVEWAY,
        severity=SeverityLevel.HEAVY,  # 1.6x multiplier
        sqft=400
    )
    
    # (150 base + 100 area) * 1.6 = 400, rounded to nearest $25 = $400
    assert result["final_price"] == 400
    assert result["severity_multiplier"] == 1.6

def test_material_multiplier():
    """Test material type multiplier"""
    result = QuotingService.calculate_quote(
        tenant_id="test_tenant",
        service_type=ServiceType.DRIVEWAY,
        severity=SeverityLevel.LIGHT,
        sqft=400,
        material=MaterialType.BRICK  # 1.2x multiplier
    )
    
    # (150 + 100) * 1.0 * 1.2 = 300
    assert result["final_price"] == 300
    assert result["material_multiplier"] == 1.2

def test_no_sqft_provides_range():
    """Test quote without square footage provides range estimate"""
    result = QuotingService.calculate_quote(
        tenant_id="test_tenant",
        service_type=ServiceType.HOUSE,
        severity=SeverityLevel.MODERATE
    )
    
    assert result["confidence"] == "low"
    assert "price_range" in result
    assert result["price_range"]["min"] < result["price_range"]["max"]
    assert result["estimated_sqft"] == 1500  # House estimate

def test_windows_unit_count():
    """Test windows service with unit count instead of sqft"""
    result = QuotingService.calculate_quote(
        tenant_id="test_tenant",
        service_type=ServiceType.WINDOWS,
        severity=SeverityLevel.LIGHT,
        unit_count=10  # 10 windows
    )
    
    # 80 base + (10 * 2.00) = 100, rounded to 100
    assert result["final_price"] == 100
    assert result["unit_count"] == 10

def test_parse_service_from_text():
    """Test service type parsing from text"""
    assert QuotingService.parse_service_from_text("clean my driveway") == ServiceType.DRIVEWAY
    assert QuotingService.parse_service_from_text("roof cleaning needed") == ServiceType.ROOF
    assert QuotingService.parse_service_from_text("house exterior wash") == ServiceType.HOUSE
    assert QuotingService.parse_service_from_text("clean windows") == ServiceType.WINDOWS
    assert QuotingService.parse_service_from_text("general cleaning") == ServiceType.OTHER

def test_parse_severity_from_text():
    """Test severity parsing from text"""
    assert QuotingService.parse_severity_from_text("extremely dirty") == SeverityLevel.EXTREME
    assert QuotingService.parse_severity_from_text("heavily stained") == SeverityLevel.HEAVY
    assert QuotingService.parse_severity_from_text("moderately dirty") == SeverityLevel.MODERATE
    assert QuotingService.parse_severity_from_text("light cleaning") == SeverityLevel.LIGHT

def test_generate_quote_message():
    """Test quote message generation"""
    quote_data = {
        "service_type": "driveway",
        "price_range": {"min": 200, "max": 300},
        "confidence": "medium"
    }
    
    message = QuotingService.generate_quote_message(quote_data)
    
    assert "Driveway cleaning" in message
    assert "$200-$300" in message or "$250" in message  # Should show range or average
    assert "📅" in message  # Should include scheduling emoji

def test_quote_error_handling():
    """Test quote calculation error handling"""
    # This would test actual error scenarios, but for now just test the structure
    quote_data = {"error": "Failed to calculate quote"}
    message = QuotingService.generate_quote_message(quote_data)
    
    assert "Sorry" in message
    assert "call us" in message