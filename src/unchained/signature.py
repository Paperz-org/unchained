import inspect
from functools import partial
from typing import Annotated, Any, get_args, get_origin

from django.http import HttpRequest
from fast_depends.dependencies import model


class Signature(inspect.Signature):
    @property
    def has_request_object(self) -> bool:
        """
        Check if the signature has a request parameter (HttpRequest from Django).
        """
        for param_name, param in self.parameters.items():
            if self._param_is_annotated(param):
                continue
            if self._param_is_request(param) or param_name == "request":
                return True

        return False

    def new_signature_without_request(self) -> "Signature":
        """
        Create a new instance of the signature without the request parameter.
        """
        parameters = []
        for _, param in self.parameters.items():
            if self._param_is_annotated(param):
                parameters.append(param)
                continue
            if self._param_is_request(param):
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
            if self._param_is_annotated(param):
                continue
            parameters.append(param)

        return Signature(parameters)

    @staticmethod
    def _param_is_annotated(param: Any) -> bool:
        annotation = param.annotation
        return hasattr(annotation, "__origin__") and get_origin(annotation) is Annotated

    @staticmethod
    def _param_is_request(param: Any) -> bool:
        return issubclass(param.annotation, HttpRequest)


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

    @staticmethod
    def _param_is_annotated(param: Any) -> bool:
        annotation = param.annotation
        return hasattr(annotation, "__origin__") and get_origin(annotation) is Annotated

    def _param_is_depends(self, param: Any) -> bool:
        """
        Function to check if the parameter is a Depends.
        First we check if the parameter is annotated with Annotated.
        If it is, we check if the instance is a Depends.
        If it is not, we return False.

        Exemple:
            def dependency(a: Annotated[str, Depends(other_dependency)])
        """
        if self._param_is_annotated(param):
            _, instance = get_args(param.annotation)
            return isinstance(instance, model.Depends)
        return False

    def update_deep_dependencies(self, instance: model.Depends):
        # Get the signature of the dependency
        signature = Signature.from_callable(instance.dependency)

        # If the dependency has a request parameter, we need to remove it
        # because we will inject the request parameter later
        if signature.has_request_object:
            # Create a partial function with the request parameter (with request=None because we will inject it later)
            instance.dependency = partial(instance.dependency, request=None)
            # Update the signature of the dependency
            instance.dependency.__signature__ = (  # type: ignore
                signature.new_signature_without_request()
            )  # type: ignore
            # Store the dependency to inject it later
            self.partialised_dependencies.append(instance)

        # We check all the dependencies of the current signature
        for _, param in signature.parameters.items():
            # If the dependency is not a Depends, we skip it
            if not self._param_is_depends(param):
                continue
            # If the dependency is a Depends, we call the function recursively to update the signature of the dependency and
            # create the partial function if needed.
            _, next_dependency = get_args(param.annotation)
            self.update_deep_dependencies(next_dependency)
