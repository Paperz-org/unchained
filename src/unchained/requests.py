import json

# from django.core.handlers.asgi import ASGIRequest
from fastapi import Request as FastAPIRequest

from unchained.errors import ValidationError


class Request(FastAPIRequest):
    ...
    # def query_params(self):
    #     return self.GET

    # @property
    # def has_body(self):
    #     return self.body is not None

    # def json(self):
    #     try:
    #         return json.loads(self.body)
    #     except Exception as e:
    #         raise ValidationError([{"msg": f"Invalid request body: {str(e)}"}])
