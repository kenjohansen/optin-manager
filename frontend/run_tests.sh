#!/bin/bash

# Navigate to the frontend directory
cd "$(dirname "$0")"

# Create a temporary file for the raw test output
npm test > test_raw_output.txt 2>&1

# Extract the test summary information and create a focused report
{
  echo "# FRONTEND TEST SUMMARY REPORT"
  echo "Generated: $(date)"
  echo ""
  
  # Extract test suite and test count information
  echo "## TEST RESULTS"
  TEST_SUITES=$(grep "Test Suites:" test_raw_output.txt)
  TESTS=$(grep "Tests:" test_raw_output.txt)
  TIME=$(grep "Time:" test_raw_output.txt)
  
  echo "$TEST_SUITES"
  echo "$TESTS"
  echo "$TIME"
  
  # Extract key metrics for the summary
  TOTAL_TESTS=$(echo "$TESTS" | grep -oE '[0-9]+ total' | grep -oE '[0-9]+')
  PASSED_TESTS=$(echo "$TESTS" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+')
  FAILED_TESTS=$(echo "$TESTS" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+')
  
  # Calculate pass percentage
  PASS_PERCENTAGE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
  
  echo ""
  echo "### SUMMARY"
  echo "Total Tests: $TOTAL_TESTS"
  echo "Passed: $PASSED_TESTS ($PASS_PERCENTAGE%)"
  echo "Failed: $FAILED_TESTS"
  echo ""
  
  # Extract overall coverage metrics
  echo "## OVERALL COVERAGE"
  grep "All files" test_raw_output.txt
  echo ""
  
  # Extract coverage by directory
  echo "## COVERAGE BY DIRECTORY"
  grep -A4 "All files" test_raw_output.txt | tail -n 4
  echo ""
  
  # Extract fully tested components (100% coverage)
  echo "## FULLY TESTED COMPONENTS (100% coverage)"
  grep "100 |      100 |     100 |     100" test_raw_output.txt
  echo ""
  
  # Extract components with low coverage (below 50%)
  echo "## COMPONENTS NEEDING ATTENTION (below 50% line coverage)"
  grep -E "\| +[0-4][0-9]\.[0-9]+ \|" test_raw_output.txt | grep -v "All files"
  grep -E "\| +[0-9]+ \|" test_raw_output.txt | grep -v "All files"
  echo ""
  
  # Add the full coverage report for reference
  echo "## DETAILED COVERAGE REPORT"
  grep -A 30 -- "---------------------------|---------|----------|---------|---------|" test_raw_output.txt
  
} > frontend_test_report.txt

# Clean up the raw output file
rm test_raw_output.txt

echo "Frontend test report saved to frontend_test_report.txt"
