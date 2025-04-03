from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.header import PATH, TEST_HEADER_VALUE
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Unchained
from unchained.dependencies.header import Header


@pytest.fixture
def client(app: Unchained, async_test_client: UnchainedAsyncTestClient) -> UnchainedAsyncTestClient:
    async def header_dependency_route(x_api_key: Annotated[str, Header()]) -> str:
        return x_api_key

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(PATH)(header_dependency_route)

    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_header_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(PATH, headers={"X-API-Key": TEST_HEADER_VALUE})
    assert response.status_code == 200
    assert response.json() == TEST_HEADER_VALUE
