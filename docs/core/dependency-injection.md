# Dependency Injection

!!! info "Power of Dependency Injection"
    Unchained provides a robust dependency injection system built on FastDepends, enabling clean, testable, and modular code with full type safety.

## What is Dependency Injection?

Dependency injection is a design pattern that allows you to:

- Separate the creation of dependencies from their usage
- Improve testability by making dependencies replaceable
- Create reusable components that can be shared across your application
- Keep your code modular and maintainable

In Unchained, dependency injection is implemented using Python's `Annotated` type and the `Depends` function.

## Basic Usage

!!! warning "Important: Using `Annotated`"
    Unchained's dependency injection system **requires** the use of Python's `Annotated` type. Direct parameter typing without `Annotated` will not work for dependencies.

=== "Simple Dependency"
    ```python
    from typing import Annotated
    from unchained import Depends, Unchained

    app = Unchained()

    def get_current_user():
        return {"username": "johndoe"}

    @app.get("/me")
    def read_current_user(user: Annotated[dict, Depends(get_current_user)]):
        return user
    ```

=== "Parameterized Dependency"
    ```python
    from typing import Annotated
    from unchained import Depends, Unchained

    app = Unchained()

    def get_item_by_id(item_id: int):
        return {"item_id": item_id, "name": f"Item {item_id}"}

    @app.get("/items/{item_id}")
    def read_item(item: Annotated[dict, Depends(get_item_by_id)]):
        return item
    ```

## Automatic Dependencies

Unchained provides several built-in dependencies that are automatically injected when you type-annotate your parameters:

=== "Request Object"
    ```python
    from unchained import Request, Unchained

    app = Unchained()

    @app.get("/request-info")
    def get_request_info(request: Request):
        return {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers)
        }
    ```

=== "Application Object"
    ```python
    from unchained import Unchained
    from unchained.base import BaseUnchained

    app = Unchained()

    @app.get("/app-info")
    def get_app_info(app: BaseUnchained):
        return {
            "debug": app.debug,
            "version": app.version
        }
    ```

=== "State Object"
    ```python
    from unchained import Unchained
    from unchained.states import BaseState
    # Or your custom state
    from myapp.state import AppState

    app = Unchained()

    @app.get("/state-info")
    def get_state_info(state: BaseState):  # Or state: AppState
        return {
            "debug": state.debug,
            "environment": state.environment
        }
    ```

=== "Settings Object"
    ```python
    from unchained import Unchained
    from unchained.settings.base import UnchainedSettings
    # Or your custom settings
    from myapp.settings import AppSettings

    app = Unchained()

    @app.get("/settings-info")
    def get_settings_info(settings: UnchainedSettings):  # Or settings: AppSettings
        return {
            "debug": settings.debug,
            "database_url": settings.database_url
        }
    ```

For more information about state management, see the [state management documentation](state.md).

## Type Aliases for Dependencies

You can create clear and reusable type aliases for your dependencies, which improves code organization and readability:

```python
from typing import Annotated
from unchained import Depends, Unchained
from httpx import AsyncClient

app = Unchained()

def get_api_client() -> AsyncClient:
    return AsyncClient(base_url="https://api.example.com")

# Create a type alias for the dependency
ApiClient = Annotated[AsyncClient, Depends(get_api_client)]

@app.get("/external-data")
def get_external_data(client: ApiClient):
    # Use the client with full IDE completion
    response = client.get("/data")
    return response.json()
```

This pattern is particularly useful for:

- Improving code readability
- Enabling better IDE support
- Reusing dependencies across multiple endpoints
- Making the dependency relationship clear

## Nested Dependencies

Dependencies can depend on other dependencies, creating a dependency graph:

```python
from typing import Annotated
from unchained import Depends, Unchained

app = Unchained()

def get_api_key():
    return "api-key-1234"

def get_headers(api_key: Annotated[str, Depends(get_api_key)]):
    return {"Authorization": f"Bearer {api_key}"}

def get_client(headers: Annotated[dict, Depends(get_headers)]):
    # In a real app, you might return httpx.AsyncClient or similar
    return {"headers": headers, "client": "api_client"}

@app.get("/api-data")
def get_data(client: Annotated[dict, Depends(get_client)]):
    # Access the fully resolved dependency chain
    return {"data": "some data", "client": client}
```

