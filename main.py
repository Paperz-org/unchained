import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, Generator, List, Optional, Set, TypeVar, cast

from django.contrib import admin
from fast_depends import Depends

from admin import ProductAdmin, UserAdmin
from models import Order, OrderItem, Product, User
from unchained import Unchained
from unchained.models.base import BaseModel

# Create API instance and set up Django
app = Unchained()

admin.site.register(User, UserAdmin)
admin.site.register(Product, ProductAdmin)

# Security dependencies


class AuthenticationError(Exception):
    """Raised when authentication fails"""

    pass


class AuthorizationError(Exception):
    """Raised when authorization fails"""

    pass


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded"""

    pass


class SecurityContext:
    """Holds security-related information for the current request"""

    _instance = None

    @classmethod
    def get_instance(cls) -> "SecurityContext":
        if cls._instance is None:
            cls._instance = SecurityContext()
        return cls._instance

    def __init__(self) -> None:
        self.tokens: Dict[str, Dict] = {}  # Token storage
        self.rate_limits: Dict[str, Dict] = {}  # Rate limit storage
        self.csrf_tokens: Dict[str, str] = {}  # CSRF token storage
        self.api_keys: Dict[str, Dict[str, Any]] = {}  # API key storage
        print("Security context initialized")

        # Add some demo API keys
        self._initialize_demo_api_keys()

    def _initialize_demo_api_keys(self) -> None:
        """Initialize demo API keys for testing"""
        self.register_api_key("demo-key-1", user_id=1, permissions=["read", "write"], rate_limit=100)
        self.register_api_key("demo-key-2", user_id=2, permissions=["read"], rate_limit=50)
        self.register_api_key("admin-key", user_id=3, permissions=["read", "write", "admin"], rate_limit=1000)

    def register_api_key(self, api_key: str, user_id: int, permissions: List[str], rate_limit: int = 60) -> None:
        """Register a new API key"""
        self.api_keys[api_key] = {
            "user_id": user_id,
            "permissions": permissions,
            "rate_limit": rate_limit,
            "created_at": datetime.now(),
        }
        print(f"API key registered for user {user_id}")

    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate an API key and return its metadata"""
        if not api_key or api_key not in self.api_keys:
            raise AuthenticationError("Invalid API key")

        return self.api_keys[api_key]

    def create_token(self, user_id: int, expires_in: int = 3600) -> str:
        """Create an authentication token for a user"""
        token = secrets.token_hex(32)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        self.tokens[token] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "scopes": ["read", "write"],  # Default scopes
        }
        return token

    def validate_token(self, token: str) -> Dict:
        """Validate an authentication token"""
        if token not in self.tokens:
            raise AuthenticationError("Invalid token")

        token_data = self.tokens[token]
        if datetime.now() > token_data["expires_at"]:
            del self.tokens[token]
            raise AuthenticationError("Token expired")

        return token_data

    def check_rate_limit(self, key: str, limit: int, window: int) -> None:
        """Check if a rate limit has been exceeded"""
        now = time.time()
        if key not in self.rate_limits:
            self.rate_limits[key] = {"count": 1, "window_start": now}
            return

        rate_limit = self.rate_limits[key]
        window_elapsed = now - rate_limit["window_start"]

        if window_elapsed > window:
            # Reset window
            rate_limit["count"] = 1
            rate_limit["window_start"] = now
        else:
            # Increment count
            rate_limit["count"] += 1

            if rate_limit["count"] > limit:
                raise RateLimitExceededError(f"Rate limit exceeded: {limit} requests per {window} seconds")

    def generate_csrf_token(self, session_id: str) -> str:
        """Generate a CSRF token for a session"""
        csrf_token = secrets.token_hex(16)
        self.csrf_tokens[session_id] = csrf_token
        return csrf_token

    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """Validate a CSRF token"""
        if session_id not in self.csrf_tokens:
            return False

        expected_token = self.csrf_tokens[session_id]
        return hmac.compare_digest(expected_token, token)


def security_context() -> Generator[SecurityContext, None, None]:
    """
    Yield dependency that provides the security context.
    The security context is a singleton.
    """
    context = SecurityContext.get_instance()
    try:
        yield context
    finally:
        pass  # Singleton, no cleanup needed


