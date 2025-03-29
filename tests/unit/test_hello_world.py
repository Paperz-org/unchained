import pytest

from tests.utils.unchained_test_client import UnchainedTestClient
from unchained import Unchained


def setup_routes(api: Unchained) -> None:
    """Set up the routes for testing."""
    @api.get("/hello")
    def hello_world(request):
        return {"message": "Hello, World!"}

@pytest.fixture
def api(api: Unchained) -> Unchained:
    """Set up routes for this test module."""
    setup_routes(api)
    return api

@pytest.fixture
def client(api: Unchained) -> UnchainedTestClient:
    return UnchainedTestClient(api)

def test_hello_world(client: UnchainedTestClient) -> None:
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
    
    # You can also access the deserialized data using the data property
    assert response.data == {"message": "Hello, World!"}