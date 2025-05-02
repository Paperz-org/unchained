import inspect
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from pydantic import BaseModel

from unchained.dependencies import BaseCustom
from unchained.errors import ValidationError

# if TYPE_CHECKING:
from unchained.requests import Request

T = TypeVar("T")


class Header(BaseCustom[T], Generic[T]):
    _name: str | None
    _default: T | None

    def __init__(
        self,
        param_name: str | None = None,
        required: bool = True,
        default: T | None = None,
    ):
        super().__init__()
        self.param_name = param_name
        self._default = default
        self.required = required

    def __call__(self, request: Request) -> T | None:
        headers = request.headers

        param_name = self.param_name or self.signature_param_name

        if issubclass(self.annotation_type, BaseModel):
            return cast(T, self.annotation_type.model_validate(headers))

        if param_name and param_name in headers:
            try:
                return self.annotation_type(headers[param_name])  # type: ignore
            except Exception as e:
                raise ValidationError([{"loc": ("header", param_name), "msg": f"{e}"}])

        if self._default is not None:
            return self._default

        if self.default is not inspect.Signature.empty:
            return self.default

        if self.required:
            raise ValidationError([{"loc": ("header", param_name), "msg": f"Missing header: {param_name}"}])

        return None