When a request is made to `/api-data`:

1. `get_api_key()` is called first
2. Its return value is passed to `get_headers()`
3. The result from `get_headers()` is passed to `get_client()`
4. Finally, the `get_client()` result is injected as the `client` parameter

## Advanced Examples with Custom State and Settings

Here are simpler examples showing how to leverage custom state and settings:

### Custom State Example

```python
from typing import Annotated, Optional
from unchained import Depends, Unchained
from unchained.states import BaseState
from httpx import AsyncClient

# Define custom state
class AppState(BaseState):
    weather_api_key: str = "default-key"
    logger_enabled: bool = True

# Get configuration from state
def get_api_config(state: AppState):
    return {
        "api_key": state.weather_api_key,
        "logging": state.logger_enabled
    }

# Use the configuration
def get_weather_info(config: Annotated[dict, Depends(get_api_config)]):
    # Simple function returning weather info based on config
    return {
        "source": "Weather API",
        "using_key": config["api_key"],
        "logging_enabled": config["logging"]
    }

# Create app with state
app = Unchained(state=AppState())

# Use in endpoint
@app.get("/weather-config")
def weather_config(info: Annotated[dict, Depends(get_weather_info)]):
    return info
```

### Custom Settings Example

```python
from typing import Annotated
from unchained import Depends, Unchained
from unchained.settings.base import UnchainedSettings
from pydantic import Field

# Define custom settings
class AppSettings(UnchainedSettings):
    # API Settings
    api_timeout: int = Field(default=30, ge=1, le=120)
    enable_cache: bool = Field(default=True)

# Simple feature flag checker
def is_feature_enabled(feature_name: str, settings: AppSettings):
    if feature_name == "cache":
        return settings.enable_cache
    return False

# Get timeout configuration
def get_timeout_config(settings: AppSettings):
    return {
        "timeout": settings.api_timeout,
        "cache_enabled": settings.enable_cache
    }

# Create app
app = Unchained()

# Use settings in endpoint
@app.get("/api-config")
def api_config(
    config: Annotated[dict, Depends(get_timeout_config)],
    cache_enabled: Annotated[bool, Depends(lambda s: is_feature_enabled("cache", s))]
):
    return {
        "config": config,
        "cache_status": "enabled" if cache_enabled else "disabled"
    }
```

### Combining Custom State and Settings

```python
from typing import Annotated
from unchained import Depends, Unchained
from unchained.states import BaseState
from unchained.settings.base import UnchainedSettings
from pydantic import Field

# Custom settings
class ApiSettings(UnchainedSettings):
    base_url: str = Field(default="https://api.example.com")
    timeout: int = Field(default=30)

# Custom state
class AppState(BaseState):
    api_key: str = "default-key"
    debug_mode: bool = False

# Initialize app
app = Unchained(state=AppState())

# Function that uses both state and settings
def get_api_configuration(state: AppState, settings: ApiSettings):
    return {
        "base_url": settings.base_url,
        "timeout": settings.timeout,
        "api_key": state.api_key,
        "debug": state.debug_mode
    }

# Use the configuration
@app.get("/api-status")
def api_status(config: Annotated[dict, Depends(get_api_configuration)]):
    return {
        "status": "configured",
        "config": config
    }
```

## Best Practices

1. **Use `Annotated` for All Dependencies**: Always use `Annotated` with `Depends` for proper type inference.

2. **Keep Dependencies Focused**: Each dependency should have a single responsibility.

3. **Prefer Function Dependencies**: Function-based dependencies are easier to test and mock.

4. **Cache When Appropriate**: Use `use_cache=True` (the default) to avoid recalculating the same dependency.

5. **Handle Errors Properly**: Dependencies should raise appropriate exceptions for error scenarios.

## Implementation Details

Under the hood, Unchained uses FastDepends to handle dependency resolution. The process works as follows:

1. When a route is registered, Unchained analyzes its signature
2. For each parameter with `Annotated[Type, Depends(...)]`, it registers the dependency
3. Automatic dependencies like `Request`, `BaseUnchained`, `BaseState`, and `UnchainedSettings` are detected by type
4. When a request arrives, dependencies are resolved in the correct order
5. The resolved values are passed to the route handler