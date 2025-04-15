"""Tests for multi-level and complex dependency structures."""

from typing import Annotated, Callable, Dict, List, Tuple

import pytest

from tests.functional import SUPPORTED_HTTP_METHODS
from tests.functional.dependencies.nested_dependencies import (
    EXPECTED_DOUBLE_NESTED_RESULT,
    MULTILEVEL_PATH,
    TEST_RETURN_VALUE_1,
    TEST_RETURN_VALUE_2,
    NestedDependencyTestCase,
)
from tests.utils.client import UnchainedAsyncTestClient, UnchainedTestClient
from tests.utils.test_case import (
    ExpectedResponse,
    get_async_test_case,
    get_sync_test_case,
)
from unchained import Depends, Unchained


# Original double-nested structure (kept for backward compatibility)
def first_dependency() -> str:
    return TEST_RETURN_VALUE_1


def second_dependency() -> str:
    return TEST_RETURN_VALUE_2


def nested_dependency(
    dep1: Annotated[str, Depends(first_dependency)],
    dep2: Annotated[str, Depends(second_dependency)],
) -> str:
    return f"{dep1}_{dep2}"


def double_nested_dependency(
    nested_result: Annotated[str, Depends(nested_dependency)],
    dep1: Annotated[str, Depends(first_dependency)],
) -> str:
    return f"{nested_result}_{dep1}"


def double_nested_route(
    double_nested_result: Annotated[str, Depends(double_nested_dependency)],
) -> str:
    return double_nested_result


# Async Routes for backward compatibility
async def first_dependency_async() -> str:
    return TEST_RETURN_VALUE_1


async def second_dependency_async() -> str:
    return TEST_RETURN_VALUE_2


async def nested_dependency_async(
    dep1: Annotated[str, Depends(first_dependency_async)],
    dep2: Annotated[str, Depends(second_dependency_async)],
) -> str:
    return f"{dep1}_{dep2}"


async def double_nested_dependency_async(
    nested_result: Annotated[str, Depends(nested_dependency_async)],
    dep1: Annotated[str, Depends(first_dependency_async)],
) -> str:
    return f"{nested_result}_{dep1}"


async def double_nested_route_async(
    double_nested_result: Annotated[str, Depends(double_nested_dependency_async)],
) -> str:
    return double_nested_result


class DependencyGenerator:
    """Generator for creating multi-level dependency chains."""

    def __init__(self):
        self.sync_deps = {}
        self.async_deps = {}

    def create_dependency_chain(self, depth: int, is_async: bool = False) -> Tuple[List[Callable], Callable]:
        """
        Dynamically generate a chain of dependencies with the specified depth.

        Args:
            depth: Number of levels in the dependency chain
            is_async: Whether to create async dependencies

        Returns:
            Tuple containing (list of dependencies, route handler)
        """
        if depth < 1:
            raise ValueError("Depth must be at least 1")

        cache_key = f"{depth}_{is_async}"
        cache = self.async_deps if is_async else self.sync_deps

        # Return cached result if available
        if cache_key in cache:
            return cache[cache_key]

        dependencies = []

        # Create base dependency (deepest level)
        base_name = f"{'async_' if is_async else ''}level{depth}"
        base_return = f"level{depth}"

        if is_async:
            # Define asynchronous base dependency
            async def base_dependency() -> str:
                return base_return
        else:
            # Define synchronous base dependency
            def base_dependency() -> str:
                return base_return

        # Rename the function for better debugging
        base_dependency.__name__ = base_name
        dependencies.append(base_dependency)

        # Current dependency to depend on
        current_dependency = base_dependency

        # Create intermediate dependencies
        for level in range(depth - 1, 0, -1):
            level_name = f"{'async_' if is_async else ''}level{level}"

            if is_async:

                def make_level_dependency(level_num: int):
                    async def level_dependency(dep: Annotated[str, Depends(current_dependency)]) -> str:
                        return f"level{level_num}_{dep}"

                    return level_dependency

                level_dependency = make_level_dependency(level)
            else:

                def make_level_dependency(level_num: int):
                    def level_dependency(dep: Annotated[str, Depends(current_dependency)]) -> str:
                        return f"level{level_num}_{dep}"

                    return level_dependency

                level_dependency = make_level_dependency(level)

            level_dependency.__name__ = level_name
            dependencies.append(level_dependency)
            current_dependency = level_dependency

        # Create the route handler
        if is_async:

            async def route_handler(result: Annotated[str, Depends(current_dependency)]) -> str:
                return result
        else:

            def route_handler(result: Annotated[str, Depends(current_dependency)]) -> str:
                return result

        route_handler.__name__ = f"{'async_' if is_async else ''}route_depth_{depth}"

        # Cache the result
        cache[cache_key] = (dependencies, route_handler)

        return dependencies, route_handler

    def generate_expected_output(self, depth: int) -> str:
        """Generate the expected output string for a dependency chain of the given depth."""
        result = f"level{depth}"
        for level in range(depth - 1, 0, -1):
            result = f"level{level}_{result}"
        return result