def authenticate_api_key(
    security: Annotated[SecurityContext, Depends(security_context)],
    api_key: Optional[str] = None,  # In a real app, this would come from the request header
) -> Generator[Dict[str, Any], None, None]:
    """
    Yield dependency that authenticates a request based on an API key in the header.
    Raises AuthenticationError if authentication fails.

    In a real application, the API key would be extracted from the request headers:
    api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
    """
    if api_key is None:
        raise AuthenticationError("API key is required")

    print(f"Authenticating API key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")

    try:
        # Validate the API key
        api_key_data = security.validate_api_key(api_key)
        user_id = api_key_data["user_id"]
        print(f"API key authentication successful for user {user_id}")

        try:
            yield api_key_data
        finally:
            # Any cleanup after the request
            print("API key authentication context cleaned up")
    except AuthenticationError as e:
        print(f"API key authentication failed: {e}")
        raise


def check_api_key_permission(
    api_key_data: Annotated[Dict[str, Any], Depends(authenticate_api_key)], required_permission: str = "read"
) -> Generator[Dict[str, Any], None, None]:
    """
    Yield dependency that checks if the API key has the required permission.
    Depends on the authenticate_api_key dependency.
    Raises AuthorizationError if authorization fails.
    """
    permissions = api_key_data["permissions"]
    user_id = api_key_data["user_id"]
    print(f"Checking permission '{required_permission}' for user {user_id} with permissions {permissions}")

    if required_permission not in permissions:
        raise AuthorizationError(f"API key does not have permission: {required_permission}")

    print(f"Permission check successful for '{required_permission}'")

    try:
        yield api_key_data
    finally:
        print("API key permission check context cleaned up")


def api_rate_limit(
    security: Annotated[SecurityContext, Depends(security_context)],
    api_key_data: Annotated[Dict[str, Any], Depends(authenticate_api_key)],
) -> Generator[None, None, None]:
    """
    Yield dependency that implements rate limiting for API keys.
    Uses the rate limit defined in the API key data.
    Raises RateLimitExceededError if rate limit is exceeded.
    """
    user_id = api_key_data["user_id"]
    rate_limit_key = f"api_key:{user_id}"
    limit = api_key_data.get("rate_limit", 60)  # Default to 60 requests per minute

    print(f"Checking API rate limit for {rate_limit_key}, limit: {limit} per minute")

    try:
        # Check if rate limit exceeded (60 seconds window)
        security.check_rate_limit(rate_limit_key, limit, 60)
        print(f"API rate limit check passed for {rate_limit_key}")

        yield
    finally:
        print("API rate limit context cleaned up")


# API-key protected endpoints
@app.get("/api/products")
def api_products(
    request,
    _rate_limit: Annotated[None, Depends(api_rate_limit)],
    api_key_data: Annotated[Dict[str, Any], Depends(check_api_key_permission)],
):
    """API endpoint that requires an API key with read permission"""
    products = [
        {"id": 1, "name": "API Product 1", "price": 29.99},
        {"id": 2, "name": "API Product 2", "price": 49.99},
    ]
    return {"products": products, "user_id": api_key_data["user_id"], "permissions": api_key_data["permissions"]}


@app.post("/api/products")
def create_product(
    request,
    name: str,
    price: float,
    description: str = "",
    api_key_data: Annotated[Dict[str, Any], Depends(check_api_key_permission)] = None,
    _rate_limit: Annotated[None, Depends(api_rate_limit)] = None,
):
    """API endpoint that requires an API key with write permission"""
    # Check for write permission
    if "write" not in api_key_data["permissions"]:
        raise AuthorizationError("API key does not have write permission")

    # In a real implementation, we would create the product in the database
    return {
        "message": f"Product created: {name}, ${price}",
        "user_id": api_key_data["user_id"],
        "permissions": api_key_data["permissions"],
    }


@app.get("/api/admin/users")
def list_users(
    request,
    _rate_limit: Annotated[None, Depends(api_rate_limit)],
    api_key_data: Annotated[Dict[str, Any], Depends(check_api_key_permission)],
):
    """Admin API endpoint that requires an API key with admin permission"""
    # Check for admin permission
    if "admin" not in api_key_data["permissions"]:
        raise AuthorizationError("API key does not have admin permission")

    # In a real implementation, we would fetch users from the database
    users = [
        {"id": 1, "name": "User 1", "email": "user1@example.com"},
        {"id": 2, "name": "User 2", "email": "user2@example.com"},
    ]

    return {"users": users, "admin_user_id": api_key_data["user_id"]}


