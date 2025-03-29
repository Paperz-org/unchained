"""
Global test configuration and shared fixtures.

This file contains fixtures that can be used across multiple test modules.
"""
import pytest

from tests.utils.unchained_test_client import UnchainedTestClient
from unchained import Unchained


@pytest.fixture
def api():
    """Create a new Unchained API instance for tests."""
    app = Unchained()
    app()  # Initialize the application
    return app

@pytest.fixture
def client(api):
    """Provides a test client for the Unchained application."""
    return UnchainedTestClient(api) 