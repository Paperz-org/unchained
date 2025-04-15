"""Tests for nested header dependencies."""

import re
from enum import Enum
from typing import Annotated, Dict, List, Optional

import pytest
from ninja.errors import HttpError

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    EXPECTED_HEADER_RESULT,
    HEADER_DEPENDENCY_PATH,
    TEST_HEADER_VALUE,
    TEST_RETURN_VALUE_1,
    NestedDependencyTestCase,
)
from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from tests.utils.test_case import (
    ExpectedResponse,
    get_async_test_case,
    get_sync_test_case,
)
from unchained import Depends, Unchained
from unchained.dependencies.header import Header


# Sync Routes
def first_dependency() -> str:
    return TEST_RETURN_VALUE_1


def header_dependency(x_test_header: Annotated[str, Header()]) -> str:
    return x_test_header


def nested_header_dependency(
    header_val: Annotated[str, Depends(header_dependency)],
    dep1: Annotated[str, Depends(first_dependency)],
) -> str:
    return f"{header_val}_{dep1}"


def header_route(header_result: Annotated[str, Depends(nested_header_dependency)]) -> str:
    return header_result


# Async Routes
async def first_dependency_async() -> str:
    return TEST_RETURN_VALUE_1


async def header_dependency_async(x_test_header: Annotated[str, Header()]) -> str:
    return x_test_header


async def nested_header_dependency_async(
    header_val: Annotated[str, Depends(header_dependency_async)],
    dep1: Annotated[str, Depends(first_dependency_async)],
) -> str:
    return f"{header_val}_{dep1}"


async def header_route_async(header_result: Annotated[str, Depends(nested_header_dependency_async)]) -> str:
    return header_result


# Optional header dependency
def optional_header_dependency(x_optional_header: Annotated[str, Header()] = "default_value") -> str:
    return x_optional_header


def optional_header_route(header_val: Annotated[str, Depends(optional_header_dependency)]) -> Dict[str, str]:
    return {"header_value": header_val}


async def optional_header_dependency_async(x_optional_header: Annotated[str, Header()] = "default_value") -> str:
    return x_optional_header


async def optional_header_route_async(
    header_val: Annotated[str, Depends(optional_header_dependency_async)],
) -> Dict[str, str]:
    return {"header_value": header_val}


# Multiple headers in a dependency
def multi_header_dependency(x_header1: Annotated[str, Header()], x_header2: Annotated[str, Header()]) -> Dict[str, str]:
    return {"header1": x_header1, "header2": x_header2}


def multi_header_route(headers: Annotated[Dict[str, str], Depends(multi_header_dependency)]) -> Dict[str, str]:
    return headers


async def multi_header_dependency_async(
    x_header1: Annotated[str, Header()], x_header2: Annotated[str, Header()]
) -> Dict[str, str]:
    return {"header1": x_header1, "header2": x_header2}


async def multi_header_route_async(
    headers: Annotated[Dict[str, str], Depends(multi_header_dependency_async)],
) -> Dict[str, str]:
    return headers


# Header validation with regex
def validated_header_dependency(x_validated_header: Annotated[str, Header()]) -> str:
    # Validate header format (only alphanumeric)
    if not re.match(r"^[a-zA-Z0-9]+$", x_validated_header):
        raise HttpError(status_code=400, message="Header must be alphanumeric")
    return x_validated_header


def validated_header_route(header_val: Annotated[str, Depends(validated_header_dependency)]) -> Dict[str, str]:
    return {"validated_header": header_val}


# Header validation with enum
class AllowedHeaderValues(str, Enum):
    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"


def enum_header_dependency(x_enum_header: Annotated[str, Header()]) -> str:
    # Check if header value is in allowed values
    try:
        return AllowedHeaderValues(x_enum_header)
    except ValueError:
        raise HttpError(
            status_code=400, message=f"Header must be one of: {', '.join([v.value for v in AllowedHeaderValues])}"
        )


def enum_header_route(header_val: Annotated[str, Depends(enum_header_dependency)]) -> Dict[str, str]:
    return {"enum_header": header_val}


test_cases = [
    NestedDependencyTestCase(
        route_func=header_route,
        request_headers={"X-Test-Header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=EXPECTED_HEADER_RESULT),
    ),
    NestedDependencyTestCase(
        route_func=header_route_async,
        request_headers={"X-Test-Header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=EXPECTED_HEADER_RESULT),
    ),
    # Optional header - provided
    NestedDependencyTestCase(
        route_func=optional_header_route,
        request_headers={"X-Optional-Header": "custom_value"},
        expected_response=ExpectedResponse(status=200, message={"header_value": "custom_value"}),
    ),
    # Optional header - using default
    NestedDependencyTestCase(
        route_func=optional_header_route,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"header_value": "default_value"}),
    ),
    # Optional header async - provided
    NestedDependencyTestCase(
        route_func=optional_header_route_async,
        request_headers={"X-Optional-Header": "custom_value"},
        expected_response=ExpectedResponse(status=200, message={"header_value": "custom_value"}),
    ),
    # Optional header async - using default
    NestedDependencyTestCase(
        route_func=optional_header_route_async,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"header_value": "default_value"}),
    ),
    # Multiple headers in a dependency
    NestedDependencyTestCase(
        route_func=multi_header_route,
        request_headers={"X-Header1": "value1", "X-Header2": "value2"},
        expected_response=ExpectedResponse(status=200, message={"header1": "value1", "header2": "value2"}),
    ),
    # Multiple headers async
    NestedDependencyTestCase(
        route_func=multi_header_route_async,
        request_headers={"X-Header1": "value1", "X-Header2": "value2"},
        expected_response=ExpectedResponse(status=200, message={"header1": "value1", "header2": "value2"}),
    ),
    # Validated header - valid
    NestedDependencyTestCase(
        route_func=validated_header_route,
        request_headers={"X-Validated-Header": "abc123"},
        expected_response=ExpectedResponse(status=200, message={"validated_header": "abc123"}),
    ),
    # Validated header - invalid
    NestedDependencyTestCase(
        route_func=validated_header_route,
        request_headers={"X-Validated-Header": "invalid@value"},
        expected_response=ExpectedResponse(status=400, message={"detail": "Header must be alphanumeric"}),
    ),
    # Enum header - valid
    NestedDependencyTestCase(
        route_func=enum_header_route,
        request_headers={"X-Enum-Header": "value1"},
        expected_response=ExpectedResponse(status=200, message={"enum_header": "value1"}),
    ),
    # Enum header - invalid
    NestedDependencyTestCase(
        route_func=enum_header_route,
        request_headers={"X-Enum-Header": "invalid_value"},
        expected_response=ExpectedResponse(
            status=400, message={"detail": "Header must be one of: value1, value2, value3"}
        ),
    ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_nested_header_dependency_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test nested header dependency with synchronous routes."""
    # Arrange
    getattr(app, method)(HEADER_DEPENDENCY_PATH)(case.route_func)

    # Act
    response = getattr(test_client, method)(HEADER_DEPENDENCY_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_nested_header_dependency_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test nested header dependency with asynchronous routes."""
    # Arrange
    getattr(app, method)(HEADER_DEPENDENCY_PATH)(case.route_func)

    # Act
    response = await getattr(async_test_client, method)(HEADER_DEPENDENCY_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
    assert response.json() == case.expected_response.message
