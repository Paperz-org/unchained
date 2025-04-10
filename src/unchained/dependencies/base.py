from typing import Annotated

from django.conf import Settings
from django.http import HttpRequest as DjangoHttpRequest
from fast_depends.dependencies import Depends

from unchained.base import BaseUnchained
from unchained.states import BaseState
from unchained.unchained import app, request


def _get_app():
    return app.get()


def _get_request():
    return request.get()


AppDependency = Annotated[BaseUnchained, Depends(_get_app)]
RequestDependency = Annotated[DjangoHttpRequest, Depends(_get_request)]


def _get_settings(app: AppDependency) -> Settings:
    return app.settings


def _get_state(app: AppDependency) -> BaseState:
    return app.state


SettingsDependency = Annotated[Settings, Depends(_get_settings)]
StateDependency = Annotated[BaseState, Depends(_get_state)]
