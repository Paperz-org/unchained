"""
Tests for Query Parameter dependency injection features.
"""

import json
from typing import Annotated, Callable, List, Optional

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


def route_sync_query_optional(q: Annotated[Optional[str], QueryParams()] = "default"):
    return {"q": q}


def route_sync_query_typed(limit: Annotated[int, QueryParams(default=10)]):
    return {"limit": limit}


def route_sync_query_multi_value(tags: Annotated[List[str], QueryParams()]):
    return {"tags": tags}


# --- Async Routes ---


async def route_async_query_required(q: Annotated[str, QueryParams()]):
    return {"q": q}


async def route_async_query_optional(q: Annotated[Optional[str], QueryParams()] = "default"):
    return {"q": q}


async def route_async_query_typed(limit: Annotated[int, QueryParams(default=10)]):
    return {"limit": limit}


async def route_async_query_multi_value(tags: Annotated[List[str], QueryParams()]):
    return {"tags": tags}


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


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_required_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_required if not is_async else route_async_query_required
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/required-{route_suffix}"
    query_path = f"{route_path}?q=hello"
    app.get(route_path)(route)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "hello"}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_required_missing_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_required if not is_async else route_async_query_required
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/missing-{route_suffix}"
    app.get(route_path)(route)

    with pytest.raises(ValidationError) as excinfo:
        await make_request(test_client, route_path, is_async)
    # TODO: Assert specific error message content if Query dependency provides one
    assert "q" in str(excinfo.value).lower(), (
        f"Route {route_path}: ValidationError message should mention missing parameter 'q'"
    )


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_optional_not_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_optional if not is_async else route_async_query_optional
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-default-{route_suffix}"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "default"}, f"Route {route_path}: Unexpected response JSON (expected default)."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_optional_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_optional if not is_async else route_async_query_optional
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/optional-provided-{route_suffix}"
    query_path = f"{route_path}?q=provided"
    app.get(route_path)(route)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"q": "provided"}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_type_conversion(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_typed if not is_async else route_async_query_typed
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/typed-{route_suffix}"
    query_path = f"{route_path}?limit=50"
    app.get(route_path)(route)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"limit": 50}, f"Route {query_path}: Unexpected response JSON."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_type_conversion_default(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_typed if not is_async else route_async_query_typed
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/typed-default-{route_suffix}"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)  # Use default

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"limit": 10}, f"Route {route_path}: Unexpected response JSON (expected default)."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_type_conversion_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_typed if not is_async else route_async_query_typed
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/typed-error-{route_suffix}"
    query_path = f"{route_path}?limit=abc"
    app.get(route_path)(route)

    response = await make_request(test_client, query_path, is_async)
    data = json.loads(response.content.decode())

    assert response.status_code == 422, (
        f"Route {query_path}: Expected 422, got {response.status_code}. Response: {data}"
    )
    # Check the detail message in the JSON response
    assert "detail" in data and isinstance(data["detail"], list) and len(data["detail"]) > 0, (
        f"Route {query_path}: Expected 'detail' list in error response: {data}"
    )
    error_detail = data["detail"][0]
    assert "msg" in error_detail, f"Route {query_path}: Expected 'msg' in error detail: {error_detail}"
    assert "valid integer" in error_detail["msg"].lower(), (
        f"Route {query_path}: Expected validation error message not found in response detail msg: {error_detail['msg']}"
    )


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_query_multi_value(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_query_multi_value if not is_async else route_async_query_multi_value
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/multi-{route_suffix}"
    query_path = f"{route_path}?tags=a&tags=b&tags=c"
    app.get(route_path)(route)

    response = await make_request(test_client, query_path, is_async)

    assert response.status_code == 200, (
        f"Route {query_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"tags": ["a", "b", "c"]}, f"Route {query_path}: Unexpected response JSON."
