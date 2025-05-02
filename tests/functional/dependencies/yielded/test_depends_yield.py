# """
# Tests for yield dependencies (lifecycle, error handling).
# """

from typing import Annotated, AsyncGenerator, Callable, Generator
from unittest.mock import Mock, call

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Depends, Unchained
from unchained.errors import HTTPError
from unchained.responses import HTTPResponse

# Mock object to track calls
lifecycle_tracker = Mock()

# --- Dependencies ---


def yield_sync_basic() -> Generator[str, None, None]:
    lifecycle_tracker.setup_sync_basic()
    try:
        yield "sync_yield_value"
    finally:
        lifecycle_tracker.teardown_sync_basic()


def yield_sync_nested(d1: Annotated[str, Depends(yield_sync_basic)]) -> Generator[str, None, None]:
    lifecycle_tracker.setup_sync_nested()
    try:
        yield f"nested_using_{d1}"
    finally:
        lifecycle_tracker.teardown_sync_nested()


def yield_sync_setup_error() -> Generator[str, None, None]:
    lifecycle_tracker.setup_sync_setup_error()
    raise ValueError("Setup Failed")
    # try:
    #     yield "never_reached"
    # finally:
    #     lifecycle_tracker.teardown_sync_setup_error()  # Should not be called


def yield_sync_teardown_error() -> Generator[str, None, None]:
    lifecycle_tracker.setup_sync_teardown_error()
    try:
        yield "value_before_teardown_error"
    finally:
        lifecycle_tracker.teardown_sync_teardown_error()
        raise ValueError("Teardown Failed")  # Should be logged, request succeeds


def yield_sync_http_error() -> Generator[str, None, None]:
    lifecycle_tracker.setup_sync_http_error()
    try:
        raise HTTPError(403, "Forbidden by sync dep")
        # yield "never_reached"
    finally:
        lifecycle_tracker.teardown_sync_http_error()  # Should still be called


async def yield_async_basic() -> AsyncGenerator[str, None]:
    lifecycle_tracker.setup_async_basic()
    try:
        yield "async_yield_value"
    finally:
        lifecycle_tracker.teardown_async_basic()


async def yield_async_nested(d1: Annotated[str, Depends(yield_async_basic)]) -> AsyncGenerator[str, None]:
    lifecycle_tracker.setup_async_nested()
    try:
        yield f"nested_using_{d1}"
    finally:
        lifecycle_tracker.teardown_async_nested()


async def yield_async_setup_error() -> AsyncGenerator[str, None]:
    lifecycle_tracker.setup_async_setup_error()
    raise ValueError("Async Setup Failed")
    # try:
    #     yield "never_reached"
    # finally:
    #     lifecycle_tracker.teardown_async_setup_error()  # Should not be called


async def yield_async_teardown_error() -> AsyncGenerator[str, None]:
    lifecycle_tracker.setup_async_teardown_error()
    try:
        yield "value_before_teardown_error_async"
    finally:
        lifecycle_tracker.teardown_async_teardown_error()
        raise ValueError("Async Teardown Failed")  # Should be logged, request succeeds


async def yield_async_http_error() -> AsyncGenerator[str, None]:
    lifecycle_tracker.setup_async_http_error()
    try:
        raise HTTPError(403, "Forbidden by async dep")
        # yield "never_reached"
    finally:
        lifecycle_tracker.teardown_async_http_error()  # Should still be called


# --- Routes ---


def route_sync_yield_basic(d: Annotated[str, Depends(yield_sync_basic)]):
    lifecycle_tracker.route_sync_basic()
    return {"data": d}


def route_sync_yield_nested(d: Annotated[str, Depends(yield_sync_nested)]):
    lifecycle_tracker.route_sync_nested()
    return {"data": d}


def route_sync_yield_setup_error(d: Annotated[str, Depends(yield_sync_setup_error)]):
    lifecycle_tracker.route_sync_setup_error()  # Should not be called
    return {"data": d}


def route_sync_yield_teardown_error(d: Annotated[str, Depends(yield_sync_teardown_error)]):
    lifecycle_tracker.route_sync_teardown_error()
    return {"data": d}


def route_sync_yield_http_error(d: Annotated[str, Depends(yield_sync_http_error)]):
    lifecycle_tracker.route_sync_http_error()  # Should not be called
    return {"data": d}


def route_sync_error_after_yield(d: Annotated[str, Depends(yield_sync_basic)]):
    lifecycle_tracker.route_sync_error_after_yield()
    raise RuntimeError("Route Error")


async def route_async_yield_basic(d: Annotated[str, Depends(yield_async_basic)]):
    lifecycle_tracker.route_async_basic()
    return {"data": d}


async def route_async_yield_nested(d: Annotated[str, Depends(yield_async_nested)]):
    lifecycle_tracker.route_async_nested()
    return {"data": d}


async def route_async_yield_setup_error(d: Annotated[str, Depends(yield_async_setup_error)]):
    lifecycle_tracker.route_async_setup_error()  # Should not be called
    return {"data": d}


async def route_async_yield_teardown_error(d: Annotated[str, Depends(yield_async_teardown_error)]):
    lifecycle_tracker.route_async_teardown_error()
    return {"data": d}


async def route_async_yield_http_error(d: Annotated[str, Depends(yield_async_http_error)]):
    lifecycle_tracker.route_async_http_error()  # Should not be called
    return {"data": d}


