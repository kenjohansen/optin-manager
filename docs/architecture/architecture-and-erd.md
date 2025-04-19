# OptIn Manager Architecture & ERD

## Overview
This document is the single source of truth for the OptIn Manager architecture and data model. All legacy references to a `users` table have been removed. The backend strictly separates:
- **Contacts:** End-user recipients of opt-in/consent, identified by email or phone (`contacts` table).
- **Auth Users:** Admin/staff/service accounts for authentication and admin UI (`auth_users` table).

All foreign keys referencing recipients use `contact_id` and point to `contacts.id`. No `users` table exists in the schema. This separation ensures clarity, scalability, and compliance.

### Configuration, Provider Credential Storage, and Security

#### Vault Key Management (Hybrid Approach)
- The provider secrets vault key is loaded using a prioritized hybrid approach:
    1. Environment variable (`PROVIDER_VAULT_KEY`)
    2. HashiCorp Vault (if configured)
    3. Kubernetes Secret (mounted as file)
    4. OS-protected file (Linux: `/etc/optin-manager/provider_vault.key`, Windows: `%PROGRAMDATA%\OptInManager\provider_vault.key`)
    5. Project directory fallback (dev only, with warning)
- **Key is never stored with the vault file** unless fallback is required for dev/testing.
- Production deployments should use K8s Secret, HashiCorp Vault, or OS-protected file.
- Key rotation is supported; all access is auditable.
- This design is compliant with SOC2/ISO27K and extensible to KMS/cloud secret managers.


#### Vault Key Management (Hybrid Approach)
- The provider secrets vault key is loaded using a prioritized hybrid approach:
    1. Environment variable (`PROVIDER_VAULT_KEY`)
    2. HashiCorp Vault (if configured)
    3. Kubernetes Secret (mounted as file)
    4. OS-protected file (Linux: `/etc/optin-manager/provider_vault.key`, Windows: `%PROGRAMDATA%\OptInManager\provider_vault.key`)
    5. Project directory fallback (dev only, with warning)
- **Key is never stored with the vault file** unless fallback is required for dev/testing.
- Production deployments should use K8s Secret, HashiCorp Vault, or OS-protected file.
- Key rotation is supported; all access is auditable.
- This design is compliant with SOC2/ISO27K and extensible to KMS/cloud secret managers.

- Admin UI allows configuration of:
    - Company branding (logo, colors, company name, privacy policy link)
    - Email/SMS provider selection (e.g., AWS SES/SNS; extensible for others)
    - Separate credentials for email and SMS providers (access key, secret key, region, etc.)
- **Provider Credentials Vault Design:**
    - All provider credentials are stored ONLY in a secure, encrypted vault at `backend/vault/provider_secrets.vault` (Fernet/AES-256 encryption).
    - The vault is never committed to git, never exposed to the frontend, and is not stored in the main database.
    - Only the backend service can access the vault; access is controlled by a master key provided via environment variable.
    - All access and modifications to the vault are auditable (API logs, file change times).
    - In production, external vaults or Kubernetes Secrets may be used, but the dev/test default is the encrypted local vault.
- **SQLite DB Location (dev):** `backend/optin_manager.db` (all persistent relational data except secrets).
- **Separation of Sensitive and Non-Sensitive Configuration:**
    - Sensitive config (provider credentials) is always in the encrypted vault.
    - Non-sensitive config (branding, connection/test status) is in the customization table (main DB).
- **Connection/Test Status Persistence:**
    - Connection/test status is persisted in the customization table, never in the vault.
    - UI can show connection/test status without exposing secrets.
- **Delete Credentials Feature:**
    - Admin UI provides a button to delete provider credentials at any time, resetting connection status to 'untested'.
    - This ensures customers have full control and can revoke access at any time, supporting compliance (ISO27K, SOC2, etc.).
- **Test Connection Feature:** For each provider, admin UI can test credentials via backend API (never exposes secrets).
- **Extensible Design:** System is built to add new providers and vault integrations as needed.

