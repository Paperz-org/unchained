import dataclasses
import inspect
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
)
from unittest.mock import DEFAULT, Mock, call, patch

import pytest
from ninja.errors import HttpError

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from tests.utils.test_case import (
    ExpectedResponse,
    UnchainedTestCase,
    get_async_test_case,
    get_sync_test_case,
)
from unchained import Depends, Unchained


# Utility functions for tracking lifecycle events
def setup_a():
    """Simulate setup operation A."""
    pass


def teardown_a():
    """Simulate teardown operation A."""
    pass


def setup_b():
    """Simulate setup operation B."""
    pass


def teardown_b():
    """Simulate teardown operation B."""
    pass


def setup_c():
    """Simulate setup operation C."""
    pass


def teardown_c():
    """Simulate teardown operation C."""
    pass


async def async_setup_a():
    """Simulate async setup operation A."""
    pass


async def async_teardown_a():
    """Simulate async teardown operation A."""
    pass


async def async_setup_b():
    """Simulate async setup operation B."""
    pass


async def async_teardown_b():
    """Simulate async teardown operation B."""
    pass


# Synchronous yield dependencies that mimic real-world usage
def get_dependency_a() -> Generator[str, None, None]:
    """
    A typical yield dependency.

    1. Runs setup operation
    2. Yields a value for use in the route handler
    3. Runs teardown operation after the route finishes
    """
    setup_a()  # Setup
    try:
        value = "dependency_a"
        yield value
    finally:
        teardown_a()  # Teardown


def get_dependency_b(dep_a: Annotated[str, Depends(get_dependency_a)]) -> Generator[Dict[str, str], None, None]:
    """
    A nested dependency that depends on another dependency.

    1. Runs setup operation
    2. Yields a value
    3. Runs teardown operation
    """
    setup_b()  # Setup
    try:
        value = {"type": "dependency_b", "dep_a": dep_a}
        yield value
    finally:
        teardown_b()  # Teardown


# Asynchronous yield dependencies
async def get_async_dependency() -> AsyncGenerator[str, None]:
    """
    An async dependency.

    1. Asynchronously runs setup
    2. Yields a value
    3. Asynchronously runs teardown
    """
    await async_setup_a()
    try:
        value = "async_dependency"
        yield value
    finally:
        await async_teardown_a()


# Dependencies with exception handling
def get_dependency_with_setup_error() -> Generator[str, None, None]:
    """
    A dependency that raises an exception during setup.
    Teardown should not be called.
    """
    setup_a()  # Setup is called
    raise ValueError("Setup error")  # Error during setup
    try:
        yield "never_reached"
    finally:
        teardown_a()  # Should not be called


def get_dependency_with_teardown_error() -> Generator[str, None, None]:
    """
    A dependency that raises an exception during teardown.
    """
    setup_a()  # Setup
    try:
        yield "dependency_with_teardown_error"
    finally:
        teardown_a()  # Teardown is called
        raise ValueError("Teardown error")  # Error during teardown


async def get_async_dependency_with_setup_error() -> AsyncGenerator[str, None]:
    """
    An async dependency that raises an exception during setup.
    """
    await async_setup_a()  # Setup is called
    raise ValueError("Async setup error")
    try:
        yield "never_reached"
    finally:
        await async_teardown_a()  # Should not be called


async def get_async_dependency_with_teardown_error() -> AsyncGenerator[str, None]:
    """
    An async dependency that raises an exception during teardown.
    """
    await async_setup_a()  # Setup
    try:
        yield "async_dependency_with_teardown_error"
    finally:
        await async_teardown_a()  # Teardown is called
        raise ValueError("Async teardown error")


# HTTP exception dependency
def get_dependency_with_http_error() -> Generator[str, None, None]:
    """
    A dependency that raises an HTTP exception.
    """
    setup_a()  # Setup
    try:
        raise HttpError(status_code=403, message="Forbidden by dependency")
        yield "never_reached"
    finally:
        teardown_a()  # Should still be called


# Deep nested yield dependencies for testing complex lifecycle
def get_dependency_c() -> Generator[str, None, None]:
    """Level 3 dependency."""
    setup_c()
    try:
        yield "dependency_c"
    finally:
        teardown_c()


def get_dependency_deep_b(dep_c: Annotated[str, Depends(get_dependency_c)]) -> Generator[Dict[str, str], None, None]:
    """Level 2 dependency."""
    setup_b()
    try:
        yield {"type": "deep_b", "dep_c": dep_c}
    finally:
        teardown_b()


def get_dependency_deep_a(
    dep_b: Annotated[Dict[str, str], Depends(get_dependency_deep_b)],
) -> Generator[Dict[str, str], None, None]:
    """Level 1 dependency."""
    setup_a()
    try:
        yield {"type": "deep_a", "deep_b": dep_b}
    finally:
        teardown_a()


