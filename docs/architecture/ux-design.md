# OptIn Manager UX Design

## Overview
Describes the user experience (UX) and high-level UI design for the OptIn Manager frontend, supporting all major use cases, compliance, and secure handling of sensitive data.

---

## Primary Use Cases
1. **Administration**
   - Secure login for admin/staff users (role-based access: Admin/Support)
   - Admin dashboard with navigation to all major features
2. **Customization**
   - Upload and preview organization logo
   - Set and preview primary/secondary colors
   - Live preview of branding changes
   - Enter provider credentials (email/SMS); UI only shows “configured” status after save
3. **Verbal Opt-ins**
   - Manual entry of opt-in requests received verbally (e.g., via phone)
   - Verification workflow (send code, confirm identity)
   - Audit trail for compliant recordkeeping
4. **Contact Opt-Out & Dashboard Access**
   - Self-service opt-out for contacts (unsubscribe from campaigns/products)
   - Verification workflow (send code, confirm identity)
   - Option to request access to Contact Dashboard for consent/preference management
   - Confirmation and feedback messaging
5. **Campaign Setup**
   - Create/edit campaigns, select type, assign templates, view analytics
6. **Product Setup**
   - Define products/services, link to campaigns, configure templates/alerts
7. **Contact Dashboard**
   - Search, view, manage contacts, consent/opt-in status, preferences, opt-outs

---

## UI Principles
- **Horizontally Centered Layout:** All main pages use Box sx={{ width: '90vw', margin: 'auto' }} for consistent centering.
- **Accessibility:** Keyboard navigable, screen-reader friendly.
- **Branding:** Custom logo/colors reflected throughout admin UI.
- **Compliance:** All opt-in/out actions are auditable and require verification where necessary.
- **Feedback:** Clear, actionable success/error messages.
- **Responsiveness:** Works on desktop and mobile.
- **Role-Based Navigation:** Admin (full), Support (read-only), Unauthenticated (Opt-Out/Login/Theme only).

---

## Security & Compliance in the UX
- **Secrets Storage:** Provider credentials are never stored or exposed in the frontend. All secrets are securely stored in the backend vault (`backend/vault/provider_secrets.vault`), encrypted at rest. All changes are logged (API-level audit trail).
- **Database:** Main database (SQLite for dev) is at `backend/optin_manager.db`. All persistent data except secrets is stored here.
- **No Secrets in UI:** UI never exposes or logs secrets. Vault and DB are never committed to git. Designed to pass security audits (ISO27K, SOC2, etc.).

---

## Screen Wireframes (Textual)
### 1. Admin Dashboard
- Sidebar: Navigation (Dashboard, Customization, Campaigns, Products, Contacts, Reports)
- Main: Quick stats (opt-ins, campaigns, alerts), recent activity

### 2. Customization
- Logo upload area (with preview)
- Color pickers for primary/secondary colors (with live preview)
- Save/cancel buttons
- **Provider Credentials:**
    - Fields for email and SMS provider credentials (access key, secret key, region)
    - “Test Connection” button for each provider
    - After save, UI only shows “configured” status

### 3. Verbal Opt-ins
- Manual entry form
- Verification workflow (send code, confirm identity)
- Audit trail display

### 4. Contact Opt-Out / Dashboard
- Self-service opt-out form
- Verification code workflow
- Option to access/manage preferences

### 5. Campaign/Product Setup
- Create/edit forms, template selection, analytics

### 6. Contact Dashboard
- Search, view, manage contacts, consent/opt-in status, preferences

---

## Summary
- All pages are horizontally centered and visually consistent.
- All secrets are backend-only and never exposed in the UI.
- UI is accessible, responsive, and compliant by design.

## Overview
This document describes the user experience (UX) and high-level UI design for the OptIn Manager frontend, supporting all major use cases and compliance requirements.

---

## Primary Use Cases
1. **Administration**
   - Secure login for admin/staff users
   - Admin dashboard with navigation to all major features
2. **Customization**
   - Upload and preview organization logo
   - Set and preview primary/secondary colors
   - Live preview of branding changes
3. **Verbal Opt-ins**
   - Manual entry of opt-in requests received verbally (e.g., via phone)
   - Verification workflow (send code, confirm identity)
   - Audit trail for compliant recordkeeping
4. **Contact Opt-Out & Dashboard Access**
   - Self-service opt-out for contacts (unsubscribe from campaigns/products)
   - Verification workflow (send code, confirm identity)
   - Option to request access to the Contact Dashboard for consent/preference management
   - Confirmation and feedback messaging
5. **Campaign Setup**
   - Create/edit campaigns
   - Select campaign type: promotional, transactional, alert
   - Assign message templates
   - View campaign status and analytics
6. **Product Setup**
   - Define products/services for which notifications may be sent
   - Link products to campaigns
   - Configure default templates/alerts per product
7. **Contact Dashboard**
   - Search, view, and manage contacts
   - View consent/opt-in status for each campaign/product
   - Manage preferences and opt-outs

---

## UI Principles
- **Accessibility:** All screens are keyboard navigable and screen-reader friendly
- **Branding:** Custom logo/colors are reflected throughout the admin UI
- **Compliance:** All opt-in/out actions are auditable and require verification where necessary
- **Feedback:** Success/error messages are clear and actionable
- **Responsiveness:** Works on desktop and mobile

---

## Screen Wireframes (Textual)

### 1. Admin Dashboard
- Sidebar: Navigation (Dashboard, Customization, Campaigns, Products, Contacts, Reports)
- Main: Quick stats (opt-ins, campaigns, alerts), recent activity

### 2. Customization
- Logo upload area (with preview)
- Color pickers for primary/secondary colors (with live preview)
- Save/cancel buttons
- **Provider Credentials:**
    - Fields for email and SMS provider credentials (access key, secret key, region)
    - Save/Update button color reflects connection status (green=success, yellow=untested, red=failed)
    - Test Connection button for each provider
    - **Delete Credentials button** for each provider, allowing the admin to remove credentials at any time
    - Status is shown using only non-sensitive data from the customization API (never from secrets vault)
- **Provider Credentials:**
    - Fields for email and SMS provider credentials (access key, secret key, region)
    - Save/Update button color reflects connection status (green=success, yellow=untested, red=failed)
    - Test Connection button for each provider
    - **Delete Credentials button** for each provider, allowing the admin to remove credentials at any time
    - Status is shown using only non-sensitive data from the customization API (never from secrets vault)

### 3. Verbal Opt-in
- Contact search/add
- Campaign/product selection
- Opt-in method: verbal (with compliance attestation)
- Verification: Send code, enter code, confirm
- Audit log display

### 4. Campaign Setup
- List of campaigns (type, status, metrics)
- Create/edit campaign form (name, type dropdown: promotional/transactional/alert, assign templates)
- Analytics tab (opt-in rates, delivery stats)

### 5. Product Setup
- List of products/services
- Create/edit product form
- Assign to campaigns
- Configure notification templates

### 6. Contact Dashboard
- Search bar, filters
- Contact details panel
- Consent status per campaign/product
- Opt-in/out controls
- Preference management

---

## Compliance & Audit
- All opt-in/out changes require verification and are logged
- Admins can export audit logs for compliance review

---

## Next Steps
- Finalize UI wireframes (visual)
- Choose frontend stack (React, Vue, etc.)
- Scaffold frontend project structure
- Implement authentication and API integration

---

*This document is maintained in `docs/architecture/ux-design.md` as the canonical UX reference.*
