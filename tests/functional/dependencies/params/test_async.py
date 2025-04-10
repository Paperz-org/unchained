from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.params import (
    CUSTOM_PARAM_PATH,
    DEFAULT_PARAM_PATH,
    TEST_CUSTOM_VALUE,
    TEST_DEFAULT_VALUE,
)
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(app: Unchained, async_test_client: UnchainedAsyncTestClient) -> UnchainedAsyncTestClient:
    async def dependency(param: str) -> str:
        return param

    async def dependency_with_default_param(param: str = TEST_DEFAULT_VALUE) -> str:
        return param

    async def default_param_route(result: Annotated[str, Depends(dependency_with_default_param)]) -> str:
        return result

    async def route(result: Annotated[str, Depends(dependency)]) -> str:
        return result

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(DEFAULT_PARAM_PATH)(default_param_route)
        getattr(app, method)(f"{CUSTOM_PARAM_PATH}/{{required_param}}")(route)

    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_default_param_dependency_without_param(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(DEFAULT_PARAM_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_DEFAULT_VALUE


# @pytest.mark.asyncio
# @pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
# async def test_async_default_param_dependency_with_param(client: UnchainedAsyncTestClient, method: str) -> None:
#     response = await getattr(client, method)(f"{DEFAULT_PARAM_PATH}/{TEST_CUSTOM_VALUE}")
#     assert response.status_code == 200
#     assert response.json() == TEST_CUSTOM_VALUE


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_dependency_without_required_param(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(CUSTOM_PARAM_PATH)
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_dependency_with_required_param(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(f"{CUSTOM_PARAM_PATH}/{TEST_CUSTOM_VALUE}")
    assert response.status_code == 200
    assert response.json() == TEST_CUSTOM_VALUE
