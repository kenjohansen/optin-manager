# OptIn Manager PRD

## 1. Product Overview
A compliant SMS notification management system that handles opt-in/opt-out processes and message delivery while ensuring regulatory compliance and best practices.

## 2. Core Requirements

### 2.1 Opt-In Management
- Support multiple opt-in methods:
  - Website/app form submission
  - In-person event registration
  - Customer service phone calls
  - Direct text message opt-in
- Implement both single and double opt-in flows
- Store and manage consent records
- Support campaign-specific opt-ins
- Handle transactional vs promotional message consent separately

### 2.2 Compliance Features
- Explicit consent tracking
- Clear opt-out instructions in all messages
- Automated STOP/HELP keyword handling
- Message frequency controls
- Content filtering for prohibited categories (SHAFT)
- Audit trail for all opt-in/opt-out actions
- Support for A2P 10DLC registration
- Custom link shortening (no generic shorteners)

### 2.3 Message Management
- Campaign management system
- Message templating
- Scheduled message delivery
- Rate limiting and throttling
- Delivery status tracking
- Support for different message types:
  - Transactional (order confirmations, 2FA)
  - Promotional (marketing campaigns)
  - Service updates
  - Appointment reminders

### 2.3.1 Provider Credentials Management and Security

- The provider secrets vault key is managed using a hybrid approach:

### 2.4 Verification & Preferences Workflows

#### 2.4.1 Contact Self-Service (Opt-In/Opt-Out)
- A contact (user) visits the Preferences page (formerly Opt-Out page) to check or change their opt-in/out status for email or SMS.
- The contact enters their email or phone number.
- The backend sends a verification code to the entered contact info (email/SMS).
- The contact enters the received code on the Preferences page.
- If the code is correct, the user is granted access to view and update their opt-in/out preferences for all campaigns associated with their contact info.
- This workflow ensures only the owner of the email/phone can access or change preferences.

#### 2.4.2 Verbal Opt-In (Double Opt-In by Authorized User)
- A Sales or Marketing team member (authenticated user) receives a verbal opt-in from a customer.
- The team member enters the customer’s email or phone and desired preferences into the system.
- The backend triggers a Double Opt-In:
    - Sends an email/SMS to the contact with: (a) the verbal authorization statement, (b) a link to the Preferences page, and (c) a verification code.
- The contact clicks the link to the Preferences page, which detects that the session is a Verbal Auth (because the user is logged in, or via a special link parameter).
- The contact enters the verification code (or requests a new one) to confirm their consent.
- The contact can then review and adjust their preferences as needed.

#### 2.4.3 Unified Preferences Page
- The Preferences page supports both workflows:
    - If there is **no authenticated user**, assume a contact is self-managing preferences (self-service).
    - If there **is an authenticated user**, assume this is a Verbal Auth/Double Opt-In flow.
- The page UI adapts to show the appropriate prompts and actions for each case.
- All verification codes are single-use, time-limited, and tracked for audit/compliance.

#### 2.4.4 Post-Verification Confirmation Messages
- After a contact has successfully verified their opt-in status, the system sends a confirmation SMS with the following elements:
  - Confirmation of successful opt-in
  - Company name identification
  - Description of message types they'll receive
  - HELP and STOP keyword instructions
  - Message and data rates disclaimer
  - Message frequency information
- Sample confirmation message template:
  ```
  Thank you for confirming your opt-in to {company_name} messages. You will now receive {message_types} from us. Reply HELP for assistance or STOP to unsubscribe at any time. Msg&data rates may apply. {frequency_info}
  ```
- HELP response message template:
  ```
  Thank you for contacting {company_name}. For assistance with your messaging preferences, please visit {preferences_url} or reply STOP to unsubscribe from all messages. Standard message & data rates may apply.
  ```
