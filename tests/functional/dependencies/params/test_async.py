from typing import Annotated, Callable

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.params import (
    COMBINED_PARAMS_PATH,
    CUSTOM_PARAM_PATH,
    DEFAULT_PARAM_PATH,
    DYNAMIC_PARAM_PATH,
    TEST_CUSTOM_VALUE,
    TEST_DEFAULT_VALUE,
)
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(app: Unchained, async_test_client: UnchainedAsyncTestClient) -> UnchainedAsyncTestClient:
    def create_async_param_dependency(
        param_value: str = TEST_DEFAULT_VALUE,
    ) -> Callable[[], str]:
        async def dependency() -> str:
            return param_value

        return dependency

    default_dep = create_async_param_dependency()
    custom_dep = create_async_param_dependency(TEST_CUSTOM_VALUE)

    async def using_both_deps(
        default_result: Annotated[str, Depends(default_dep)],
        custom_result: Annotated[str, Depends(custom_dep)],
    ) -> dict:
        return {"default": default_result, "custom": custom_result}

    async def default_param_route(result: Annotated[str, Depends(default_dep)]) -> str:
        return result

    async def custom_param_route(result: Annotated[str, Depends(custom_dep)]) -> str:
        return result

    async def combined_params_route(result: Annotated[dict, Depends(using_both_deps)]) -> dict:
        return result

    async def dynamic_param_route(param_value: str) -> str:
        return param_value

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(DEFAULT_PARAM_PATH)(default_param_route)
        getattr(app, method)(CUSTOM_PARAM_PATH)(custom_param_route)
        getattr(app, method)(COMBINED_PARAMS_PATH)(combined_params_route)
        getattr(app, method)(f"{DYNAMIC_PARAM_PATH}{{param_value}}")(dynamic_param_route)

    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_default_param_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(DEFAULT_PARAM_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_DEFAULT_VALUE


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_custom_param_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(CUSTOM_PARAM_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_CUSTOM_VALUE


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_combined_params_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(COMBINED_PARAMS_PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["default"] == TEST_DEFAULT_VALUE
    assert result["custom"] == TEST_CUSTOM_VALUE


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_dynamic_param(client: UnchainedAsyncTestClient, method: str) -> None:
    dynamic_value = "dynamic-test-value"
    response = await getattr(client, method)(f"{DYNAMIC_PARAM_PATH}{dynamic_value}")
    assert response.status_code == 200
    assert response.json() == dynamic_value