# Async deep nested dependencies
async def get_async_dependency_b() -> AsyncGenerator[str, None]:
    """Async Level 2 dependency."""
    await async_setup_b()
    try:
        yield "async_dependency_b"
    finally:
        await async_teardown_b()


async def get_async_dependency_deep(
    async_dep_b: Annotated[str, Depends(get_async_dependency_b)],
) -> AsyncGenerator[Dict[str, str], None]:
    """Async Level 1 dependency."""
    await async_setup_a()
    try:
        yield {"type": "async_deep", "async_dep_b": async_dep_b}
    finally:
        await async_teardown_a()


# Route handlers for error cases
def route_with_setup_error(dep: Annotated[str, Depends(get_dependency_with_setup_error)]) -> Dict[str, str]:
    """This route should never complete due to setup error."""
    return {"dep": dep}


def route_with_teardown_error(dep: Annotated[str, Depends(get_dependency_with_teardown_error)]) -> Dict[str, str]:
    """This route completes but teardown will fail."""
    return {"dep": dep}


def route_with_http_error(dep: Annotated[str, Depends(get_dependency_with_http_error)]) -> Dict[str, str]:
    """This route should return 403 from dependency."""
    return {"dep": dep}


async def async_route_with_setup_error(
    dep: Annotated[str, Depends(get_async_dependency_with_setup_error)],
) -> Dict[str, str]:
    """This async route should never complete due to setup error."""
    return {"dep": dep}


async def async_route_with_teardown_error(
    dep: Annotated[str, Depends(get_async_dependency_with_teardown_error)],
) -> Dict[str, str]:
    """This async route completes but teardown will fail."""
    return {"dep": dep}


# Route handlers for deep nested dependencies
def route_with_deep_dependencies(dep: Annotated[Dict[str, str], Depends(get_dependency_deep_a)]) -> Dict[str, str]:
    """Route with deeply nested dependencies."""
    return dep


async def async_route_with_deep_dependencies(
    dep: Annotated[Dict[str, str], Depends(get_async_dependency_deep)],
) -> Dict[str, str]:
    """Async route with deeply nested dependencies."""
    return dep


# Simple route handlers that use these dependencies
def route_with_dependency_a(dep_a: Annotated[str, Depends(get_dependency_a)]) -> Dict[str, str]:
    """Route handler that uses dependency A."""
    return {"dep_a": dep_a}


def route_with_dependency_b(dep_b: Annotated[Dict[str, str], Depends(get_dependency_b)]) -> Dict[str, str]:
    """Route handler that uses dependency B with a nested dependency A."""
    return dep_b


async def async_route(async_dep: Annotated[str, Depends(get_async_dependency)]) -> Dict[str, str]:
    """Async route handler that uses an async dependency."""
    return {"async_dep": async_dep}


async def mixed_route(
    dep_a: Annotated[str, Depends(get_dependency_a)], async_dep: Annotated[str, Depends(get_async_dependency)]
) -> Dict[str, str]:
    """Async route handler that uses both sync and async dependencies."""
    return {"dep_a": dep_a, "async_dep": async_dep}


@dataclasses.dataclass
class YieldDependencyTestCase(UnchainedTestCase):
    """Test case for yield dependencies."""

    expected_call_order: List[Callable]  # Expected order of lifecycle function calls
    expected_error: Optional[type] = None  # Expected exception type, if any


