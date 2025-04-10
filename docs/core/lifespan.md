# Lifespan Management

!!! info "Application Lifecycle"
    Unchained provides a powerful lifespan management system that allows you to handle application startup and shutdown events.

## What is Lifespan?

Lifespan is a concept from the ASGI (Asynchronous Server Gateway Interface) specification that manages the lifecycle of an application. The lifespan protocol provides hooks for:

- **Startup**: Actions to perform when the server starts, before handling any requests
- **Shutdown**: Cleanup actions to perform when the server is shutting down

Unchained builds upon this ASGI concept to provide a clean, intuitive API for managing application lifecycle events.

!!! warning "Lifespan Functions Must Yield"
    All lifespan functions **must** use the `yield` statement to separate startup from shutdown logic. Failing to yield will result in an error.

## Ways to Define Lifespan

There are two ways to define lifespan handlers in Unchained:

### 1. Using the Decorator

```python
from unchained import Unchained

app = Unchained()

@app.lifespan
def startup(app: Unchained):
    # Startup code (executed before the server starts handling requests)
    print("Server is starting up")
    app.state.initialized = True
    
    yield  # This yield separates startup from shutdown code
    
    # Shutdown code (executed when the server is shutting down)
    print("Server is shutting down")
    app.state.initialized = False
```

### 2. During Initialization

```python
from unchained import Unchained

async def my_lifespan(app: Unchained):
    # Startup code
    print("Starting up")
    yield
    # Shutdown code
    print("Shutting down")

# Pass the lifespan function during app initialization
app = Unchained(lifespan=my_lifespan)
```

## Sync vs Async Lifespan

Unchained supports both synchronous and asynchronous lifespan handlers:

=== "Sync Lifespan"
    ```python
    @app.lifespan
    def startup(app: Unchained):
        # Synchronous startup code
        app.state.initialized = True
        yield
        # Synchronous shutdown code
        app.state.initialized = False
    ```

=== "Async Lifespan"
    ```python
    @app.lifespan
    async def startup(app: Unchained):
        # Asynchronous startup code
        await app.state.http_client.aopen()
        yield
        # Asynchronous shutdown code
        await app.state.http_client.aclose()
    ```

## How Lifespan Works in ASGI

When an ASGI server (like Uvicorn or Daphne) starts, it sends a lifespan event to the application:

1. Server sends `{"type": "lifespan.startup"}` to the application
2. Application executes all startup code (before the `yield`)
3. Application responds with `{"type": "lifespan.startup.complete"}`
4. Server starts handling HTTP requests
5. When shutting down, server sends `{"type": "lifespan.shutdown"}`
6. Application executes all shutdown code (after the `yield`)
7. Application responds with `{"type": "lifespan.shutdown.complete"}`

Unchained handles all of this communication for you, providing a clean API that focuses on your application logic rather than the ASGI protocol details.

## Multiple Lifespan Handlers

You can define multiple lifespan handlers, and they will be executed in the order they are defined:

```python
@app.lifespan
async def http_client_lifespan(app: Unchained):
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()

@app.lifespan
async def cache_lifespan(app: Unchained):
    await app.state.cache.connect()
    yield
    await app.state.cache.disconnect()
```

On startup, the handlers execute in order (http_client_lifespan then cache_lifespan). 
On shutdown, they execute in **reverse** order (cache_lifespan cleanup then http_client_lifespan cleanup).

## Common Use Cases

### Resource Initialization and Cleanup

The most common use case for lifespan is initializing resources at startup and cleaning them up at shutdown:

```python
@app.lifespan
async def initialize_resources(app: Unchained):
    # Initialize resources
    app.state.http_client = AsyncClient()
    app.state.redis = Redis.from_url(os.getenv("REDIS_URL"))
    
    # Return control to the server
    yield
    
    # Clean up resources
    await app.state.http_client.aclose()
    await app.state.redis.close()
```

## Error Handling

When working with lifespan functions, it's important to handle potential errors properly:

=== "Startup Error Handling"
    ```python
    @app.lifespan
    async def startup(app: Unchained):
        # Initialize client
        app.state.http_client = httpx.AsyncClient()
        
        # Yield control back to the server
        yield
        
        # Always clean up resources
        await app.state.http_client.aclose()
    ```

=== "Shutdown Error Handling"
    ```python
    @app.lifespan
    async def shutdown(app: Unchained):
        # Initialize client
        app.state.http_client = httpx.AsyncClient()
        
        # Yield control back to the server
        yield
        
        # Clean up (errors here will be logged but won't crash the application)
        await app.state.http_client.aclose()
    ```

## Best Practices

1. **Always Yield**: Every lifespan function must yield exactly once
2. **Resource Management**: Always clean up resources during shutdown
3. **Error Handling**: Use try/except/finally for robust error handling
4. **State Initialization**: Use lifespan for initializing application state
5. **Ordering**: Be conscious of the order of lifespan handlers

## Example: Complete Application Setup

```python
from unchained import Unchained
from unchained.states import BaseState
import httpx
import redis
import os

class AppState(BaseState):
    debug: bool = False
    api_key: str
    environment: str = "development"

app = Unchained(state=AppState())

@app.lifespan
def load_config(app: Unchained):
    # Load configuration
    app.state.debug = os.getenv("DEBUG", "false").lower() == "true"
    app.state.api_key = os.getenv("API_KEY")
    app.state.environment = os.getenv("ENVIRONMENT", "development")
    yield
    # No cleanup needed

@app.lifespan
async def initialize_clients(app: Unchained):
    # Initialize clients
    app.state.http_client = httpx.AsyncClient(
        headers={"Authorization": f"Bearer {app.state.api_key}"}
    )
    app.state.redis = redis.Redis.from_url(os.getenv("REDIS_URL"))
    
    yield
    
    # Clean up
    await app.state.http_client.aclose()
    await app.state.redis.close()
``` 