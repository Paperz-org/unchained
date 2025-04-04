from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.simple_dependencies import (
    ANOTHER_TEST_RETURN_VALUE,
    SIMPLE_DEPENDENCY_PATH,
    SIMPLE_DEPENDENCY_WITH_ANOTHER_DEPENDENCY_PATH,
    TEST_RETURN_VALUE,
)
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(
    app: Unchained, async_test_client: UnchainedAsyncTestClient
) -> UnchainedAsyncTestClient:
    async def async_simple_dependency() -> str:
        return TEST_RETURN_VALUE
    
    async def another_async_simple_dependency() -> str:
        return ANOTHER_TEST_RETURN_VALUE

    async def async_simple_dependency_route(
        dependency: Annotated[str, Depends(async_simple_dependency)],
    ):
        return dependency
    
    async def async_simple_dependency_route_with_another_dependency(
        dependency: Annotated[str, Depends(async_simple_dependency)],
        another_dependency: Annotated[str, Depends(another_async_simple_dependency)],
    ):
        return f"{dependency}_{another_dependency}"

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(SIMPLE_DEPENDENCY_PATH)(async_simple_dependency_route)
        getattr(app, method)(SIMPLE_DEPENDENCY_WITH_ANOTHER_DEPENDENCY_PATH)(async_simple_dependency_route_with_another_dependency)
    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_simple_dependency(
    client: UnchainedAsyncTestClient, method: str
) -> None:
    response = await getattr(client, method)(SIMPLE_DEPENDENCY_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_RETURN_VALUE

@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_simple_dependency_with_another_dependency(
    client: UnchainedAsyncTestClient, method: str
) -> None:
    response = await getattr(client, method)(SIMPLE_DEPENDENCY_WITH_ANOTHER_DEPENDENCY_PATH)
    assert response.status_code == 200
    assert response.json() == f"{TEST_RETURN_VALUE}_{ANOTHER_TEST_RETURN_VALUE}"
