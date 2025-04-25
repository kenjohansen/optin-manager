-- SQL script to create the consents table
CREATE TABLE IF NOT EXISTS consents (
    id VARCHAR NOT NULL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    optin_id VARCHAR,
    channel VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    consent_timestamp DATETIME,
    revoked_timestamp DATETIME,
    verification_id VARCHAR,
    record VARCHAR,
    notes VARCHAR,
    FOREIGN KEY (user_id) REFERENCES contacts(id),
    FOREIGN KEY (optin_id) REFERENCES optins(id),
    FOREIGN KEY (verification_id) REFERENCES verification_codes(id)
);
