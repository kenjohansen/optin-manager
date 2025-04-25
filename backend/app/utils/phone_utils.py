"""
Phone number validation and formatting utilities.
"""
import re
import logging

logger = logging.getLogger(__name__)

def normalize_phone_number(phone_number):
    """
    Normalize a phone number to E.164 format.
    
    Args:
        phone_number (str): The phone number to normalize
        
    Returns:
        str: The normalized phone number in E.164 format
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
    Check if a phone number is valid.
    
    Args:
        phone_number (str): The phone number to check
        
    Returns:
        bool: True if the phone number is valid
    """
    if not phone_number:
        return False
        
    # Normalize the phone number first
    normalized = normalize_phone_number(phone_number)
    
    # Check if it's in E.164 format (+ followed by 8-15 digits)
    return bool(re.match(r'^\+\d{8,15}$', normalized))

def mask_phone_number(phone_number):
    """
    Mask a phone number for privacy.
    
    Args:
        phone_number (str): The phone number to mask
        
    Returns:
        str: The masked phone number
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
