import asyncio
from typing import Generic, TypeVar

from fastapi import FastAPI
from pydantic import BaseModel

T = TypeVar("T")

app = FastAPI()



class HelloWorldResponse(BaseModel, Generic[T]):
    message: str

class ErrorResponse(BaseModel, Generic[T]):
    message: str


@app.get("/api/")
async def root() -> HelloWorldResponse[200] | ErrorResponse[400]:
    await asyncio.sleep(0.01)
    return HelloWorldResponse(message="Hello, world!")
