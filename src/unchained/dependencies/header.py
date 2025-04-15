from typing import Generic, TypeVar, cast

from pydantic import BaseModel

from unchained import Request
from unchained.dependencies.custom import BaseCustom
from unchained.errors import ValidationError

T = TypeVar("T")


class Header(BaseCustom[T], Generic[T]):
    _param_name: str
    _default: T | None

    def __init__(self, name: str | None = None, required: bool = True, default: T | None = None):
        super().__init__()
        self._name = name
        self._default = default
        self.required = required
        self.annotation_type: type[T]

    def __call__(self, request: Request) -> T | None:
        headers = request.headers
        name = self._name or self.param_name
        if name and name in headers:
            if issubclass(self.annotation_type, BaseModel):
                return cast(T, self.annotation_type.model_validate(headers))
            else:
                return self.annotation_type(headers[name])  # type: ignore

        default = self._default or self.default
        if default is not None:
            return default
        if self.required:
            raise ValidationError([{"msg": f"Missing header: {name.lower()}"}])

        return None
