# Testing Unchained Framework

This directory contains tests for the Unchained framework. The tests are organized in a structured way to maintain clarity and separation of concerns.


## Test Categories

- **Unit Tests**: Test basic components in isolation
- **Integration Tests**: Test how components interact with each other
- **Functional Tests**: Test full features from a user's perspective

## Running the Tests

To run all tests:

```bash
pytest
```

To run a specific category of tests:

```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/functional/
```

To run a specific test file:

```bash
pytest tests/unit/test_hello_world.py
```

## Global Fixtures

The `conftest.py` file contains fixtures available to all tests:

- `api`: Creates a new Unchained API instance
- `client`: Provides an UnchainedTestClient for making HTTP requests

