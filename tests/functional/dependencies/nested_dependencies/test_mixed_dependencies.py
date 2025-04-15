"""Tests for mixed sync/async dependencies."""

from typing import Annotated, Dict

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    MIXED_DEPENDENCIES_PATH,
    TEST_RETURN_VALUE_1,
    NestedDependencyTestCase,
)
from tests.utils.client import UnchainedAsyncTestClient
from tests.utils.test_case import ExpectedResponse, get_async_test_case
from unchained import Depends, Unchained


# Used only in async tests
def sync_dependency() -> str:
    return "sync_value"


async def first_dependency_async() -> str:
    return TEST_RETURN_VALUE_1


async def mixed_route(
    sync_result: Annotated[str, Depends(sync_dependency)], async_result: Annotated[str, Depends(first_dependency_async)]
) -> str:
    return f"{sync_result}_{async_result}"


test_cases = [
    NestedDependencyTestCase(
        route_func=mixed_route,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message=f"sync_value_{TEST_RETURN_VALUE_1}"),
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_mixed_dependencies_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test mixed sync/async dependencies in an asynchronous route."""
    # Arrange
    getattr(app, method)(MIXED_DEPENDENCIES_PATH)(case.route_func)

    # Act
    response = await getattr(async_test_client, method)(MIXED_DEPENDENCIES_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
