"""
Tests for App object dependency injection.
"""

from typing import Annotated, Callable

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Depends, Unchained

# --- Sync Routes & Dependencies ---


def route_sync_app_direct(injected_app: Unchained):
    return {"injected_app_id": id(injected_app)}


def dep_sync_uses_app(injected_app: Unchained):
    return {"dep_injected_app_id": id(injected_app)}


def route_sync_uses_dep_with_app(data: Annotated[dict, Depends(dep_sync_uses_app)]):
    return data


# --- Async Routes & Dependencies ---


async def route_async_app_direct(injected_app: Unchained):
    return {"injected_app_id": id(injected_app)}


async def dep_async_uses_app(injected_app: Unchained):
    return {"dep_injected_app_id": id(injected_app)}


async def route_async_uses_dep_with_app(data: Annotated[dict, Depends(dep_async_uses_app)]):
    return data


# --- Test Cases ---


@pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_app_direct, "test_client", False),
        ("async", route_async_app_direct, "async_test_client", True),
    ],
)
@pytest.mark.asyncio
async def test_app_injected_directly(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    """
    Verify that the Unchained app instance is correctly injected directly into route handlers.
    Covers both synchronous and asynchronous handlers.
    """
    test_client: UnchainedTestClient | UnchainedAsyncTestClient = request.getfixturevalue(client_fixture_name)
    route_path = f"/direct-app-{route_suffix}"
    app.get(route_path)(route_handler)

    if is_async:
        response = await test_client.get(route_path)
    else:
        response = test_client.get(route_path)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code} for route {route_path}"
    expected_data = {"injected_app_id": id(app)}
    assert response.json() == expected_data, f"Route {route_path} - Expected {expected_data}, got {response.json()}"


@pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_uses_dep_with_app, "test_client", False),
        ("async", route_async_uses_dep_with_app, "async_test_client", True),
    ],
)
@pytest.mark.asyncio
async def test_app_injected_into_dependency(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    """
    Verify that the Unchained app instance is correctly injected into dependencies used by route handlers.
    Covers both synchronous and asynchronous handlers and dependencies.
    """
    test_client: UnchainedTestClient | UnchainedAsyncTestClient = request.getfixturevalue(client_fixture_name)
    route_path = f"/dep-app-{route_suffix}"
    app.get(route_path)(route_handler)

    if is_async:
        response = await test_client.get(route_path)
    else:
        response = test_client.get(route_path)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code} for route {route_path}"
    expected_data = {"dep_injected_app_id": id(app)}
    assert response.json() == expected_data, f"Route {route_path} - Expected {expected_data}, got {response.json()}"
