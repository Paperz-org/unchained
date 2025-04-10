"""Tests for nested dependencies functionality."""

# Path constants
NESTED_PATH = "/nested-dependency"
DOUBLE_NESTED_PATH = "/double-nested-dependency"
OVERRIDE_NESTED_PATH = "/override-nested-dependency"
MIXED_DEPENDENCIES_PATH = "/mixed-dependencies"

# Test values
TEST_RETURN_VALUE_1 = "first_dependency"
TEST_RETURN_VALUE_2 = "second_dependency"
TEST_NESTED_VALUE = "nested_result"

# Expected output values
EXPECTED_NESTED_RESULT = f"{TEST_RETURN_VALUE_1}_{TEST_RETURN_VALUE_2}"
EXPECTED_DOUBLE_NESTED_RESULT = f"{TEST_RETURN_VALUE_1}_{TEST_RETURN_VALUE_2}_{TEST_RETURN_VALUE_1}"
