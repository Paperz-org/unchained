---
title: App Object Dependency
---

# Injecting the App Object

You can inject the `Unchained` application instance itself by type-hinting a parameter with `unchained.Unchained` in your route handlers or dependencies.

This allows dependencies or routes to access application-level configuration, state, or methods if needed.

```python
from unchained import Unchained, Request
from typing import Annotated
from unchained import Depends

# Assume app is configured with some settings
app = Unchained()
app.config["SERVICE_URL"] = "http://example.com/api"
app.state.some_shared_resource = object() # Example state

@app.get("/app-config")
def get_app_config_route(app_instance: Unchained):
    return {
        "service_url": app_instance.config.get("SERVICE_URL"),
        "has_resource": hasattr(app_instance.state, "some_shared_resource"),
    }

def get_service_url_from_app(app_instance: Unchained) -> str:
    url = app_instance.config.get("SERVICE_URL", "default_url")
    print(f"Retrieved service URL: {url}")
    return url

@app.get("/service-endpoint")
def route_using_app_dep(
    service_url: Annotated[str, Depends(get_service_url_from_app)]
):
    return {"endpoint": f"{service_url}/data"}

```

!!! warning "Use Judiciously"
    Injecting the `App` object should be done judiciously. Often, it's better to inject specific configuration values or services rather than the entire application instance to maintain better separation of concerns and improve testability. 