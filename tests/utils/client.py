from typing import Any, Callable, Dict, Tuple
from unittest.mock import Mock

from penta.testing import TestAsyncClient as PentaAsyncTestClient
from penta.testing import TestClient as PentaTestClient
from penta.testing.client import PentaResponse


class UnchainedTestClient(PentaTestClient):
    pass


class UnchainedAsyncTestClient(PentaAsyncTestClient):
    async def _call(self, func: Callable, request: Mock, kwargs: Dict) -> PentaResponse:
        res = await func(request, **kwargs)
        return PentaResponse(res)

    def _resolve(self, method: str, path: str, data: Dict, request_params: Any) -> Tuple[Callable, Mock, Dict]:
        url_path = path.split("?")[0].lstrip("/")
        for url in self.urls:
            match = url.resolve(url_path)
            if match:
                request = self._build_request(method, path, data, request_params)
                return match.func, request, match.kwargs
        raise Exception(f'Cannot resolve "{path}"')
