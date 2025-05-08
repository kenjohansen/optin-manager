"""
core/encryption.py

Encryption utilities for handling PII data securely.

This module provides functions for encrypting and decrypting personally identifiable
information (PII) such as email addresses and phone numbers, as well as generating
deterministic IDs from this data. These utilities are essential for protecting
sensitive user information while still allowing the system to function effectively.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

import os
import hashlib
import base64
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

# Get encryption key from environment variable or use a default for development
# In production, this should ALWAYS come from a secure environment variable
DEFAULT_DEV_KEY = "LKrSPTm-DkUx5eI4_AYl6Jn2vxONZKi9xnXQ3GdwJ5c="  # Only for development!
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", DEFAULT_DEV_KEY)

# Initialize the cipher suite with the encryption key
try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
    logger.info("Encryption service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize encryption service: {str(e)}")
    # In production, this should probably raise an exception to prevent starting with insecure settings
    # For now, we'll create a new key for development purposes
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    logger.warning(f"Using generated encryption key: {key.decode()}. Set this in your environment variables!")

def encrypt_pii(data):
    """
    Encrypt personally identifiable information.
    
    This function is critical for protecting user privacy and complying with
    data protection regulations like GDPR and CCPA. It ensures that sensitive
    personal information (emails and phone numbers) is never stored in plaintext
    in the database, reducing the risk of data breaches exposing user PII.
    
    As noted in the memories, contacts are stored with encrypted values, and this
    function provides that encryption capability. The system uses Fernet symmetric
    encryption, which provides authenticated encryption to protect against
    tampering and unauthorized decryption.
    
    Args:
        data (str): The PII data to encrypt (email or phone)
        
    Returns:
        str: The encrypted data as a base64-encoded string
    """
    if not data:
        return None
    
    try:
        # Convert string to bytes, encrypt, and convert back to string
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return None

def decrypt_pii(encrypted_data):
    """
    Decrypt encrypted personally identifiable information.
    
    This function allows the system to access the original PII data when necessary
    for specific operations like sending messages or displaying information to the
    user who owns the data. Decryption is performed in memory and only when needed,
    ensuring that plaintext PII is never persistently stored.
    
    As noted in the memories, for partial searches or phone numbers, the system
    fetches records and decrypts them in memory to check for matches. This function
    enables that capability while maintaining security.
    
    Args:
        encrypted_data (str): The encrypted PII data
        
    Returns:
        str: The decrypted data
    """
    if not encrypted_data:
        return None
    
    try:
        # Convert string to bytes, decrypt, and convert back to string
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return None

def generate_deterministic_id(data):
    """
    Generate a deterministic ID from PII data.
    
    This function is a cornerstone of the system's privacy-preserving architecture.
    It creates a consistent, non-reversible ID from PII that can be used as a
    database key without storing the actual PII in plaintext. This enables lookups
    and relationships without exposing sensitive data.
    
    As noted in the memories, the system uses deterministic IDs derived from the
    contact value (email/phone) to enable lookups without decrypting the data,
    balancing security with functionality. For example, when searching for contacts,
    the system generates deterministic IDs from search terms and looks for matching
    patterns.
    
    The ID is generated using a keyed hash with part of the encryption key as salt,
    ensuring that the IDs cannot be reversed without the key, adding an extra layer
    of security.
    
    Args:
        data (str): The PII data to generate an ID from
        
    Returns:
        str: A deterministic ID (hex string) that will always be the same for the
             same input data
    """
    if not data:
        return None
    
    # Use a keyed hash with the encryption key for added security
    # This ensures the IDs can't be reversed without the key
    salt = ENCRYPTION_KEY[:16]  # Use part of the encryption key as salt
    h = hashlib.sha256((data + salt).encode())
    return h.hexdigest()

def mask_email(email):
    """
    Create a masked version of an email address for display purposes.
    
    This function supports privacy-conscious UI displays by showing only partial
    email addresses. It reveals just enough information for users to recognize
    their own email while hiding most of the characters to protect privacy when
    displayed on screen or in reports.
    
    As noted in the memories, the API response for contacts includes masked_value
    for display purposes. This function provides that masking capability for email
    addresses, ensuring that even in the UI, full PII is not unnecessarily exposed.
    
    Args:
        email (str): The email address to mask
        
    Returns:
        str: The masked email address (e.g., "j***@example.com") with only the
             first character of the username and the full domain visible
    """
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    if len(username) <= 1:
        masked_username = username
    else:
        masked_username = username[0] + '*' * min(len(username) - 1, 3)
    
    return f"{masked_username}@{domain}"

def mask_phone(phone):
    """
    Create a masked version of a phone number for display purposes.
    
    This function supports privacy-conscious UI displays by showing only partial
    phone numbers. It reveals just the last 4 digits, which is a common industry
    practice that allows users to recognize their own number while protecting
    privacy when displayed on screen or in reports.
    
    As noted in the memories, the API response for contacts includes masked_value
    for display purposes. This function provides that masking capability for phone
    numbers, ensuring that even in the UI, full PII is not unnecessarily exposed.
    
    Args:
        phone (str): The phone number to mask
        
    Returns:
        str: The masked phone number (e.g., "***-***-1234") with only the last
             4 digits visible
    """
    if not phone:
        return phone
    
    # Remove any non-digit characters
    digits = ''.join(c for c in phone if c.isdigit())
    
    # Keep only the last 4 digits unmasked
    if len(digits) <= 4:
        return digits
    else:
        visible_part = digits[-4:]
        masked_part = '*' * (len(digits) - 4)
        return masked_part + visible_part
