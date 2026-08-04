from typing import TYPE_CHECKING

from penta import Penta

if TYPE_CHECKING:
    from unchained.settings.base import UnchainedSettings
    from unchained.states import BaseState


class BaseUnchained(Penta):
    """What the dependencies of an app can count on, whatever builds it."""

    settings: "UnchainedSettings"
    state: "BaseState"