@app.get("/api/headers-demo")
def headers_demo(
    request,
):
    """Demo endpoint that extracts and displays the API key from headers"""
    # In a real application, you would extract the API key like this:
    # Note: This is just an example showing how to extract headers
    headers = request.headers
    api_key = headers.get("X-API-Key") or headers.get("Authorization")

    # For demo purposes only - don't echo API keys in real applications!
    return {
        "message": "Headers processed",
        "api_key_present": api_key is not None,
        "api_key_preview": f"{api_key[:4]}...{api_key[-4:]}" if api_key and len(api_key) > 8 else None,
    }


# Other security dependencies
def authenticate(
    security: Annotated[SecurityContext, Depends(security_context)],
    token: str = "dummy-token",  # In a real app, this would come from the request
) -> Generator[Dict, None, None]:
    """
    Yield dependency that authenticates a user based on a token.
    Raises AuthenticationError if authentication fails.
    """
    print(f"Authenticating token: {token}")

    try:
        # For demo purposes, create a token if it doesn't exist
        if token == "dummy-token" and token not in security.tokens:
            print("Creating dummy token for demo purposes")
            security.create_token(user_id=1)

        # Validate the token
        user_data = security.validate_token(token)
        print(f"Authentication successful for user {user_data['user_id']}")

        try:
            yield user_data
        finally:
            # Any cleanup after the request (token refresh, logging, etc.)
            print("Authentication context cleaned up")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        raise


def authorize(
    auth_data: Annotated[Dict, Depends(authenticate)], required_scopes: Set[str] = {"read"}
) -> Generator[Dict, None, None]:
    """
    Yield dependency that checks if the authenticated user has the required scopes.
    Depends on the authenticate dependency.
    Raises AuthorizationError if authorization fails.
    """
    user_scopes = set(auth_data["scopes"])
    print(f"Authorizing user {auth_data['user_id']} with scopes {user_scopes}")

    if not required_scopes.issubset(user_scopes):
        missing_scopes = required_scopes - user_scopes
        raise AuthorizationError(f"Missing required scopes: {missing_scopes}")

    print(f"Authorization successful for scopes {required_scopes}")

    try:
        yield auth_data
    finally:
        print("Authorization context cleaned up")


def rate_limit(
    security: Annotated[SecurityContext, Depends(security_context)],
    auth_data: Annotated[Dict, Depends(authenticate)],
    requests_per_minute: int = 60,
) -> Generator[None, None, None]:
    """
    Yield dependency that implements rate limiting.
    Depends on the authenticate dependency to identify the user.
    Raises RateLimitExceededError if rate limit is exceeded.
    """
    user_id = auth_data["user_id"]
    rate_limit_key = f"user:{user_id}"
    print(f"Checking rate limit for {rate_limit_key}")

    try:
        # Check if rate limit exceeded (60 seconds window)
        security.check_rate_limit(rate_limit_key, requests_per_minute, 60)
        print(f"Rate limit check passed for {rate_limit_key}")

        yield
    finally:
        print("Rate limit context cleaned up")


def csrf_protection(
    security: Annotated[SecurityContext, Depends(security_context)],
    auth_data: Annotated[Dict, Depends(authenticate)],
    csrf_token: Optional[str] = None,  # In a real app, this would come from the request
) -> Generator[str, None, None]:
    """
    Yield dependency that implements CSRF protection.
    Generates a CSRF token or validates an existing one.
    """
    user_id = auth_data["user_id"]
    session_id = f"session:{user_id}"

    if csrf_token is None:
        # Generate a new CSRF token
        token = security.generate_csrf_token(session_id)
        print(f"Generated new CSRF token for {session_id}")
    else:
        # Validate the provided CSRF token
        is_valid = security.validate_csrf_token(session_id, csrf_token)
        if not is_valid:
            raise AuthenticationError("Invalid CSRF token")
        token = csrf_token
        print(f"CSRF token validated for {session_id}")

    try:
        yield token
    finally:
        print("CSRF protection context cleaned up")


# Secure endpoint examples
@app.get("/secure/products")
def secure_products(
    request,
    _: Annotated[None, Depends(rate_limit)],
    auth_data: Annotated[Dict, Depends(authorize)],
):
    """Secure endpoint that requires authentication, authorization, and respects rate limits"""
    products = [
        {"id": 1, "name": "Secure Product 1", "price": 29.99},
        {"id": 2, "name": "Secure Product 2", "price": 49.99},
    ]
    return {"products": products, "user_id": auth_data["user_id"], "scopes": auth_data["scopes"]}


