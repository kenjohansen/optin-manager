# Mautic: Technical Review and Key Decisions

## Overview
Mautic is an open-source marketing automation platform supporting email, SMS, and multi-channel campaigns. It is PHP-based with a Symfony framework backend and Vue.js frontend.

## Key Technical Decisions
- **Language & Stack:** PHP (Symfony) backend, Vue.js frontend.
- **Database:** Supports MySQL/MariaDB, PostgreSQL.
- **Campaign Automation:** Visual campaign builder with drag-and-drop logic, supports triggers, actions, and conditions.
- **Consent Management:** Tracks consent and preferences per contact, supports double opt-in, GDPR fields, and audit logs.
- **Multi-Channel:** Integrates with email, SMS, social, and web notifications.
- **Plugin System:** Extensive plugin architecture for integrations (CRM, SMS, analytics, etc.).
- **REST API:** Full-featured API for integration and automation.
- **Preference Center:** Customizable for user preferences and opt-out.
- **Segmentation:** Dynamic lists and segmentation based on contact attributes and behavior.
- **Admin UI:** Rich web UI for campaign, contact, and asset management.

## Notable Approaches
- **Compliance:** Includes GDPR tools, consent tracking, and double opt-in, but compliance is implementer’s responsibility.
- **Extensibility:** Highly modular with plugins and custom fields.
- **Scalability:** Suitable for SMBs and enterprises; supports clustering and scaling.
- **Deployment:** Composer-based install, Docker images available, requires PHP stack.

## References
- [Mautic GitHub](https://github.com/mautic/mautic)
- [Mautic Docs](https://docs.mautic.org/)
