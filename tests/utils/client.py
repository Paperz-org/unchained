from typing import Any, Callable, Dict, Tuple
from unittest.mock import Mock

from unchained.ninja.testing import TestAsyncClient as NinjaAsyncTestClient
from unchained.ninja.testing import TestClient as NinjaTestClient
from unchained.ninja.testing.client import NinjaResponse


class UnchainedTestClient(NinjaTestClient):
    pass


class UnchainedAsyncTestClient(NinjaAsyncTestClient):
    async def _call(self, func: Callable, request: Mock, kwargs: Dict) -> "NinjaResponse":
        res = await func(request, **kwargs)
        return NinjaResponse(res)

    def _resolve(self, method: str, path: str, data: Dict, request_params: Any) -> Tuple[Callable, Mock, Dict]:
        url_path = path.split("?")[0].lstrip("/")
        for url in self.urls:
            match = url.resolve(url_path)
            if match:
                request = self._build_request(method, path, data, request_params)
                return match.func, request, match.kwargs
        raise Exception(f'Cannot resolve "{path}"')
