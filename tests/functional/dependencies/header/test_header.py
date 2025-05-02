"""
Tests for Header dependency injection features.
"""

from typing import Annotated, Callable, Optional

import pytest
from _pytest.fixtures import FixtureRequest

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Unchained
from unchained.dependencies import Header
from unchained.errors import ValidationError
from unchained.responses import HTTPResponse

# --- Sync Routes ---


def route_sync_required_header(val: Annotated[str, Header(param_name="X-Required")]):
    return {"value": val}


def route_sync_optional_header(val: Annotated[Optional[str], Header("X-Optional")] = "default"):
    return {"value": val}


def route_sync_case_insensitive(val: Annotated[str, Header("X-Mixed-Case")]):
    return {"value": val}


def route_sync_infer_name(x_infer_dash_me: Annotated[str, Header()]):
    return {"value": x_infer_dash_me}


def route_sync_multiple_headers(h1: Annotated[str, Header("X-H1")], h2: Annotated[str, Header("X-H2")]) -> dict:
    return {"h1": h1, "h2": h2}


# --- Async Routes ---


async def route_async_required_header(val: Annotated[str, Header("X-Required")]):
    return {"value": val}


async def route_async_optional_header(val: Annotated[Optional[str], Header("X-Optional")] = "default"):
    return {"value": val}


async def route_async_case_insensitive(val: Annotated[str, Header("X-Mixed-Case")]):
    return {"value": val}


async def route_async_infer_name(x_infer_dash_me: Annotated[str, Header()]):
    return {"value": x_infer_dash_me}


async def route_async_multiple_headers(h1: Annotated[str, Header("X-H1")], h2: Annotated[str, Header("X-H2")]) -> dict:
    return {"h1": h1, "h2": h2}


# --- Test Cases ---

PARAMETRIZE_CLIENT = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_required_header, "test_client", False),
        ("async", route_async_required_header, "async_test_client", True),
    ],
)


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_header_required_provided(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/test-required-{route_suffix}"
    headers = {"X-Required": "test-value"}
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async, headers=headers)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected status 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_data = {"value": "test-value"}
    assert response.json() == expected_data, f"Route {route_path}: Expected {expected_data}, got {response.json()}"


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_header_required_missing_raises_validation_error(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/test-missing-{route_suffix}"
    app.get(route_path)(route_handler)

    with pytest.raises(ValidationError) as excinfo:
        await make_request(test_client, route_path, is_async)

    assert "Missing header: X-Required" in str(excinfo.value), (
        f"Route {route_path}: Incorrect or missing ValidationError message."
    )


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_header_optional_not_provided_uses_default(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/test-optional-default-{route_suffix}"
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async=is_async)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected status 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_data = {"value": "default"}
    assert response.json() == expected_data, f"Route {route_path}: Expected {expected_data}, got {response.json()}"


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_header_optional_provided_uses_value(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/test-optional-provided-{route_suffix}"
    headers = {"X-Optional": "provided"}
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async=is_async, headers=headers)
    assert response.status_code == 200, (
        f"Route {route_path}: Expected status 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_data = {"value": "provided"}
    assert response.json() == expected_data, f"Route {route_path}: Expected {expected_data}, got {response.json()}"


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_header_lookup_is_case_insensitive(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/test-case-insensitive-{route_suffix}"
    headers = {"x-mixed-case": "case-test"}  # Request header is lowercase
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async=is_async, headers=headers)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected status 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_data = {"value": "case-test"}
    assert response.json() == expected_data, f"Route {route_path}: Expected {expected_data}, got {response.json()}"


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_header_name_inferred_from_param(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/test-infer-{route_suffix}"
    headers = {"x-infer-dash-me": "inferred"}  # Header matches dashed param name
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async, headers=headers)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected status 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_data = {"value": "inferred"}
    assert response.json() == expected_data, f"Route {route_path}: Expected {expected_data}, got {response.json()}"


@PARAMETRIZE_CLIENT
@pytest.mark.asyncio
async def test_header_multiple_different_headers(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/test-multiple-{route_suffix}"
    headers = {"X-H1": "val1", "X-H2": "val2"}
    app.get(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async, headers=headers)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected status 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_data = {"h1": "val1", "h2": "val2"}
    assert response.json() == expected_data, f"Route {route_path}: Expected {expected_data}, got {response.json()}"


# --- Test Helpers ---


async def make_request(test_client, route_path: str, is_async: bool, headers: dict | None = None) -> HTTPResponse:
    kwargs = {"headers": headers} if headers else {}
    if is_async:
        return await test_client.get(route_path, **kwargs)
    else:
        return test_client.get(route_path, **kwargs)
