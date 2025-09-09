# Lily AI Integrations

## Overview

Lily AI integrates with external services for core business functionality. All integrations use native automations via Redis queue instead of n8n workflows.

## Stripe Integration

### Purpose
- Subscription billing and payment processing
- 14-day free trial management
- Customer portal for subscription management

### Configuration
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_GROWTH=price_...
```

### Setup Steps
1. Create Stripe account and get API keys
2. Create products and prices for each plan
3. Configure webhook endpoint: `https://your-domain.com/webhooks/stripe`
4. Select events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
5. Copy webhook secret to environment

### Webhook Events Handled
- **checkout.session.completed**: Create/update subscription, set tenant plan
- **customer.subscription.updated**: Sync subscription status changes
- **customer.subscription.deleted**: Handle subscription cancellation

## Twilio Integration

### Purpose
- Missed call → SMS automation
- SMS messaging for quotes and confirmations
- STOP/HELP compliance

### Configuration
```bash
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1234567890
```

### Setup Steps
1. Create Twilio account and get credentials
2. Purchase phone number for business
3. Configure Voice webhook: `https://your-domain.com/webhooks/twilio/voice`
4. Set HTTP POST method
5. Optional: Configure SMS webhook for STOP/HELP handling

### Voice Webhook Processing
- Validates Twilio signature
- Checks CallStatus for missed calls (no-answer, busy, failed)
- Queues MISSED_CALL_SMS task with 10-45s jitter delay
- Returns empty TwiML response

### SMS Features
- **Missed Call Follow-up**: Friendly message asking for photos + ZIP
- **STOP Handling**: Automatic unsubscribe confirmation
- **HELP Handling**: Information about the service

## Cal.com Integration

### Purpose
- Appointment booking and scheduling
- Google Calendar synchronization
- SMS confirmations for bookings

### Configuration
```bash
CALCOM_API_KEY=cal_...
CALCOM_WEBHOOK_SECRET=...
```

### Setup Steps (Cal.com Hosted)
1. Create Cal.com account
2. Set up event types (e.g., "Pressure Washing Estimate")
3. Configure webhook: `https://your-domain.com/webhooks/calcom`
4. Select events: BOOKING_CREATED, BOOKING_CANCELLED, BOOKING_RESCHEDULED
5. Get embed URL for your event type

### Self-Hosted Cal.com (Future)
For full control, deploy Cal.com instance:
```bash
# Add to compose.satellites.yml when needed
calcom:
  image: calcom/cal.com:latest
  environment:
    DATABASE_URL: postgresql://...
    NEXTAUTH_SECRET: ...
```

### Webhook Events Handled
- **BOOKING_CREATED**: Create internal booking, send SMS confirmation, create calendar event
- **BOOKING_CANCELLED**: Send cancellation SMS, update/delete calendar event
- **BOOKING_RESCHEDULED**: Send reschedule SMS, update calendar event

## Google Calendar Integration

### Purpose
- Create calendar events for bookings
- Sync appointments with business calendar
- Share calendar with team members

### Configuration
```bash
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### Setup Steps
1. Create Google Cloud Project
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials (Web application)
4. Add authorized redirect URIs
5. Download credentials JSON

### OAuth Flow
1. First-time setup requires OAuth consent
2. Credentials stored per tenant
3. Automatic refresh token handling
4. Fallback gracefully if not configured

### Calendar Event Creation
- **Title**: Service type + Customer name
- **Description**: Customer details and service info
- **Duration**: Based on service type (default: 1 hour)
- **Attendees**: Customer email (if provided)
- **Location**: Service address

## AWS S3 Integration

### Purpose
- Photo storage for quote requests
- Presigned uploads for direct client-to-S3 transfer
- Secure photo access with expiring URLs

### Configuration
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=lily-ai-photos
```

### Setup Steps
1. Create AWS account and IAM user
2. Create S3 bucket with private access
3. Configure IAM permissions for bucket access
4. Set up CORS policy for web uploads

### S3 Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT:user/lily-ai"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::lily-ai-photos/*"
    }
  ]
}
```

### CORS Configuration
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "POST", "PUT"],
    "AllowedOrigins": ["http://localhost:3000", "https://your-domain.com"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

## Native Automations (Replaces n8n)

### Redis-Based Queue System
- **Technology**: Redis ZSET for delayed task processing
- **Jitter**: Natural 10-45 second delays for human-like interaction
- **Reliability**: Exponential backoff retry with max 5 attempts
- **Monitoring**: Structured logging for all task processing

### Automation Types

#### Missed Call → SMS
```
Trigger: Twilio voice webhook (CallStatus: no-answer/busy/failed)
Delay: 10-45 seconds (random jitter)
Action: Send friendly SMS asking for photos + ZIP
Message: "Sorry we missed your call! 📞 Text us 2-3 photos..."
```

#### Review Request SMS
```
Trigger: Job completion (manual or API call)
Delay: 24 hours (configurable per tenant)
Action: Send review request SMS
Message: "Hi [name]! 🌟 How did we do with your cleaning?..."
```

#### Future: Chatwoot Replies
```
Trigger: Keyword detection in messages
Delay: 10-45 seconds (jitter)
Action: Send automated reply via Chatwoot API
```

## Error Handling & Monitoring

### Integration Health Checks
- **Stripe**: API key validation
- **Twilio**: Account status check
- **Google**: Calendar API accessibility
- **S3**: Bucket permissions test

### Failure Modes
- **Not Configured**: Return "service not available" messages
- **API Errors**: Log error, retry with backoff
- **Rate Limits**: Respect limits, queue for later
- **Timeouts**: Fail fast, log for investigation

### Monitoring
- **Webhook Success/Failure Rates**: Track per integration
- **Task Queue Depth**: Monitor queue backlog
- **API Response Times**: Track external service performance
- **Error Patterns**: Alert on repeated failures

## Compliance & Security

### SMS Compliance
- **STOP Commands**: Automatic unsubscribe with confirmation
- **HELP Commands**: Provide service information
- **Quiet Hours**: Respect tenant timezone settings (9 PM - 9 AM default)
- **Opt-out Tracking**: Maintain suppression lists per tenant

### Webhook Security
- **Signature Validation**: All webhooks cryptographically verified
- **HTTPS Only**: All webhook endpoints require HTTPS in production
- **Idempotency**: Handle duplicate webhook deliveries gracefully
- **Rate Limiting**: Prevent webhook flooding (future)

### Data Protection
- **PII Encryption**: Customer data encrypted at rest (future)
- **Access Logging**: All data access logged with user attribution
- **Tenant Isolation**: Strict data separation between tenants
- **Data Retention**: Configurable retention policies per tenant

## Testing & Development

### Local Testing
```bash
# Start cloudflared tunnel
cloudflared tunnel --url http://localhost:8000

# Test webhooks with real services
# Use webhook testing tools (Stripe CLI, etc.)
```

### Mock Testing
- **Unit Tests**: Mock external API calls
- **Integration Tests**: Use service sandboxes/test modes
- **Webhook Testing**: Validate signature verification and event handling

### Production Deployment
- All integrations work identically in production
- Environment variables managed securely
- Health checks verify integration status
- Gradual rollout for integration changes