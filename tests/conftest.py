import os

# the test suite builds one app per test: they all share the same urls namespace, which
# penta otherwise refuses (`Penta(..., urls_namespace=...)` is how apps are told apart)
os.environ.setdefault("PENTA_SKIP_REGISTRY", "yes")

from .functional.fixtures import app, async_test_client, test_client  # noqa: E402

__all__ = ["app", "async_test_client", "test_client"]
