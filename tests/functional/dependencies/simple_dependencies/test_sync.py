from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.simple_dependencies import PATH, TEST_RETURN_VALUE
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(app: Unchained, test_client: UnchainedTestClient) -> UnchainedTestClient:
    def simple_dependency() -> str:
        return TEST_RETURN_VALUE

    def simple_dependency_route(dependency: Annotated[str, Depends(simple_dependency)]):
        return dependency

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(PATH)(simple_dependency_route)

    return test_client


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_simple_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(PATH)
    assert response.status_code == 200
    assert response.json() == TEST_RETURN_VALUE
