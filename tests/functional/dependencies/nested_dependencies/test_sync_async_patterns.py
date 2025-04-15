"""Tests for various sync/async dependency interaction patterns."""

from typing import Annotated, Dict, List

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    ASYNC_SYNC_PATH,
    NestedDependencyTestCase,
)
from tests.utils.client import UnchainedAsyncTestClient
from tests.utils.test_case import ExpectedResponse, get_async_test_case
from unchained import Depends, Unchained


# Basic dependencies (sync and async)
def sync_dependency() -> str:
    return "sync_value"


async def async_dependency() -> str:
    return "async_value"


# Pattern 1: Async route with sync dependencies
async def async_route_with_sync_deps(dep: Annotated[str, Depends(sync_dependency)]) -> str:
    return f"async_route_with_{dep}"


# Pattern 2: Async route with multiple sync dependencies
async def async_route_with_multiple_sync_deps(
    dep1: Annotated[str, Depends(sync_dependency)],
    dep2: Annotated[str, Depends(sync_dependency)],
) -> Dict[str, str]:
    return {"dep1": dep1, "dep2": dep2}


# Pattern 3: Async route with mixed sync and async dependencies
async def async_route_with_mixed_deps(
    sync_dep: Annotated[str, Depends(sync_dependency)],
    async_dep: Annotated[str, Depends(async_dependency)],
) -> Dict[str, str]:
    return {"sync_dep": sync_dep, "async_dep": async_dep}


# Pattern 4: Sync dependency that depends on async dependency (should work in async route)
def sync_dep_with_async_dep(async_dep: Annotated[str, Depends(async_dependency)]) -> str:
    return f"sync_wrapper_around_{async_dep}"


async def async_route_with_sync_wrapper(dep: Annotated[str, Depends(sync_dep_with_async_dep)]) -> str:
    return dep


# Pattern 5: Async dependency chain (async depending on async)
async def nested_async_dependency(async_dep: Annotated[str, Depends(async_dependency)]) -> str:
    return f"nested_{async_dep}"


async def async_route_with_nested_async(dep: Annotated[str, Depends(nested_async_dependency)]) -> str:
    return dep


# Pattern 6: Complex dependency tree mixing sync and async
def complex_sync_dep1() -> str:
    return "complex_sync_1"


def complex_sync_dep2() -> str:
    return "complex_sync_2"


async def complex_async_dep1() -> str:
    return "complex_async_1"


async def complex_async_dep2(sync_dep: Annotated[str, Depends(complex_sync_dep1)]) -> str:
    return f"complex_async_2_with_{sync_dep}"


async def complex_nested_dep(
    async_dep1: Annotated[str, Depends(complex_async_dep1)],
    async_dep2: Annotated[str, Depends(complex_async_dep2)],
    sync_dep: Annotated[str, Depends(complex_sync_dep2)],
) -> Dict[str, str]:
    return {
        "async_dep1": async_dep1,
        "async_dep2": async_dep2,
        "sync_dep": sync_dep,
    }


async def complex_route(
    nested_dep: Annotated[Dict[str, str], Depends(complex_nested_dep)],
    root_sync: Annotated[str, Depends(sync_dependency)],
) -> Dict[str, str]:
    result = nested_dep.copy()
    result["root_sync"] = root_sync
    return result


test_cases = [
    NestedDependencyTestCase(
        route_func=async_route_with_sync_deps,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message="async_route_with_sync_value"),
    ),
    NestedDependencyTestCase(
        route_func=async_route_with_multiple_sync_deps,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"dep1": "sync_value", "dep2": "sync_value"}),
    ),
    NestedDependencyTestCase(
        route_func=async_route_with_mixed_deps,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"sync_dep": "sync_value", "async_dep": "async_value"}),
    ),
    NestedDependencyTestCase(
        route_func=async_route_with_sync_wrapper,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message="sync_wrapper_around_async_value"),
    ),
    NestedDependencyTestCase(
        route_func=async_route_with_nested_async,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message="nested_async_value"),
    ),
    NestedDependencyTestCase(
        route_func=complex_route,
        request_headers={},
        expected_response=ExpectedResponse(
            status=200,
            message={
                "async_dep1": "complex_async_1",
                "async_dep2": "complex_async_2_with_complex_sync_1",
                "sync_dep": "complex_sync_2",
                "root_sync": "sync_value",
            },
        ),
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_sync_async_patterns(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test various sync/async dependency interaction patterns."""
    # Arrange
    getattr(app, method)(ASYNC_SYNC_PATH)(case.route_func)

    # Act
    response = await getattr(async_test_client, method)(ASYNC_SYNC_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
