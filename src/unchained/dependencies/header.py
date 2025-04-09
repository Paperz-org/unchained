from typing import Generic, TypeVar, cast

from django.http import HttpRequest as DjangoHttpRequest
from fast_depends.dependencies import model
from ninja.errors import ValidationError
from pydantic import BaseModel

T = TypeVar("T")


class BaseCustom(model.Depends, Generic[T]):
    annotation_type: type[T]

    def __init__(
        self,
        *,
        use_cache: bool = True,
        cast: bool = True,
    ) -> None:
        self.dependency = self.__call__
        self.use_cache = use_cache
        self.cast = cast

        # This is the name of the parameter in the signature of the function.
        # It is injected during the parsing of the dependencies.
        self._signature_param_name: str | None = None

        # This is the type of the parameter in the signature of the function.
        # It is injected during the parsing of the dependencies.
        self.annotation_type: type[T]

    def __call__(self, *args, **kwargs) -> T:
        raise NotImplementedError("This method should be implemented by the subclass")


class Header(BaseCustom, Generic[T]):
    def __init__(self, param_name: str | None = None, required: bool = True):
        super().__init__()
        self.param_name = param_name
        self.required = required

    def __call__(self, request: DjangoHttpRequest) -> T | None:
        headers = request.headers
        param_name = self.param_name or self._signature_param_name

        if param_name and param_name in headers:
            if issubclass(self.annotation_type, BaseModel):
                return cast(T, self.annotation_type.model_validate(headers))
            else:
                return self.annotation_type(headers[param_name])  # type: ignore

        if self.required:
            raise ValidationError([{"msg": f"Missing header: {self.param_name}"}])

        return None
