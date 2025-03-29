from typing import Annotated, Dict

import pytest
from ninja import Schema

from tests.utils.unchained_test_client import UnchainedTestClient
from unchained import Unchained


# Define a schema for testing
class Item(Schema):
    name: str
    description: str | None = None
    price: float
    quantity: int = 1

# Dependency injection example
def get_current_user() -> dict:
    return {"id": 1, "username": "testuser"}

def setup_routes(api: Unchained) -> None:
    """Set up the routes for testing."""
    @api.post("/items")
    def create_item(request, item: Item):
        return {"item_id": 1, "item": item.dict()}

    @api.get("/items/{item_id}")
    def get_item(request, item_id: int):
        return {"item_id": item_id, "name": "Test Item"}

    @api.get("/users/me")
    def get_current_user_info(request, user: Annotated[Dict, get_current_user]):
        return user

@pytest.fixture
def api(api: Unchained) -> Unchained:
    """Set up routes for this test module."""
    setup_routes(api)
    return api

def test_create_item(client: UnchainedTestClient) -> None:
    response = client.post(
        "/items", 
        json={"name": "Test Item", "price": 10.5, "quantity": 5}
    )
    assert response.status_code == 200
    assert response.json()["item"]["name"] == "Test Item"
    assert response.json()["item"]["price"] == 10.5
    assert response.json()["item"]["quantity"] == 5

def test_get_item(client: UnchainedTestClient) -> None:
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "name": "Test Item"}
