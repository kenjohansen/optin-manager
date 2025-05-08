"""
app/utils/phone_utils.py

Phone number validation and formatting utilities for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
import re
import logging

logger = logging.getLogger(__name__)

def normalize_phone_number(phone_number):
    """
    Normalize a phone number to E.164 format.
    
    E.164 is the international standard format for phone numbers, which is
    required by most SMS providers and ensures consistent storage and processing
    of phone numbers across the system. Normalization is essential for proper
    contact identification, preventing duplicates with different formats, and
    ensuring deliverability of SMS messages.
    
    Args:
        phone_number (str): The phone number to normalize
        
    Returns:
        str: The normalized phone number in E.164 format (+[country code][number])
              or None if the input is empty
    """
    if not phone_number:
        return None
        
    # Remove all non-digit characters except leading +
    digits_only = re.sub(r'[^\d+]', '', phone_number)
    
    # If it doesn't start with +, assume it's a US number
    if not digits_only.startswith('+'):
        # If it's 10 digits, add +1 (US country code)
        if len(digits_only) == 10:
            return f"+1{digits_only}"
        # If it's 11 digits and starts with 1, add +
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            return f"+{digits_only}"
        # Otherwise, just add + (assume it already has country code)
        else:
            return f"+{digits_only}"
    
    return digits_only

def is_valid_phone_number(phone_number):
    """
    Check if a phone number is valid according to E.164 format requirements.
    
    Validation is critical for preventing errors in SMS delivery and ensuring
    that users provide legitimate contact information. This function uses the
    E.164 standard which requires a plus sign followed by 8-15 digits, covering
    all valid international phone numbers. Validation happens before attempting
    to send verification codes to avoid wasting resources on invalid numbers.
    
    Args:
        phone_number (str): The phone number to check
        
    Returns:
        bool: True if the phone number is valid according to E.164 format
    """
    if not phone_number:
        return False
        
    # Normalize the phone number first
    normalized = normalize_phone_number(phone_number)
    
    # Check if it's in E.164 format (+ followed by 8-15 digits)
    return bool(re.match(r'^\+\d{8,15}$', normalized))

def mask_phone_number(phone_number):
    """
    Mask a phone number for privacy while maintaining recognizability.
    
    Phone numbers are considered personally identifiable information (PII) and
    should not be displayed in full in user interfaces or logs. This masking
    approach preserves the country code and last 4 digits, which allows users
    to recognize their own number while protecting privacy. This is essential
    for compliance with privacy regulations like GDPR and CCPA.
    
    Args:
        phone_number (str): The phone number to mask
        
    Returns:
        str: The masked phone number (e.g., +1*****1234)
              or empty string if the input is empty
    """
    if not phone_number:
        return ""
        
    # Normalize the phone number first
    normalized = normalize_phone_number(phone_number)
    
    # Keep country code and first 3 digits, mask the rest
    if len(normalized) > 7:  # +1XXXXXXX
        country_code = normalized[:3]  # +1X
        masked_middle = '*' * (len(normalized) - 7)  # *****
        last_digits = normalized[-4:]  # XXXX
        return f"{country_code}{masked_middle}{last_digits}"
    else:
        # For very short numbers, just mask half
        visible_chars = max(2, len(normalized) // 3)
        return normalized[:visible_chars] + '*' * (len(normalized) - visible_chars)
