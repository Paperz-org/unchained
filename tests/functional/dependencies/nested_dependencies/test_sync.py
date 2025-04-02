from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    DOUBLE_NESTED_PATH,
    EXPECTED_DOUBLE_NESTED_RESULT,
    EXPECTED_NESTED_RESULT,
    NESTED_PATH,
    OVERRIDE_NESTED_PATH,
    TEST_RETURN_VALUE_1,
    TEST_RETURN_VALUE_2,
)
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(app: Unchained, test_client: UnchainedTestClient) -> UnchainedTestClient:
    def first_dependency() -> str:
        return TEST_RETURN_VALUE_1

    def second_dependency() -> str:
        return TEST_RETURN_VALUE_2

    def nested_dependency(
        dep1: Annotated[str, Depends(first_dependency)],
        dep2: Annotated[str, Depends(second_dependency)],
    ) -> str:
        return f"{dep1}_{dep2}"

    def double_nested_dependency(
        nested: Annotated[str, Depends(nested_dependency)],
        dep1: Annotated[str, Depends(first_dependency)],
    ) -> str:
        return f"{nested}_{dep1}"

    def nested_route(result: Annotated[str, Depends(nested_dependency)]) -> str:
        return result

    def double_nested_route(
        result: Annotated[str, Depends(double_nested_dependency)],
    ) -> str:
        return result

    def override_route(
        result: Annotated[str, Depends(nested_dependency)],
        _: Annotated[str, Depends(first_dependency, use_cache=False)],
    ) -> str:
        return result

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(NESTED_PATH)(nested_route)
        getattr(app, method)(DOUBLE_NESTED_PATH)(double_nested_route)
        getattr(app, method)(OVERRIDE_NESTED_PATH)(override_route)

    return test_client


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_nested_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(NESTED_PATH)
    assert response.status_code == 200
    assert response.json() == EXPECTED_NESTED_RESULT


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_double_nested_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(DOUBLE_NESTED_PATH)
    assert response.status_code == 200
    assert response.json() == EXPECTED_DOUBLE_NESTED_RESULT


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_override_nested_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(OVERRIDE_NESTED_PATH)
    assert response.status_code == 200
    assert response.json() == EXPECTED_NESTED_RESULT
