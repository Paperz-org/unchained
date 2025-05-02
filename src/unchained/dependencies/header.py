from typing import TYPE_CHECKING, Generic, TypeVar, cast

from pydantic import BaseModel

from unchained.dependencies import BaseCustom
from unchained.ninja.errors import ValidationError

# if TYPE_CHECKING:
from unchained.requests import Request

T = TypeVar("T")


class Header(BaseCustom[T], Generic[T]):
    _name: str | None
    _default: T | None

    def __init__(self, param_name: str | None = None, required: bool = True, default: T | None = None):
        super().__init__()
        print("===========", param_name)
        self.param_name = param_name
        self._default = default
        self.required = required
        self.annotation_type: type[T]
        self.default: type[T]

    def __call__(self, request: Request) -> T | None:
        headers = request.headers

        if issubclass(self.annotation_type, BaseModel):
            return cast(T, self.annotation_type.model_validate(headers))

        print("===========", self.param_name)
        print("===========", headers)

        if "self.param_name" and self.param_name in headers:
            return self.annotation_type(headers[self.param_name])  # type: ignore

        if self.default is not None:
            return self.default

        default = self._default or self.default
        if default is not None:
            return default
        if self.required:
            raise ValidationError([{"msg": f"Missing header: {self._name.lower()}"}])

        return None
