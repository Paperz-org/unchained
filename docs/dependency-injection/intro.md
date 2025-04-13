# Dependency Injection

!!! abstract "Overview"
    Unchained leverages Python's `typing.Annotated` and a powerful dependency injection system based on `FastDepends` to manage dependencies in your API endpoints. This allows for clean, reusable, and testable code.
    ```python
    from typing import Annotated
    from unchained import Depends, Unchained, Request
    
    app = Unchained()
    
    @app.get("/hello")
    def hello(
        request: Request,
        message: Annotated[str, Depends(get_common_message)]
    ):
        return {"message": f"Hello {message}!"}
    ```

## Basic Usage

At its core, dependency injection in Unchained uses `Annotated` to pair a type hint with a `Depends` marker, indicating that the parameter's value should be provided by a _dependency function_ (also called a _dependable_ or _dependency_).

```python
from typing import Annotated
from unchained import Depends, Unchained, Request

app = Unchained()

# This is a dependency function
def get_message() -> str:
    return "world"

@app.get("/hello")
def hello(
    request: Request,
    message: Annotated[str, Depends(get_message)]
):
    return {"message": f"Hello {message}!"}
```

!!! tip "How it works"
    When a request hits `/hello`, Unchained automatically:

    1. Injects the `Request` object.
    2. Calls the `get_common_message()` function.
    3. Injects the return value (`"world"`) as the `message` argument.
    4. Calls your route handler `hello` with all the resolved arguments.


!!! danger "Bad patterns"
    Dependency injection system must be seen as syntactic sugar for avoiding complexity in your code base.
    
    If you are doing something that you think is not possible unless you use the dependency injection system, it might be a sign that you are doing something wrong.

    Dependency injection is just a way to make your code more readable and maintainable and reusable.

    
## Nested Dependencies

Dependencies can depend on other dependencies, forming a graph that Unchained resolves automatically.

```python
from typing import Annotated
from unchained import Depends, Unchained, Request

app = Unchained()

def first_dependency() -> str:
    return "world"

# second_dependency depends on first_dependency
def second_dependency(value: Annotated[str, Depends(first_dependency)]) -> str:
    return f"wonderful {value}"

@app.get("/hello")
def hello(
    request: Request,
    message: Annotated[str, Depends(second_dependency)] # Resolved recursively
):
    return {"message": f"Hello {message}!"}
```

You can also use [built-in dependencies](./built-in/intro.md) within your custom dependencies and nested dependencies. See the specific documentation for each type for examples.

## Custom Dependencies

TODO

### Function-based Dependency

Functions are straightforward for simpler dependency logic. Here's an example that validates an API key from a header:

```python
from typing import Annotated
from unchained import Depends, Unchained, Request
from unchained.dependencies import Header
from unchained.errors import AuthorizationError

app = Unchained()

# A simple function dependency
def verify_api_key(api_key: Annotated[str | None, Header("X-API-Key")] = None) -> str:
    if not api_key:
        raise AuthorizationError(message="X-API-Key header is missing")
    if api_key != "SECRET_KEY":
        raise AuthorizationError(message="Invalid API Key")
    return api_key

@app.get("/secure-data")
def get_secure_data(
    request: Request,
    verified_key: Annotated[str, Depends(verify_api_key)]
):
    return {"data": "sensitive information", "api_key_used": verified_key}
```

For more details on extracting headers, see the [Header Dependency](./built-in/header.md) documentation.

### Class-based Dependencies
TODO

## Built-in & Auto-Injected Dependencies

Unchained provides several built-in dependency utilities and automatically injects certain objects when type-hinted in your route handlers or other dependencies. These simplify common tasks like accessing request data, headers, parameters, and application settings.

Refer to the dedicated documentation for details:

*   [`Request`](./built-in/request.md): Access the raw request object. (Auto-injected)
*   [`Header`](./built-in/header.md): Extract request headers.
*   [`Settings`](./built-in/settings.md): Access application settings. (Auto-injected via `SettingsDependency`)

## Dependency Overriding (for Testing)
TODO

## Async and Sync Support

Unchained seamlessly supports both `async def` and `def` for route handlers and dependency functions. You can mix and match them; Unchained handles running sync dependencies in a thread pool when called from an async context if necessary.




## Further Reading

For more depth on the underlying concepts:

- :material-github: [FastDepends Documentation](https://lancetnik.github.io/FastDepends/) (The library powering Unchained's DI)
- :fontawesome-brands-python: [Python Annotated Type](https://docs.python.org/3/library/typing.html#typing.Annotated)