This document describes the architecture and data model (ERD) for the OptIn Manager system, focusing on:
- Backend: Data layer and API
- Frontend: Middleware and presentation
- Security and compliance features (PII encryption, masking, data retention)
- Identity verification for opt-in/opt-out (compliance-critical)
- Message template support (Phase 1) with a set of default templates for SMS and email (opt-in invite, confirmation, transactional, promotional, opt-out confirmation, etc.)
- When sending a message, the user can specify a template or the system uses a default template from the set
- All templates must include opt-out/unsubscribe language as appropriate
- Extensible design for web form templates (future phase)
- Smart helper API for compliant message delivery

### Phased Approach
- **Phase 1 (MVP):** Core consent management, message templates, smart send-with-consent API, standard web forms
- **Phase 2+:** Advanced web form templates, campaign management, preference center, analytics, etc.

---

## 1. System Architecture (Mermaid)

- **Message Templates:** Supported in Phase 1 for all outbound messages (opt-in invites, confirmations, marketing, etc.)
    - System includes a set of default templates for SMS and email covering all core use cases
    - When sending a message, the API allows the user to specify a template or defaults to a standard template
    - All templates must include opt-out/unsubscribe instructions (e.g., "Reply STOP to opt out", "Unsubscribe link")
- **Web Form Templates:** Standard forms in MVP; system is designed for future extensibility to allow customizable web forms for opt-in/opt-out flows.
- **Smart Helper API:** Exposed to handle compliant message delivery and consent workflow in a single call.

```mermaid
flowchart TD
  subgraph Backend
    DB[(PostgreSQL DB)]
    API[FastAPI Application]
    VCODE[Verification Service]
    DB <--> API
    API <--> VCODE
  end

  subgraph Frontend
    REACT[React Web App]
    MW[Middleware/API Client]
    REACT --> MW
    MW --> VFORM[Verification Form (Code Entry)]
  end

  API <--> MW

  subgraph Security
    ENC[Encryption at Rest & Transit]
    MASK[PII Masking & Logging]
    RET[Retention Policy Engine]
  end

  DB <--> ENC
  API <--> MASK
  DB <--> RET
```

- **Identity Verification:** When a user requests opt-in or opt-out, a verification code is sent to their email or phone. The status change is only saved after successful code entry.

- **Encryption at Rest:** PostgreSQL native encryption, encrypted volumes.
- **Encryption in Transit:** HTTPS/TLS for all API and DB connections.
- **Masking:**
    - **Email:** Show first character, mask the rest before @, show domain (e.g., `j***@gmail.com`).
    - **Phone:** Show country code and first digit after, mask the rest except last 4 digits (e.g., `1-3**-***-1234` for US number).
    - Masking applies in logs and UI; only authorized users can view full data.
- **Retention:** Automated deletion/archival per policy.

---

## 2. Entity Relationship Diagram (ERD, Mermaid)

```mermaid
erDiagram
  CONTACT ||--o{ CONSENT : has
  CONTACT ||--o{ MESSAGE : receives
  CONTACT ||--o{ PREFERENCE : sets
  CONTACT ||--o{ VERIFICATION_CODE : requests
  CAMPAIGN ||--o{ MESSAGE : sends
  CAMPAIGN ||--o{ CONSENT : manages
  MESSAGE }o--|| MESSAGE_TEMPLATE : uses
  // MESSAGE_TEMPLATE can be extended in future to support web form templates
  CONSENT ||--|| VERIFICATION_CODE : verified_by
  USER {
    id UUID
    email string
    phone string
    created_at date
    status string
  }
  CONSENT {
    id UUID
    user_id UUID
    campaign_id UUID
    channel string
    status string
    consent_timestamp date
    revoked_timestamp date
    verification_id UUID
    record string
  }
  VERIFICATION_CODE {
    id UUID
    user_id UUID
    code string
    channel string
    sent_to string
    expires_at date
    verified_at date
    purpose string
    status string
  }
  CAMPAIGN {
    id UUID
    name string
    type string // One of: "promotional", "transactional", "alert"
    created_at date
    status string
  }
  MESSAGE {
    id UUID
    user_id UUID
    campaign_id UUID
    template_id UUID
    channel string
    content string
    status string
    sent_at date
    delivery_status string
  }
  MESSAGE_TEMPLATE {
    id UUID
    name string
    content string
    channel string
  }
  PREFERENCE {
    id UUID
    user_id UUID
    preference_key string
    preference_value string
    updated_at date
  }
```

