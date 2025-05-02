"""
Tests for Query Parameter dependency injection features.
"""

import json
from typing import Annotated, Callable, List, Optional, overload

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Unchained
from unchained.dependencies import QueryParams
from unchained.errors import ValidationError
from unchained.responses import HTTPResponse

# --- Sync Routes ---


def route_sync_query_required(q: Annotated[str, QueryParams()]):
    return {"q": q}


def route_sync_query_optional(q: Annotated[str, QueryParams()] = "default"):
    return {"q": q}


def route_sync_query_typed(limit: Annotated[int, QueryParams(default=10)]):
    return {"limit": limit}


def route_sync_query_multi_value(tags: Annotated[List[str], QueryParams()]):
    return {"tags": tags}


def route_sync_query_multi_value_builtin(tags: Annotated[list[str], QueryParams()]):
    return {"tags": tags}


def route_sync_query_optional_none(q: Annotated[Optional[str], QueryParams(default=None)]):
    return {"q": q}


def route_sync_query_optional_sig_none(q: Annotated[Optional[str], QueryParams()] = None):
    return {"q": q}


# --- Async Routes ---


async def route_async_query_required(q: Annotated[str, QueryParams()]):
    return {"q": q}


async def route_async_query_optional(q: Annotated[str, QueryParams()] = "default"):
    return {"q": q}


async def route_async_query_typed(limit: Annotated[int, QueryParams(default=10)]):
    return {"limit": limit}


async def route_async_query_multi_value(tags: Annotated[List[str], QueryParams()]):
    return {"tags": tags}


async def route_async_query_multi_value_builtin(tags: Annotated[list[str], QueryParams()]):
    return {"tags": tags}


async def route_async_query_optional_none(q: Annotated[Optional[str], QueryParams(default=None)]):
    return {"q": q}


async def route_async_query_optional_sig_none(q: Annotated[Optional[str], QueryParams()] = None):
    return {"q": q}


# --- Test Parametrizations ---

PARAMETRIZE_REQUIRED = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_query_required, "test_client", False),
        ("async", route_async_query_required, "async_test_client", True),
    ],
)

PARAMETRIZE_OPTIONAL = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_query_optional, "test_client", False),
        ("async", route_async_query_optional, "async_test_client", True),
    ],
)

PARAMETRIZE_TYPED = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_query_typed, "test_client", False),
        ("async", route_async_query_typed, "async_test_client", True),
    ],
)

PARAMETRIZE_MULTI = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_query_multi_value, "test_client", False),
        ("async", route_async_query_multi_value, "async_test_client", True),
    ],
)

PARAMETRIZE_MULTI_BUILTIN = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_query_multi_value_builtin, "test_client", False),
        ("async", route_async_query_multi_value_builtin, "async_test_client", True),
    ],
)

PARAMETRIZE_OPTIONAL_NONE = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_query_optional_none, "test_client", False),
        ("async", route_async_query_optional_none, "async_test_client", True),
    ],
)

PARAMETRIZE_OPTIONAL_SIG_NONE = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_query_optional_sig_none, "test_client", False),
        ("async", route_async_query_optional_sig_none, "async_test_client", True),
    ],
)

# --- Test Helpers ---


@overload
def make_request(test_client: UnchainedTestClient, route_path: str, is_async: bool = False) -> HTTPResponse: ...


@overload
def make_request(test_client: UnchainedAsyncTestClient, route_path: str, is_async: bool = True) -> HTTPResponse: ...


async def make_request(
    test_client: UnchainedTestClient | UnchainedAsyncTestClient, route_path: str, is_async: bool
) -> HTTPResponse:
    if is_async:
        return await test_client.get(route_path)
    else:
        return test_client.get(route_path)


# --- Test Cases ---


@PARAMETRIZE_REQUIRED
@pytest.mark.asyncio
async def test_query_required_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/required-{route_suffix}"
    query_path = f"{route_path}?q=hello"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "hello"}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_REQUIRED
