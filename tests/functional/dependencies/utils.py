from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from unchained import Unchained


def register_routes(app: Unchained, routes: Dict[str, Callable[..., Any]]) -> None:
    """Register route handlers for all supported HTTP methods.
    
    Args:
        app: The Unchained app instance
        routes: A dictionary mapping paths to route handler functions
    """
    for path, handler in routes.items():
        for method in SUPPORTED_HTTP_METHODS:
            getattr(app, method)(path)(handler)


def create_test_endpoint(
    path: str,
    expected_result: Any,
    headers: Optional[Dict[str, str]] = None,
    is_async: bool = False,
) -> Callable:
    """Create a test function for testing an endpoint.
    
    This is a decorator that generates a test function for a specific endpoint.
    Use it like:
    
    @create_test_endpoint("/path", "expected_result")
    def test_name(client, method):
        # This function will automatically have the right test behavior
        # Any code here will run before the assertions
    
    Args:
        path: The endpoint path to test
        expected_result: The expected result from the endpoint
        headers: Optional headers to include in the request
        is_async: Whether the test should be async
    """
    def decorator(func):
        if is_async:
            @pytest.mark.asyncio
            @pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
            @wraps(func)
            async def wrapper(client: UnchainedAsyncTestClient, method: str, *args, **kwargs):
                # Run the original function first
                result = await func(client, method, *args, **kwargs) if is_async else func(client, method, *args, **kwargs)
                
                # Then make the request and assertions
                response = await getattr(client, method)(path, headers=headers)
                assert response.status_code == 200
                assert response.json() == expected_result
                
                return result
        else:
            @pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
            @wraps(func)
            def wrapper(client: UnchainedTestClient, method: str, *args, **kwargs):
                # Run the original function first
                result = func(client, method, *args, **kwargs)
                
                # Then make the request and assertions
                response = getattr(client, method)(path, headers=headers)
                assert response.status_code == 200
                assert response.json() == expected_result
                
                return result
        
        return wrapper
    
    return decorator


def create_client_fixture(
    is_async: bool = False,
) -> Callable:
    """Create a client fixture with a simplified setup.
    
    Usage:
    
    @pytest.fixture
    @create_client_fixture(is_async=True)
    def client(app, async_test_client):
        # Define your dependencies and routes here
        routes = {"/path": handler}
        return routes  # Just return your routes, the fixture handles registration
    
    Args:
        is_async: Whether to use the async client
    """
    def decorator(func):
        @wraps(func)
        def wrapper(app: Unchained, *args, **kwargs):
            client_arg = 'async_test_client' if is_async else 'test_client'
            client = kwargs.get(client_arg)
            
            # Call the original function to get routes
            routes = func(app, *args, **kwargs)
            
            # Register routes
            register_routes(app, routes)
            
            return client
            
        return wrapper
    
    return decorator


def dependency_test(
    path: str, 
    expected_result: Any,
    headers: Optional[Dict[str, str]] = None,
    is_async: bool = False
) -> Callable:
    """Generate a complete test function for a dependency.
    
    This creates a standalone test function without requiring
    a decorated function. Use when you just need a simple test.
    
    Usage:
    test_simple_dep = dependency_test("/path", "expected")
    
    Args:
        path: The endpoint path to test
        expected_result: The expected result
        headers: Optional request headers
        is_async: Whether the test should be async
    """
    if is_async:
        @pytest.mark.asyncio
        @pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
        async def test_func(client: UnchainedAsyncTestClient, method: str) -> None:
            response = await getattr(client, method)(path, headers=headers)
            assert response.status_code == 200
            assert response.json() == expected_result
    else:
        @pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
        def test_func(client: UnchainedTestClient, method: str) -> None:
            response = getattr(client, method)(path, headers=headers)
            assert response.status_code == 200
            assert response.json() == expected_result
               
    return test_func 