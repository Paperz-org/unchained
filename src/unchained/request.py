from django.core.handlers.asgi import ASGIRequest

class Request(ASGIRequest):
    def query_params(self):
        return self.GET
