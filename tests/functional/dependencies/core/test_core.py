"""
Tests for core DI features like caching and sync/async interactions.
"""

from typing import Annotated, Callable

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Depends, Unchained

# --- Dependencies ---

sync_counter = 0
async_counter = 0


@pytest.fixture(autouse=True)
def reset_counters_fixture():
    global sync_counter, async_counter
    sync_counter = 0
    async_counter = 0
    yield
    sync_counter = 0
    async_counter = 0


def sync_dependency_counter() -> int:
    global sync_counter
    sync_counter += 1
    return sync_counter


async def async_dependency_counter() -> int:
    global async_counter
    async_counter += 1
    return async_counter


# Sync dep depending on async (only works in async context)
def sync_dep_needs_async(val: Annotated[int, Depends(async_dependency_counter)]) -> dict:
    return {"sync_got_async_val": val}


# --- Routes ---


# Caching routes
def route_sync_shared_dep(
    d1: Annotated[int, Depends(sync_dependency_counter)],
    d2: Annotated[int, Depends(sync_dependency_counter)],
):
    return {"d1": d1, "d2": d2, "count": sync_counter}


def route_sync_no_cache(
    d1: Annotated[int, Depends(sync_dependency_counter)],
    d2: Annotated[int, Depends(sync_dependency_counter, use_cache=False)],
):
    return {"d1": d1, "d2": d2, "count": sync_counter}


async def route_async_shared_dep(
    d1: Annotated[int, Depends(async_dependency_counter)],
    d2: Annotated[int, Depends(async_dependency_counter)],
):
    return {"d1": d1, "d2": d2, "count": async_counter}


async def route_async_no_cache(
    d1: Annotated[int, Depends(async_dependency_counter)],
    d2: Annotated[int, Depends(async_dependency_counter, use_cache=False)],
):
    return {"d1": d1, "d2": d2, "count": async_counter}


# Sync/Async interaction routes
async def route_async_needs_sync(val: Annotated[int, Depends(sync_dependency_counter)]):
    return {"async_got_sync_val": val, "count": sync_counter}


async def route_async_needs_sync_and_async(
    d_sync: Annotated[int, Depends(sync_dependency_counter)],
    d_async: Annotated[int, Depends(async_dependency_counter)],
):
    return {"sync_val": d_sync, "async_val": d_async, "sync_count": sync_counter, "async_count": async_counter}


async def route_async_runs_sync_dep_needs_async(val: Annotated[dict, Depends(sync_dep_needs_async)]):
    return val


# Route for failure case
def route_sync_needs_async(val: Annotated[int, Depends(async_dependency_counter)]):
    return {"should_not_reach": val}


# --- Test Cases ---


# Caching Tests
def test_dependency_cached_by_default_sync(app: Unchained, test_client: UnchainedTestClient):
    route_path = "/cache-sync"
    app.get(route_path)(route_sync_shared_dep)
    response = test_client.get(route_path)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"d1": 1, "d2": 1, "count": 1}
    # Dependency ran once, both injections get the same value (1)
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"


def test_dependency_no_cache_reruns_sync(app: Unchained, test_client: UnchainedTestClient):
    route_path = "/no-cache-sync"
    app.get(route_path)(route_sync_no_cache)
    response = test_client.get(route_path)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"d1": 1, "d2": 2, "count": 2}
    # First injection gets 1, second reruns dep (use_cache=False) and gets 2
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"


@pytest.mark.asyncio
async def test_dependency_cached_by_default_async(app: Unchained, async_test_client: UnchainedAsyncTestClient):
    route_path = "/cache-async"
    app.get(route_path)(route_async_shared_dep)
    response = await async_test_client.get(route_path)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"d1": 1, "d2": 1, "count": 1}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"


@pytest.mark.asyncio
async def test_dependency_no_cache_reruns_async(app: Unchained, async_test_client: UnchainedAsyncTestClient):
    route_path = "/no-cache-async"
    app.get(route_path)(route_async_no_cache)
    response = await async_test_client.get(route_path)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"d1": 1, "d2": 2, "count": 2}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"


# Sync/Async Interaction Tests
@pytest.mark.asyncio
async def test_async_route_can_run_sync_dep(app: Unchained, async_test_client: UnchainedAsyncTestClient):
    route_path = "/async-runs-sync"
    app.get(route_path)(route_async_needs_sync)
    response = await async_test_client.get(route_path)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"async_got_sync_val": 1, "count": 1}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"
    assert sync_counter == 1, "Sync counter should be 1"
    assert async_counter == 0, "Async counter should be 0"


@pytest.mark.asyncio
async def test_async_route_can_run_sync_and_async_deps(app: Unchained, async_test_client: UnchainedAsyncTestClient):
    route_path = "/async-runs-both"
    app.get(route_path)(route_async_needs_sync_and_async)
    response = await async_test_client.get(route_path)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    # Both counters incremented once
    expected_json = {"sync_val": 1, "async_val": 1, "sync_count": 1, "async_count": 1}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"
    assert sync_counter == 1, "Sync counter should be 1"
    assert async_counter == 1, "Async counter should be 1"


@pytest.mark.asyncio
async def test_async_context_runs_sync_dep_needing_async(app: Unchained, async_test_client: UnchainedAsyncTestClient):
    route_path = "/async-sync-needs-async"
    app.get(route_path)(route_async_runs_sync_dep_needs_async)
    response = await async_test_client.get(route_path)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    # Async counter incremented by nested dep
    expected_json = {"sync_got_async_val": 1}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"
    assert sync_counter == 0, "Sync counter should be 0"
    assert async_counter == 1, "Async counter should be 1"


# def test_sync_route_cannot_run_async_dep(app: Unchained, test_client: UnchainedTestClient):
#     """Verify that a sync route handler cannot execute an async dependency."""
#     route_path = "/sync-needs-async"
#     app.get(route_path)(route_sync_needs_async)
#     with pytest.raises(DIError) as excinfo:
#         test_client.get(route_path)
#     assert "Cannot run async dependency" in str(excinfo.value), (
#         f"Route {route_path}: Expected DIError for async dep in sync route."
#     )
#     assert async_counter == 0, "Async counter should not have incremented"
