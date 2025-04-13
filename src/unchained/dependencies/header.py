from typing import Generic, TypeVar, cast

from pydantic import BaseModel

from unchained import Request
from unchained.dependencies.custom import BaseCustom
from unchained.errors import ValidationError

T = TypeVar("T")


class Header(BaseCustom, Generic[T]):
    _param_name: str
    def __init__(self, name: str | None = None, required: bool = True):
        super().__init__()
        self._name = name
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

        if self.required:
            raise ValidationError([{"msg": f"Missing header: {name.lower()}"}])

        return None
