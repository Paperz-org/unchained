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
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(app: Unchained, test_client: UnchainedTestClient) -> UnchainedTestClient:
    def create_param_dependency(
        param_value: str = TEST_DEFAULT_VALUE,
    ) -> Callable[[], str]:
        def dependency() -> str:
            return param_value

        return dependency

    # Default parameter dependency
    default_dep = create_param_dependency()

    # Custom parameter dependency
    custom_dep = create_param_dependency(TEST_CUSTOM_VALUE)

    def using_both_deps(
        default_result: Annotated[str, Depends(default_dep)],
        custom_result: Annotated[str, Depends(custom_dep)],
    ) -> dict[str, str]:
        return {"default": default_result, "custom": custom_result}

    def default_param_route(result: Annotated[str, Depends(default_dep)]) -> str:
        return result

    def custom_param_route(result: Annotated[str, Depends(custom_dep)]) -> str:
        return result

    def combined_params_route(result: Annotated[dict, Depends(using_both_deps)]) -> dict:
        return result

    def dynamic_param_route(param_value: str) -> str:
        return param_value

    # Register routes for all HTTP methods
    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(DEFAULT_PARAM_PATH)(default_param_route)
        getattr(app, method)(CUSTOM_PARAM_PATH)(custom_param_route)
        getattr(app, method)(COMBINED_PARAMS_PATH)(combined_params_route)
        getattr(app, method)(f"{DYNAMIC_PARAM_PATH}{{param_value}}")(dynamic_param_route)

    return test_client


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_default_param_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(DEFAULT_PARAM_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_DEFAULT_VALUE


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_custom_param_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(CUSTOM_PARAM_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_CUSTOM_VALUE


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_combined_params_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(COMBINED_PARAMS_PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["default"] == TEST_DEFAULT_VALUE
    assert result["custom"] == TEST_CUSTOM_VALUE


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_dynamic_param(client: UnchainedTestClient, method: str) -> None:
    dynamic_value = "dynamic-test-value"
    response = getattr(client, method)(f"{DYNAMIC_PARAM_PATH}{dynamic_value}")
    assert response.status_code == 200
    assert response.json() == dynamic_value
