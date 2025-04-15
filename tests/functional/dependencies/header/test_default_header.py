from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.header import (
    TEST_HEADER_DEFAULT_VALUE,
    TEST_HEADER_VALUE,
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


# Default value using Header's default parameter
def route_header_default_param(
    value: Annotated[str, Header("x-custom-header", default=TEST_HEADER_DEFAULT_VALUE)],
) -> str:
    return value


async def route_header_default_param_async(
    value: Annotated[str, Header("x-custom-header", default=TEST_HEADER_DEFAULT_VALUE)],
) -> str:
    return value


# Default value using function parameter
def route_param_default(value: Annotated[str, Header("x-custom-header")] = TEST_HEADER_DEFAULT_VALUE) -> str:
    return value


async def route_param_default_async(
    value: Annotated[str, Header("x-custom-header")] = TEST_HEADER_DEFAULT_VALUE,
) -> str:
    return value


test_cases = [
    # Test cases for Header default parameter
    HeaderTestCase(
        route_func=route_header_default_param,
        request_headers={"x-custom-header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
    HeaderTestCase(
        route_func=route_header_default_param,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_DEFAULT_VALUE),
    ),
    HeaderTestCase(
        route_func=route_header_default_param_async,
        request_headers={"x-custom-header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
    HeaderTestCase(
        route_func=route_header_default_param_async,
        request_headers={},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_DEFAULT_VALUE),
    ),
    # Test cases for function parameter default
    HeaderTestCase(
        route_func=route_param_default,
        request_headers={"x-custom-header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
    # HeaderTestCase(
    #     route_func=route_param_default,
    #     request_headers={},
    #     expected_response=ExpectedResponse(status=200, message=TEST_HEADER_DEFAULT_VALUE),
    # ),
    HeaderTestCase(
        route_func=route_param_default_async,
        request_headers={"x-custom-header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
    # HeaderTestCase(
    #     route_func=route_param_default_async,
    #     request_headers={},
    #     expected_response=ExpectedResponse(status=200, message=TEST_HEADER_DEFAULT_VALUE),
    # ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_default_header_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: HeaderTestCase,
) -> None:
    """Test default header values with synchronous routes."""
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
async def test_default_header_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: HeaderTestCase,
) -> None:
    """Test default header values with asynchronous routes."""
    # Arrange
    getattr(app, method)("/")(case.route_func)

    # Act
    response = await getattr(async_test_client, method)("/", headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
