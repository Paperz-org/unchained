# """
# Tests for Body Parameter dependency injection features.

# NOTE: Assumes existence of a `unchained.dependencies.Body` marker similar to FastAPI's,
# and integration with Pydantic for validation.
# """

import json
from typing import Annotated, Callable, Optional

import pytest
from _pytest.fixtures import FixtureRequest
from pydantic import BaseModel

from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Unchained
from unchained.dependencies import Body
from unchained.responses import HTTPResponse

# --- Pydantic Models ---


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


# --- Sync Routes ---


def route_sync_body_pydantic(item: Annotated[Item, Body()]):
    return item.model_dump()


# --- Async Routes ---


async def route_async_body_pydantic(item: Annotated[Item, Body()]):
    return item.model_dump()


# --- Test Parametrization ---

PARAMETRIZE_PYDANTIC = pytest.mark.parametrize(
    "route_suffix, route_handler, client_fixture_name, is_async",
    [
        ("sync", route_sync_body_pydantic, "test_client", False),
        ("async", route_async_body_pydantic, "async_test_client", True),
    ],
)


# --- Test Helpers ---


async def make_request(test_client, route_path: str, is_async: bool, json_data: dict) -> HTTPResponse:
    if is_async:
        return await test_client.post(route_path, json=json_data)
    else:
        return test_client.post(route_path, json=json_data)


# --- Test Cases ---


@pytest.mark.skip(reason="Body dependency not yet supported")
@PARAMETRIZE_PYDANTIC
@pytest.mark.asyncio
async def test_body_pydantic_valid(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/items-valid-{route_suffix}/"
    item_data = {"name": "Test Item", "price": 19.99}
    app.post(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async, json_data=item_data)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"name": "Test Item", "price": 19.99, "is_offer": None}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"


@pytest.mark.skip(reason="Body dependency not yet supported")
@PARAMETRIZE_PYDANTIC
@pytest.mark.asyncio
async def test_body_pydantic_valid_with_optional(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/items-optional-{route_suffix}/"
    item_data = {"name": "Test Item", "price": 19.99, "is_offer": True}
    app.post(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async, json_data=item_data)

    assert response.status_code == 200, (
        f"Route {route_path}: Expected 200, got {response.status_code}. Response: {response.content.decode()}"
    )
    expected_json = {"name": "Test Item", "price": 19.99, "is_offer": True}
    assert response.json() == expected_json, f"Route {route_path}: Expected {expected_json}, got {response.json()}"


@pytest.mark.skip(reason="Body dependency not yet supported")
@PARAMETRIZE_PYDANTIC
@pytest.mark.asyncio
async def test_body_pydantic_invalid_missing_field(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/items-missing-{route_suffix}/"
    item_data = {"price": 19.99}  # Missing 'name'
    app.post(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async, json_data=item_data)
    data = json.loads(response.content.decode())

    assert response.status_code == 422, (
        f"Route {route_path}: Expected 422, got {response.status_code}. Response: {data}"
    )
    assert "detail" in data and isinstance(data["detail"], list) and len(data["detail"]) > 0, (
        f"Route {route_path}: Expected 'detail' list in error response: {data}"
    )
    error_detail = data["detail"][0]
    assert "msg" in error_detail, f"Route {route_path}: Expected 'msg' in error detail: {error_detail}"
    # Check for message indicating required field
    assert "field required" in error_detail["msg"].lower(), (
        f"Route {route_path}: Expected 'field required' message, got: {error_detail['msg']}"
    )
    # Optionally, check which field was missing if the detail includes it (e.g., in `loc`)
    assert "loc" in error_detail and "name" in error_detail["loc"], (
        f"Route {route_path}: Expected error location to include 'name': {error_detail.get('loc')}"
    )


@pytest.mark.skip(reason="Body dependency not yet supported")
@PARAMETRIZE_PYDANTIC
@pytest.mark.asyncio
async def test_body_pydantic_invalid_wrong_type(
    app: Unchained,
    request: FixtureRequest,
    route_suffix: str,
    route_handler: Callable,
    client_fixture_name: str,
    is_async: bool,
):
    test_client = request.getfixturevalue(client_fixture_name)
    route_path = f"/items-type-error-{route_suffix}/"
    item_data = {"name": "Test Item", "price": "nineteen-ninety-nine"}  # Wrong type for price
    app.post(route_path)(route_handler)

    response = await make_request(test_client, route_path, is_async, json_data=item_data)
    data = json.loads(response.content.decode())

    assert response.status_code == 422, (
        f"Route {route_path}: Expected 422, got {response.status_code}. Response: {data}"
    )
    assert "detail" in data and isinstance(data["detail"], list) and len(data["detail"]) > 0, (
        f"Route {route_path}: Expected 'detail' list in error response: {data}"
    )
    error_detail = data["detail"][0]
    assert "msg" in error_detail, f"Route {route_path}: Expected 'msg' in error detail: {error_detail}"
    # Check for message indicating incorrect type
    assert "float" in error_detail["msg"].lower(), (
        f"Route {route_path}: Expected message about float type, got: {error_detail['msg']}"
    )
    # Optionally, check which field had the wrong type if the detail includes it (e.g., in `loc`)
    assert "loc" in error_detail and "price" in error_detail["loc"], (
        f"Route {route_path}: Expected error location to include 'price': {error_detail.get('loc')}"
    )
