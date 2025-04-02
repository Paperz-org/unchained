from typing import Annotated, Any

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.request import PATH
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Depends, Request, Unchained


@pytest.fixture
def client(app: Unchained, async_test_client: UnchainedAsyncTestClient) -> UnchainedAsyncTestClient:
    async def request_dependency(request: Request) -> dict[str, Any]:
        return {"method": request.method, "path": request.url.path}

    async def request_dependency_route(info: Annotated[dict[str, Any], Depends(request_dependency)]) -> dict[str, Any]:
        return info

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(PATH)(request_dependency_route)

    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_request_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == method.upper()
    assert result["path"] == PATH
