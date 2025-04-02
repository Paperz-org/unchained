from typing import Annotated, Any

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.request import PATH
from tests.utils.client import UnchainedTestClient
from unchained import Depends, Request, Unchained


@pytest.fixture
def client(app: Unchained, test_client: UnchainedTestClient) -> UnchainedTestClient:
    def request_dependency(request: Request) -> dict[str, Any]:
        return {"method": request.method, "path": request.url.path}

    def request_dependency_route(info: Annotated[dict, Depends(request_dependency)]):
        return info

    for method in SUPPORTED_HTTP_METHODS:
        getattr(app, method)(PATH)(request_dependency_route)

    return test_client


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
def test_request_dependency(client: UnchainedTestClient, method: str) -> None:
    response = getattr(client, method)(PATH)
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == method.upper()
    assert result["path"] == PATH
