# Functional Testing Guidelines

This directory contains functional tests for the Unchained framework. These tests aim to verify the behavior of the framework from an end-user perspective, typically by making HTTP requests to a test application instance and asserting the responses.

## Test Structure Philosophy

We aim for clarity, maintainability, and comprehensive coverage. To achieve this, we follow these structural guidelines:

1.  **One File Per Feature/Scenario:** Each distinct feature, dependency type (e.g., Header, Query), or component should generally have its own dedicated test file within an appropriate subdirectory (e.g., `tests/functional/dependencies/header/`). This keeps tests focused and easier to locate.

2.  **Data-Driven Tests:**

    - Define a structure (like a `dataclass` or `NamedTuple`) specific to the test file to encapsulate the parameters for a single test variation. This typically includes the route function under test, necessary request details (headers, query params, body, etc.), and the expected response (status code, JSON body, etc.).
    - Create a collection (e.g., a list) of instances of this structure (`test_cases`) to represent all the different scenarios (success, failure, edge cases) for the feature being tested.

3.  **Parameterized Tests:**

    - Use `pytest.mark.parametrize` extensively. This allows a single test function definition to run multiple times with different inputs drawn from the `test_cases` collection.
    - Consider parameterizing over dimensions like supported HTTP methods if the behavior should be consistent across them.

4.  **Separate Sync and Async Tests:**

    - Maintain two distinct test functions within each file whenever a feature supports both synchronous and asynchronous operations: one for sync (`test_*_sync`) and one for async (`test_*_async`).
    - Use the appropriate test client fixture for sync or async tests.
    - Utilize helper functions or mechanisms (e.g., filtering the `test_cases` collection) to supply the correct test case data (sync or async routes) to the corresponding parameterized test function.

5.  **Clear Test Functions (Arrange-Act-Assert):**
    - Keep the logic inside the actual `test_*` functions minimal and focused on the standard Arrange-Act-Assert pattern.
    - **Arrange:** Set up prerequisites. Often this involves registering the specific route function from the current test case with the test `app` instance.
    - **Act:** Perform the action under test, typically making the request using the test client and the parameters from the test case.
    - **Assert:** Verify the outcome, usually by checking the response status code and content against the expected values defined in the test case.

By following these guidelines, we aim to build a functional test suite that is easy to understand, extend, and maintain.
