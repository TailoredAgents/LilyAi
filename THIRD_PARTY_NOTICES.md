# Third Party Notices

This project includes third-party code from various open source projects. Each vendored project maintains its original LICENSE file under `vendors/*/LICENSE`.

## Purpose

We vendor real code (not just dependencies) to:
- Ensure compatibility and customization
- Keep original licensing intact
- Maintain clear attribution to original authors

## Vendored Projects

The following projects are included in this repository:

### Stripe Integration

**vercel/nextjs-subscription-payments**
- Source: https://github.com/vercel/nextjs-subscription-payments
- License: MIT License
- Location: vendors/stripe/ui/
- Purpose: Next.js components and utilities for Stripe subscription management

**stripe-samples/subscription-use-cases**
- Source: https://github.com/stripe-samples/subscription-use-cases
- License: MIT License  
- Location: vendors/stripe/server/
- Purpose: Python server-side Stripe subscription examples

### Twilio Integration

**TwilioDevEd/webhooks-course**
- Source: https://github.com/TwilioDevEd/webhooks-course
- License: MIT License
- Location: vendors/twilio/voice/
- Purpose: Twilio voice webhook handling examples

**TwilioDevEd/clicktocall-flask**
- Source: https://github.com/TwilioDevEd/clicktocall-flask
- License: MIT License
- Location: vendors/twilio/sms/
- Purpose: Twilio SMS and voice call examples

### Google Calendar Integration

**googleworkspace/python-samples**
- Source: https://github.com/googleworkspace/python-samples
- License: Apache License 2.0
- Location: vendors/google/calendar/
- Purpose: Google Calendar API integration examples

### S3 Integration

**tiangolo/full-stack-fastapi-postgresql**
- Source: https://github.com/tiangolo/full-stack-fastapi-postgresql
- License: MIT License
- Location: vendors/fastapi_fs/
- Purpose: FastAPI S3 presigned URL utilities and patterns
