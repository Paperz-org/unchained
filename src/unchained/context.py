from contextvars import ContextVar

app = ContextVar("app", default=None)
request = ContextVar("request", default=None)


