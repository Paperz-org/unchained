from typing import Annotated

import pytest

from tests.utils.client import UnchainedTestClient
from unchained import Unchained


# Define some dependencies
def get_db() -> dict:
    return {"name": "test_db", "connected": True}


def get_user(db: Annotated[dict, get_db]) -> dict:
    # This dependency depends on another dependency
    return {"id": 1, "username": "testuser", "db": db["name"]}


def get_config() -> dict:
    return {"debug": True, "version": "1.0.0"}


def setup_routes(api: Unchained) -> None:
    """Set up the routes for testing."""

    # API routes with various dependency injection patterns
    @api.get("/db")
    def get_db_info(request, db: Annotated[dict, get_db]):
        return db

    @api.get("/user")
    def get_user_info(request, user: Annotated[dict, get_user]):
        return user

    @api.get("/combined")
    def get_combined_info(
        request, user: Annotated[dict, get_user], config: Annotated[dict, get_config]
    ):
        return {"user": user, "config": config}


@pytest.fixture
def api(api: Unchained) -> Unchained:
    """Set up routes for this test module."""
    setup_routes(api)
    return api
