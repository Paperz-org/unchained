# Functional Requirements & Coverage: Dependency Injection System

This document outlines the desired capabilities of the Unchained framework's dependency injection system and tracks the current functional test coverage based on files in `tests/functional/dependencies`.

**Status Key:**

- ✅: Covered by existing functional tests.
- ⚠️: Partially covered or requires clarification/more specific tests.
- ❌: Not covered by existing functional tests (Blind Spot).
- ❓: Clarification needed in requirements definition itself.

---

## I. Core Capabilities

1.  ✅ **Dependency Declaration:** Using type hints, `Annotated`, `Depends`, `Header`, `Query`, `Body`, Path params, `Request`, `Unchained`.
2.  ✅ **Automatic Resolution:** Framework resolves and injects dependencies.
3.  ⚠️ **Sync/Async Agnostic:**
    - ✅ Sync/async functions for handlers and dependencies supported.
    - ✅ Async handlers/deps can call sync/async deps.
    - ✅ Sync deps can call async deps _only_ in async context.
    - ❌ Explicit test needed for sync route handler calling async dependency (should fail).
4.  ✅ **Request Scope Caching:** Dependency result cached within a single request by default. (Verified in `test_core.py`).
5.  ✅ **Cache Invalidation:** `use_cache=False` disables caching. (Verified in `test_core.py`).
6.  ✅ **Consistency Across Methods:** Tested primarily with GET/POST, mechanism appears general.

## II. Dependency Sources

1.  ✅ **Callable Dependencies (`Depends`):**
    - ✅ Inject return value (sync/async).
    - ✅ Support complex return types (dataclasses tested).
    - ✅ Handle dependencies returning `None` (into `Optional`).
2.  ⚠️ **HTTP Headers (`Header`):**
    - ✅ Extract values.
    - ✅ Specify header name or infer (underscore -> dash).
    - ✅ Case-insensitive matching.
    - ✅ Required headers (error if missing).
    - ✅ Optional headers with default values.
    - ✅ Multiple different header values.
    - ❌ **Blind Spot:** Behavior with multiple request headers sharing the _same_ name.
3.  ✅ **URL Path Parameters:**
    - ✅ Inject values from path segments.
    - ✅ Automatic type conversion (str, int tested).
    - ✅ Required parameters (error on mismatch).
4.  ⚠️ **URL Query Parameters (`Query`):**
    - ✅ Extract values from query string.
    - ✅ Specify name explicitly (inferring from param name needs confirmation/test).
    - ✅ Automatic type conversion (str, int tested).
    - ✅ Required and optional parameters (with defaults).
    - ✅ Support multi-value parameters (into `list[str]`).
    - ❌ **Blind Spot:** Injecting all query parameters as a dict/model.
5.  ⚠️ **Request Body (`Body`):**
    - ✅ Parse and inject JSON data.
    - ✅ Automatic parsing/validation into Pydantic models.
    - ✅ Required/optional fields within the body model.
    - ❌ **Blind Spot:** Support for non-JSON content types (e.g., form data).
6.  ✅ **Request Object:** Direct injection of `Request` tested in handlers and dependencies.
7.  ✅ **Application Instance:** Direct injection of `Unchained` app instance tested in handlers and dependencies.

## III. Nested and Complex Dependencies

1.  ✅ **Nested Resolution:** Resolve dependencies that have their own dependencies.
2.  ✅ **Multi-Level Chains:** Support deep nesting.
3.  ⚠️ **Branching Dependencies:** Correctly resolve graphs with shared dependencies.
    - ⚠️ Caching verification (shared dep runs only once) needs explicit mock/counter checks (current tests have TODOs).
4.  ⚠️ **Parameter Resolution within Dependencies:**
    - ✅ Allow dependency parameters to be resolved from path parameters.
    - ✅ Support default values for dependency parameters.
    - ❌ **Blind Spot:** Explicitly test resolving _query_ parameters within a dependency function.
    - ❌ **Blind Spot / ❓:** Define and test precise precedence rules: How are parameters within dependencies resolved (e.g., path param vs. query param vs. nested `Depends`)?

## IV. Lifecycle and Error Handling (Yield Dependencies)

1.  ✅ **Setup/Teardown (`yield`):** Support sync/async generators for resource management.
2.  ✅ **Teardown Guarantee:** Teardown runs even if errors occur during request handling (in route or later dependencies).
3.  ✅ **Nested Lifecycle:** Correct setup/teardown order for nested yield dependencies.
4.  ✅ **Setup Errors:** Teardown does _not_ run if setup (before `yield`) fails. Teardown for _previously successful_ dependencies still runs.
5.  ⚠️ **Teardown Errors:** Errors after `yield` are handled (logged), request succeeds/fails based on original processing.
    - ⚠️ Need test verifying logs for teardown errors (current tests have TODOs).
6.  ✅ **HTTP Exceptions:** Dependencies can raise `HttpError`; teardown logic still executes correctly.
