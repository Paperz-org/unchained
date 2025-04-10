import inspect
from unchained.signature.parameter import Parameter


class Signature(inspect.Signature):
    parameters: dict[str, Parameter]

    def __init__(self, parameters=None, return_annotation=inspect.Signature.empty, __validate_parameters__=True):
        if parameters is not None:
            parameters = [Parameter.from_parameter(p) if not isinstance(p, Parameter) else p for p in parameters]
        super().__init__(
            parameters=parameters, return_annotation=return_annotation, __validate_parameters__=__validate_parameters__
        )

    @classmethod
    def from_callable(cls, obj, *, follow_wrapped=True, globals=None, locals=None, eval_str=False):
        sig = super().from_callable(
            obj, follow_wrapped=follow_wrapped, globals=globals, locals=locals, eval_str=eval_str
        )
        parameters = [
            Parameter.from_parameter(p) if not isinstance(p, Parameter) else p for p in sig.parameters.values()
        ]
        return cls(parameters=parameters, return_annotation=sig.return_annotation)
