import inspect
from typing import Generic, Literal, TypeVar, cast, get_origin

from pydantic import BaseModel

from unchained.dependencies import BaseCustom
from unchained.ninja.errors import ValidationError
from unchained.ninja.params.models import Query
from unchained.requests import Request
from unchained.signature.helpers import get_optional_annotation, is_optional_annotation

T = TypeVar("T")

empty = object()


class QueryParams(BaseCustom, Generic[T]):
    ITERABLES = (list, tuple, set)
    _ninja_equivalent = Query

    def __init__(
        self,
        param_name: str | None = None,
        required: bool = True,
        default: T = empty,
    ):
        super().__init__()
        self.param_name = param_name
        self._default = default
        self.required = required

    def __call__(self, request: Request) -> T | None:
        query_params = request.query_params()
        param_name = self.param_name or self.signature_param_name

        if not get_origin(self.annotation_type) and issubclass(self.annotation_type, BaseModel):
            model_input = self._get_model_values(query_params)
            return cast(T, self.annotation_type.model_validate(model_input))

        if param_name and param_name in query_params:
            # TODO: need factorization to use it
            try:
                annotation_type = self.annotation_type
                if is_optional_annotation(self.annotation_type):
                    annotation_type = get_optional_annotation(annotation_type)

                annotation_origin = get_origin(annotation_type)

                if annotation_origin is not None:
                    if annotation_origin is list:
                        return list(query_params.getlist(param_name))  # type: ignore
                    elif annotation_origin is Literal:
                        return cast(T, query_params[param_name])
                    else:
                        raise ValueError(f"Unsupported annotation type: {annotation_origin}")
                else:
                    if issubclass(annotation_type, list):
                        return annotation_type(query_params.getlist(param_name))  # type: ignore
                    else:
                        return cast(T, annotation_type(query_params[param_name]))
            except Exception as e:
                if is_optional_annotation(self.annotation_type):
                    pass
                else:
                    raise ValidationError([{"loc": ("query", param_name), "msg": f"{e}"}])

        if self._default is not empty:
            return self._default

        if self.default is not inspect.Signature.empty:
            return self.default

        if self.required:
            raise ValidationError([{"msg": f"Missing query parameter: {param_name}"}])

        return None

    def _get_model_values(self, query_params: dict[str, str]) -> dict[str, str | list[str]]:
        model_values = {}

        for field_name, field in self.annotation_type.model_fields.items():
            if field_name not in query_params:
                continue

            origin = get_origin(field.annotation)

            if origin in self.ITERABLES:
                model_values[field_name] = query_params.getlist(field_name)
                continue

            try:
                if issubclass(origin, self.ITERABLES):
                    model_values[field_name] = query_params.getlist(field_name)
                else:
                    model_values[field_name] = query_params.get(field_name)
            except TypeError:
                model_values[field_name] = query_params.get(field_name)
            finally:
                continue

        return model_values
