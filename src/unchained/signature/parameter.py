from typing import get_args

from unchained.base import BaseUnchained

from unchained.settings.base import UnchainedSettings
from unchained.states import BaseState
from penta.signature.parser import Parameter


class Parameter(Parameter):
    """
    A custom parameter class that extends inspect.Parameter to add Unchained-specific functionality.
    """

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
    def is_state(self) -> bool:
        if self.is_annotated:
            _, instance = get_args(self.annotation)
            return isinstance(instance, BaseState)
        return issubclass(self.annotation, BaseState)
