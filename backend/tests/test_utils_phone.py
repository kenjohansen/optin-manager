"""
tests/test_utils_phone.py

Tests for the phone utility functions.
"""
import pytest
from app.utils.phone_utils import normalize_phone_number, is_valid_phone_number, mask_phone_number

class TestPhoneUtils:
    """Test suite for phone utility functions."""
    
    def test_normalize_phone_number(self):
        """Test phone number normalization function."""
        # Test None/empty input
        assert normalize_phone_number(None) is None
        assert normalize_phone_number("") is None
        
        # Test US numbers (10 digits)
        assert normalize_phone_number("2065551234") == "+12065551234"
        assert normalize_phone_number("(206) 555-1234") == "+12065551234"
        assert normalize_phone_number("206-555-1234") == "+12065551234"
        assert normalize_phone_number("206.555.1234") == "+12065551234"
        
        # Test US numbers with country code (11 digits)
        assert normalize_phone_number("12065551234") == "+12065551234"
        assert normalize_phone_number("1-206-555-1234") == "+12065551234"
        assert normalize_phone_number("1 (206) 555-1234") == "+12065551234"
        
        # Test international numbers
        assert normalize_phone_number("+442071234567") == "+442071234567"  # UK
        assert normalize_phone_number("+33123456789") == "+33123456789"    # France
        
        # Test numbers with + already included
        assert normalize_phone_number("+12065551234") == "+12065551234"
        
        # Test other formats
        assert normalize_phone_number("442071234567") == "+442071234567"  # Without +

    def test_is_valid_phone_number(self):
        """Test phone number validation function."""
        # Test None/empty input
        assert is_valid_phone_number(None) is False
        assert is_valid_phone_number("") is False
        
        # Test valid E.164 format numbers
        assert is_valid_phone_number("+12065551234") is True  # US
        assert is_valid_phone_number("+442071234567") is True  # UK
        assert is_valid_phone_number("+33123456789") is True   # France
        
        # Test numbers that will be normalized
        assert is_valid_phone_number("2065551234") is True     # US without country code
        assert is_valid_phone_number("(206) 555-1234") is True # US with formatting
        
        # Test invalid numbers
        assert is_valid_phone_number("+123") is False  # Too short
        assert is_valid_phone_number("ABC") is False   # Not a number
        assert is_valid_phone_number("+1234567890123456789") is False  # Too long
    
    def test_mask_phone_number(self):
        """Test phone number masking function."""
        # Test None/empty input
        assert mask_phone_number(None) == ""
        assert mask_phone_number("") == ""
        
        # Test standard US number
        masked = mask_phone_number("+12065551234")
        assert masked.startswith("+12")
        assert masked.endswith("1234")
        assert "*" in masked
        assert len(masked) == len("+12065551234")
        
        # Test international number
        masked = mask_phone_number("+442071234567")
        assert masked.startswith("+44")
        assert masked.endswith("4567")
        assert "*" in masked
        
        # Test short number
        masked = mask_phone_number("+1234")
        assert masked.startswith("+1")
        assert "*" in masked
