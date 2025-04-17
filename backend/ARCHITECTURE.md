# Opt-in Manager Backend Architecture (Phase 1)

## Overview
The backend is designed to strictly separate authentication and recipient/opt-in management. This ensures clarity, scalability, and maintainability.

---

## Data Models & Tables

### 1. Contact (contacts)
- **Purpose:** Represents recipients who can opt in/out of campaigns, identified by email or phone.
- **Table:** `contacts`
- **Key Fields:**
  - `id` (UUID, PK)
  - `email` (unique, nullable)
  - `phone` (unique, nullable)
  - `created_at`, `status`

### 2. AuthUser (auth_users)
- **Purpose:** Represents admin/staff/service accounts for authentication and admin UI access.
- **Table:** `auth_users`
- **Key Fields:**
  - `id` (UUID, PK)
  - `username` (unique, required)
  - `password_hash`
  - `role` (admin, staff, etc.)
  - `is_active`, `created_at`

### 3. Campaigns, Messages, Templates, Consents, Verification Codes
- All foreign keys that previously referenced `users` now reference `contacts` (via `contact_id`).
- No table named `users` exists in the schema.

---

## Key Design Decisions
- **No `users` Table:** All legacy references to a `users` table/model have been removed. The codebase uses only `contacts` for recipients and `auth_users` for authentication.
- **Clear Separation:** Authentication and recipient management are fully decoupled.
- **Consistent Naming:** All foreign keys and columns referencing recipients use `contact_id` and point to `contacts.id`.
- **Endpoints:**
  - `/api/v1/contacts/` for recipient CRUD
  - `/api/v1/auth_users/` for authentication management

---

## Migration Policy
- Migrations create `contacts` and `auth_users` tables only.
- All tables that previously referenced `users` now reference `contacts`.
- No `users` table is created or referenced.

---

## Testing
- Authentication dependencies are overridden in tests to allow unit testing of protected endpoints.
- All tests pass as of Phase 1 completion.

---

## Next Steps
- Review for any lingering references to `users` or `User` in code, docs, or migrations.
- Prepare for Phase 2: extend models/endpoints as needed for additional features.
