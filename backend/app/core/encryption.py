"""
Encryption utilities for handling PII data securely.

This module provides functions for encrypting and decrypting personally identifiable
information (PII) such as email addresses and phone numbers, as well as generating
deterministic IDs from this data.
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
    This will always generate the same ID for the same input data.
    
    Args:
        data (str): The PII data to generate an ID from
        
    Returns:
        str: A deterministic ID (hex string)
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
    
    Args:
        email (str): The email address to mask
        
    Returns:
        str: The masked email address (e.g., "j***@example.com")
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
    
    Args:
        phone (str): The phone number to mask
        
    Returns:
        str: The masked phone number (e.g., "***-***-1234")
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
