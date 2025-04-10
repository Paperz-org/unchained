from typing import Annotated, Any

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.request import (
    DEFAULT_RETURN_VALUE,
    REQUEST_DEPENDENCY_PATH,
    REQUEST_ROUTE_PATH,
    REQUEST_ROUTE_WITH_BOTH_REQUEST_AND_DEPENDENCY_PATH,
    REQUEST_ROUTE_WITHOUT_REQUEST_PATH,
)
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Request, Unchained


@pytest.fixture
def client(app: Unchained, test_client: UnchainedTestClient) -> UnchainedTestClient:
    def request_dependency(request: Request) -> dict[str, Any]:
        return {"method": request.method}

    def request_dependency_route(info: Annotated[dict[str, Any], Depends(request_dependency)]) -> dict[str, Any]:
        return info

    def request_route(request: Request) -> dict[str, Any]:
        return {"method": request.method}

    def route_without_request() -> str:
        return DEFAULT_RETURN_VALUE

    def route_with_both_request_and_dependency(
        request: Request, info: Annotated[dict[str, Any], Depends(request_dependency)]
    ) -> dict[str, Any]:
        return {"has_request": request is not None, "method": info["method"]}

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(REQUEST_DEPENDENCY_PATH)(request_dependency_route)
        getattr(app, method)(REQUEST_ROUTE_PATH)(request_route)
        getattr(app, method)(REQUEST_ROUTE_WITHOUT_REQUEST_PATH)(route_without_request)
        getattr(app, method)(REQUEST_ROUTE_WITH_BOTH_REQUEST_AND_DEPENDENCY_PATH)(
            route_with_both_request_and_dependency
        )
    return test_client


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_sync_request_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(REQUEST_DEPENDENCY_PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == method.upper()


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_sync_request_route(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(REQUEST_ROUTE_PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == method.upper()


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_sync_request_route_without_request(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(REQUEST_ROUTE_WITHOUT_REQUEST_PATH)
    assert response.status_code == 200
    assert response.json() == DEFAULT_RETURN_VALUE


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_sync_request_route_with_both_request_and_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(REQUEST_ROUTE_WITH_BOTH_REQUEST_AND_DEPENDENCY_PATH)
    assert response.status_code == 200
    assert response.json() == {"has_request": True, "method": method.upper()}
