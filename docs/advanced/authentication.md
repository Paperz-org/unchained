# Authentication

!!! danger "Experimental Feature"
    Authentication in Unchained is not stable and may change significantly in future versions. The current implementation is minimal and relies entirely on external systems.

!!! warning "External Integration"
    Unchained does not implement custom authentication mechanisms. Instead, it leverages the authentication systems provided by [Django](https://docs.djangoproject.com/en/stable/topics/auth/) and [Django Ninja](https://django-ninja.dev/guides/authentication/).

## Available Authentication Options

When implementing authentication in your Unchained application, you have several options:

=== "Django Authentication"
    Django provides a robust authentication system that can be used with Unchained:
    
    - [User authentication](https://docs.djangoproject.com/en/stable/topics/auth/default/)
    - [Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions-and-authorization)
    - [Groups](https://docs.djangoproject.com/en/stable/topics/auth/default/#groups)
    - [Password validation](https://docs.djangoproject.com/en/stable/topics/auth/passwords/)

=== "Django Ninja Authentication"
    Django Ninja offers several authentication mechanisms:
    
    - [API Key authentication](https://django-ninja.dev/guides/authentication/)
    - [HTTP Bearer](https://django-ninja.dev/guides/authentication/)
    - [HTTP Basic authentication](https://django-ninja.dev/guides/authentication/)
    - [Custom authentication schemes](https://django-ninja.dev/guides/authentication/)

## Implementation Guidelines

When adding authentication to your Unchained application:

1. Configure Django's authentication middleware (included by default)
2. Choose an authentication strategy based on your requirements
3. Implement the appropriate authentication handlers
4. Apply authentication to your routes

!!! example "Django Ninja Example"
    ```python
    from ninja.security import HttpBearer
    from unchained import Unchained
    
    class AuthBearer(HttpBearer):
        def authenticate(self, request, token):
            if token == "supersecret":
                return token
            # Return None for failed authentication
    
    app = Unchained()
    
    @app.get("/protected", auth=AuthBearer())
    def protected_endpoint(request):
        return {"message": "This is a protected endpoint"}
    ```

## Stability Warning

!!! bug "Known Issues"
    Authentication integration with dependency injection is still in development. You may encounter unexpected behavior when using authenticated routes with complex dependency chains.

## Further Reading

For comprehensive documentation on authentication:

- :material-account-key: [Django Authentication System](https://docs.djangoproject.com/en/stable/topics/auth/)
- :material-shield-lock: [Django Ninja Authentication](https://django-ninja.dev/guides/authentication/)
- :material-security: [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
