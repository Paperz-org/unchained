import json
from tempfile import SpooledTemporaryFile
from typing import Any, Callable, Dict, Tuple
from unittest.mock import Mock

from django.http import QueryDict
from django.http.request import HttpHeaders

from unchained.ninja.testing import TestAsyncClient as NinjaAsyncTestClient
from unchained.ninja.testing import TestClient as NinjaTestClient
from unchained.ninja.testing.client import NinjaResponse, build_absolute_uri
from unchained.requests import Request


class UnchainedTestClientBase:
    def _build_request(self, method: str, path: str, data: bytes, request_params: Any) -> Mock:
        body_file = SpooledTemporaryFile(max_size=65536, mode="w+b")
        body_file.write(data)
        body_file.seek(0)
        request = Request(scope={"path": path, "method": method}, body_file=body_file)
        request.COOKIES = {}
        request._dont_enforce_csrf_checks = True
        request.build_absolute_uri = build_absolute_uri

        request.user = Mock()
        if "user" not in request_params:
            request.user.is_authenticated = False
            request.user.is_staff = False
            request.user.is_superuser = False

        request.META = request_params.pop("META", {"REMOTE_ADDR": "127.0.0.1"})

        request.META.update({f"HTTP_{k.replace('-', '_')}": v for k, v in request_params.pop("headers", {}).items()})

        request.headers = HttpHeaders(request.META)

        if isinstance(data, QueryDict):
            request.POST = data
        else:
            request.POST = QueryDict(mutable=True)

        if "?" in path:
            request.GET = QueryDict(path.split("?")[1])
        else:
            query_params = request_params.pop("query_params", None)
            if query_params:
                query_dict = QueryDict(mutable=True)
                for k, v in query_params.items():
                    if isinstance(v, list):
                        for item in v:
                            query_dict.appendlist(k, item)
                    else:
                        query_dict[k] = v
                request.GET = query_dict
            else:
                request.GET = QueryDict()

        for k, v in request_params.items():
            setattr(request, k, v)
        return request

    def _resolve(self, method: str, path: str, data: Any, request_params: Any) -> Tuple[Callable, Mock, Dict]:
        url_path = path.split("?")[0].lstrip("/")
        for url in self.urls:
            match = url.resolve(url_path)
            if match:
                try:
                    data = json.dumps(data)
                except json.JSONDecodeError:
                    pass
                if isinstance(data, str):
                    data = data.encode("utf-8")
                request = self._build_request(method, path, data, request_params)
                return match.func, request, match.kwargs
        raise Exception(f'Cannot resolve "{path}"')


class UnchainedTestClient(UnchainedTestClientBase, NinjaTestClient):
    pass


class UnchainedAsyncTestClient(UnchainedTestClientBase, NinjaAsyncTestClient):
    async def _call(self, func: Callable, request: Mock, kwargs: Dict) -> "NinjaResponse":
        res = await func(request, **kwargs)
        return NinjaResponse(res)
