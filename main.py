import inspect
from typing import Annotated

from fast_depends import Depends

from models import User
from unchained import Unchained

# Create API instance and set up Django
app = Unchained()


def dependency() -> str:
    return "my dependency"


def toto(func):
    signature = inspect.signature(func)

    def wrapper(*args, **kwargs):
        # Filter out parameters with Annotated type
        filtered_params = {}
        for name, param in signature.parameters.items():
            if param.annotation is not inspect.Parameter.empty:
                if getattr(param.annotation, "__origin__", None) is not Annotated:
                    filtered_params[name] = param
            else:
                filtered_params[name] = param

        # Create new signature without Annotated parameters
        new_signature = signature.replace(parameters=filtered_params)

        # Apply the new signature to the wrapped function
        wrapper.__signature__ = new_signature

        return func(*args, **kwargs)

    return wrapper


# Define your endpoints


@app.get("/hello")
def hello(request, a: Annotated[str, Depends(dependency)]):
    return {"message": f"Hello {a}!"}


@app.get("/add/{a}/{b}")
def add(request, a: int, b: int, c: Annotated[str, Depends(dependency)]):
    return {"result": a + b, "c": c}


app.crud(User)