**Note:**
- Fields such as `email`, `phone`, `content`, `sent_to`, and `record` are encrypted and/or masked at rest and in presentation.
- Enum values and allowed values are described in the documentation above.

---

## Customization Feature

The backend supports a Customization feature, allowing administrators to:
- Upload a custom logo (served from `/static/uploads/`)
- Set primary and secondary UI colors

These settings are stored in the `customization` table and are accessible via secured API endpoints. This enables real-time branding for the web application.

## Migration Policy
- Migrations create only `contacts` and `auth_users` (not `users`).
- All tables referencing recipients use `contacts`.
- Legacy `users` references have been fully removed.

## Testing Policy
- Authentication dependencies are overridden in tests to allow full coverage of protected endpoints.
- All backend tests pass as of the latest commit, with evidence in `backend_test_output.txt`.

## 3. Compliance & Security Features
- **Encryption:** All PII fields (email, phone, message content) encrypted at rest; TLS for all connections.
- **Masking:**
    - Email: Show first character, mask the rest before @, show domain (e.g., `j***@gmail.com`).
    - Phone: Show country code and first digit after, mask the rest except last 4 digits (e.g., `1-3**-***-1234` for US number).
    - Masking applies in logs and UI; only authorized users can view full data.
- **Verification:** All opt-in/opt-out and preference changes require identity verification via code sent to the user’s email or phone. Verification is logged and linked to consent records for auditability.
- **Retention:** Data retention engine enforces deletion/archival per jurisdictional requirements (GDPR, CCPA, etc.).
- **Audit Trail:** All consent and message actions are logged for compliance.
- **Access Control:** RBAC for admin/API access.

---

## 4. Verification Flow (Compliance Requirement)

1. User initiates opt-in, opt-out, or preference change via web form or API.
2. System generates a verification code and sends it to the provided email or phone number.
3. User must enter the received code to confirm their identity.
4. Only upon successful verification is the consent or preference change recorded.
5. All verification events are logged and linked to consent records for compliance and auditability.

---

## 5. Data Retention Policy (Sample)
- **Consent Records:** Retained for 5 years or as required by law.
- **Testing:** React Testing Library + Jest for unit/integration testing; @testing-library/jest-dom for improved assertions; Cypress for E2E (optional)
- **Automated Testing:** All components and user flows will be covered by automated tests. Critical journeys (opt-in, opt-out, customization, dashboard) will have test coverage. Tests run in CI/CD to prevent regressions.
- **Messages:** Retained for 1 year, then archived or deleted.
- **User Data:** Deleted upon verified opt-out or inactivity per policy.
- **Logs:** Masked, retained for 90 days.

---

## 5. API Layer (OpenAPI/Swagger)
- RESTful endpoints for all entities (CRUD)
- Secure authentication & RBAC
- OpenAPI/Swagger docs auto-generated
- Versioned API endpoints (e.g., `/api/v1/`)
- **Smart Helper API:**
    - `POST /api/v1/messages/send_with_consent`
    - Accepts user identifier, message content, channel, template ID, and campaign info
    - Checks consent status, initiates opt-in workflow if needed, and ensures message is delivered only upon valid consent
    - Returns message status (sent, pending opt-in, blocked by opt-out)
    - Supports status checks and webhooks for workflow updates

---

## 6. Frontend Middleware & Presentation
- Middleware/API client handles auth, error handling, and masking
- React UI displays masked PII, supports opt-in/out, preference management, and admin features
- User-facing forms and admin dashboard separated
- **Web Form Templates:**
    - MVP uses standard, branded forms for opt-in/opt-out
    - System is architected to allow loading and rendering of custom web form templates in a future phase (e.g., by referencing a template ID or config)

---

## References
- [GDPR](https://gdpr-info.eu/)
- [CCPA](https://oag.ca.gov/privacy/ccpa)
- [TCPA](https://www.fcc.gov/sites/default/files/tcpa-rules.pdf)
- [OpenAPI](https://swagger.io/specification/)
