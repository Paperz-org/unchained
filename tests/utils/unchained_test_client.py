from typing import Callable, Dict
from unittest.mock import Mock

from ninja.testing import TestClient as NinjaTestClient
from ninja.testing.client import NinjaResponse


class UnchainedTestClient(NinjaTestClient):
    pass