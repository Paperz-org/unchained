from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    DOUBLE_NESTED_PATH,
    EXPECTED_DOUBLE_NESTED_RESULT,
    EXPECTED_HEADER_RESULT,
    EXPECTED_NESTED_RESULT,
    HEADER_DEPENDENCY_PATH,
    NESTED_PATH,
    OVERRIDE_NESTED_PATH,
    TEST_HEADER_VALUE,
    TEST_RETURN_VALUE_1,
    TEST_RETURN_VALUE_2,
)
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Unchained
from unchained.dependencies.header import Header


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
        nested_result: Annotated[str, Depends(nested_dependency)],
        dep1: Annotated[str, Depends(first_dependency)],
    ) -> str:
        return f"{nested_result}_{dep1}"

    def header_dependency(x_test_header: Annotated[str, Header()]) -> str:
        return x_test_header

    def nested_header_dependency(
        header_val: Annotated[str, Depends(header_dependency)],
        dep1: Annotated[str, Depends(first_dependency)],
    ) -> str:
        return f"{header_val}_{dep1}"

    def nested_route(nested_result: Annotated[str, Depends(nested_dependency)]) -> str:
        return nested_result

    def double_nested_route(
        double_nested_result: Annotated[str, Depends(double_nested_dependency)],
    ) -> str:
        return double_nested_result

    def override_route(
        nested_result: Annotated[str, Depends(nested_dependency)],
        _: Annotated[str, Depends(first_dependency, use_cache=False)],
    ) -> str:
        return nested_result

    def header_route(header_result: Annotated[str, Depends(nested_header_dependency)]) -> str:
        return header_result

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(NESTED_PATH)(nested_route)
        getattr(app, method)(DOUBLE_NESTED_PATH)(double_nested_route)
        getattr(app, method)(OVERRIDE_NESTED_PATH)(override_route)
        getattr(app, method)(HEADER_DEPENDENCY_PATH)(header_route)

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


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_nested_header_dependency(client: UnchainedTestClient, method: str) -> None:
    headers = {"X-Test-Header": TEST_HEADER_VALUE}
    response = getattr(client, method)(HEADER_DEPENDENCY_PATH, headers=headers)
    assert response.status_code == 200
    assert response.json() == EXPECTED_HEADER_RESULT
