import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.jitter_queue import jitter_queue

client = TestClient(app)

@patch.object(jitter_queue, 'enqueue_delayed')
@patch('app.api.webhooks.twilio_voice.TwilioClient')
def test_twilio_missed_call_webhook(mock_twilio_client, mock_enqueue):
    """Test missed call webhook queues SMS task"""
    # Mock validation to return True
    mock_client_instance = mock_twilio_client.return_value
    mock_client_instance.validate_webhook.return_value = True
    
    # Mock successful task enqueuing
    mock_enqueue.return_value = "test_task_id"
    
    form_data = {
        "CallSid": "CA123456789",
        "CallStatus": "no-answer",
        "From": "+1234567890",
        "To": "+0987654321",
        "Direction": "inbound"
    }
    
    response = client.post("/webhooks/twilio/voice", data=form_data)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml; charset=utf-8"
    
    # Verify task was enqueued
    mock_enqueue.assert_called_once()
    call_args = mock_enqueue.call_args
    assert call_args[1]['task_type'] == "MISSED_CALL_SMS"
    assert call_args[1]['payload']['to_number'] == "+1234567890"

@patch('app.api.webhooks.twilio_voice.TwilioClient')
def test_twilio_answered_call_no_task(mock_twilio_client):
    """Test that answered calls don't trigger SMS tasks"""
    mock_client_instance = mock_twilio_client.return_value
    mock_client_instance.validate_webhook.return_value = True
    
    form_data = {
        "CallSid": "CA123456789",
        "CallStatus": "completed",  # Answered call
        "From": "+1234567890",
        "To": "+0987654321",
        "Direction": "inbound"
    }
    
    response = client.post("/webhooks/twilio/voice", data=form_data)
    
    assert response.status_code == 200

@patch('app.api.webhooks.twilio_voice.TwilioClient')
def test_twilio_invalid_signature(mock_twilio_client):
    """Test webhook with invalid signature"""
    mock_client_instance = mock_twilio_client.return_value
    mock_client_instance.validate_webhook.return_value = False
    
    form_data = {
        "CallSid": "CA123456789",
        "CallStatus": "no-answer",
        "From": "+1234567890",
        "To": "+0987654321"
    }
    
    response = client.post("/webhooks/twilio/voice", data=form_data)
    
    assert response.status_code == 401