@app.post("/secure/orders")
def secure_create_order(
    request,
    product_id: int,
    quantity: int,
    auth_data: Annotated[Dict, Depends(authorize)] = None,
    _rate_limit: Annotated[None, Depends(rate_limit)] = None,
    csrf_token: Annotated[str, Depends(csrf_protection)] = None,
):
    """
    Secure endpoint for creating orders.
    Requires authentication, authorization, rate limiting, CSRF protection, and uses transactions.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    # In a real implementation, we would create the order in the database
    return {
        "message": f"Secure order created for product {product_id}, quantity {quantity}",
        "user_id": auth_data["user_id"],
        "csrf_token": csrf_token,
    }


def other_dependency() -> str:
    return "other dependency"


def dependency(other_dependency: Annotated[str, Depends(other_dependency)]) -> str:
    return other_dependency


# Yield dependency examples


def db_connection() -> Generator[Dict, None, None]:
    """
    Yield dependency that creates a database connection,
    yields it, and then closes it after the request is complete.
    """
    print("Opening database connection")
    connection = {"connection": "db_connection_object"}

    try:
        yield connection
    finally:
        # This code runs after the route function completes
        print("Closing database connection")


def request_logger() -> Generator[None, None, None]:
    """
    Yield dependency for logging request lifecycle events.
    Logs start and end of request processing.
    """
    print("Request started")

    try:
        yield
    finally:
        print("Request completed")


def transaction(connection: Annotated[Dict, Depends(db_connection)]) -> Generator[Dict, None, None]:
    """
    Nested yield dependency that manages a database transaction.
    Depends on the db_connection dependency.
    """
    print(f"Beginning transaction with connection {connection}")
    # In real implementation, would begin transaction on the connection
    transaction_obj = {"transaction": "tx_object", "connection": connection}

    try:
        yield transaction_obj
        print("Committing transaction")
        # Would commit transaction here
    except Exception as e:
        print(f"Rolling back transaction due to error: {e}")
        # Would rollback here
        raise
    finally:
        print("Transaction finished")


# More complex dependencies
def get_current_user() -> User:
    # In a real application, this would get the user from the request
    # For demo purposes, creating a mock user
    return User(id=1, name="John Doe", email="john@example.com", password="hashed_password")


def product_service(current_user: Annotated[User, Depends(get_current_user)]) -> Dict:
    # A service that depends on the current user
    return {"user_id": current_user.id, "user_name": current_user.name, "service_name": "ProductService"}


def order_service(
    product_svc: Annotated[Dict, Depends(product_service)], current_user: Annotated[User, Depends(get_current_user)]
) -> Dict:
    # Nested dependency - order service depends on product service and current user
    return {"product_service": product_svc, "user_id": current_user.id, "service_name": "OrderService"}


# Define your endpoints
@app.get("/hello")
def hello(request, a: Annotated[str, Depends(dependency)]):
    return {"message": f"Hello {a}!"}


@app.get("/add/{a}/{b}")
def add(request, a: int, b: int, c: Annotated[str, Depends(dependency)]):
    return {"result": a + b, "c": c}


@app.get("/products")
def list_products(
    request, product_svc: Annotated[Dict, Depends(product_service)], _: Annotated[None, Depends(request_logger)]
):
    # In a real application, we would query the database
    products = [
        {"id": 1, "name": "Product 1", "price": 29.99},
        {"id": 2, "name": "Product 2", "price": 49.99},
    ]
    return {"products": products, "service_info": product_svc}


@app.get("/orders")
def list_orders(
    request, order_svc: Annotated[Dict, Depends(order_service)], conn: Annotated[Dict, Depends(db_connection)]
):
    # In a real application, we would query the database using the connection
    print(f"Using connection {conn} to fetch orders")
    orders = [
        {"id": 1, "user_id": order_svc["user_id"], "status": "pending", "amount": 79.98},
    ]
    return {"orders": orders, "service_info": order_svc}


@app.post("/orders")
def create_order(
    request,
    product_id: int,
    quantity: int,
    order_svc: Annotated[Dict, Depends(order_service)],
    tx: Annotated[Dict, Depends(transaction)],
):
    # This example uses the transaction yield dependency
    print(f"Creating order with transaction {tx}")

    # In a real implementation, we would use the transaction to create the order
    return {
        "message": f"Order created for product {product_id}, quantity {quantity}",
        "user_id": order_svc["user_id"],
        "service_info": order_svc,
        "transaction_id": id(tx),
    }


@app.post("/advanced-order")
def advanced_order(
    request,
    product_id: int,
    quantity: int,
    user_id: int,
    tx: Annotated[Dict, Depends(transaction)],
    _: Annotated[None, Depends(request_logger)],
    order_svc: Annotated[Dict, Depends(order_service)],
):
    """
    Advanced endpoint demonstrating multiple yield dependencies.
    Shows how yield dependencies handle both setup and teardown automatically.

    The dependencies will execute in this order:
    1. request_logger setup runs (prints "Request started")
    2. db_connection setup runs (from transaction dependency)
    3. transaction setup runs (begins transaction)
    4. This function body executes
    5. transaction teardown runs (commits or rolls back)
    6. db_connection teardown runs (closes connection)
    7. request_logger teardown runs (prints "Request completed")
    """
    # Simulate some operation that might fail
    if quantity <= 0:
        # This will trigger transaction rollback in the exception handler
        raise ValueError("Quantity must be positive")

    # Simulate creating an order
    print(f"Creating advanced order with transaction {tx}")

    # Return a response with all dependency info
    return {
        "message": f"Advanced order created for product {product_id}, quantity {quantity}, user {user_id}",
        "transaction_info": tx,
        "service_info": order_svc,
    }


# Register all models with CRUD operations
app.crud(cast(BaseModel, User))
app.crud(cast(BaseModel, Product))
app.crud(cast(BaseModel, Order))
app.crud(cast(BaseModel, OrderItem))

# More yield dependency examples


T = TypeVar("T")


class CacheManager:
    """Simulates a cache manager for demonstration purposes"""

    _instance = None

    @classmethod
    def get_instance(cls) -> "CacheManager":
        if cls._instance is None:
            cls._instance = CacheManager()
        return cls._instance

    def __init__(self) -> None:
        self.cache: Dict[str, Any] = {}
        print("Cache manager initialized")

    def get(self, key: str) -> Any:
        """Get a value from the cache, return None if not found"""
        if key in self.cache:
            print(f"Cache hit for {key}")
            return self.cache[key]
        print(f"Cache miss for {key}")
        return None

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Set a value in the cache with an optional TTL"""
        print(f"Setting cache for {key} with TTL {ttl}s")
        self.cache[key] = value
        # In a real implementation, we would handle TTL expiration

    def invalidate(self, key: str) -> None:
        """Remove a value from the cache"""
        if key in self.cache:
            print(f"Invalidating cache for {key}")
            del self.cache[key]

    def close(self) -> None:
        """Close the cache manager and clean up resources"""
        print("Closing cache manager")
        # In real implementation, might flush pending writes, etc.


