# Listmonk: Technical Review and Key Decisions

## Overview
Listmonk is a high-performance, self-hosted newsletter and mailing list manager. It is written in Go with a React-based admin UI, and is designed for speed, scalability, and ease of deployment.

## Key Technical Decisions
- **Language & Stack:** Go for backend (concurrency, performance), React for frontend (modern UX).
- **Database:** PostgreSQL is required; leverages advanced features (JSONB, full-text search).
- **API-First Design:** RESTful API powers all UI and integrations.
- **Bulk Messaging Engine:** Custom-built for high throughput, supports parallel delivery, queueing, and retries.
- **Template Engine:** Uses Go templates for message content personalization.
- **Double Opt-In:** Built-in support for double opt-in flows, with confirmation links and audit trails.
- **Preference Center:** Exposes endpoints and UI for subscribers to manage preferences and opt-out.
- **Unsubscribe Links:** Every message includes unique, secure unsubscribe URLs.
- **Webhooks:** Supports event webhooks for integration with external systems.
- **Admin UI:** Modern, single-page React app for list, campaign, and subscriber management.
- **Plugin System:** No formal plugin system, but API and webhooks allow for extensibility.

## Notable Approaches
- **Performance:** Designed for large lists (millions of subscribers) and high message volumes.
- **Data Model:** Separates lists, campaigns, subscribers, and templates for flexibility.
- **Compliance:** Implements best practices (double opt-in, clear unsubscribe), but leaves legal compliance enforcement to implementers.
- **Deployment:** Single binary for backend, easy Docker deployment, minimal external dependencies.

## References
- [Listmonk GitHub](https://github.com/knadh/listmonk)
- [Listmonk Docs](https://listmonk.app/docs/)
