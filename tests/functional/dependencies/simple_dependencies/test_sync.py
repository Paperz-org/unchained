from typing import Annotated

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.simple_dependencies import (
    ANOTHER_TEST_RETURN_VALUE,
    SIMPLE_DEPENDENCY_PATH,
    SIMPLE_DEPENDENCY_WITH_ANOTHER_DEPENDENCY_PATH,
    TEST_RETURN_VALUE,
)
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Unchained


@pytest.fixture
def client(
    app: Unchained, test_client: UnchainedTestClient
) -> UnchainedTestClient:
    def sync_simple_dependency() -> str:
        return TEST_RETURN_VALUE
    
    def another_sync_simple_dependency() -> str:
        return ANOTHER_TEST_RETURN_VALUE

    def sync_simple_dependency_route(
        dependency: Annotated[str, Depends(sync_simple_dependency)],
    ):
        return dependency
    
    def sync_simple_dependency_route_with_another_dependency(
        dependency: Annotated[str, Depends(sync_simple_dependency)],
            another_dependency: Annotated[str, Depends(another_sync_simple_dependency)],
    ):
        return f"{dependency}_{another_dependency}"

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(SIMPLE_DEPENDENCY_PATH)(sync_simple_dependency_route)
        getattr(app, method)(SIMPLE_DEPENDENCY_WITH_ANOTHER_DEPENDENCY_PATH)(sync_simple_dependency_route_with_another_dependency)
    return test_client


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_sync_simple_dependency(
    client: UnchainedTestClient, method: str
) -> None:
    response = getattr(client, method)(SIMPLE_DEPENDENCY_PATH)
    assert response.status_code == 200
    assert response.json() == TEST_RETURN_VALUE

@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_sync_simple_dependency_with_another_dependency(
    client: UnchainedTestClient, method: str
) -> None:
    response = getattr(client, method)(SIMPLE_DEPENDENCY_WITH_ANOTHER_DEPENDENCY_PATH)
    assert response.status_code == 200
    assert response.json() == f"{TEST_RETURN_VALUE}_{ANOTHER_TEST_RETURN_VALUE}"
