from typing import Generic, TypeVar, cast

from ninja.errors import ValidationError
from pydantic import BaseModel

from unchained.request import Request
from unchained.dependencies.custom import BaseCustom

T = TypeVar("T")


class JsonBody(BaseCustom, Generic[T]):
    def __init__(self, embed: bool = False, param_name: str | None = None, required: bool = True):
        super().__init__()
        self.required = required
        self.param_name = param_name
        self.embed = embed

    def __call__(self, request: Request) -> T | None:
        param_name = self.param_name or self.signature_param_name

        if not request.has_body:
            if self.default is not None:
                return self.default
            
            if self.required:
                raise ValidationError([{"msg": "Missing request body"}])
            
            return None

        if self.embed:
            body_data = request.json().get(param_name)
            if not body_data and self.required:
                raise ValidationError([{"msg": f"Missing request body: {param_name}"}])
        else:
            body_data = request.json()

         
        if issubclass(self.annotation_type, BaseModel):
            try:
                return cast(T, self.annotation_type.model_validate(body_data))
            except Exception as e:
                raise ValidationError([{"msg": f"Invalid request body: {str(e)}"}])
        
        # For non-BaseModel types, try direct casting
        try:
            return cast(T, self.annotation_type(body_data))
        except Exception as e:
            raise ValidationError([{"msg": f"Failed to parse body: {str(e)}"}])