# Define the test cases
test_cases = [
    # Simple Dependency Lifecycle
    YieldDependencyTestCase(
        route_func=route_with_dependency_a,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"dep_a": "dependency_a"}),
        expected_call_order=[setup_a, teardown_a],
    ),
    # Nested Dependency Lifecycle
    YieldDependencyTestCase(
        route_func=route_with_dependency_b,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"type": "dependency_b", "dep_a": "dependency_a"}),
        expected_call_order=[setup_a, setup_b, teardown_b, teardown_a],
    ),
    # Async Dependency Lifecycle
    YieldDependencyTestCase(
        route_func=async_route,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"async_dep": "async_dependency"}),
        expected_call_order=[async_setup_a, async_teardown_a],
    ),
    # Mixed Sync and Async Dependencies
    YieldDependencyTestCase(
        route_func=mixed_route,
        request_headers={},
        expected_response=ExpectedResponse(
            status=200, message={"dep_a": "dependency_a", "async_dep": "async_dependency"}
        ),
        expected_call_order=[async_setup_a, setup_a, teardown_a, async_teardown_a],
    ),
    # Setup error in dependency
    YieldDependencyTestCase(
        route_func=route_with_setup_error,
        request_headers={},
        expected_response=ExpectedResponse(status=500, message=None),
        expected_call_order=[setup_a],  # Only setup_a is called, not teardown_a
        expected_error=ValueError,
    ),
    # Teardown error in dependency
    YieldDependencyTestCase(
        route_func=route_with_teardown_error,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"dep": "dependency_with_teardown_error"}),
        expected_call_order=[setup_a, teardown_a],  # Both are called even though teardown fails
        expected_error=ValueError,  # After response is sent
    ),
    # HTTP exception in dependency
    YieldDependencyTestCase(
        route_func=route_with_http_error,
        request_headers={},
        expected_response=ExpectedResponse(status=403, message={"detail": "Forbidden by dependency"}),
        expected_call_order=[setup_a, teardown_a],  # Teardown still runs on HTTP exceptions
    ),
    # Async setup error
    YieldDependencyTestCase(
        route_func=async_route_with_setup_error,
        request_headers={},
        expected_response=ExpectedResponse(status=500, message=None),
        expected_call_order=[async_setup_a],  # Only setup is called
        expected_error=ValueError,
    ),
    # Async teardown error
    YieldDependencyTestCase(
        route_func=async_route_with_teardown_error,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message={"dep": "async_dependency_with_teardown_error"}),
        expected_call_order=[async_setup_a, async_teardown_a],
        expected_error=ValueError,  # After response is sent
    ),
    # Deep nested dependencies
    YieldDependencyTestCase(
        route_func=route_with_deep_dependencies,
        request_headers={},
        expected_response=ExpectedResponse(
            status=200,
            message={"type": "deep_a", "deep_b": {"type": "deep_b", "dep_c": "dependency_c"}},
        ),
        expected_call_order=[setup_c, setup_b, setup_a, teardown_a, teardown_b, teardown_c],
    ),
    # Async deep nested dependencies
    YieldDependencyTestCase(
        route_func=async_route_with_deep_dependencies,
        request_headers={},
        expected_response=ExpectedResponse(
            status=200, message={"type": "async_deep", "async_dep_b": "async_dependency_b"}
        ),
        expected_call_order=[async_setup_b, async_setup_a, async_teardown_a, async_teardown_b],
    ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_yield_dependencies_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: YieldDependencyTestCase,
) -> None:
    """Test synchronous yield dependencies with proper lifecycle management."""
    # Setup route
    route_path = "/yield-dependency"
    getattr(app, method)(route_path)(case.route_func)

    # Get all lifecycle functions to patch
    lifecycle_funcs = list(set(case.expected_call_order))

    # Setup mocks for lifecycle methods
    with patch.multiple(
        "tests.functional.dependencies.nested_dependencies.test_yield_dependencies",
        **{func.__name__: DEFAULT for func in lifecycle_funcs},
    ) as patched:
        # Create a manager to track call order
        manager = Mock()

        # Attach each mock to the manager
        for func in lifecycle_funcs:
            manager.attach_mock(patched[func.__name__], func.__name__)

        # Act - Make the request
        response = getattr(test_client, method)(route_path, headers=case.request_headers)

        # Assert response
        assert response.status_code == case.expected_response.status
        if case.expected_response.message is not None:
            assert response.json() == case.expected_response.message

        # Verify lifecycle methods were called in the expected order
        expected_calls = [getattr(call, func.__name__)() for func in case.expected_call_order]
        assert manager.mock_calls == expected_calls


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_yield_dependencies_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: YieldDependencyTestCase,
) -> None:
    """Test asynchronous yield dependencies with proper lifecycle management."""
    # Setup route
    route_path = "/yield-dependency"
    getattr(app, method)(route_path)(case.route_func)

    # Get all lifecycle functions to patch
    lifecycle_funcs = list(set(case.expected_call_order))

    # Setup mocks for lifecycle methods
    with patch.multiple(
        "tests.functional.dependencies.nested_dependencies.test_yield_dependencies",
        **{func.__name__: DEFAULT for func in lifecycle_funcs},
    ) as patched:
        # For async lifecycle methods, configure return values
        for func in lifecycle_funcs:
            if inspect.iscoroutinefunction(func) and func.__name__ in patched:
                patched[func.__name__].return_value = None

        # Create a manager to track call order
        manager = Mock()

        # Attach each mock to the manager
        for func in lifecycle_funcs:
            manager.attach_mock(patched[func.__name__], func.__name__)

        # Act - Make the request
        response = await getattr(async_test_client, method)(route_path, headers=case.request_headers)

        # Assert response
        assert response.status_code == case.expected_response.status
        if case.expected_response.message is not None:
            assert response.json() == case.expected_response.message

        # Create expected calls list format for comparison
        expected_calls = [getattr(call, func.__name__)() for func in case.expected_call_order]

        # Verify the call order
        assert manager.mock_calls == expected_calls
        assert manager.mock_calls == expected_calls
