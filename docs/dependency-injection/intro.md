---
title: Dependency Injection Introduction
---

# Dependency Injection

Unchained provides a powerful and flexible Dependency Injection (DI) system inspired by FastAPI. It allows you to structure your code with reusable components, manage resources effectively, and automatically inject parameters like request data into your route handlers and dependencies.

This page covers the core concepts. For specific injection methods, see the dedicated pages.

## Core Concepts

### 1. `Depends` Marker

The core of the DI system is the `Depends` marker used in conjunction with `typing.Annotated`. You annotate your function parameters with the type of the dependency and mark it with `Depends(your_dependency_callable)`.

```python
from typing import Annotated
from unchained import Depends, Unchained

# Define a simple dependency (a callable)
def get_common_data() -> dict:
    return {"message": "Hello from dependency!"}

# Inject the dependency into a route handler
def read_items(common: Annotated[dict, Depends(get_common_data)]):
    # 'common' now holds the dictionary returned by get_common_data
    return {"data": common}

app = Unchained()
app.get("/items/")(read_items)
```

When a request comes to `/items/`, Unchained will:
1. See the `common` parameter annotated with `Depends(get_common_data)`.
2. Call the `get_common_data` function.
3. Pass the returned value (`{"message": "Hello from dependency!"}`) as the `common` argument to `read_items`.

### 2. Sync and Async Support

The DI system seamlessly handles both synchronous (`def`) and asynchronous (`async def`) functions for both route handlers and dependencies.

-   **Async Routes**: Can depend on both `sync` and `async` dependencies. Unchained runs `sync` dependencies in a thread pool to avoid blocking the event loop.
-   **Sync Routes**: Can **only** depend on `sync` dependencies. Trying to use an `async` dependency in a `sync` route will result in an error.

```python
# Async dependency
async def get_async_value() -> str:
    # Imagine an async operation here
    return "async_value"

# Sync dependency
def get_sync_value() -> str:
    return "sync_value"

# Async route using both
async def async_route(
    a_val: Annotated[str, Depends(get_async_value)],
    s_val: Annotated[str, Depends(get_sync_value)],
):
    return {"async": a_val, "sync": s_val}

# Sync route using only sync
def sync_route(s_val: Annotated[str, Depends(get_sync_value)]):
    return {"sync": s_val}

app = Unchained()
app.get("/async")(async_route)
app.get("/sync")(sync_route)
```

### 3. Caching

By default, Unchained caches the return value of a dependency **within the scope of a single request**. This means if the same dependency callable is requested multiple times (e.g., by different parameters in the same route, or by nested dependencies), the callable is only executed *once* per request, and the cached value is reused.

```python
counter = 0
def get_request_service():
    global counter
    counter += 1
    print(f"Executing get_request_service: Count = {counter}")
    return {"instance_id": counter}

def route_with_cache(
    service1: Annotated[dict, Depends(get_request_service)],
    service2: Annotated[dict, Depends(get_request_service)],
):
    # service1 and service2 will be the *same* dictionary instance
    # 'Executing get_request_service' will print only once per request
    assert service1 is service2
    return {"s1": service1, "s2": service2, "final_count": counter}

app = Unchained()
app.get("/cached")(route_with_cache)
```

You can disable caching for a specific injection using `use_cache=False`:

```python
# route_without_cache assumes get_request_service is defined as above
def route_without_cache(
    service1: Annotated[dict, Depends(get_request_service)], # Cached (first call)
    service2: Annotated[dict, Depends(get_request_service, use_cache=False)], # Not cached
):
    # service1 and service2 will be *different* dictionary instances
    assert service1 is not service2
    return {"s1": service1, "s2": service2, "final_count": counter}

app.get("/not-cached")(route_without_cache)
```

### 4. Nested Dependencies

Dependencies can depend on other dependencies. Unchained automatically resolves the entire dependency tree, respecting the caching rules at each level.

```python
from typing import Annotated
from unchained import Depends, Unchained

class DBConnection: ...
class UserRepo:
    def __init__(self, conn: DBConnection):
        self.conn = conn
    def get_user(self, user_id: int): ...

def get_db_connection() -> DBConnection:
    print("Getting DB Connection")
    return DBConnection()

# UserRepo depends on DBConnection
def get_user_repo(conn: Annotated[DBConnection, Depends(get_db_connection)]) -> UserRepo:
    print("Getting User Repo")
    return UserRepo(conn=conn)

# Route depends on UserRepo
def get_user_profile(user_id: int, repo: Annotated[UserRepo, Depends(get_user_repo)]):
    print("Getting User Profile")
    # Unchained automatically calls get_db_connection, passes the result to
    # get_user_repo, and passes that result here as 'repo'.
    # Due to caching, get_db_connection runs only once.
    user = repo.get_user(user_id)
    return {"user_data": user} # Example response

app = Unchained()
app.get("/users/{user_id}")(get_user_profile)
```

This structure allows you to build modular and testable components by managing dependencies explicitly.

## Types of Dependencies

Unchained offers several ways to inject data or services:

-   **Built-in Objects**: Automatically inject framework objects.
    -   [Request Object](./request-object.md)
    -   [App Object](./app-object.md)
-   **Parameter Sources**: Extract data directly from the request.
    -   [Path Parameters](./path-parameters.md)
    -   [Query Parameters](./query-parameters.md)
    -   [Header Parameters](./header-parameters.md)
    -   [Body Parameters](./body-parameters.md)
-   **Generator Dependencies**: Manage resources with setup and teardown phases.
    -   [Generator Dependencies (`yield`)](./generator-dependencies.md)

## Further Reading

For more depth on the underlying concepts:

- :material-github: [FastDepends Documentation](https://lancetnik.github.io/FastDepends/) (The library powering Unchained's DI)
- :fontawesome-brands-python: [Python Annotated Type](https://docs.python.org/3/library/typing.html#typing.Annotated)
