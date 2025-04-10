from typing import Annotated
from unchained.request import Request
from unchained.base import BaseUnchained
from unchained.settings.base import UnchainedSettings
from unchained.states import BaseState
from unchained import context
from fast_depends.dependencies import model


def _get_app():
    return context.app.get()


AppDependency = Annotated[BaseUnchained, model.Depends(_get_app)]


def _get_request():
    return context.request.get()


def _get_settings(app: AppDependency) -> UnchainedSettings:
    return app.settings


def _get_state(app: AppDependency) -> BaseState:
    return app.state


RequestDependency = Annotated[Request, model.Depends(_get_request, use_cache=False)]
SettingsDependency = Annotated[UnchainedSettings, model.Depends(_get_settings)]
StateDependency = Annotated[BaseState, model.Depends(_get_state)]
