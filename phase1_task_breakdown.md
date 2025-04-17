# Phase 1 (MVP) Task Breakdown – OptIn Manager

This document breaks down all Phase 1 deliverables into actionable tasks. Each task can be tracked as an issue/ticket in your project board.

---

## 1. Project Setup & Documentation
- [ ] Initialize backend repo: FastAPI, PostgreSQL, Alembic
- [ ] Initialize frontend repo: React (Vite)
- [ ] Set up Python virtual environment and requirements
- [ ] Set up project structure for separation of backend/frontend
- [ ] Migrate and adapt PRD.md and DEPLOYMENT.md
- [ ] Create architecture and ERD documentation

## 2. Core Database Models & Migrations
- [ ] User model (with PII fields, encryption/masking)
- [ ] Consent model (status, channel, audit fields)
- [ ] Message model (content, delivery status)
- [ ] MessageTemplate model (default templates for SMS/email)
- [ ] Campaign model (for grouping messages)
- [ ] VerificationCode model (for identity verification)
- [ ] Alembic migrations for all models

## 3. Backend API Endpoints (FastAPI)
- [ ] CRUD endpoints for all models (User, Consent, Message, MessageTemplate, Campaign)
- [ ] Verification endpoints (send code, verify code)
- [ ] Opt-in/Opt-out endpoints (with verification flow)
- [ ] Smart helper API: `POST /api/v1/messages/send_with_consent`
- [ ] Status check endpoint for messages
- [ ] Audit logging for all consent/message changes
- [ ] Data retention/cleanup jobs (basic)
- [ ] OpenAPI/Swagger documentation

## 4. Message Template System
- [ ] Implement default SMS/email templates (opt-in invite, confirmation, transactional, promotional, opt-out confirmation)
- [ ] Template selection logic (allow user to specify or use default)
- [ ] Enforce opt-out/unsubscribe language in all templates
- [ ] Template rendering engine (variable substitution)

## 5. Identity Verification Flows
- [ ] Generate and send verification codes (SMS/email)
- [ ] Store and validate codes
- [ ] Link verification to consent changes
- [ ] Mask PII in logs and UI

## 6. Frontend (React Admin UI)
- [ ] User management screen
- [ ] Consent management screen
- [ ] Message history screen
- [ ] Template management screen
- [ ] Simple dashboard/analytics (Phase 1 scope)
- [ ] Web forms for opt-in/opt-out (standard, not customizable)
- [ ] API client/middleware for secure backend communication

## 7. Compliance, Security, and Retention
- [ ] PII encryption at rest and in transit
- [ ] Masking in logs and UI
- [ ] Data retention policy enforcement (deletion/archival)
- [ ] Audit trail for all consent/message actions

## 8. Testing
- [ ] Unit tests for all models and APIs
- [ ] Integration tests for verification and opt-in/out flows
- [ ] Mocking of external services (SMS/email)
- [ ] Validation/error handling tests

## 9. Deployment & Infrastructure
- [ ] Helm chart for backend deployment
- [ ] FluxCD configuration for GitOps
- [ ] Kubernetes manifests for all services
- [ ] Secure secret management
- [ ] Production DB setup (PostgreSQL HA)
- [ ] Backup and restore scripts

## 10. Success Criteria Review
- [ ] Confirm all MVP success criteria are met (see implementation_plan.md)

---

**Next Steps:**
- Create issues/tickets from this breakdown in your project board.
- Assign owners and track progress.
- Begin with project setup and core models, then proceed to API, frontend, and compliance tasks.
