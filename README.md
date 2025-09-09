# Lily AI - Multi-Tenant SaaS for Pressure Washing Businesses

Production-ready SaaS platform for exterior cleaning businesses with AI-powered customer engagement, automated quoting, and booking management.

## Quick Start

### Prerequisites
- Docker Desktop
- Node.js 20+
- Python 3.11+
- GitHub CLI (optional for forking)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/lily-saas.git
cd lily-saas

# Copy environment files
cp .env.example infra/.env
cp web/.env.local.example web/.env.local

# Start core services
docker compose -f infra/compose.core.yml up --build -d

# Start satellite services (Chatwoot, n8n)
docker compose -f infra/compose.satellites.yml up -d

# Run database migrations
docker compose -f infra/compose.core.yml exec api alembic upgrade head

# Seed initial data
make seed
```

### Access Points
- **API**: http://localhost:8000/docs
- **Web App**: http://localhost:3000
- **Chatwoot**: http://localhost:8080
- **n8n**: http://localhost:5678

## Features

### Day-1 MVP Loops
- **Unified Inbox**: SMS, Instagram DM, Facebook Messenger via Chatwoot
- **Auto-Quoting**: AI-powered ballpark quotes from customer photos
- **Missed Call to Text**: Automatic SMS follow-up with booking link
- **Smart Booking**: Cal.com integration with Google Calendar sync
- **Review Management**: Automated review requests post-service
- **Jittered AI Responses**: Natural 10-45 second delays for human-like interaction
- **Plan-Based Billing**: Stripe integration with 14-day trial

### Core Capabilities
- Multi-tenant architecture with tenant isolation
- JWT-based authentication
- Redis-powered rate limiting and job queues
- Webhook-driven integrations
- STOP/HELP compliance
- Quiet hours enforcement by tenant timezone

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy, Alembic, Redis
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 16
- **Queue**: Redis 7
- **Satellites**: Chatwoot (inbox), n8n (workflows), Cal.com (booking)

### Service Plans
- **Starter**: $149/mo - Basic features, 100 conversations
- **Pro**: $299/mo - Advanced features, 500 conversations
- **Growth**: $499/mo - All features, unlimited conversations

## Development

```bash
# Run tests
make test

# Format code
make format

# Type checking
make typecheck

# Database migrations
make migrate

# Create new migration
make migration name="add_new_feature"
```

## Acceptance Criteria

✅ **Inbox Flow**
- New SMS/DM appears in Chatwoot within 5 seconds
- Webhook creates Lead/Conversation/Message records
- AI replies with 10-45s jitter delay
- STOP/HELP commands respected

✅ **Quoting Flow**
- Keyword triggers quote request
- Photos analyzed for ballpark pricing
- Quote delivered with booking link
- In-person toggle for complex jobs

✅ **Booking Flow**
- Cal.com embed displays available slots
- Webhook creates internal booking record
- Google Calendar event created
- SMS confirmation sent

✅ **Review Flow**
- Job completion triggers review workflow
- Configurable delay (default 24h)
- SMS with review link sent
- Response tracked in system

✅ **Billing Flow**
- 14-day trial on signup
- Stripe Checkout for upgrades
- Plan features properly gated
- Usage tracking per tenant

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [API Reference](docs/API.md) - Endpoint documentation
- [Integrations](docs/INTEGRATIONS.md) - External service setup
- [Operations](docs/OPERATIONS.md) - Deployment and maintenance
- [Security](docs/SECURITY.md) - Authentication and compliance
- [Deployment](docs/DEPLOYMENT.md) - Production deployment guide
- [Pricebook](docs/PRICEBOOK.md) - Pricing rules and calculations
- [Roadmap](docs/ROADMAP.md) - Future features and timeline

## Support

For issues or questions, please check our documentation or open an issue in the repository.

## License

Proprietary - All rights reserved