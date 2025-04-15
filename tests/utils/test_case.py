import dataclasses
import inspect
from typing import Any, Callable, Dict, List


@dataclasses.dataclass
class ExpectedResponse:
    status: int
    message: str


@dataclasses.dataclass
class UnchainedTestCase:
    route_func: Callable[..., Any]
    request_headers: Dict[str, str]
    expected_response: ExpectedResponse

    @property
    def id(self) -> str:
        return f"{self.route_func.__name__}_{self.expected_response.status}"

    @property
    def is_async(self) -> bool:
        return inspect.iscoroutinefunction(self.route_func)


def get_sync_test_case(test_cases: List[UnchainedTestCase]) -> List[UnchainedTestCase]:
    return [test_case for test_case in test_cases if not test_case.is_async]


def get_async_test_case(test_cases: List[UnchainedTestCase]) -> List[UnchainedTestCase]:
    return [test_case for test_case in test_cases if test_case.is_async]
