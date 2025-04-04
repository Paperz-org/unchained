from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    DOUBLE_NESTED_PATH,
    EXPECTED_DOUBLE_NESTED_RESULT,
    EXPECTED_NESTED_RESULT,
    MIXED_DEPENDENCIES_PATH,
    NESTED_PATH,
    OVERRIDE_NESTED_PATH,
    TEST_RETURN_VALUE_1,
    TEST_RETURN_VALUE_2,
)
from tests.utils.client import UnchainedAsyncTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(app: Unchained, async_test_client: UnchainedAsyncTestClient) -> UnchainedAsyncTestClient:
    async def first_dependency() -> str:
        return TEST_RETURN_VALUE_1

    async def second_dependency() -> str:
        return TEST_RETURN_VALUE_2

    async def nested_dependency(
        dep1: Annotated[str, Depends(first_dependency)],
        dep2: Annotated[str, Depends(second_dependency)],
    ) -> str:
        return f"{dep1}_{dep2}"

    async def double_nested_dependency(
        nested: Annotated[str, Depends(nested_dependency)],
        dep1: Annotated[str, Depends(first_dependency)],
    ) -> str:
        return f"{nested}_{dep1}"

    def sync_dependency() -> str:
        return "sync_value"

    async def nested_route(result: Annotated[str, Depends(nested_dependency)]) -> str:
        return result

    async def double_nested_route(result: Annotated[str, Depends(double_nested_dependency)]) -> str:
        return result

    async def override_route(
        result: Annotated[str, Depends(nested_dependency)],
        _: Annotated[str, Depends(first_dependency, use_cache=False)],
    ) -> str:
        return result

    async def mixed_route(
        sync_result: Annotated[str, Depends(sync_dependency)], async_result: Annotated[str, Depends(first_dependency)]
    ) -> str:
        return f"{sync_result}_{async_result}"

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(NESTED_PATH)(nested_route)
        getattr(app, method)(DOUBLE_NESTED_PATH)(double_nested_route)
        getattr(app, method)(OVERRIDE_NESTED_PATH)(override_route)
        getattr(app, method)(MIXED_DEPENDENCIES_PATH)(mixed_route)

    return async_test_client


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_nested_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(NESTED_PATH)
    assert response.status_code == 200
    assert response.json() == EXPECTED_NESTED_RESULT


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_double_nested_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(DOUBLE_NESTED_PATH)
    assert response.status_code == 200
    assert response.json() == EXPECTED_DOUBLE_NESTED_RESULT


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_async_override_nested_dependency(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(OVERRIDE_NESTED_PATH)
    assert response.status_code == 200
    assert response.json() == EXPECTED_NESTED_RESULT


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
async def test_mixed_dependencies(client: UnchainedAsyncTestClient, method: str) -> None:
    response = await getattr(client, method)(MIXED_DEPENDENCIES_PATH)
    assert response.status_code == 200
    assert response.json() == f"sync_value_{TEST_RETURN_VALUE_1}"
