"""
Global test configuration and shared fixtures.

This file contains fixtures that can be used across multiple test modules.
"""

import pytest

from unchained import Unchained

from ...utils.client import UnchainedAsyncTestClient, UnchainedTestClient


@pytest.fixture
def app() -> Unchained:
    """Create a new Unchained app instance for tests."""
    app = Unchained()
    # app()
    return app


@pytest.fixture
def test_client(app: Unchained) -> UnchainedTestClient:
    """Provides a test client for the Unchained application."""
    return UnchainedTestClient(app)


@pytest.fixture
def async_test_client(app: Unchained) -> UnchainedAsyncTestClient:
    """Provides a test client for the Unchained application."""
    return UnchainedAsyncTestClient(app)