@pytest.mark.asyncio
async def test_query_required_missing_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/missing-{route_suffix}"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)
    assert response.status_code == 422
    data = json.loads(response.content.decode())
    assert "detail" in data and isinstance(data["detail"], list) and len(data["detail"]) > 0, (
        f"Route {route_path}: Expected 'detail' list in error response: {data}"
    )
    error_detail = data["detail"][0]
    assert "msg" in error_detail, f"Route {route_path}: Expected 'msg' in error detail: {error_detail}"
    assert "missing query parameter" in error_detail["msg"].lower() and "q" in error_detail["msg"], (
        f"Route {route_path}: Expected missing query param error for 'q', got: {error_detail['msg']}"
    )


@PARAMETRIZE_OPTIONAL
@pytest.mark.asyncio
async def test_query_optional_not_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-default-{route_suffix}"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "default"}, f"Route {route_path}: Unexpected response JSON (expected default)."


@PARAMETRIZE_OPTIONAL
@pytest.mark.asyncio
async def test_query_optional_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-provided-{route_suffix}"
    query_path = f"{route_path}?q=provided"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "provided"}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_TYPED
@pytest.mark.asyncio
async def test_query_type_conversion(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/typed-{route_suffix}"
    query_path = f"{route_path}?limit=50"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"limit": 50}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_TYPED
@pytest.mark.asyncio
async def test_query_type_conversion_default(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/typed-default-{route_suffix}"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"limit": 10}, f"Route {route_path}: Unexpected response JSON (expected default)."


@PARAMETRIZE_TYPED
@pytest.mark.asyncio
async def test_query_type_conversion_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/typed-error-{route_suffix}"
    query_path = f"{route_path}?limit=abc"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 422, (
        f"Route {query_path}: Expected 422, got {response.status_code}. Response: {response.content.decode()}"
    )
    data = json.loads(response.content.decode())
    assert "detail" in data and isinstance(data["detail"], list) and len(data["detail"]) > 0, (
        f"Route {query_path}: Expected 'detail' list in error response: {data}"
    )
    error_detail = data["detail"][0]
    assert "msg" in error_detail, f"Route {query_path}: Expected 'msg' in error detail: {error_detail}"
    assert "invalid literal" in error_detail["msg"].lower(), (
        f"Route {query_path}: Expected validation error message not found in response detail msg: {error_detail['msg']}"
    )


@PARAMETRIZE_MULTI
@pytest.mark.asyncio
async def test_query_multi_value(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/multi-{route_suffix}"
    query_path = f"{route_path}?tags=a&tags=b&tags=c"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"tags": ["a", "b", "c"]}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_MULTI_BUILTIN
@pytest.mark.asyncio
async def test_query_multi_value_builtin_list(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    """Verify that multi-value query params work with list[T] type hint."""
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/multi-builtin-{route_suffix}"
    query_path = f"{route_path}?tags=x&tags=y"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"tags": ["x", "y"]}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_OPTIONAL_NONE
@pytest.mark.asyncio
async def test_query_optional_none_default(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    """Verify Optional[T] with default=None results in None when not provided."""
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-none-default-{route_suffix}"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": None}, f"Route {route_path}: Expected value to be None."


@PARAMETRIZE_OPTIONAL_NONE
@pytest.mark.asyncio
async def test_query_optional_none_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    """Verify Optional[T] with default=None uses provided value."""
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-none-provided-{route_suffix}"
    query_path = f"{route_path}?q=value-when-none-is-default"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "value-when-none-is-default"}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_OPTIONAL_SIG_NONE
@pytest.mark.asyncio
async def test_query_optional_sig_none_default(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    """Verify Optional[T] with signature default=None results in None when not provided."""
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-sig-none-default-{route_suffix}"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": None}, f"Route {route_path}: Expected value to be None."


@PARAMETRIZE_OPTIONAL_SIG_NONE
@pytest.mark.asyncio
async def test_query_optional_sig_none_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    """Verify Optional[T] with signature default=None uses provided value."""
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-sig-none-provided-{route_suffix}"
    query_path = f"{route_path}?q=value-sig-none"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "value-sig-none"}, f"Route {query_path}: Unexpected response JSON."
