from typing import Annotated, Generic, TypeVar, cast

from ninja.errors import ValidationError
from pydantic import BaseModel

from unchained import Request
from unchained.dependencies.custom import BaseCustom

T = TypeVar("T")


class Header(BaseCustom, Generic[T]):
    def __init__(self, param_name: str | None = None, required: bool = True):
        super().__init__()
        self.param_name = param_name
        self.required = required


    def __call__(self, request: Request) -> T | None:
        headers = request.headers

        param_name = self.param_name or self.signature_param_name 

        if issubclass(self.annotation_type, BaseModel):
            return cast(T, self.annotation_type.model_validate(headers))

        if param_name and param_name in headers:
            return self.annotation_type(headers[param_name])  # type: ignore

        if self.default is not None:
            return self.default

        if self.required:
            raise ValidationError([{"msg": f"Missing header: {param_name}"}])

        return None


