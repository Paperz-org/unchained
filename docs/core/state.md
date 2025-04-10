# State Management

!!! info "Application State"
    Unchained provides a powerful state management system that allows you to maintain application-wide variables and configurations, with full IDE completion support.

!!! tip "State and Lifespan"
    State management is closely tied to [lifespan management](lifespan.md). The lifespan provides the ideal place to initialize state values at application startup and clean up resources at shutdown.

!!! note "Custom State Classes"
    Custom BaseState classes are currently used primarily for typing purposes. They define the structure and type information for your application state, but the actual initialization happens in lifespan functions, not within the state class itself.

## Basic Usage

=== "Define State"
    ```python
    from unchained.states import BaseState
    from typing import Optional
    from redis import Redis
    from httpx import AsyncClient

    # State class is a type placeholder that defines structure
    class AppState(BaseState):
        # Cache
        redis: Redis
        # API Clients
        http_client: Optional[AsyncClient] = None
        weather_client: Optional[AsyncClient] = None
        # Feature Flags
        enable_new_ui: bool = False
        enable_experimental_features: bool = False
        # Configuration
        api_key: str
        debug: bool = False
    ```

=== "Initialize with State"
    ```python
    from unchained import Unchained
    from redis import Redis
    from httpx import AsyncClient

    # Create app with state placeholder
    app = Unchained(state=AppState())

    # Actual initialization happens in lifespan
    @app.lifespan
    async def startup(app: Unchained):
        # Initialize Redis
        app.state.redis = Redis.from_url("redis://localhost:6379")
        
        # Initialize API clients
        app.state.http_client = AsyncClient()
        app.state.weather_client = AsyncClient(
            base_url="https://api.openweathermap.org/data/2.5",
            params={"appid": app.state.api_key}
        )
        
        yield
        
        # Cleanup
        await app.state.redis.close()
        await app.state.http_client.aclose()
        await app.state.weather_client.aclose()
    ```

## State Access

=== "Direct Access"
    ```python
    # Access state properties directly from app
    debug_mode = app.state.debug
    
    # Conditionally use features
    if app.state.enable_experimental_features:
        # Do something with experimental features
        pass
    ```

=== "State with Dependency Injection"
    ```python
    from unchained import Depends
    
    # State can be accessed through dependency injection
    def get_http_client(app = Depends()):
        return app.state.http_client
        
    # Note: For detailed examples of using state with dependency injection,
    # see the Dependency Injection documentation
    ```

## State Setup Example

```python
from typing import Optional
from unchained.states import BaseState
from redis import Redis
from httpx import AsyncClient
import os

# Define state structure with typing
class AppState(BaseState):
    # Cache
    redis: Redis
    # API Clients
    http_client: Optional[AsyncClient] = None
    weather_client: Optional[AsyncClient] = None
    open_ai_client: Optional[AsyncClient] = None
    # Feature Flags
    enable_new_ui: bool = False
    enable_experimental_features: bool = False
    # Configuration
    api_key: str
    debug: bool = False
    # Environment
    environment: str = "development"

app = Unchained(state=AppState())

# Actual state initialization in lifespan
@app.lifespan
async def startup(app: Unchained):
    # Load configuration from environment
    app.state.api_key = os.getenv("WEATHER_API_KEY")
    app.state.environment = os.getenv("ENVIRONMENT", "development")
    app.state.debug = app.state.environment == "development"
    
    # Initialize services
    app.state.redis = Redis.from_url(os.getenv("REDIS_URL"))
    
    # Initialize API clients
    app.state.http_client = AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_connections=100)
    )
    app.state.weather_client = AsyncClient(
        base_url="https://api.openweathermap.org/data/2.5",
        params={"appid": app.state.api_key}
    )
    app.state.open_ai_client = AsyncClient(
        base_url="https://api.openai.com/v1",
        headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    )
    
    # Set feature flags based on environment
    app.state.enable_new_ui = app.state.environment == "production"
    app.state.enable_experimental_features = app.state.debug
    
    yield
    
    # Cleanup
    await app.state.redis.close()
    await app.state.http_client.aclose()
    await app.state.weather_client.aclose()
    await app.state.open_ai_client.aclose()
```

## Best Practices

1. **Type Safety**: Define state classes with proper type hints
2. **IDE Completion**: Use state classes for better IDE support
3. **Lifespan Initialization**: Initialize state in lifespan functions, not state classes
4. **Environment Awareness**: Use state for environment-specific configuration

## Common Patterns

### Service Clients

```python
from unchained.states import BaseState
from typing import Optional
from httpx import AsyncClient

# Type definition for service clients
class ServiceClients(BaseState):
    http: Optional[AsyncClient] = None
    weather: Optional[AsyncClient] = None
    github: Optional[AsyncClient] = None
```

### Feature Flags

```python
from unchained.states import BaseState

# Type definition for feature flags
class FeatureFlags(BaseState):
    enable_new_ui: bool = False
    enable_experimental_features: bool = False
    max_connections: int = 100
    cache_timeout: int = 300
```

### Configuration

```python
from unchained.states import BaseState

# Type definition for app configuration
class AppConfig(BaseState):
    api_key: str
    environment: str = "development"
    debug: bool = False
    redis_url: str
    cache_ttl: int = 300
``` 