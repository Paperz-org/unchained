from ninja.testing import TestAsyncClient as NinjaAsyncTestClient
from ninja.testing import TestClient as NinjaTestClient


class UnchainedTestClient(NinjaTestClient):
    pass


class UnchainedAsyncTestClient(NinjaAsyncTestClient):
    pass
