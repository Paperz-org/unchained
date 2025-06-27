# Unchained Dependency Injection Features

This document outlines the core features of the Unchained dependency injection (DI) system, derived from the functional tests.

## Core Concepts

- **`Depends` Marker**: Used with `typing.Annotated` to mark parameters for dependency injection.

  ```python
  from typing import Annotated
  from unchained import Depends

  def my_dependency():
      return "dependency_value"

  def my_route(value: Annotated[str, Depends(my_dependency)]):
      return {"result": value}
  ```

- **Sync/Async Support**: Dependencies and route handlers can be synchronous (`def`) or asynchronous (`async def`). The framework handles the execution context.
  - Async routes can depend on sync or async dependencies.
  - Sync routes can only depend on sync dependencies.
- **Caching**: By default, the result of a dependency function is cached within a single request cycle. The same dependency function will not be executed multiple times if requested by different parts of the application (e.g., multiple route parameters, nested dependencies). Caching can be disabled per-injection.

  ```python
  # Runs once per request
  dep1: Annotated[MyService, Depends(get_my_service)]

  # Runs every time it's injected, even within the same request
  dep2: Annotated[MyService, Depends(get_my_service, use_cache=False)]
  ```

- **Nested Dependencies**: Dependencies can depend on other dependencies, forming a tree. The framework resolves the entire dependency graph.

  ```python
  def get_db_conn(): ...
  def get_user_repo(conn: Annotated[DBConn, Depends(get_db_conn)]): ...
  def get_user(repo: Annotated[UserRepo, Depends(get_user_repo)]): ...

  # Route handler only needs the final dependency
  def user_profile(user: Annotated[User, Depends(get_user)]): ...
  ```

## Built-in Dependencies & Parameter Sources

### Request Object

- The raw `Request` object can be injected directly.

  ```python
  from unchained import Request

  def get_request_details(request: Request):
      return {"method": request.method, "path": request.path}
  ```

### App Object

- The `Unchained` application instance itself can be injected.

  ```python
  from unchained import Unchained

  def get_app_config(app: Unchained):
      # Access app-level configuration or state
      return app.config.get("SOME_SETTING")
  ```

### Path Parameters

- Route path parameters are automatically injected into route handlers or dependencies based on matching names and type hints. Type conversion (e.g., `str` to `int`) is performed. Validation errors result in a 422 response.
  ```python
  # Route: /users/{user_id}
  def get_user_by_id(user_id: int): # Injected from path
      # user_id is already converted to int
      return db.get_user(user_id)
  ```

### Query Parameters (`QueryParams`)

- Use `unchained.dependencies.QueryParams` with `Annotated` to inject query parameters.
- **Required/Optional**: Determined by function signature defaults or `QueryParams(default=...)`. Missing required parameters result in a 422 error.
- **Type Conversion**: Handled based on type hints (e.g., `int`, `bool`, `List[str]`). Conversion errors result in a 422 error.
- **Multi-value Parameters**: Use `typing.List[T]` or `list[T]` as the type hint.

  ```python
  from typing import Annotated, List, Optional
  from unchained.dependencies import QueryParams

  def search_items(
      q: Annotated[Optional[str], QueryParams()] = None, # Optional, defaults to None
      limit: Annotated[int, QueryParams(default=10)],   # Optional, defaults to 10
      tags: Annotated[List[str], QueryParams()]          # Required list of strings
  ):
      # q = request.query_params.get("q") or None
      # limit = int(request.query_params.get("limit", 10))
      # tags = request.query_params.getlist("tags")
      ...
  ```

### Headers (`Header`)

- Use `unchained.dependencies.Header` with `Annotated` to inject request headers.
- **Header Name**: Explicitly provided (`Header("X-Custom-Header")`) or inferred from the parameter name (underscores converted to dashes: `x_api_key` -> `x-api-key`). Case-insensitive lookup.
- **Required/Optional**: Determined by function signature defaults or `Header(default=...)`. Missing required headers result in a 422 error.
- **Type Conversion**: Basic type conversion (e.g., to `int`, `float`) can be applied based on type hints.

  ```python
  from typing import Annotated, Optional
  from unchained.dependencies import Header

  def process_request(
      user_agent: Annotated[str, Header()], # Inferred: user-agent
      api_key: Annotated[Optional[str], Header("X-API-Key")] = None
  ):
      ...
  ```

## Generator Dependencies (`yield`)

- Dependencies can be defined as generators (`Generator[...]`) or async generators (`AsyncGenerator[...]`).
- **Lifecycle**: Code before `yield` runs during the dependency resolution phase. The yielded value is injected. Code after `yield` (in a `finally` block) runs before the http response is built.
- **Resource Management**: Useful for setup/teardown logic like database connections or transactions.
- **Error Handling**:

  - Errors _before_ `yield` prevent the route handler from running and typically result in a 500 error (unless it's an `HTTPError`). The teardown phase is skipped.
  - Errors _after_ `yield` (in `finally`) are logged, but the request likely already succeeded (if the route handler finished). The specific behavior might depend on the error type.
  - `HTTPError` raised before `yield` will return the specified HTTP error response, but the teardown phase _will_ still run.

  ```python
  from typing import Generator
  from contextlib import contextmanager

  @contextmanager
  def db_transaction():
      conn = db.connect()
      tx = conn.begin()
      try:
          yield tx # Provide the transaction object
          tx.commit()
      except Exception:
          tx.rollback()
          raise
      finally:
          conn.close()

  def dependency_with_transaction() -> Generator[DBTransaction, None, None]:
      # Using context manager for cleaner syntax
      with db_transaction() as tx:
          yield tx

  # --- Async example ---
  from typing import AsyncGenerator

  async def get_async_resource() -> AsyncGenerator[ResourceType, None]:
      resource = await setup_async_resource()
      try:
          yield resource
      finally:
          await teardown_async_resource(resource)

  # --- Usage in route ---
  def route_using_yield(tx: Annotated[DBTransaction, Depends(dependency_with_transaction)]):
      # Use the transaction object tx
      ...
  ```
