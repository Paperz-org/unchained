"""
Tests for Path Parameter dependency injection features.
"""

import json
from typing import Annotated, Callable

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Unchained
from unchained.errors import ValidationError
from unchained.responses import HTTPResponse

# --- Sync Routes ---


def route_sync_path_param_str(item_id: str):
    return {"item_id": item_id}


def route_sync_path_param_int(item_id: int):
    return {"item_id": item_id}


# --- Async Routes ---


async def route_async_path_param_str(item_id: str):
    return {"item_id": item_id}


async def route_async_path_param_int(item_id: int):
    return {"item_id": item_id}


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
async def test_path_param_string(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_path_param_str if not is_async else route_async_path_param_str
    test_client = request.getfixturevalue(client_fixture_name)
    base_path = f"/items-str-{route_suffix}"
    item_value = "abc"
    request_path = f"{base_path}/{item_value}"
    app.get(f"{base_path}/{{item_id}}")(route)

    response = await make_request(test_client, request_path, is_async)

    assert response.status_code == 200, (
        f"Route {request_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"item_id": item_value}, f"Route {request_path}: Unexpected response JSON."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_path_param_int(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_path_param_int if not is_async else route_async_path_param_int
    test_client = request.getfixturevalue(client_fixture_name)
    base_path = f"/items-int-{route_suffix}"
    item_value = 123
    request_path = f"{base_path}/{item_value}"
    app.get(f"{base_path}/{{item_id}}")(route)

    response = await make_request(test_client, request_path, is_async)

    assert response.status_code == 200, (
        f"Route {request_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"item_id": item_value}, f"Route {request_path}: Unexpected response JSON."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_path_param_int_conversion_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_path_param_int if not is_async else route_async_path_param_int
    test_client = request.getfixturevalue(client_fixture_name)
    base_path = f"/items-int-error-{route_suffix}"
    item_value = "abc"  # Invalid integer
    request_path = f"{base_path}/{item_value}"
    app.get(f"{base_path}/{{item_id}}")(route)

    response = await make_request(test_client, request_path, is_async)
    data = json.loads(response.content.decode())
    assert response.status_code == 422, (
        f"Route {request_path}: Expected 422, got {response.status_code}. Response: {data}"
    )
    assert "detail" in data and isinstance(data["detail"], list) and len(data["detail"]) > 0, (
        f"Route {request_path}: Expected 'detail' list in error response: {data}"
    )
    error_detail = data["detail"][0]
    assert "msg" in error_detail, f"Route {request_path}: Expected 'msg' in error detail: {error_detail}"
    assert "valid integer" in error_detail["msg"].lower(), (
        f"Route {request_path}: Expected validation error message not found in response detail msg: {error_detail['msg']}"
    )
