"""
test_utils.py

Utility functions for testing in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

def remove_timestamp_fields(data):
    """
    Remove timestamp fields from a dictionary or list of dictionaries.
    This is useful for comparing API responses without worrying about timestamp fields.
    
    Args:
        data: Dictionary or list of dictionaries to process
        
    Returns:
        Processed data with timestamp fields removed
    """
    timestamp_fields = ['created_at', 'updated_at', 'timestamp', 'consent_timestamp', 'revoked_timestamp']
    
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k not in timestamp_fields}
    elif isinstance(data, list):
        return [remove_timestamp_fields(item) for item in data]
    else:
        return data
