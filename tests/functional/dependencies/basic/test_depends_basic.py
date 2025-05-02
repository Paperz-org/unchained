"""
Tests for basic Depends usage (callables, complex types, None).
"""

from dataclasses import asdict, dataclass
from typing import Annotated, Callable, Optional

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Depends, Unchained
from unchained.responses import HTTPResponse

# --- Dependencies ---

SYNC_DEP_VALUE = "sync_value"
ASYNC_DEP_VALUE = "async_value"


def sync_dependency() -> str:
    return SYNC_DEP_VALUE


async def async_dependency() -> str:
    return ASYNC_DEP_VALUE


def sync_dep_returns_none() -> None:
    return None


async def async_dep_returns_none() -> None:
    return None


@dataclass
class DepDataclass:
    id: int
    name: str


SYNC_DATACLASS_INSTANCE = DepDataclass(id=1, name="sync_dataclass")
ASYNC_DATACLASS_INSTANCE = DepDataclass(id=2, name="async_dataclass")


def sync_dep_returns_dataclass() -> DepDataclass:
    return SYNC_DATACLASS_INSTANCE


async def async_dep_returns_dataclass() -> DepDataclass:
    return ASYNC_DATACLASS_INSTANCE


# --- Sync Routes ---


def route_sync_basic_dep(val: Annotated[str, Depends(sync_dependency)]):
    return {"value": val}


def route_sync_none_dep(val: Annotated[Optional[str], Depends(sync_dep_returns_none)]):
    # Note: The type hint on `val` should be Optional if the dep can return None
    return {"value": val}


def route_sync_dataclass_dep(val: Annotated[DepDataclass, Depends(sync_dep_returns_dataclass)]):
    return val  # Pydantic handles dataclass serialization


# --- Async Routes ---


async def route_async_basic_dep(val: Annotated[str, Depends(async_dependency)]):
    return {"value": val}


async def route_async_none_dep(val: Annotated[Optional[str], Depends(async_dep_returns_none)]):
    return {"value": val}


async def route_async_dataclass_dep(val: Annotated[DepDataclass, Depends(async_dep_returns_dataclass)]):
    return val


# --- Test Parametrizations ---

PARAMETRIZE_BASIC = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_basic_dep, "test_client", False),
        ("async", route_async_basic_dep, "async_test_client", True),
    ],
)

PARAMETRIZE_NONE = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_none_dep, "test_client", False),
        ("async", route_async_none_dep, "async_test_client", True),
    ],
)

PARAMETRIZE_DATACLASS = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_dataclass_dep, "test_client", False),
        ("async", route_async_dataclass_dep, "async_test_client", True),
    ],
)


# --- Test Helpers ---


async def make_request(test_client, route_path: str, is_async: bool) -> HTTPResponse:
    if is_async:
        return await test_client.get(route_path)
    else:
        return test_client.get(route_path)


# --- Test Cases ---


@PARAMETRIZE_BASIC
@pytest.mark.asyncio
async def test_depends_basic(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/basic-{route_suffix}"
    expected_value = SYNC_DEP_VALUE if not is_async else ASYNC_DEP_VALUE
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"value": expected_value}, f"Route {route_path}: Unexpected response JSON."


@PARAMETRIZE_NONE
@pytest.mark.asyncio
async def test_depends_none(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/none-{route_suffix}"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    assert response.json() == {"value": None}, f"Route {route_path}: Expected value to be None."


@PARAMETRIZE_DATACLASS
@pytest.mark.asyncio
@pytest.mark.skip(reason="Not supported yet")
async def test_depends_dataclass(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/dataclass-{route_suffix}"
    expected_dataclass = SYNC_DATACLASS_INSTANCE if not is_async else ASYNC_DATACLASS_INSTANCE
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    # Use asdict for comparison if the response is automatically serialized
    assert response.json() == asdict(expected_dataclass), f"Route {route_path}: Unexpected response JSON."
