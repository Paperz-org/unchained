---
title: Generator Dependencies (Yield)
---

# Generator Dependencies (`yield`)

Dependencies can be defined using generators (`yield`) for scenarios requiring setup and teardown logic, like managing resources (e.g., database connections, transactions, external service clients) within the request lifecycle.

Both synchronous (`Generator`) and asynchronous (`AsyncGenerator`) dependencies are supported.

## Lifecycle Management

A generator dependency allows you to execute code *before* yielding the dependency value (setup phase) and *after* the route handler has finished and the response is being prepared (teardown phase).

-   **Setup Phase**: Code before the `yield` statement runs during dependency resolution. The value yielded is what gets injected into the dependent function (route handler or another dependency).
-   **Teardown Phase**: Code after the `yield` statement (typically within a `finally` block to ensure execution) runs *after* the route handler has returned but *before* the response is sent to the client.

```python
import time
from typing import Annotated, Generator, AsyncGenerator
from unchained import Unchained, Depends

app = Unchained()

# --- Synchronous Example --- #

def get_sync_resource() -> Generator[dict, None, None]:
    print("SYNC: Setting up resource...")
    resource = {"id": time.time_ns(), "status": "initialized"}
    try:
        yield resource # Value injected into route
    finally:
        # This runs after the route handler finishes
        print(f"SYNC: Tearing down resource {resource['id']}")
        resource["status"] = "closed"

@app.get("/sync-resource")
def use_sync_resource(res: Annotated[dict, Depends(get_sync_resource)]):
    print(f"SYNC: Using resource {res['id']} with status {res['status']}")
    # Simulate work
    time.sleep(0.1)
    print("SYNC: Finished using resource.")
    return res

# --- Asynchronous Example --- #

async def get_async_resource() -> AsyncGenerator[dict, None]:
    print("ASYNC: Setting up resource...")
    resource = {"id": time.time_ns(), "status": "initialized"}
    try:
        yield resource
    finally:
        # This runs after the route handler finishes
        print(f"ASYNC: Tearing down resource {resource['id']}")
        # Simulate async teardown
        await asyncio.sleep(0.05)
        resource["status"] = "closed"

@app.get("/async-resource")
async def use_async_resource(res: Annotated[dict, Depends(get_async_resource)]):
    print(f"ASYNC: Using resource {res['id']} with status {res['status']}")
    # Simulate async work
    await asyncio.sleep(0.1)
    print("ASYNC: Finished using resource.")
    return res

```

**Typical Use Case: Database Transactions**

A common pattern is managing database transactions:

```python
from contextlib import contextmanager, asynccontextmanager

# Assume db_conn is a synchronous DB connection pool/object
@contextmanager
def db_transaction_sync():
    tx = db_conn.begin()
    print("Starting DB transaction")
    try:
        yield tx # Yield the transaction object
        print("Committing DB transaction")
        tx.commit()
    except Exception as e:
        print(f"Rolling back DB transaction due to: {e}")
        tx.rollback()
        raise # Re-raise the exception
    finally:
        print("Transaction context finished (committed or rolled back)")
        # Connection might be closed here or returned to pool depending on db_conn logic

def get_db_tx_sync() -> Generator[DBTransaction, None, None]:
    with db_transaction_sync() as transaction:
        yield transaction

# Assume async_db_conn is an asynchronous DB connection pool/object
@asynccontextmanager
async def db_transaction_async():
    tx = await async_db_conn.begin()
    print("Starting ASYNC DB transaction")
    try:
        yield tx
        print("Committing ASYNC DB transaction")
        await tx.commit()
    except Exception as e:
        print(f"Rolling back ASYNC DB transaction due to: {e}")
        await tx.rollback()
        raise
    finally:
        print("ASYNC Transaction context finished (committed or rolled back)")

async def get_db_tx_async() -> AsyncGenerator[AsyncDBTransaction, None]:
    async with db_transaction_async() as transaction:
        yield transaction

# Usage in routes:
def route_sync_db(tx: Annotated[DBTransaction, Depends(get_db_tx_sync)]):
    # Use the transaction object 'tx' to perform database operations
    repo = UserRepository(tx)
    repo.create_user(...)
    return {"status": "ok"}

async def route_async_db(tx: Annotated[AsyncDBTransaction, Depends(get_db_tx_async)]):
    repo = AsyncUserRepository(tx)
    await repo.create_user(...)
    return {"status": "ok"}
```

## Error Handling

The behavior depends on *when* the error occurs in the generator dependency:

1.  **Error Before `yield` (Setup Phase)**:
    *   The route handler will **not** be executed.
    *   The code after `yield` (teardown phase) will **not** run.
    *   If the error is a standard Python exception (`ValueError`, `TypeError`, etc.), Unchained typically returns an HTTP 500 Internal Server Error.
    *   If the error is an `unchained.errors.HTTPError`, Unchained returns the corresponding HTTP error response (e.g., 403 Forbidden, 404 Not Found).

2.  **Error After `yield` (Teardown Phase)**:
    *   The route handler has already finished execution.
    *   The error occurs while the response is being finalized.
    *   The error is typically logged by Unchained.
    *   The client likely already received or will receive the response generated by the route handler (often a 200 OK if the route handler succeeded), unless the teardown error somehow prevents the response from being sent (less common).
    *   If an `HTTPError` is raised during teardown, it's generally too late to change the response status code sent to the client. The error will likely just be logged.

3.  **`HTTPError` Raised Before `yield`**:
    *   The route handler will **not** be executed.
    *   Unchained will catch the `HTTPError` and prepare the corresponding HTTP error response for the client.
    *   Crucially, the teardown phase (code after `yield` in `finally`) **will still execute**. This is important for cleaning up resources even if the main operation failed validation or authorization checks performed during setup.

```python
from unchained.errors import HTTPError

# Example: Error during setup
def dep_setup_error() -> Generator[str, None, None]:
    print("SETUP: Entering")
    try:
        raise ValueError("Failed during setup!")
        yield "never_reached"
    finally:
        print("SETUP: Teardown - THIS WILL NOT RUN")

# Example: HTTPError during setup (teardown *will* run)
def dep_http_error() -> Generator[str, None, None]:
    print("HTTP_SETUP: Entering")
    try:
        raise HTTPError(403, "Permission Denied during setup")
        yield "never_reached"
    finally:
        print("HTTP_SETUP: Teardown - THIS WILL RUN")

# Example: Error during teardown
def dep_teardown_error() -> Generator[str, None, None]:
    print("TEARDOWN_ERROR: Entering")
    try:
        yield "value_from_dependency"
    finally:
        print("TEARDOWN_ERROR: Teardown - Raising error now!")
        raise ValueError("Failed during teardown!")

@app.get("/setup-fail")
def route_setup_fail(d: Annotated[str, Depends(dep_setup_error)]): return d # Route not called

@app.get("/http-fail")
def route_http_fail(d: Annotated[str, Depends(dep_http_error)]): return d # Route not called

@app.get("/teardown-fail")
def route_teardown_fail(d: Annotated[str, Depends(dep_teardown_error)]):
    print(f"ROUTE_TEARDOWN_FAIL: Received value: {d}")
    return {"data": d} # This route runs, client gets 200 OK, error logged server-side
```

