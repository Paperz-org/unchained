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
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Depends, Request, Unchained


@pytest.fixture
def client(app: Unchained, async_test_client: UnchainedAsyncTestClient) -> UnchainedAsyncTestClient:
    async def request_dependency(request: Request) -> dict[str, Any]:
        return {"method": request.method, "path": request.url.path}

    async def request_dependency_route(info: Annotated[dict[str, Any], Depends(request_dependency)]) -> dict[str, Any]:
        return info
    
    async def request_route(request: Request) -> dict[str, Any]:
        return {"method": request.method, "path": request.url.path}
    
    async def route_without_request() -> str:
        return DEFAULT_RETURN_VALUE
    
    async def route_with_both_request_and_dependency(request: Request, info: Annotated[dict[str, Any], Depends(request_dependency)]) -> dict[str, Any]:
        return {"has_request": request is not None, "method": info["method"], "path": info["path"]}

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(REQUEST_DEPENDENCY_PATH)(request_dependency_route)
        getattr(app, method)(REQUEST_ROUTE_PATH)(request_route)
        getattr(app, method)(REQUEST_ROUTE_WITHOUT_REQUEST_PATH)(route_without_request)
        getattr(app, method)(REQUEST_ROUTE_WITH_BOTH_REQUEST_AND_DEPENDENCY_PATH)(route_with_both_request_and_dependency)
    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_request_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(REQUEST_DEPENDENCY_PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == method.upper()
    assert result["path"] == REQUEST_DEPENDENCY_PATH

@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_request_route(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(REQUEST_ROUTE_PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == method.upper()
    assert result["path"] == REQUEST_ROUTE_PATH

@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_request_route_without_request(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(REQUEST_ROUTE_WITHOUT_REQUEST_PATH)
    assert response.status_code == 200
    assert response.json() == DEFAULT_RETURN_VALUE

@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_request_route_with_both_request_and_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(REQUEST_ROUTE_WITH_BOTH_REQUEST_AND_DEPENDENCY_PATH)
    assert response.status_code == 200
    assert response.json() == {"has_request": True, "method": method.upper(), "path": REQUEST_ROUTE_WITH_BOTH_REQUEST_AND_DEPENDENCY_PATH}
