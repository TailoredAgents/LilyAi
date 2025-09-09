# Lily AI API Reference

Base URL: `http://localhost:8000` (development)

## Core Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "ok": true
}
```

### API Documentation
```http
GET /docs
```
Interactive OpenAPI/Swagger documentation

## Billing Endpoints

### Create Checkout Session
```http
POST /api/v1/billing/checkout
```

**Request Body:**
```json
{
  "plan_code": "starter|pro|growth",
  "tenant_id": "string",
  "customer_email": "string",
  "success_url": "string",
  "cancel_url": "string",
  "trial_days": 14
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_..."
}
```

### Create Portal Session
```http
POST /api/v1/billing/portal
```

**Request Body:**
```json
{
  "customer_id": "cus_...",
  "return_url": "string"
}
```

**Response:**
```json
{
  "portal_url": "https://billing.stripe.com/...",
  "session_id": "bps_..."
}
```

## Photo/Lead Endpoints

### Presign Photo Upload
```http
POST /api/v1/leads/{lead_id}/photos/presign
```

**Request Body:**
```json
{
  "tenant_id": "string",
  "lead_id": "string", 
  "file_extension": "jpg",
  "expiration_seconds": 3600
}
```

**Response:**
```json
{
  "upload_url": "https://...",
  "fields": {...},
  "file_key": "photos/tenant/lead/uuid.jpg",
  "file_id": "uuid",
  "expires_at": "2023-...",
  "max_size_bytes": 10485760
}
```

### Get Photo Download URL
```http
GET /api/v1/leads/{lead_id}/photos/{file_key}/download?expiration=3600
```

**Response:**
```json
{
  "download_url": "https://...",
  "expires_in_seconds": 3600
}
```

### List Lead Photos
```http
GET /api/v1/leads/{lead_id}/photos?tenant_id=string
```

**Response:**
```json
{
  "photos": [
    {
      "file_key": "photos/tenant/lead/uuid.jpg",
      "size_bytes": 1024000,
      "last_modified": "2023-...",
      "etag": "abc123"
    }
  ]
}
```

### Delete Photo
```http
DELETE /api/v1/leads/{lead_id}/photos/{file_key}
```

**Response:**
```json
{
  "status": "deleted"
}
```

## Webhook Endpoints

### Stripe Webhooks
```http
POST /webhooks/stripe
```

**Headers:**
- `Stripe-Signature`: Webhook signature

**Handled Events:**
- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

### Twilio Voice Webhooks
```http
POST /webhooks/twilio/voice
```

**Headers:**
- `X-Twilio-Signature`: Webhook signature

**Form Data:**
- `CallSid`: Unique call identifier
- `CallStatus`: Call status (no-answer, busy, failed, completed)
- `From`: Caller phone number
- `To`: Called phone number
- `Direction`: inbound/outbound

**Response:** TwiML XML

### Cal.com Webhooks
```http
POST /webhooks/calcom
```

**Headers:**
- `X-Cal-Signature`: Webhook signature

**Handled Events:**
- `BOOKING_CREATED`
- `BOOKING_CANCELLED`
- `BOOKING_RESCHEDULED`

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

### Common Status Codes
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized (invalid signature)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error
- `503`: Service Unavailable

## Authentication

### Webhook Authentication
All webhook endpoints validate signatures using the respective service's signing secrets:

- **Stripe**: HMAC-SHA256 with `STRIPE_WEBHOOK_SECRET`
- **Twilio**: RequestValidator with `TWILIO_AUTH_TOKEN`
- **Cal.com**: HMAC-SHA256 with `CALCOM_WEBHOOK_SECRET`

### API Key Authentication (Future)
Future versions will include API key authentication for tenant-specific endpoints.

## Rate Limiting

### Current Limits
- No explicit rate limiting implemented
- Relies on external service limits (Stripe, Twilio, etc.)

### Future Implementation
- Tenant-based rate limiting
- Redis-backed sliding window
- Plan-based limits (Starter: 100/hr, Pro: 500/hr, Growth: unlimited)

## Pagination

### Standard Format (Future)
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 1000,
    "pages": 20
  }
}
```

## Webhooks Best Practices

### For Webhook Consumers

1. **Verify Signatures**: Always validate webhook signatures
2. **Handle Idempotency**: Same webhook may be delivered multiple times
3. **Respond Quickly**: Return 200 status within 10 seconds
4. **Handle Failures**: Implement retry logic for processing failures
5. **Log Everything**: Comprehensive logging for debugging

### Webhook Retry Policy

External services (Stripe, Cal.com, Twilio) have their own retry policies:
- **Stripe**: Exponential backoff up to 3 days
- **Twilio**: Immediate retry, then exponential backoff
- **Cal.com**: Configurable retry settings

## Development

### Testing Webhooks Locally

1. Start cloudflared tunnel:
```bash
cloudflared tunnel --url http://localhost:8000
```

2. Configure webhook URLs in external services
3. Test with actual events or webhook testing tools
4. Monitor logs for processing details

### Mock Testing
Use webhook testing tools:
- **Stripe CLI**: `stripe listen --forward-to localhost:8000/webhooks/stripe`
- **ngrok**: Alternative to cloudflared
- **Webhook.site**: Online webhook testing