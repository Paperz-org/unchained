from typing import Callable, AsyncContextManager
from contextlib import AsyncExitStack
import inspect



class Lifespan:
    def __init__(self, app, user_func: Callable | None = None):
        self.app = app
        self.user_func = user_func
        self.exit_stack = AsyncExitStack()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan" and self.user_func:
            try:
                while True:
                    message = await receive()
                    if message["type"] == "lifespan.startup":
                        # Create the context manager with the lifespan parameter (app or None)
                        cm = self.user_func(**self._lifespan_parameter())
                       
                        await self.exit_stack.enter_async_context(cm) 
                        await send({"type": "lifespan.startup.complete"})
        
                    elif message["type"] == "lifespan.shutdown":
                        # Exit all context managers
                        await self.exit_stack.aclose()
                        await send({"type": "lifespan.shutdown.complete"})
                        break
            except Exception as e:
                # Handle errors during startup/shutdown
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.failed", "message": str(e)})
                else:
                    await send({"type": "lifespan.shutdown.failed", "message": str(e)})
        else:
            await self.app(scope, receive, send)
    
    def _lifespan_parameter(self):
        """
        Check if the lifespan function has a parameter and if it is a Unchained app.
        If it is, return the parameter name and annotation.
        If it is not, return an empty dictionary.

        So we can use this syntax: user_func(**self._lifespan_parameter())
        """
        from unchained.unchained import Unchained

        signature = inspect.signature(self.user_func)
        signature_length = len(signature.parameters)

        if signature_length > 1:
            raise ValueError("Lifespan function must have exactly one or no parameters")
        
        if signature_length == 0:
            return {}
        
        for param in signature.parameters.values():
            if param.annotation and not issubclass(param.annotation, Unchained):
                raise ValueError("The only parameter of the lifespan function must be a Unchained app")
            return {param.name: self.app}