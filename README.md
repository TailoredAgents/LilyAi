# Lily AI - Local-First MVP

Production-grade, multi-tenant SaaS for pressure washing businesses with AI-powered customer engagement, automated quoting, and booking management.

## Quick Start

### Prerequisites
- Docker Desktop for Mac
- Node.js 20+
- Python 3.11+
- cloudflared (for webhook tunneling)

Install missing dependencies:
```bash
# Install Docker Desktop from: https://docs.docker.com/desktop/install/mac/
brew install cloudflared
```

### Local Development

1. **Start core services**:
```bash
cp .env.example .env
cp .env infra/.env

docker compose -f infra/compose.core.yml up --build -d
```

2. **Access points**:
- API: http://localhost:8000/docs
- Web: http://localhost:3000
- Health: http://localhost:8000/health

### Webhook Testing with cloudflared

Start tunnel for webhook testing:
```bash
cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflared.log 2>&1 &
sleep 3
PUBLIC_URL=$(grep -Eo "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cloudflared.log | head -1)
echo "PUBLIC_API_URL=$PUBLIC_URL"
```

Configure webhooks:
- **Stripe**: `$PUBLIC_URL/webhooks/stripe`
- **Cal.com**: `$PUBLIC_URL/webhooks/calcom`  
- **Twilio Voice**: `$PUBLIC_URL/webhooks/twilio/voice`

## Features

### Day-1 MVP Loops
- **Missed Call → SMS**: Automatic SMS follow-up with booking link
- **Photo Quoting**: AI-powered ballpark quotes from customer photos
- **Smart Booking**: Cal.com integration with Google Calendar sync
- **Review Automation**: SMS review requests post-service
- **Stripe Billing**: Subscription management with 14-day trial

### Technical Features
- Multi-tenant architecture with tenant isolation
- Redis-based jitter queue for natural message delays (10-45s)
- Presigned S3 uploads for photo intake
- Webhook-driven integrations with signature validation
- STOP/HELP compliance for SMS
- Quiet hours enforcement per tenant timezone

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11), SQLAlchemy, Redis, PostgreSQL 16
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Queue**: Redis 7 ZSET-based delayed task processing
- **Storage**: S3 for photos, PostgreSQL for structured data
- **Deployment**: Docker Compose (local), Render-ready

### Service Plans
- **Starter**: $149/mo - Basic features, 100 conversations
- **Pro**: $299/mo - Advanced features, 500 conversations
- **Growth**: $499/mo - All features, unlimited conversations

## Development

### Running Tests
```bash
docker compose -f infra/compose.core.yml exec api pytest -q
```

### Code Quality
```bash
# Backend
docker compose -f infra/compose.core.yml exec api black .
docker compose -f infra/compose.core.yml exec api ruff check .

# Frontend  
cd web && npm run lint
```

## Vendored Code

This project vendors real code from permissive open-source projects:
- **Stripe**: Subscription and portal management
- **Twilio**: Voice/SMS webhooks and client libraries
- **Google**: Calendar API integration patterns
- **S3**: Presigned upload utilities

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for full attribution.

## License

Proprietary - All rights reserved