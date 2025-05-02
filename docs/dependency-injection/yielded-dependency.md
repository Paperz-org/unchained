## Usage of `yield` in dependency

Unchained supports yielded dependencies. It's very useful when you want to execute code after the injected callable ends it's execution.

```python
from unchained import Depends, Unchained

app = Unchained()

def dependency() -> None:
    print("Dependency")
    yield
    print("Dependency after yield")

@app.get("/")
def endpoint(
    dependency: Annotated[None, Depends(dependency)],
) -> None:
    print("Endpoint")
```

```bash
curl http://localhost:8000/
```

Output:

```bash
Dependency
Endpoint
Dependency after yield
```

## Usage of `yield` in nested dependencies

You can also use `yield` in nested dependencies.

```python
from unchained import Depends, Unchained

app = Unchained()

def dependency_1() -> None:
    print("Dependency 1")
    yield
    print("Dependency 1 after yield")

def dependency_2(dependency: Annotated[None, Depends(dependency_1)]) -> None:
    print("Dependency 2")
    yield
    print("Dependency 2 after yield")

@app.get("/")
def endpoint(
    dependency_2: Annotated[None, Depends(dependency_2)],
) -> None:
    print("Endpoint")
```

```bash
curl http://localhost:8000/
```

Output:

```bash
Dependency 1
Dependency 2
Endpoint
Dependency 1 after yield
Dependency 2 after yield
```

## Usage of `yield` in async dependencies

You can also use `yield` in async dependencies.

```python
from unchained import Depends, Unchained

async def dependency() -> None:
    print("Dependency")
    yield
    print("Dependency after yield")

@app.get("/")
async def endpoint(
    dependency: Annotated[None, Depends(dependency)],
) -> None:
    print("Endpoint")
```

```bash
curl http://localhost:8000/
```

Output:

```bash
Dependency
Endpoint
Dependency after yield
```

## Advanced usage

You should consider yielded dependencies as chained context managers. It allows you to handle complex logic directly in dependency chaining run.


```python
from typing import Annotated
from unchained import Depends, Unchained
from unchained.db import transaction
from unchained.models import BaseModel
from unchained

app = Unchained()

class User(BaseModel):
    name: str = models.CharField()

def atomic_transaction() -> None:
    try:
        with transaction.atomic():
            yield
    except Exception as e:
        print(f"Transaction rolled back: {e}")
    else:
        print("Transaction committed successfully")

@app.post("/create-multiple-users")
def create_multiple_users(_: Annotated[None, Depends(atomic_transaction)]):
    User.objects.create(name="John Doe")
    User.objects.create(name="Jane Doe")
```

Is the equivalent of:

```python
from typing import Annotated
from unchained import Depends, Unchained
from unchained.db import transaction
from unchained.models import BaseModel

app = Unchained()

class User(BaseModel):
    name: str = models.CharField()

@app.post("/create-multiple-users")
def create_multiple_users():
    try:
        with transaction.atomic():
            User.objects.create(name="John Doe")
            User.objects.create(name="Jane Doe")
    except Exception as e:
        print(f"Transaction rolled back: {e}")
    else:
        print("Transaction committed successfully")
```
