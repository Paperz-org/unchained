from typing import Any, Dict, TypedDict

from fast_depends.library import CustomField
from ninja.errors import ValidationError
from pydantic import BaseModel

from unchained import Request


class BaseParams(TypedDict, total=False):
    request: Request


class BaseCustomField(CustomField):
    param_name: str
    _annotation_type: type

    def __getattribute__(self, name: str) -> Any:
        if name == "use":
            return super().__getattribute__("use")
        return super().__getattribute__(name)


class Header(BaseCustomField):
    param_name: str
    _annotation_type: type

    def __init__(self, param_name: str | None = None, required: bool = True):
        super().__init__()
        self._wanted_param_name = param_name

    def use(self, /, **kwargs: BaseParams) -> Dict[str, Any]:
        params: BaseParams = kwargs
        request = params.get("request")
        breakpoint()
        validated_kwargs = super().use(request=request, **kwargs)

        header_param_name = self._wanted_param_name or self.param_name

        # Extract the header value from the request headers
        headers = request.headers

        if header_param_name and header_param_name in headers:
            if issubclass(self._annotation_type, BaseModel):
                new_kwargs = {header_param_name: headers[header_param_name]}
            else:
                new_kwargs = headers[header_param_name]
            validated_kwargs[self.param_name] = new_kwargs
            return validated_kwargs

        if self.required:
            raise ValidationError([{"msg": f"Missing header: {self.param_name}"}])

        validated_kwargs[self.param_name] = None
        return validated_kwargs