async def route_async_error_after_yield(d: Annotated[str, Depends(yield_async_basic)]):
    lifecycle_tracker.route_async_error_after_yield()
    raise RuntimeError("Route Error Async")


# --- Test Helpers ---

PARAMETRIZE_CLIENT = pytest.mark.parametrize(
    "route_suffix, client_fixture_name, is_async",
    [
        ("sync", "test_client", False),
        ("async", "async_test_client", True),
    ],
)


async def make_request(test_client, route_path: str, is_async: bool) -> HTTPResponse:
    if is_async:
        return await test_client.get(route_path)
    else:
        return test_client.get(route_path)


# --- Test Cases ---


@pytest.fixture(autouse=True)
def reset_tracker():
    lifecycle_tracker.reset_mock()
    yield
    lifecycle_tracker.reset_mock()


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_yield_lifecycle_basic(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_yield_basic if not is_async else route_async_yield_basic
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/basic-{route_suffix}"
    yield_value = "sync_yield_value" if not is_async else "async_yield_value"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"data": yield_value}, f"Route {route_path}: Unexpected response JSON."
    getattr(lifecycle_tracker, f"setup_{route_suffix}_basic").assert_called_once()
    getattr(lifecycle_tracker, f"route_{route_suffix}_basic").assert_called_once()
    getattr(lifecycle_tracker, f"teardown_{route_suffix}_basic").assert_called_once()


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_yield_lifecycle_nested(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_yield_nested if not is_async else route_async_yield_nested
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/nested-{route_suffix}"
    base_yield_value = "sync_yield_value" if not is_async else "async_yield_value"
    nested_yield_value = f"nested_using_{base_yield_value}"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"data": nested_yield_value}, f"Route {route_path}: Unexpected response JSON."

    expected_calls = [
        call[0](getattr(lifecycle_tracker, f"setup_{route_suffix}_basic"))(),
        call[0](getattr(lifecycle_tracker, f"setup_{route_suffix}_nested"))(),
        call[0](getattr(lifecycle_tracker, f"route_{route_suffix}_nested"))(),
        call[0](getattr(lifecycle_tracker, f"teardown_{route_suffix}_nested"))(),
        call[0](getattr(lifecycle_tracker, f"teardown_{route_suffix}_basic"))(),
    ]
    # Check call order using the mock's call list
    actual_calls = [c[0] for c in lifecycle_tracker.mock_calls]
    expected_call_names = [c[1][0].__name__ for c in expected_calls]
    assert actual_calls == expected_call_names, (
        f"Route {route_path}: Incorrect call order. Expected {expected_call_names}, got {actual_calls}"
    )


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_yield_setup_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_yield_setup_error if not is_async else route_async_yield_setup_error
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/setup-error-{route_suffix}"
    error_msg = "Setup Failed" if not is_async else "Async Setup Failed"
    app.get(route_path)(route)

    with pytest.raises(ValueError, match=error_msg) as excinfo:
        await make_request(test_client, route_path, is_async)

    getattr(lifecycle_tracker, f"setup_{route_suffix}_setup_error").assert_called_once()
    getattr(lifecycle_tracker, f"route_{route_suffix}_setup_error").assert_not_called()
    getattr(lifecycle_tracker, f"teardown_{route_suffix}_setup_error").assert_not_called()


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_yield_teardown_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    # Teardown errors should be logged but not fail the request
    route = route_sync_yield_teardown_error if not is_async else route_async_yield_teardown_error
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/teardown-error-{route_suffix}"
    yield_value = "value_before_teardown_error" if not is_async else "value_before_teardown_error_async"
    app.get(route_path)(route)

    # TODO: Check logs for teardown error message
    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"data": yield_value}, f"Route {route_path}: Unexpected response JSON."
    getattr(lifecycle_tracker, f"setup_{route_suffix}_teardown_error").assert_called_once()
    getattr(lifecycle_tracker, f"route_{route_suffix}_teardown_error").assert_called_once()
    getattr(lifecycle_tracker, f"teardown_{route_suffix}_teardown_error").assert_called_once()


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_yield_http_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_yield_http_error if not is_async else route_async_yield_http_error
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/http-error-{route_suffix}"
    error_msg = "Forbidden by sync dep" if not is_async else "Forbidden by async dep"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 403, (
        f"Route {route_path}: Expected 403, got {response.status_code}. Response: {response.content.decode()}"
    )
    # Decode content for checking the error message string
    response_text = response.content.decode()
    assert error_msg in response_text, (
        f"Route {route_path}: Expected error message '{error_msg}' not found in response: {response_text}"
    )
    getattr(lifecycle_tracker, f"setup_{route_suffix}_http_error").assert_called_once()
    getattr(lifecycle_tracker, f"route_{route_suffix}_http_error").assert_not_called()
    getattr(lifecycle_tracker, f"teardown_{route_suffix}_http_error").assert_called_once()  # Teardown still runs


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_yield_error_in_route_runs_teardown(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_error_after_yield if not is_async else route_async_error_after_yield
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/route-error-{route_suffix}"
    error_msg = "Route Error" if not is_async else "Route Error Async"
    app.get(route_path)(route)

    with pytest.raises(RuntimeError, match=error_msg):
        await make_request(test_client, route_path, is_async)

    getattr(lifecycle_tracker, f"setup_{route_suffix}_basic").assert_called_once()
    getattr(lifecycle_tracker, f"route_{route_suffix}_error_after_yield").assert_called_once()
    getattr(lifecycle_tracker, f"teardown_{route_suffix}_basic").assert_called_once()  # Teardown still runs