- STOP response message template:
  ```
  You have been unsubscribed from {company_name} messages. You will no longer receive SMS messages from this number. Reply HELP for help or visit {preferences_url} to manage your preferences.
  ```

    - Priority: ENV variable (`PROVIDER_VAULT_KEY`), HashiCorp Vault, K8s Secret, OS-protected file, fallback to project dir (dev only)
    - Linux: `/etc/optin-manager/provider_vault.key`, Windows: `%PROGRAMDATA%\OptInManager\provider_vault.key`
    - Never store key with vault file unless fallback is required (dev only, with warning)
    - Production deployments must use K8s Secret, Vault, or OS-protected file
    - Key rotation and audit trail supported
    - Rationale: separation of key and lock, compliance (SOC2/ISO27K), extensibility for cloud KMS/secret managers

- Admin UI for configuring branding (company name, privacy policy link, logo, colors)
- Admin UI for selecting email and SMS providers (e.g., AWS SES/SNS; extensible for others)
- Separate credential entry for email and SMS providers (access key, secret key, region, etc.)
- Credentials are stored securely in an **encrypted vault** (never in the main database, never in the frontend, never in plaintext after saving)
- **Vault Location:** `backend/vault/provider_secrets.vault` (encrypted, audit-ready, never committed to git)
- In production, may use Kubernetes Secrets or external Vault; in dev/testing, always use the local encrypted vault
- Admin UI shows only a "configured" status after save
- "Test Connection" feature for each provider to validate credentials from the UI
- Backend retrieves credentials from secure vault storage for sending email/SMS
- System is designed for future extensibility to support additional providers (e.g., Twilio, SendGrid, etc.)
- **SQLite DB Location (dev):** `backend/optin_manager.db`

### 2.4 Security & Privacy
- Encrypted storage of phone numbers
- Role-based access control
- No sharing of user data with third parties
- Secure API endpoints
- Compliance with privacy regulations

### 2.5 Integration Capabilities

#### 2.5.1 REST API
- Core Message API with Opt-in Flow:
  ```
  POST /api/v1/messages/send
  {
    "recipient": "+1234567890",
    "messageType": "PROMOTIONAL|TRANSACTIONAL",
    "content": "Message content",
    "campaignId": "optional-campaign-id",
    "optInFlow": {
      "enabled": true,
      "optInMessage": "Custom opt-in message",
      "fallbackEmail": "user@example.com",
      "waitForOptIn": true|false,
      "optInTimeoutMinutes": 1440,
      "onOptInSuccess": {
        "sendOriginalMessage": true|false,
        "customMessage": "Optional custom message"
      }
    }
  }
  ```
- Status Check API
- Webhook support
- CRM system integration capabilities
- Analytics and reporting tools

### 2.6 Web Interfaces

#### 2.6.1 Public Web Pages
- Opt-in landing pages:
  - Clear description of message types and frequency
  - Terms of service and privacy policy
  - Phone number validation
  - Campaign selection options
- Opt-out confirmation pages:
  - Confirmation of successful opt-out
  - Instructions for opting back in
  - Survey for feedback (optional)
  - Retention of preferences for future opt-in
- Preference Center:
  - Message type preferences
  - Frequency settings
  - Campaign subscriptions
  - Contact information updates

#### 2.6.2 Administrative Interface
- Campaign creation and management
- Template management
- Subscriber management
- Analytics dashboard
- Compliance monitoring
- Audit log viewer
- System configuration

## 3. Technical Requirements

### 3.1 Performance
- Message delivery < 5 seconds
- System uptime > 99.9%
- Support for high-volume campaigns
- Scalable architecture
- Web page load time < 2 seconds

### 3.2 Data Management
- Consent record retention
- Message history archival
- Audit logs
- Analytics data storage
- Preference history tracking

### 3.3 Monitoring
- Real-time delivery status
- Opt-out rate monitoring
- Campaign performance metrics
- System health monitoring
- Web interface usage analytics

## 4. Future Considerations
- Multi-country support
- Additional channel support (MMS, WhatsApp)
- AI-powered message optimization
- Advanced analytics and reporting
- Integration with additional messaging providers
- Mobile app for preference management

## 5. Success Metrics
- Opt-in conversion rate
- Message delivery rate
- Compliance violation rate (target: 0)
- Customer engagement metrics
- System reliability metrics
- Web interface satisfaction score
- Preference center usage rate
