from ezq import EZQEndEvent, consumer, publish_event  # type: ignore

from unchained.dependencies.background_tasks import *  # type: ignore


class TaskWorkerManager:
    """Manages a pool of worker threads for background tasks"""

    async def start(self):
        await consumer()

    async def shutdown(self):
        await publish_event(EZQEndEvent())
