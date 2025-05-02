"""
Tests for nested Depends usage (nesting, multi-level, branching, param resolution).
"""

from typing import Annotated, Callable

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Depends, Unchained
from unchained.responses import HTTPResponse

# --- Dependencies ---


# Basic Nesting
def dep_level_1_sync():
    return "level1"


def dep_level_2_sync(l1: Annotated[str, Depends(dep_level_1_sync)]):
    return f"{l1}_level2"


async def dep_level_1_async():
    return "level1_async"


async def dep_level_2_async(l1: Annotated[str, Depends(dep_level_1_async)]):
    return f"{l1}_level2_async"


# Multi-Level Nesting
def dep_level_3_sync(l2: Annotated[str, Depends(dep_level_2_sync)]):
    return f"{l2}_level3"


async def dep_level_3_async(l2: Annotated[str, Depends(dep_level_2_async)]):
    return f"{l2}_level3_async"


# Branching
def dep_shared_base_sync():
    return "shared_base"


def dep_branch_a_sync(base: Annotated[str, Depends(dep_shared_base_sync)]):
    return f"branch_a({base})"


def dep_branch_b_sync(base: Annotated[str, Depends(dep_shared_base_sync)]):
    return f"branch_b({base})"


async def dep_shared_base_async():
    return "shared_base_async"


async def dep_branch_a_async(base: Annotated[str, Depends(dep_shared_base_async)]):
    return f"branch_a({base})"


async def dep_branch_b_async(base: Annotated[str, Depends(dep_shared_base_async)]):
    return f"branch_b({base})"


# Parameter Resolution within Dependency
def dep_needs_path_param_sync(item_id: str, prefix: str = "item"):  # item_id from path
    return f"{prefix}:{item_id}"


async def dep_needs_path_param_async(item_id: int, prefix: str = "item_async"):  # item_id from path
    return f"{prefix}:{item_id * 10}"


# --- Routes ---


def route_sync_basic_nested(l2: Annotated[str, Depends(dep_level_2_sync)]):
    return {"value": l2}


def route_sync_multi_level(l3: Annotated[str, Depends(dep_level_3_sync)]):
    return {"value": l3}


def route_sync_branching(a: Annotated[str, Depends(dep_branch_a_sync)], b: Annotated[str, Depends(dep_branch_b_sync)]):
    # Assumes dep_shared_base_sync runs only once due to caching
    return {"a": a, "b": b}


def route_sync_dep_with_path_param(result: Annotated[str, Depends(dep_needs_path_param_sync)]):
    return {"result": result}


async def route_async_basic_nested(l2: Annotated[str, Depends(dep_level_2_async)]):
    return {"value": l2}


async def route_async_multi_level(l3: Annotated[str, Depends(dep_level_3_async)]):
    return {"value": l3}


async def route_async_branching(
    a: Annotated[str, Depends(dep_branch_a_async)], b: Annotated[str, Depends(dep_branch_b_async)]
):
    # Assumes dep_shared_base_async runs only once due to caching
    return {"a": a, "b": b}


async def route_async_dep_with_path_param(result: Annotated[str, Depends(dep_needs_path_param_async)]):
    return {"result": result}


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
async def test_nested_basic(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_basic_nested if not is_async else route_async_basic_nested
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/nested-basic-{route_suffix}"
    expected_value = "level1_level2" if not is_async else "level1_async_level2_async"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"value": expected_value}, f"Route {route_path}: Unexpected response JSON."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_nested_multi_level(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_multi_level if not is_async else route_async_multi_level
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/nested-multi-{route_suffix}"
    expected_value = "level1_level2_level3" if not is_async else "level1_async_level2_async_level3_async"
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"value": expected_value}, f"Route {route_path}: Unexpected response JSON."


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_nested_branching(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_branching if not is_async else route_async_branching
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/nested-branching-{route_suffix}"
    base = "shared_base" if not is_async else "shared_base_async"
    expected_value = {"a": f"branch_a({base})", "b": f"branch_b({base})"}
    app.get(route_path)(route)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == expected_value, f"Route {route_path}: Unexpected response JSON."
    # NOTE: Caching verification (shared base running once) requires mocks/counters, not done here.


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_nested_dep_resolves_path_param(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    client_fixture_name: str,
    is_async: bool,
):
    route = route_sync_dep_with_path_param if not is_async else route_async_dep_with_path_param
    test_client = request.getfixturevalue(client_fixture_name)
    base_path = f"/items-{route_suffix}"
    item_value = "abc" if not is_async else 123
    expected_result = f"item:{item_value}" if not is_async else f"item_async:{item_value * 10}"
    request_path = f"{base_path}/{item_value}"
    app.get(f"{base_path}/{{item_id}}")(route)

    response = await make_request(test_client, request_path, is_async)

    assert response.status_code == 200, (
        f"Route {request_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"result": expected_result}, f"Route {request_path}: Unexpected response JSON."