# Branching dependencies (multiple paths to the same dependency)
def shared_base_dependency() -> str:
    return "shared_base"


def branch1_dependency(base: Annotated[str, Depends(shared_base_dependency)]) -> str:
    return f"branch1_{base}"


def branch2_dependency(base: Annotated[str, Depends(shared_base_dependency)]) -> str:
    return f"branch2_{base}"


def branched_route(
    branch1: Annotated[str, Depends(branch1_dependency)],
    branch2: Annotated[str, Depends(branch2_dependency)],
) -> Dict[str, str]:
    return {"branch1": branch1, "branch2": branch2}


# Async branching dependencies
async def shared_base_dependency_async() -> str:
    return "shared_base"


async def branch1_dependency_async(base: Annotated[str, Depends(shared_base_dependency_async)]) -> str:
    return f"branch1_{base}"


async def branch2_dependency_async(base: Annotated[str, Depends(shared_base_dependency_async)]) -> str:
    return f"branch2_{base}"


async def branched_route_async(
    branch1: Annotated[str, Depends(branch1_dependency_async)],
    branch2: Annotated[str, Depends(branch2_dependency_async)],
) -> Dict[str, str]:
    return {"branch1": branch1, "branch2": branch2}


# Create dependency generator
dep_generator = DependencyGenerator()

# Generate test cases
test_cases = []

# Add original double-nested test cases for backward compatibility
test_cases.extend(
    [
        NestedDependencyTestCase(
            route_func=double_nested_route,
            request_headers={},
            expected_response=ExpectedResponse(status=200, message=EXPECTED_DOUBLE_NESTED_RESULT),
        ),
        NestedDependencyTestCase(
            route_func=double_nested_route_async,
            request_headers={},
            expected_response=ExpectedResponse(status=200, message=EXPECTED_DOUBLE_NESTED_RESULT),
        ),
    ]
)

# Test with various depths
DEPTHS_TO_TEST = [2, 3, 4, 5, 10, 100]  # Test with different depths

# Generate test cases for each depth
for depth in DEPTHS_TO_TEST:
    # Generate sync dependencies and route
    _, sync_route = dep_generator.create_dependency_chain(depth, is_async=False)
    # Generate async dependencies and route
    _, async_route = dep_generator.create_dependency_chain(depth, is_async=True)

    # Expected output for this depth
    expected_output = dep_generator.generate_expected_output(depth)

    # Add sync test case
    test_cases.append(
        NestedDependencyTestCase(
            route_func=sync_route,
            request_headers={},
            expected_response=ExpectedResponse(status=200, message=expected_output),
        )
    )

    # Add async test case
    test_cases.append(
        NestedDependencyTestCase(
            route_func=async_route,
            request_headers={},
            expected_response=ExpectedResponse(status=200, message=expected_output),
        )
    )

# Add branching dependency test cases
test_cases.extend(
    [
        NestedDependencyTestCase(
            route_func=branched_route,
            request_headers={},
            expected_response=ExpectedResponse(
                status=200, message={"branch1": "branch1_shared_base", "branch2": "branch2_shared_base"}
            ),
        ),
        NestedDependencyTestCase(
            route_func=branched_route_async,
            request_headers={},
            expected_response=ExpectedResponse(
                status=200, message={"branch1": "branch1_shared_base", "branch2": "branch2_shared_base"}
            ),
        ),
    ]
)


@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_sync_test_case(test_cases), ids=[c.id for c in get_sync_test_case(test_cases)])
def test_multilevel_dependency_sync(
    app: Unchained,
    test_client: UnchainedTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test multi-level dependency chains with synchronous routes."""
    # Arrange
    getattr(app, method)(MULTILEVEL_PATH)(case.route_func)

    # Act
    response = getattr(test_client, method)(MULTILEVEL_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SUPPORTED_HTTP_METHODS)
@pytest.mark.parametrize("case", get_async_test_case(test_cases), ids=[c.id for c in get_async_test_case(test_cases)])
async def test_multilevel_dependency_async(
    app: Unchained,
    async_test_client: UnchainedAsyncTestClient,
    method: str,
    case: NestedDependencyTestCase,
) -> None:
    """Test multi-level dependency chains with asynchronous routes."""
    # Arrange
    getattr(app, method)(MULTILEVEL_PATH)(case.route_func)

    # Act
    response = await getattr(async_test_client, method)(MULTILEVEL_PATH, headers=case.request_headers)

    # Assert
    assert response.status_code == case.expected_response.status
    assert response.json() == case.expected_response.message
