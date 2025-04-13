from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.params import (
    CUSTOM_PARAM_PATH,
    DEFAULT_PARAM_PATH,
    TEST_CUSTOM_VALUE,
    TEST_DEFAULT_VALUE,
)
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(app: Unchained, test_client: UnchainedTestClient) -> UnchainedTestClient:
    def dependency(required_param: str) -> str:
        return required_param

    def dependency_with_default_param(required_param: str = TEST_DEFAULT_VALUE) -> str:
        return required_param

    def default_param_route(result: Annotated[str, Depends(dependency_with_default_param)]) -> str:
        return result

    def route_required_param(result: Annotated[str, Depends(dependency)]) -> str:
        return result

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(DEFAULT_PARAM_PATH)(default_param_route)
        getattr(app, method)(f"{CUSTOM_PARAM_PATH}/{{required_param}}")(route_required_param)

    return test_client


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_default_param_dependency_without_param(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(DEFAULT_PARAM_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_DEFAULT_VALUE


@pytest.mark.xfail(reason="I don't know if we should handle the path param in the dependency")
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_dependency_with_required_param(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(f"{CUSTOM_PARAM_PATH}/{TEST_CUSTOM_VALUE}")
    assert response.status_code == 200
    assert response.json() == TEST_CUSTOM_VALUE
