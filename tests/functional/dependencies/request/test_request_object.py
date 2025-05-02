"""
Tests for Request object dependency injection.
"""

from typing import Annotated, Callable

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Depends, Request, Unchained
from unchained.responses import HTTPResponse

# --- Sync Routes & Dependencies ---


def route_sync_request_direct(request: Request):
    return {"method": request.method, "path": request.path}


def dep_sync_uses_request(request: Request):
    return {"dep_method": request.method, "dep_path": request.path}


def route_sync_uses_dep_with_request(data: Annotated[dict, Depends(dep_sync_uses_request)]):
    return data


# --- Async Routes & Dependencies ---


async def route_async_request_direct(request: Request):
    return {"method": request.method, "path": request.path}


async def dep_async_uses_request(request: Request):
    return {"dep_method": request.method, "dep_path": request.path}


async def route_async_uses_dep_with_request(data: Annotated[dict, Depends(dep_async_uses_request)]):
    return data


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
async def test_request_injected_directly(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_request_direct if not is_async else route_async_request_direct
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/direct-request-{route_suffix}"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"method": "GET", "path": route_path}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_request_injected_into_dependency(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_uses_dep_with_request if not is_async else route_async_uses_dep_with_request
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/dep-request-{route_suffix}"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"dep_method": "GET", "dep_path": route_path}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"
