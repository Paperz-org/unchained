from collections.abc import Callable
from typing import Any

from django.http import HttpRequest as DjangoHttpRequest
from fast_depends.dependencies import model
from ninja.errors import ValidationError
from pydantic import BaseModel


class BaseCustom(model.Depends):
    annotation_type: type
    param_name: str | None = None

    def __init__(
        self,
        use_cache: bool = True,
        cast: bool = True,
    ) -> None:
        super().__init__(self.__call__, use_cache=use_cache, cast=cast)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented by the subclass")


class Header(BaseCustom):
    def __init__(self, param_name: str | None = None, required: bool = True):
        super().__init__()
        self.param_name = param_name
        self.required = required

    def __call__(self, request: DjangoHttpRequest) -> Any:  # type: ignore
        headers = request.headers
        if self.param_name and self.param_name in headers:
            if issubclass(self.annotation_type, BaseModel):
                return self.annotation_type.model_validate(headers)
            else:
                return headers[self.param_name]

        if self.required:
            raise ValidationError([{"msg": f"Missing header: {self.param_name}"}])
