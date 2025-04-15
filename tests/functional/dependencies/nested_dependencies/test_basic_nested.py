"""Tests for basic nested dependencies."""

from dataclasses import dataclass
from typing import Annotated, Dict, Optional

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    EXPECTED_NESTED_RESULT,
    NESTED_PATH,
    TEST_RETURN_VALUE_1,
    TEST_RETURN_VALUE_2,
    NestedDependencyTestCase,
)
from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from tests.utils.test_case import (
    ExpectedResponse,
    get_async_test_case,
    get_sync_test_case,
)
from unchained import Depends, Unchained


# Sync Route
def first_dependency() -> str:
    return TEST_RETURN_VALUE_1


def second_dependency() -> str:
    return TEST_RETURN_VALUE_2


def nested_dependency(
    dep1: Annotated[str, Depends(first_dependency)],
    dep2: Annotated[str, Depends(second_dependency)],
) -> str:
    return f"{dep1}_{dep2}"


def nested_route(nested_result: Annotated[str, Depends(nested_dependency)]) -> str:
    return nested_result


# Async Routes
async def first_dependency_async() -> str:
    return TEST_RETURN_VALUE_1


async def second_dependency_async() -> str:
    return TEST_RETURN_VALUE_2


async def nested_dependency_async(
    dep1: Annotated[str, Depends(first_dependency_async)],
    dep2: Annotated[str, Depends(second_dependency_async)],
) -> str:
    return f"{dep1}_{dep2}"


async def nested_route_async(nested_result: Annotated[str, Depends(nested_dependency_async)]) -> str:
    return nested_result


# Shared dependency test
def shared_route(
    dep1: Annotated[str, Depends(first_dependency)],
    dep2: Annotated[str, Depends(first_dependency)],  # Same dependency used twice
) -> Dict[str, str]:
    return {"dep1": dep1, "dep2": dep2}


async def shared_route_async(
    dep1: Annotated[str, Depends(first_dependency_async)],
    dep2: Annotated[str, Depends(first_dependency_async)],  # Same dependency used twice
) -> Dict[str, str]:
    return {"dep1": dep1, "dep2": dep2}


# None-returning dependency test
def none_dependency() -> None:
    return None


def route_with_none_dependency(dep: Annotated[Optional[str], Depends(none_dependency)]) -> Dict[str, Optional[str]]:
    return {"dep": dep}


async def none_dependency_async() -> None:
    return None


async def route_with_none_dependency_async(
    dep: Annotated[Optional[str], Depends(none_dependency_async)],
) -> Dict[str, Optional[str]]:
    return {"dep": dep}


# Dataclass dependency test
@dataclass
class DependencyData:
    name: str
    value: int


def dataclass_dependency() -> DependencyData:
    return DependencyData(name="test", value=42)


def route_with_dataclass_dependency(data: Annotated[DependencyData, Depends(dataclass_dependency)]) -> Dict[str, str]:
    return {"name": data.name, "value": str(data.value)}


async def dataclass_dependency_async() -> DependencyData:
    return DependencyData(name="test", value=42)


async def route_with_dataclass_dependency_async(
    data: Annotated[DependencyData, Depends(dataclass_dependency_async)],
) -> Dict[str, str]:
    return {"name": data.name, "value": str(data.value)}


test_cases = [
    NestedDependencyTestCase(
        route_func=nested_route,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message=EXPECTED_NESTED_RESULT),
    ),
    NestedDependencyTestCase(
        route_func=nested_route_async,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message=EXPECTED_NESTED_RESULT),
    ),
    # Shared dependency test cases
    NestedDependencyTestCase(
        route_func=shared_route,
        request_headers={},
        expected_response=ExpectedResponse(
            status=200, message={"dep1": TEST_RETURN_VALUE_1, "dep2": TEST_RETURN_VALUE_1}
        ),
    ),
    NestedDependencyTestCase(
        route_func=shared_route_async,
        request_headers={},
        expected_response=ExpectedResponse(
            status=200, message={"dep1": TEST_RETURN_VALUE_1, "dep2": TEST_RETURN_VALUE_1}
        ),
    ),
    # None dependency test cases
    NestedDependencyTestCase(
        route_func=route_with_none_dependency,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"dep": None}),
    ),
    NestedDependencyTestCase(
        route_func=route_with_none_dependency_async,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"dep": None}),
    ),
    # Dataclass dependency test cases
    NestedDependencyTestCase(
        route_func=route_with_dataclass_dependency,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"name": "test", "value": "42"}),
    ),
    NestedDependencyTestCase(
        route_func=route_with_dataclass_dependency_async,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"name": "test", "value": "42"}),
    ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_basic_nested_dependency_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test basic nested dependency with synchronous routes."""
    # Arrange
    getattr(app, method)(NESTED_PATH)(case.route_func)

    # Act
    response = getattr(test_client, method)(NESTED_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_basic_nested_dependency_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test basic nested dependency with asynchronous routes."""
    # Arrange
    getattr(app, method)(NESTED_PATH)(case.route_func)

    # Act
    response = await getattr(async_test_client, method)(NESTED_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
