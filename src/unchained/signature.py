import inspect
from functools import partial
from typing import Annotated, Any, get_args, get_origin

from django.http import HttpRequest
from fast_depends.dependencies import model
from unchained.base import BaseUnchained
from unchained.settings import settings
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
        """Check if the parameter is a request parameter."""
        return issubclass(self.annotation, HttpRequest)

    @property
    def is_settings(self) -> bool:
        """Check if the parameter is a settings parameter."""
        return issubclass(self.annotation, UnchainedSettings)

    @property
    def is_app(self) -> bool:
        """Check if the parameter is an app parameter."""
        return issubclass(self.annotation, BaseUnchained)

    @property
    def is_state(self) -> bool:
        """Check if the parameter is a state parameter."""
        return issubclass(self.annotation, BaseState)

    @property
    def is_depends(self) -> bool:
        """Check if the parameter is a depends parameter."""
        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, model.Depends)
        return False
    
    @property
    def is_auto_depends(self) -> bool:
        """Check if the parameter is an auto depends parameter."""
        return self.is_request or self.is_settings or self.is_app or self.is_state

    @classmethod
    def from_parameter(cls, param: inspect.Parameter) -> "Parameter":
        """Create an UnchainedParam instance from an inspect.Parameter."""
        return cls(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=param.annotation
        )

class Signature(inspect.Signature):
    parameters: dict[str, Parameter]

    def __init__(self, parameters=None, return_annotation=inspect.Signature.empty, __validate_parameters__=True):
        if parameters is not None:
            parameters = [
                Parameter.from_parameter(p) if not isinstance(p, Parameter) else p
                for p in parameters
            ]
        super().__init__(parameters=parameters, return_annotation=return_annotation, __validate_parameters__=__validate_parameters__)

    @classmethod
    def from_callable(cls, obj, *, follow_wrapped=True, globals=None, locals=None, eval_str=False):
        sig = super().from_callable(obj, follow_wrapped=follow_wrapped, globals=globals, locals=locals, eval_str=eval_str)
        parameters = [
            Parameter.from_parameter(p) if not isinstance(p, Parameter) else p
            for p in sig.parameters.values()
        ]
        return cls(parameters=parameters, return_annotation=sig.return_annotation)

    @property
    def has_request_object(self) -> bool:
        """
        Check if the signature has a request parameter (HttpRequest from Django).
        """
        for param_name, param in self.parameters.items():
            if param.is_annotated:
                continue
            if param.is_request and param_name == "request":
                return True
        return False

    @property
    def has_default_dependencies(self) -> bool:
        """
        Check if the signature has a request parameter (HttpRequest from Django).
        """
        for param_name, param in self.parameters.items():
            if param.is_annotated:
                continue
            if param.is_request or param_name == "request":
                return True
            if param.is_settings or param_name == "settings":
                return True
            if param.is_app or param_name == "app":
                return True
            if param.is_state or param_name == "state":
                return True

        return False

    def new_signature_without_default_dependencies(self) -> "Signature":
        """
        Create a new instance of the signature without the default dependencies (request, settings, app, state).
        """
        parameters = []
        for _, param in self.parameters.items():
            if param.is_annotated:
                parameters.append(param)
                continue
            if param.is_auto_depends:
                continue
            parameters.append(param)

        return Signature(parameters)

    def new_signature_without_annotated(self) -> "Signature":
        """
        Create a new instance of the signature without the annotated parameters.

        We need this for Django Ninja to parse the parameters correctly.
        """
        parameters = []
        for _, param in self.parameters.items():
            if param.is_annotated:
                continue
            parameters.append(param)

        return Signature(parameters)

    def get_default_dependencies(self) -> dict[str, Any]:
        """
        Get a dictionary of all default dependencies and their parameter names.
        Returns a dictionary where keys are parameter names and values are the parameter objects.
        """
        default_deps = {}
        for param_name, param in self.parameters.items():
            if param.is_annotated:
                continue
            if param.is_request and param_name == "request":
                default_deps["request"] = None
            elif param.is_settings and param_name == "settings":
                default_deps["settings"] = None
            elif param.is_app and param_name == "app":
                default_deps["app"] = None
            elif param.is_state and param_name == "state":
                default_deps["state"] = None
        return default_deps
    


class SignatureUpdater:
    """
    This class is used to update the signature of the dependencies.
    We need to update the signature of the dependencies to allow automatic injection of the request parameter.

    We accomplish this by:
    - Detecting if the dependency has a request parameter.
    - If it has, we remove it from the signature and we create a partial function with the request parameter.
    - If it has not, we don't need to do anything.
    - We call the function recursively to update the signature of the dependencies.

    Why the use of partial function?
    We use partial to pre-fill the request parameter with None.
    We do this to have consistent function id, and inject latter the correct request parameter.
    It's usefull to avoid to manage dependency at runtime.
    With this trick, at startup all the dependencies are pre-filled with a None request parameter.
    And when the api is called, the request parameter is injected dynamically in all the partials.
    """

    def __init__(self):
        self.partialised_dependencies: list[model.Depends] = []

    def update_deep_dependencies(self, instance: model.Depends):
        # Get the signature of the dependency
        signature = Signature.from_callable(instance.dependency)

        # If the dependency has a request parameter, we need to remove it
        # because we will inject the request parameter later
        defaults_dependencies = signature.get_default_dependencies()

        if defaults_dependencies:
            instance.dependency = partial(instance.dependency)
            # Create a partial function with all default dependencies set to None
            instance.dependency.keywords.update(**defaults_dependencies)
            # Update the signature of the dependency
            instance.dependency.__signature__ = signature.new_signature_without_default_dependencies()  # type: ignore
            # Store the dependency to inject it later
            self.partialised_dependencies.append(instance)

        # We check all the dependencies of the current signature
        for _, param in signature.parameters.items():
            # If the dependency is not a Depends, we skip it
            if not param.is_depends:
                continue
            # If the dependency is a Depends, we call the function recursively to update the signature of the dependency and
            # create the partial function if needed.
            _, next_dependency = get_args(param.annotation)
            self.update_deep_dependencies(next_dependency)
