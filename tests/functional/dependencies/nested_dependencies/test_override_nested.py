"""Tests for overriding nested dependencies."""

from typing import Annotated, Dict

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    EXPECTED_NESTED_RESULT,
    OVERRIDE_NESTED_PATH,
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


# Sync Routes
def first_dependency() -> str:
    return TEST_RETURN_VALUE_1


def second_dependency() -> str:
    return TEST_RETURN_VALUE_2


def nested_dependency(
    dep1: Annotated[str, Depends(first_dependency)],
    dep2: Annotated[str, Depends(second_dependency)],
) -> str:
    return f"{dep1}_{dep2}"


def override_route(
    nested_result: Annotated[str, Depends(nested_dependency)],
    _: Annotated[str, Depends(first_dependency, use_cache=False)],
) -> str:
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


async def override_route_async(
    result: Annotated[str, Depends(nested_dependency_async)],
    _: Annotated[str, Depends(first_dependency_async, use_cache=False)],
) -> str:
    return result


test_cases = [
    NestedDependencyTestCase(
        route_func=override_route,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message=EXPECTED_NESTED_RESULT),
    ),
    NestedDependencyTestCase(
        route_func=override_route_async,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message=EXPECTED_NESTED_RESULT),
    ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_override_nested_dependency_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test override nested dependency with synchronous routes."""
    # Arrange
    getattr(app, method)(OVERRIDE_NESTED_PATH)(case.route_func)

    # Act
    response = getattr(test_client, method)(OVERRIDE_NESTED_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_override_nested_dependency_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test override nested dependency with asynchronous routes."""
    # Arrange
    getattr(app, method)(OVERRIDE_NESTED_PATH)(case.route_func)

    # Act
    response = await getattr(async_test_client, method)(OVERRIDE_NESTED_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
