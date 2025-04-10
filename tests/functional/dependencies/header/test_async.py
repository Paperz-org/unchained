from typing import Annotated

import pytest

from tests.functional.dependencies.header import PATH, TEST_HEADER_VALUE
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Request, Unchained
from unchained.dependencies.header import Header


@pytest.fixture
def client(app: Unchained, async_test_client: UnchainedAsyncTestClient) -> UnchainedAsyncTestClient:
    # @app.get(PATH)
    # async def get_header_dependency_route(request: Request, x_api_key: Annotated[str, Header()]) -> str:
    #     return x_api_key

    # @app.post(PATH)
    # async def post_header_dependency_route(request: Request, x_api_key: Annotated[str, Header()]) -> str:
    #     return x_api_key

    # @app.put(PATH)
    # async def put_header_dependency_route(request: Request, x_api_key: Annotated[str, Header()]) -> str:
    #     return x_api_key

    @app.get(PATH, tags=["GET"])
    @app.delete(PATH, tags=["DELETE"])
    async def delete_header_dependency_route(request: Request, x_api_key: Annotated[str, Header()]) -> str:
        return x_api_key

    # for method in SUPPORTED_HTTP_METHODS:
    #     getattr(app, method)(PATH)(get_header_dependency_route)

    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["delete", "get"])
async def test_async_header_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(PATH, headers={"X-API-Key": TEST_HEADER_VALUE})
    assert response.status_code == 200
    assert response.json() == TEST_HEADER_VALUE
