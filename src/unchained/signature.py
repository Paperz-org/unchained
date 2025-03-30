import inspect
from functools import partial
from typing import Annotated, Any, Callable, get_args, get_origin

from django.http import HttpRequest
from fast_depends.dependencies import model


class Signature(inspect.Signature):
    @property
    def has_request_object(self) -> bool:
        for param_name, param in self.parameters.items():
            if self._param_is_annotated(param):
                continue
            if self._param_is_request(param) or param_name == "request":
                return True

        return False

    def new_signature_without_request(self) -> inspect.Signature:
        parameters = []
        for _, param in self.parameters.items():
            if self._param_is_annotated(param):
                parameters.append(param)
                continue
            if self._param_is_request(param):
                continue
            parameters.append(param)

        return Signature(parameters)

    def new_signature_without_annotated(self) -> inspect.Signature:
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
    def __init__(self):
        self.partialised_dependencies: list[Callable] = []

    @staticmethod
    def _param_is_annotated(param: Any) -> bool:
        annotation = param.annotation
        return hasattr(annotation, "__origin__") and get_origin(annotation) is Annotated

    def _param_is_depends(self, param: Any) -> bool:
        if self._param_is_annotated(param):
            _, instance = get_args(param.annotation)
            return isinstance(instance, model.Depends)
        return False

    def register_dependency(self, dependency: Callable):
        self.partialised_dependencies.append(dependency)

    def update_deep_dependencies(self, signature: Signature):
        for _, param in signature.parameters.items():
            if self._param_is_depends(param):
                _, instance = get_args(param.annotation)

                # If the dependency has a request parameter, we need to remove it
                # because we will inject the request parameter later
                # We need to update the signature because FastDepends will create a model based on the signature.
                dependency_signature = Signature.from_callable(instance.dependency)

                if dependency_signature.has_request_object:
                    instance.dependency = partial(instance.dependency, request=None)
                    instance.dependency.__signature__ = dependency_signature.new_signature_without_request()  # type: ignore

                    # We need to store the signature without the request to inject it later
                    # because we will create a partial function with the request parameter
                    # and the signature of the partial function will be different
                    self.partialised_dependencies.append(instance)

                self.update_deep_dependencies(dependency_signature)
