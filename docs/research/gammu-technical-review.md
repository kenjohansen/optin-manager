# Gammu: Technical Review and Key Decisions

## Overview
Gammu is an open-source SMS gateway and utility for managing mobile devices and sending/receiving SMS. Written in C, it is widely used for integrating SMS with custom applications.

## Key Technical Decisions
- **Language & Stack:** C (core), Python bindings (Gammu SMSD), CLI tools.
- **Device Support:** Works with a wide range of GSM modems and phones.
- **SMS Daemon (SMSD):** Daemonized service for automated SMS sending/receiving, with pluggable backends (files, SQL, HTTP).
- **Database Integration:** Supports MySQL, PostgreSQL, SQLite for message queueing and status tracking.
- **Extensibility:** Scripts and hooks for custom logic on message events.
- **Delivery Reports:** Supports delivery status, logs, and error handling.
- **Opt-In/Opt-Out:** No built-in consent management; must be implemented at application level.
- **APIs:** CLI and Python API for integration.

## Notable Approaches
- **Reliability:** Focuses on robust device handling and message delivery.
- **Flexibility:** Can be used as a building block for SMS services, but lacks user management or compliance features.
- **Deployment:** Cross-platform, simple binaries or packages, minimal dependencies.

## References
- [Gammu GitHub](https://github.com/gammu/gammu)
- [Gammu Docs](https://wammu.eu/docs/manual/)
