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


# Sync Routes
def multi_header_args(x_api_key: Annotated[str, Header()], x_client_id: Annotated[str, Header()]) -> Dict[str, str]:
    """Route expecting multiple headers via argument names."""
    return {"api_key": x_api_key, "client_id": x_client_id}


def multi_header_explicit(
    key: Annotated[str, Header("x-api-key")],
    client_id: Annotated[str, Header("X-Client-ID")],
) -> Dict[str, str]:
    """Route expecting multiple headers via explicit Header definitions."""
    return {"api_key": key, "client_id": client_id}


# Async Routes
async def multi_header_args_async(
    x_api_key: Annotated[str, Header()], x_client_id: Annotated[str, Header()]
) -> Dict[str, str]:
    """Route expecting multiple headers via argument names."""
    return {"api_key": x_api_key, "client_id": x_client_id}


async def multi_header_explicit_async(
    key: Annotated[str, Header("x-api-key")], client_id: Annotated[str, Header("X-Client-ID")]
) -> Dict[str, str]:
    """Route expecting multiple headers via explicit Header definitions."""
    return {"api_key": key, "client_id": client_id}


test_cases = [
    # Sync Cases
    HeaderTestCase(
        route_func=multi_header_args,
        request_headers={"x-api-key": TEST_API_KEY, "x-client-id": TEST_CLIENT_ID},
        expected_response=ExpectedResponse(status=200, message={"api_key": TEST_API_KEY, "client_id": TEST_CLIENT_ID}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit,
        request_headers={"x-api-key": TEST_API_KEY, "x-client-id": TEST_CLIENT_ID},
        expected_response=ExpectedResponse(status=200, message={"api_key": TEST_API_KEY, "client_id": TEST_CLIENT_ID}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit,
        request_headers={"X-Api-Key": TEST_API_KEY, "X-Client-ID": TEST_CLIENT_ID},  # Mixed case request headers
        expected_response=ExpectedResponse(status=200, message={"api_key": TEST_API_KEY, "client_id": TEST_CLIENT_ID}),
    ),
    # Async Cases
    HeaderTestCase(
        route_func=multi_header_args_async,
        request_headers={"x-api-key": TEST_API_KEY, "x-client-id": TEST_CLIENT_ID},
        expected_response=ExpectedResponse(status=200, message={"api_key": TEST_API_KEY, "client_id": TEST_CLIENT_ID}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit_async,
        request_headers={"x-api-key": TEST_API_KEY, "x-client-id": TEST_CLIENT_ID},
        expected_response=ExpectedResponse(status=200, message={"api_key": TEST_API_KEY, "client_id": TEST_CLIENT_ID}),
    ),
    HeaderTestCase(
        route_func=multi_header_explicit_async,
        request_headers={"X-Api-Key": TEST_API_KEY, "X-Client-ID": TEST_CLIENT_ID},  # Mixed case request headers
        expected_response=ExpectedResponse(status=200, message={"api_key": TEST_API_KEY, "client_id": TEST_CLIENT_ID}),
    ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_multiple_headers_sync(
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
async def test_multiple_headers_async(
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
