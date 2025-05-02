import asyncio

import orjson

from unchained import Unchained
from unchained.ninja.renderers import BaseRenderer


class MyRenderer(BaseRenderer):
    media_type = "text/plain"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


app = Unchained(renderer=MyRenderer())


@app.get("/")
async def hello_world() -> str:
    await asyncio.sleep(0.01)
    return "Hello, world!"
