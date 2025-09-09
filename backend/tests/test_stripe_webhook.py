import pytest
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_stripe_webhook_no_secret():
    """Test Stripe webhook when secret is not configured"""
    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "metadata": {"tenant_id": "test_tenant"}
            }
        }
    }
    
    response = client.post(
        "/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": "test_signature"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "webhook secret not configured"

@patch('app.services.stripe_service.settings.STRIPE_WEBHOOK_SECRET', 'test_secret')
@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_checkout_completed(mock_construct_event):
    """Test successful checkout completion webhook"""
    mock_event = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "metadata": {"tenant_id": "test_tenant"}
            }
        }
    }
    mock_construct_event.return_value = mock_event
    
    response = client.post(
        "/webhooks/stripe",
        json={},  # Raw body doesn't matter when mocked
        headers={"stripe-signature": "valid_signature"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_stripe_webhook_invalid_json():
    """Test webhook with invalid JSON"""
    response = client.post(
        "/webhooks/stripe",
        data="invalid json",
        headers={"content-type": "application/json", "stripe-signature": "test"}
    )
    
    assert response.status_code == 400