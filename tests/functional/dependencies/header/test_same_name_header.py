from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.header import TEST_HEADER_VALUE, HeaderTestCase
from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from tests.utils.test_case import (
    ExpectedResponse,
    get_async_test_case,
    get_sync_test_case,
)
from unchained.dependencies.header import Header
from unchained.unchained import Unchained


def route_same_name_header(x_custom_header: Annotated[str, Header()]) -> None:
    return x_custom_header


def route_same_name_header_explicit(value: Annotated[str, Header("x_custom_header")]) -> None:
    return value


async def route_same_name_header_async(x_custom_header: Annotated[str, Header()]) -> None:
    return x_custom_header


async def route_same_name_header_explicit_async(value: Annotated[str, Header("x_custom_header")]) -> None:
    return value


def error_message(header_name: str) -> str:
    return f"Missing header: {header_name}"


test_cases = [
    HeaderTestCase(
        route_func=route_same_name_header,
        request_headers={"x_custom_header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
    HeaderTestCase(
        route_func=route_same_name_header_explicit,
        request_headers={"x_custom_header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
    HeaderTestCase(
        route_func=route_same_name_header_async,
        request_headers={"x_custom_header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
    HeaderTestCase(
        route_func=route_same_name_header_explicit_async,
        request_headers={"x_custom_header": TEST_HEADER_VALUE},
        expected_response=ExpectedResponse(status=200, message=TEST_HEADER_VALUE),
    ),
]


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_same_name_header_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: HeaderTestCase,
) -> None:
    # TODO do that in a fixture ?
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
async def test_same_name_header_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: HeaderTestCase,
) -> None:
    # TODO do that in a fixture ?
    # Arrange
    getattr(app, method)("/")(case.route_func)

    # Act
    response = await getattr(async_test_client, method)("/", headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
