#!/bin/bash
# Run all tests for the OptIn Manager backend and redirect output to backend_test_output.txt

echo "Running OptIn Manager Backend Tests"
echo "---------------------------------"

# Activate virtual environment
source ../.venv/bin/activate

# Run all backend tests and redirect output to backend_test_output.txt
python -m pytest ../tests/ -v > ../backend_test_output.txt 2>&1

echo "Backend tests completed. Results saved to backend_test_output.txt"
