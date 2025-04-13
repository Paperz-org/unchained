from typing import Annotated, Any, Awaitable, Callable, Dict

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.header import (
    TEST_API_KEY,
    TEST_CLIENT_ID,
    HeaderTestCase,
)
from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from tests.utils.test_case import (
    ExpectedResponse,
    get_async_test_case,
    get_sync_test_case,
)
from unchained.dependencies.header import Header
from unchained.unchained import Unchained


def error_message(header_name: str) -> str:
    return f"Missing header: {header_name}"


# --- Sync Routes ---
def single_header_arg(x_api_key: Annotated[str, Header()]) -> str:
    return x_api_key


def single_header_snake(value: Annotated[str, Header("x_api_key")]) -> str:
    return value


def single_header_dash(value: Annotated[str, Header("x-api-key")]) -> str:
    return value


def multi_header_args(x_api_key: Annotated[str, Header()], x_client_id: Annotated[str, Header()]) -> Dict[str, str]:
    return {"api_key": x_api_key, "client_id": x_client_id}


def multi_header_explicit(
    key: Annotated[str, Header("x-api-key")],
    client_id: Annotated[str, Header("X-Client-ID")],
) -> Dict[str, str]:
    return {"api_key": key, "client_id": client_id}


# --- Async Routes ---
async def single_header_arg_async(x_api_key: Annotated[str, Header()]) -> str:
    return x_api_key


async def single_header_snake_async(value: Annotated[str, Header("x_api_key")]) -> str:
    return value


async def single_header_dash_async(value: Annotated[str, Header("x-api-key")]) -> str:
    return value


async def multi_header_args_async(
    x_api_key: Annotated[str, Header()], x_client_id: Annotated[str, Header()]
) -> Dict[str, str]:
    return {"api_key": x_api_key, "client_id": x_client_id}


async def multi_header_explicit_async(
    key: Annotated[str, Header("x-api-key")], client_id: Annotated[str, Header("X-Client-ID")]
) -> Dict[str, str]:
    return {"api_key": key, "client_id": client_id}


test_cases = [
    # --- Sync Cases ---
    # Single missing header
    HeaderTestCase(
        route_func=single_header_arg,
        request_headers={},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_api_key")}]}),
    ),
    HeaderTestCase(
        route_func=single_header_snake,
        request_headers={},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_api_key")}]}),
    ),
    HeaderTestCase(
        route_func=single_header_dash,
        request_headers={},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x-api-key")}]}),
    ),
    # Multiple missing headers (one missing)
    HeaderTestCase(
        route_func=multi_header_args,
        request_headers={"x-client-id": TEST_CLIENT_ID},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_api_key")}]}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit,
        request_headers={"x-api-key": TEST_API_KEY},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x-client-id")}]}),
    ),
    HeaderTestCase(
        route_func=multi_header_args,
        request_headers={"x-api-key": TEST_API_KEY},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_client_id")}]}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit,
        request_headers={"x-api-key": TEST_API_KEY},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x-client-id")}]}),
    ),
    # Multiple missing headers (both missing - marked xfail)
    # HeaderTestCase(
    #     route_func=multi_header_args,
    #     request_headers={},
    #     expected_response=ExpectedResponse(
    #         status=422, message={"detail": [{"msg": error_message("x_api_key")}, {"msg": error_message("x_client_id")}]}
    #     ),
    # ),
    # HeaderTestCase(
    #     route_func=multi_header_explicit,
    #     request_headers={},
    #     expected_response=ExpectedResponse(
    #         status=422, message={"detail": [{"msg": error_message("x-api-key")}, {"msg": error_message("X-Client-ID")}]}
    #     ),
    # ),
    # --- Async Cases ---
    # Single missing header
    HeaderTestCase(
        route_func=single_header_arg_async,
        request_headers={},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_api_key")}]}),
    ),
    HeaderTestCase(
        route_func=single_header_snake_async,
        request_headers={},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_api_key")}]}),
    ),
    HeaderTestCase(
        route_func=single_header_dash_async,
        request_headers={},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x-api-key")}]}),
    ),
    # Multiple missing headers (one missing)
    HeaderTestCase(
        route_func=multi_header_args_async,
        request_headers={"x-client-id": TEST_CLIENT_ID},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_api_key")}]}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit_async,
        request_headers={"x-api-key": TEST_API_KEY},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x-client-id")}]}),
    ),
    HeaderTestCase(
        route_func=multi_header_args_async,
        request_headers={"x-api-key": TEST_API_KEY},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x_client_id")}]}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit_async,
        request_headers={"x-api-key": TEST_API_KEY},
        expected_response=ExpectedResponse(status=422, message={"detail": [{"msg": error_message("x-client-id")}]}),
    ),
    # Multiple missing headers (both missing - marked xfail)
    # HeaderTestCase(
    #     route_func=multi_header_args_async,
    #     request_headers={},
    #     expected_response=ExpectedResponse(
    #         status=422, message={"detail": [{"msg": error_message("x_api_key")}, {"msg": error_message("x_client_id")}]}
    #     ),
    #     xfail="TODO: not working atm, it only returns first fail validation error, looks like a wider issue.",
    # ),
    # HeaderTestCase(
    #     route_func=multi_header_explicit_async,
    #     request_headers={},
    #     expected_response=ExpectedResponse(
    #         status=422, message={"detail": [{"msg": error_message("x-api-key")}, {"msg": error_message("X-Client-ID")}]}
    #     ),
    #     xfail="TODO: not working atm, it only returns first fail validation error, looks like a wider issue.",
    # ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_missing_headers_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: HeaderTestCase,
) -> None:
    # Arrange
    getattr(app, method)("/")(case.route_func)

    # Act
    response = getattr(test_client, method)("/", headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_missing_headers_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: HeaderTestCase,
) -> None:
    # Arrange
    getattr(app, method)("/")(case.route_func)

    # Act
    response = await getattr(async_test_client, method)("/", headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
