# Response Handling

!!! note "Django Ninja Integration"
    Unchained uses [Django Ninja](https://django-ninja.dev/) for response handling, providing automatic serialization of Python objects to JSON and other formats.

## Basic Response Types

Django Ninja automatically converts Python data types to appropriate HTTP responses:

=== "Dictionary Response"
    ```python
    from unchained import Unchained
    
    app = Unchained()
    
    @app.get("/simple")
    def simple_response():
        return {"message": "Hello, World!"}  # Returns JSON: {"message": "Hello, World!"}
    ```

=== "List Response"
    ```python
    from unchained import Unchained
    
    app = Unchained()
    
    @app.get("/list")
    def list_response():
        return [1, 2, 3]  # Returns JSON array: [1, 2, 3]
    ```

=== "Text Response"
    ```python
    from unchained import Unchained
    
    app = Unchained()
    
    @app.get("/text")
    def text_response():
        return "Hello, World!"  # Returns text: Hello, World!
    ```

## Response Content Types

| Python Type | HTTP Response | Content-Type | Documentation |
| ----------- | ------------- | ------------ | ------------- |
| `dict`, `list` | JSON object/array | `application/json` | [Django Ninja Response](https://django-ninja.dev/guides/response/) |
| `str` | Text content | `text/plain` | [Django Ninja Response](https://django-ninja.dev/guides/response/) |
| Django model | JSON object | `application/json` | [Django Models](https://docs.djangoproject.com/en/stable/topics/db/models/) |
| Pydantic model | JSON object | `application/json` | [Django Ninja Schema](https://django-ninja.dev/guides/input/schema/) |

!!! tip "Schema Validation"
    Django Ninja can validate responses against schemas defined using [Pydantic models](https://docs.pydantic.dev/) for more robust API design. See the [Django Ninja schema documentation](https://django-ninja.dev/guides/response/).

## Further Reading

For more details on response handling and features:

- :material-api: [Django Ninja Response Documentation](https://django-ninja.dev/guides/response/)
- :material-format-list-bulleted: [Django QuerySet API](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- :fontawesome-solid-globe: [Django Request/Response Objects](https://docs.djangoproject.com/en/stable/ref/request-response/) 