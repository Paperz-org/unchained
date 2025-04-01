import asyncio
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Dict

from ezq import EZQEvent as Event  # type: ignore
from ezq import on_event, publish_event  # type: ignore
from ezq.helper import clean  # type: ignore

from unchained.dependencies.header import BaseCustom  # type: ignore

# Global registry to store task functions by ID
_TASK_REGISTRY: Dict[str, Callable] = {}


class BackgroundTask(BaseCustom):
    def __init__(self, *tasks: Any, **kwargs: Any) -> None:
        super().__init__()
        for task in tasks:
            if task.__name__ not in _TASK_REGISTRY:
                _TASK_REGISTRY[task.__name__] = task
            else:
                raise ValueError(f"Task with name {task.__name__} already registered")
        self._tasks = tasks
        print("BackgroundTask", _TASK_REGISTRY)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._args = args
        self._kwargs = kwargs
        return self

    async def start(self) -> None:
        print("start")
        await clean()
        for task in self._tasks:
            await publish_event(
                BackgroundTaskEvent(
                    task_name=task.__name__,
                    args=self._args,
                    kwargs=self._kwargs,
                )
            )


@dataclass
class BackgroundTaskEvent(Event):
    task_name: str
    args: tuple[Any, ...] | None = None
    kwargs: dict[str, Any] | None = None


@on_event
async def background_task(event: BackgroundTaskEvent):
    task = _TASK_REGISTRY.get(event.task_name)
    args = event.args or ()
    kwargs = event.kwargs or {}
    print("background_task", task)
    if task is not None:
        task(*args, **kwargs)

    # if task is None:
    #     raise ValueError(f"Task with ID {event.task_id} not found in registry")

    # args = event.args or ()
    # kwargs = event.kwargs or {}
    # task(*args, **kwargs)
