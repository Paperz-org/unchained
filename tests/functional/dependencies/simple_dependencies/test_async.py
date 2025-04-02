from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.simple_dependencies import PATH, TEST_RETURN_VALUE
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(
    app: Unchained, async_test_client: UnchainedAsyncTestClient
) -> UnchainedAsyncTestClient:
    async def async_simple_dependency() -> str:
        return TEST_RETURN_VALUE

    async def async_simple_dependency_route(
        dependency: Annotated[str, Depends(async_simple_dependency)],
    ):
        return dependency

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(PATH)(async_simple_dependency_route)

    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_simple_dependency(
    client: UnchainedAsyncTestClient, method: str
) -> None:
    response = await getattr(client, method)(PATH)
    assert response.status_code == 200
    assert response.json() == TEST_RETURN_VALUE
