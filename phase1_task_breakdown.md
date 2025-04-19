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
- [x] Split existing users model/table:
    - [x] Rename users to contacts (for opt-in/consent, no authentication, minimal PII)
    - [x] Create new users model/table for admin/staff/service accounts (with authentication, roles, audit info)
    - [x] Update all schemas, CRUD, and references accordingly
    _Status: COMPLETED – Contacts and Users models, schemas, CRUD, and API endpoints implemented. Admin-only protection enforced for /users endpoints._
- [x] User model (with PII fields, encryption/masking)  
  _Status: COMPLETED – Model, schema, CRUD, API, and tests implemented._
- [x] Consent model (status, channel, audit fields)  
  _Status: COMPLETED – Model, schema, CRUD, API, and tests implemented._
- [x] Message model (content, delivery status)  
  _Status: COMPLETED – Model, schema, CRUD, API, and tests implemented._
- [x] MessageTemplate model (default templates for SMS/email)  
  _Status: COMPLETED – Model, schema, CRUD, API, and tests implemented._
- [x] Message API: send, status, opt-in flow, timeline, compliance logic
    _Status: COMPLETED – /messages/send and /messages/{id} endpoints fully implemented with opt-in and timeline logic._
- [x] Consent management: status checking, timeline, event logging
    _Status: COMPLETED – Consent status and timeline included in message details and event logging._
- [x] Campaign model (for grouping messages)  
  _Status: COMPLETED – Model, schema, CRUD, API, and tests implemented._
- [x] VerificationCode model (for identity verification)  
  _Status: COMPLETED – Model, schema, CRUD, API, and tests implemented._
- [ ] Alembic migrations for all models
- [ ] Reinstate Alembic migrations after ERD/model stabilization at end of Phase 1. Remove Alembic from the workflow during early dev to avoid migration friction.
    _Note: Alembic migrations are deferred until Phase 1 is stable, per project guidance._

## 3. Backend API Endpoints (FastAPI)
- [x] Update all endpoints to use contacts (not users) for opt-in/consent flows
- [x] Add endpoints for admin/staff user management (create, update, list, disable)
- [x] Ensure contacts cannot authenticate or access as users
- [x] Authentication & Authorization (OAuth2/JWT, code verification, backend-enforced)
    _Status: COMPLETED – Admin/staff endpoints protected. Contacts are non-authenticated._
- [x] CRUD endpoints for all models (User, Consent, Message, MessageTemplate, Campaign, VerificationCode)  
  _Status: COMPLETED – All CRUD endpoints and tests implemented._
- [x] Minimal admin endpoints: list contacts, messages, analytics
    _Status: COMPLETED – Admin endpoints for listing contacts, messages, and analytics are implemented and admin-protected._
- [x] Verification endpoints (send code, verify code)
    _Status: ENDPOINTS ADDED – Backend endpoints for sending and verifying codes implemented, but not yet verified in DEV due to SQLite/Postgres config issue. Next: ensure backend runs with SQLite, endpoints available, and frontend can complete opt-out flow._
- [x] Opt-in/Opt-out endpoints (with verification flow)
    _Status: ENDPOINTS ADDED – Backend endpoints for opt-in/opt-out with verification flow implemented, but not yet verified in DEV due to SQLite/Postgres config issue. Next: ensure backend runs with SQLite, endpoints available, and frontend can complete opt-out flow._
- [ ] Smart helper API: `POST /api/v1/messages/send_with_consent`
- [ ] Status check endpoint for messages
- [ ] Audit logging for all consent/message changes
- [ ] Data retention/cleanup jobs (basic)
- [ ] OpenAPI/Swagger documentation

## 4. Message Template System

## 4a. PII Minimization & Data Segregation
- [ ] Never store or return both email and phone together
- [ ] Do not store names or demographics
- [ ] Mask PII in logs and UI (email/phone masking)
- [ ] Ensure API never returns both email and phone in any response
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
- [x] Minimal admin interface (list subscribers, message history, analytics)
    _Status: COMPLETED – Admin endpoints for listing contacts, messages, and analytics are implemented and admin-protected._
- [ ] User management screen
- [ ] Consent management screen
- [ ] Message history screen
- [ ] Template management screen
- [ ] Simple dashboard/analytics (Phase 1 scope)
- [ ] Web forms for opt-in/opt-out (standard, not customizable)
- [ ] API client/middleware for secure backend communication

## 7. Compliance, Security, and Retention
- [ ] Ensure clear separation between contacts (no authentication, minimal PII) and users (authenticated accounts)
- [ ] Enforce that only users (admin/staff/service) can authenticate or perform admin actions
- [ ] Enforce backend-only authentication & authorization (no frontend bypass)
- [ ] Audit logging for all consent, verification, admin actions (comprehensive, immutable)
- [ ] Dashboard access for contacts gated by code verification (no history or PII until verified)
- [ ] Admins can submit opt-in, but state only updates after verification by contact
- [ ] Never associate or display both email and phone for a contact
- [ ] No names/demographics stored or shown
- [ ] PII encryption at rest and in transit
- [ ] Masking in logs and UI
- [ ] Data retention policy enforcement (deletion/archival)
- [ ] Audit trail for all consent/message actions

## 8. Testing
- [x] Unit tests for all models and APIs  
  _Status: COMPLETED – CRUD endpoint tests for all models._
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
