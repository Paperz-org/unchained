from unchained.dependencies.auto import AppDependency, RequestDependency, SettingsDependency, StateDependency
from unchained.signature.signature import Signature
from unchained.signature.parameter import Parameter


def create_signature_without_annotated(signature: Signature) -> Signature:
    """
    Create a new instance of the signature without the annotated parameters.

    We need this for Django Ninja to parse the parameters correctly.
    """
    parameters = []
    for _, param in signature.parameters.items():
        if param.is_request:
            parameters.append(Parameter(name=param.name, kind=param.kind, default=param.default))
        elif param.is_annotated:
            continue
        parameters.append(param)

    return Signature(parameters)


def create_signature_with_auto_dependencies(signature: Signature) -> Signature:
    """
    Create a new instance of the signature with the auto dependencies (request, settings, app, state).
    """
    parameters = []

    for _, param in signature.parameters.items():
        if param.is_app:
            parameters.append(
                Parameter(name=param.name, kind=param.kind, default=param.default, annotation=AppDependency)
            )
        elif param.is_request:
            parameters.append(
                Parameter(name=param.name, kind=param.kind, default=param.default, annotation=RequestDependency)
            )
        elif param.is_settings:
            parameters.append(
                Parameter(name=param.name, kind=param.kind, default=param.default, annotation=SettingsDependency)
            )
        elif param.is_state:
            parameters.append(
                Parameter(name=param.name, kind=param.kind, default=param.default, annotation=StateDependency)
            )
        else:
            parameters.append(param)

    return Signature(parameters)