def cache_dependency() -> Generator[CacheManager, None, None]:
    """
    Yield dependency that provides a cache manager.
    The cache manager is a singleton, so it's reused across requests.
    """
    # Get or create the cache manager singleton
    cache_manager = CacheManager.get_instance()
    try:
        yield cache_manager
    finally:
        # We don't close the cache manager here since it's a singleton
        # and should live for the lifetime of the application
        pass


def cached_products(cache: Annotated[CacheManager, Depends(cache_dependency)]) -> Generator[List[Dict], None, None]:
    """
    A yield dependency that caches product data.
    Shows how to combine yield dependencies with caching patterns.
    """
    cache_key = "products_list"
    cached_data = cache.get(cache_key)

    # Initialize products with proper typing
    products: List[Dict] = []

    if cached_data is not None:
        # Type checking - ensure cached_data is a list of dictionaries
        if isinstance(cached_data, list):
            products = cached_data

    if not products:
        # Simulate fetching from database
        print("Fetching products from database...")
        time.sleep(0.1)  # Simulate database query
        products = [
            {"id": 1, "name": "Cached Product 1", "price": 29.99},
            {"id": 2, "name": "Cached Product 2", "price": 49.99},
            {"id": 3, "name": "Cached Product 3", "price": 39.99},
        ]
        # Cache the result
        cache.set(cache_key, products)

    try:
        yield products
    finally:
        # No cleanup needed here, but we could invalidate the cache in some cases
        # For example, if we detect that the data has changed
        pass


# New endpoints that use the cache dependencies


