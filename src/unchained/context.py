from contextvars import ContextVar

app = ContextVar("app", default=None)
