#!/bin/bash
# Run core tests for the OptIn Manager backend
# This script focuses on the most critical functionality tests

echo "Running OptIn Manager Core Tests"
echo "--------------------------------"

# Activate virtual environment
source ../.venv/bin/activate

# Run the core functionality tests
echo "Running OptIn API tests..."
python -m pytest tests/test_api_optin.py -v

echo "Running Auth User API tests..."
python -m pytest tests/test_api_auth_user.py -v

echo "Running Contact API tests..."
python -m pytest tests/test_api_contact.py -v

echo "Running Consent API tests..."
python -m pytest tests/test_api_consent.py -v

echo "Running Message Template API tests..."
python -m pytest tests/test_api_message_template.py -v

echo "Running Verification Code API tests..."
python -m pytest tests/test_api_verification_code.py -v

echo "Running Preferences API tests..."
python -m pytest tests/test_api_preferences.py -v

# Add more critical tests here as they are fixed

echo "--------------------------------"
echo "Core tests completed"
