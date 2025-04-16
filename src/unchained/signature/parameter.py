import inspect
from typing import Annotated, get_args, get_origin

from django.http import HttpRequest
from unchained.base import BaseUnchained

from unchained.settings.base import UnchainedSettings
from unchained.states import BaseState


class Parameter(inspect.Parameter):
    """
    A custom parameter class that extends inspect.Parameter to add Unchained-specific functionality.
    """

    @property
    def is_annotated(self) -> bool:
        """Check if the parameter is annotated."""
        return hasattr(self.annotation, "__origin__") and get_origin(self.annotation) is Annotated

    @property
    def is_request(self) -> bool:
        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, HttpRequest)
        return issubclass(self.annotation, HttpRequest)

    @property
    def is_settings(self) -> bool:
        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, UnchainedSettings)
        return issubclass(self.annotation, UnchainedSettings)

    @property
    def is_app(self) -> bool:
        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, BaseUnchained)
        return issubclass(self.annotation, BaseUnchained)

    @property
    def is_header(self) -> bool:
        from unchained.dependencies.header import Header

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, Header)
        return issubclass(self.annotation, Header)
    
    @property
    def is_query_params(self) -> bool:
        from unchained.dependencies.query_params import QueryParams

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, QueryParams)
        return issubclass(self.annotation, QueryParams)

    @property
    def is_state(self) -> bool:
        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, BaseState)
        return issubclass(self.annotation, BaseState)

    @property
    def is_depends(self) -> bool:
        """Check if the parameter is a depends parameter."""
        from unchained.dependencies.depends import Depends

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, Depends)
        return issubclass(self.annotation, Depends)

    @property
    def is_auto_depends(self) -> bool:
        """Check if the parameter is an auto depends parameter."""
        return self.is_request or self.is_settings or self.is_app or self.is_state

    @property
    def is_custom_depends(self) -> bool:
        """Check if the parameter is a custom depends parameter."""
        from unchained.dependencies.custom import BaseCustom

        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, BaseCustom)
        return issubclass(self.annotation, BaseCustom)

    @classmethod
    def from_parameter(cls, param: inspect.Parameter) -> "Parameter":
        """Create an UnchainedParam instance from an inspect.Parameter."""

        return cls(name=param.name, kind=param.kind, default=param.default, annotation=param.annotation)
