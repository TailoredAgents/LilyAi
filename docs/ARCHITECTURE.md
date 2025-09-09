# Lily AI Architecture

## System Overview

Lily AI is a multi-tenant SaaS platform designed for pressure washing businesses, built with a local-first development approach and production deployment readiness.

## Core Components

### Backend (FastAPI)
- **API Server**: FastAPI application handling REST endpoints and webhooks
- **Worker Process**: Background task processor for delayed message sending
- **Database**: PostgreSQL 16 for structured data storage
- **Cache/Queue**: Redis 7 for caching and task queuing

### Frontend (Next.js)
- **Web Application**: Next.js 14 with App Router
- **UI Components**: Tailwind CSS for styling
- **API Integration**: TypeScript client for backend communication

### External Integrations
- **Stripe**: Subscription billing and payment processing
- **Twilio**: Voice calls and SMS messaging
- **Cal.com**: Appointment booking and scheduling
- **Google Calendar**: Calendar event management
- **AWS S3**: Photo storage with presigned uploads

## Data Flow Diagrams

### Missed Call → SMS Flow
```
1. Customer calls business phone
2. Call goes to voicemail (no answer/busy)
3. Twilio sends webhook to /webhooks/twilio/voice
4. System validates signature and processes CallStatus
5. If missed call: enqueue MISSED_CALL_SMS task with 10-45s jitter
6. Worker processes task and sends SMS via Twilio
7. SMS includes friendly message asking for photos + ZIP
```

### Photo Quote Flow
```
1. Customer texts photos + ZIP code
2. SMS received via Chatwoot (when integrated)
3. System detects photos and location info
4. QuotingService calculates ballpark price using PriceBook rules
5. Response queued with jitter delay (10-45s)
6. SMS sent with quote range and booking link
```

### Booking Flow
```
1. Customer clicks booking link (Cal.com)
2. Customer selects time and provides details
3. Cal.com sends webhook to /webhooks/calcom
4. System creates internal Booking record
5. Google Calendar event created
6. SMS confirmation sent to customer
```

## Database Schema

### Core Entities
- **Tenant**: Multi-tenant isolation (company/business)
- **User**: Admin users for each tenant
- **Lead**: Potential customers with contact info
- **Conversation**: SMS/message thread with lead
- **Message**: Individual messages in conversation
- **Quote**: Generated price quotes with details
- **Booking**: Scheduled appointments
- **Subscription**: Stripe subscription data

### Key Relationships
- Tenant → Users (1:many)
- Tenant → Leads (1:many)
- Lead → Conversations (1:many)
- Conversation → Messages (1:many)
- Lead → Quotes (1:many)
- Lead → Bookings (1:many)

## Queue Architecture

### Jitter Queue (Redis ZSET)
- **Purpose**: Natural message delays (10-45 seconds)
- **Implementation**: Redis sorted set with timestamp scores
- **Task Types**:
  - `MISSED_CALL_SMS`: Follow-up after missed calls
  - `REVIEW_REQUEST_SMS`: Post-service review requests
  - `CHATWOOT_REPLY`: Automated chat responses (future)

### Worker Process
- **Concurrency**: Configurable (default: 4 concurrent tasks)
- **Retry Logic**: Exponential backoff up to 5 attempts
- **Monitoring**: Structured logging for all task processing

## Security

### Authentication & Authorization
- **API Keys**: External service integration
- **Webhook Signatures**: Cryptographic validation for all webhooks
- **Tenant Isolation**: All data scoped by tenant_id

### Data Protection
- **PII Handling**: Customer phone/email encrypted at rest (future)
- **SMS Compliance**: STOP/HELP command handling
- **Quiet Hours**: Respect customer timezone preferences

## Scalability Considerations

### Horizontal Scaling
- **Stateless API**: Multiple API instances behind load balancer
- **Worker Scaling**: Multiple worker processes for queue processing
- **Database**: PostgreSQL with connection pooling

### Performance Optimizations
- **Redis Caching**: Frequently accessed data
- **S3 Direct Upload**: Bypass API for photo uploads
- **Async Processing**: Non-blocking external API calls

## Deployment

### Local Development
- **Docker Compose**: All services in containers
- **Hot Reload**: Code changes reflected immediately
- **Tunnel Testing**: cloudflared for webhook testing

### Production (Render)
- **API Service**: FastAPI container with health checks
- **Worker Service**: Background task processor
- **Web Service**: Next.js static/SSR application
- **External Services**: Managed PostgreSQL and Redis

## Monitoring & Observability

### Logging
- **Structured Logs**: JSON format with contextual data
- **Request Tracing**: Unique IDs for request correlation
- **Error Tracking**: Comprehensive error logging with context

### Metrics (Future)
- **Business Metrics**: Leads, quotes, bookings per tenant
- **System Metrics**: API latency, queue depth, error rates
- **Billing Metrics**: Usage tracking for plan limits

## Integration Patterns

### Webhook Processing
1. **Signature Validation**: Verify webhook authenticity
2. **Idempotency**: Handle duplicate webhook deliveries
3. **Error Handling**: Graceful failure with logging
4. **Async Processing**: Queue heavy operations

### API Client Pattern
- **Retry Logic**: Exponential backoff for external calls
- **Circuit Breaker**: Fail fast when services are down
- **Rate Limiting**: Respect external API rate limits
- **Fallback**: Graceful degradation when integrations fail