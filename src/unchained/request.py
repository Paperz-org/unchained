from django.core.handlers.asgi import ASGIRequest
import json
from functools import cached_property

from ninja.errors import ValidationError

class Request(ASGIRequest):
    def query_params(self):
        return self.GET
    
    @property
    def has_body(self):
        return self.body is not None

    def json(self):
        try:
            return json.loads(self.body)
        except Exception as e:
            raise ValidationError([{"msg": f"Invalid request body: {str(e)}"}])