@app.get("/cached-products")
def get_cached_products(
    request, products: Annotated[List[Dict], Depends(cached_products)], _: Annotated[None, Depends(request_logger)]
):
    """Endpoint that uses cached products"""
    return {"products": products, "source": "possibly-cached"}


@app.post("/invalidate-cache")
def invalidate_product_cache(request, cache: Annotated[CacheManager, Depends(cache_dependency)]):
    """Endpoint to invalidate the product cache"""
    cache.invalidate("products_list")
    return {"message": "Product cache invalidated"}


# Simple API key authentication


class AuthError(Exception):
    """Raised when authentication fails"""

    pass


# Simple in-memory API key store
API_KEYS = {
    "api-key-1": {"user_id": 1, "role": "admin"},
    "api-key-2": {"user_id": 2, "role": "user"},
    "api-key-3": {"user_id": 3, "role": "readonly"},
}


def get_api_key(request) -> Optional[str]:
    """Extract API key from request headers"""
    # In a real application, extract from Authorization or X-API-Key header
    # For demo purposes, we'll simulate this

    # Simulated header extraction
    headers = getattr(request, "headers", {})

    # Try to get from X-API-Key header first, then Authorization
    api_key = headers.get("X-API-Key")
    if not api_key and "Authorization" in headers:
        auth_header = headers.get("Authorization", "")
        # Handle "Bearer <token>" format
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:].strip()
        else:
            api_key = auth_header.strip()

    return api_key


def validate_api_key(api_key: Optional[str]) -> Dict:
    """Validate the API key and return user info"""
    if not api_key or api_key not in API_KEYS:
        raise AuthError("Invalid or missing API key")

    return API_KEYS[api_key]


def api_key_auth(request) -> Generator[Dict, None, None]:
    """
    Simple yield dependency for API key authentication.
    Extracts the API key from request headers and validates it.
    """
    # Extract API key from request
    api_key = get_api_key(request)

    print(f"Authenticating with API key: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else None}")

    try:
        # Validate API key
        user_info = validate_api_key(api_key)
        print(f"API key valid for user {user_info['user_id']}")

        # Yield user info to the route handler
        yield user_info
    except AuthError as e:
        print(f"API key authentication failed: {e}")
        raise
    finally:
        # Any cleanup operations would go here
        print("API authentication context cleaned up")


def require_role(required_role: str):
    """
    Factory function that creates a dependency requiring a specific role.
    Uses the api_key_auth dependency.
    """

    def role_checker(user_info: Annotated[Dict, Depends(api_key_auth)]) -> Generator[Dict, None, None]:
        user_role = user_info.get("role")
        print(f"Checking if user role '{user_role}' matches required role '{required_role}'")

        # Simple role checking
        if required_role == "admin" and user_role != "admin":
            raise AuthError("Admin role required")
        elif required_role == "user" and user_role not in ["admin", "user"]:
            raise AuthError("User or admin role required")

        print(f"Role check passed for '{required_role}'")
        yield user_info

    return role_checker


# Example protected routes


@app.get("/api/simple/me")
def get_user_profile(user_info: Annotated[Dict, Depends(api_key_auth)]):
    """Get information about the current authenticated user"""
    return {"user_id": user_info["user_id"], "role": user_info["role"], "authenticated": True}


@app.get("/api/simple/admin")
def admin_only(user_info: Annotated[Dict, Depends(require_role("admin"))]):
    """Admin-only endpoint"""
    return {"message": "You have access to admin resources", "user_id": user_info["user_id"]}


@app.get("/api/simple/data")
def get_data(user_info: Annotated[Dict, Depends(require_role("user"))]):
    """Requires at least user role"""
    return {
        "message": "Here is your data",
        "user_id": user_info["user_id"],
        "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
    }


# Demonstrate how to use it in an existing route with other dependencies
@app.post("/api/simple/items")
def create_item(
    request,
    name: str,
    user_info: Annotated[Dict, Depends(require_role("user"))],
):
    """Create a new item (requires user role)"""
    return {"message": f"Item '{name}' created", "created_by": user_info["user_id"]}


# Request-aware dependency
def get_query_params(request):
    """Dependency that accesses the request object"""
    return request.GET


# You can use it in another dependency
def get_user_id(params=Depends(get_query_params)):
    return params


# Or directly in your endpoint
@app.get("/some-endpoint")
def endpoint(request, user_id: Annotated[str, Depends(get_user_id)]):
    return {"user_id": user_id}

