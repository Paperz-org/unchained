from typing import Any, Callable, get_args
from fast_depends.dependencies import model
from unchained.signature import Signature

from unchained.signature.transformers import create_signature_with_auto_dependencies


class Depends(model.Depends):
    def __init__(
        self,
        dependency: Callable[..., Any],
        *,
        use_cache: bool = True,
        cast: bool = True,
    ) -> None:
        super().__init__(dependency, use_cache=use_cache, cast=cast)
        self._update_dependency_signature()

    def _update_dependency_signature(self):
        signature = Signature.from_callable(self.dependency)
        # Here we inject the param name and the annotation type to CustomDependencies
        for param in signature.parameters.values():
            if param.is_custom_depends:
                type_, instance = get_args(param.annotation)
                # Add the type to the CustomField
                setattr(instance, "param_name", param.name)
                setattr(instance, "annotation_type", type_)
                setattr(instance, "default", param.default)

        # This transform the signature of the dependency to add the auto dependencies (request, settings, app, state)
        self.dependency.__signature__ = create_signature_with_auto_dependencies(signature)
