# Kannel: Technical Review and Key Decisions

## Overview
Kannel is a robust open-source WAP and SMS gateway, widely used by telecom operators and enterprises for high-volume SMS delivery. Written in C, it is known for its performance and reliability.

## Key Technical Decisions
- **Language & Stack:** C (core), configuration-driven, HTTP API for integration.
- **SMS Gateway:** Handles SMS routing, delivery, and receipt at carrier scale.
- **Protocol Support:** SMPP, HTTP, CIMD2, and more for carrier and client integration.
- **Scalability:** Designed for high throughput, load balancing, and failover.
- **Routing Logic:** Flexible routing rules, sender/receiver filtering, and message transformation.
- **Admin Interface:** Web-based status and control panel.
- **Extensibility:** External scripts/hooks for custom logic.
- **Opt-In/Opt-Out:** No built-in consent or preference management; must be implemented externally.

## Notable Approaches
- **Performance:** Handles millions of messages per day; used by major operators.
- **Reliability:** Emphasizes uptime, message persistence, and failover.
- **Integration:** HTTP API for sending/receiving; can be integrated with custom opt-in/opt-out systems.
- **Deployment:** Runs on Linux/Unix, config-file driven, minimal runtime dependencies.

## References
- [Kannel GitHub](https://github.com/kannel/gateway)
- [Kannel User Guide](https://kannel.org/download/1.4.4/userguide-1.4.4/userguide.html)
