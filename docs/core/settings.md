# Settings Management

!!! info "Configuration Management"
    Unchained provides a flexible settings management system that allows you to configure your application using Python classes.

## Basic Usage

=== "Define Settings"
    ```python
    from unchained.settings import UnchainedSettings

    class Settings(UnchainedSettings):
        DEBUG: bool = False
        DATABASE_URL: str
        API_KEY: str | None = None
    ```

=== "Use Settings"
    ```python
    from unchained import Unchained

    app = Unchained(settings=Settings())
    ```

=== "Access Settings"
    ```python
    @app.get("/config")
    def get_config(settings: Settings):
        return {
            "debug": settings.DEBUG,
            "has_api_key": bool(settings.API_KEY)
        }
    ```

## Environment Variables

=== "Load from Environment"
    ```python
    class Settings(UnchainedSettings):
        DEBUG: bool = False
        DATABASE_URL: str
        API_KEY: str | None = None

        class Config:
            env_prefix = "APP_"  # APP_DEBUG, APP_DATABASE_URL, etc.
    ```

=== "Custom Environment Names"
    ```python
    class Settings(UnchainedSettings):
        DEBUG: bool = False
        DATABASE_URL: str
        API_KEY: str | None = None

        class Config:
            env_prefix = "APP_"
            env_nested_delimiter = "__"
            # APP_DATABASE__URL, APP_DATABASE__PORT
    ```

## Type Safety

=== "Type Validation"
    ```python
    class Settings(UnchainedSettings):
        PORT: int = 8000
        TIMEOUT: float = 30.0
        ALLOWED_HOSTS: list[str] = ["localhost"]
        DATABASE: dict[str, str] = {
            "url": "postgres://localhost",
            "port": "5432"
        }
    ```

=== "Custom Types"
    ```python
    from typing import Literal
    from pydantic import HttpUrl

    class Settings(UnchainedSettings):
        ENVIRONMENT: Literal["development", "production"] = "development"
        API_URL: HttpUrl
        LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    ```

## Best Practices

1. **Type Safety**: Always use type hints for settings
2. **Default Values**: Provide sensible defaults for optional settings
3. **Environment Variables**: Use environment variables for sensitive data
4. **Validation**: Use Pydantic's validation features

## Common Patterns

### Database Configuration

```python
class DatabaseSettings(UnchainedSettings):
    URL: str
    PORT: int = 5432
    USER: str
    PASSWORD: str
    NAME: str

    class Config:
        env_prefix = "DB_"
```

### API Configuration

```python
class APISettings(UnchainedSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_HOSTS: list[str] = ["*"]

    class Config:
        env_prefix = "API_"
```

### Feature Flags

```python
class FeatureSettings(UnchainedSettings):
    ENABLE_NEW_UI: bool = False
    ENABLE_EXPERIMENTAL: bool = False
    MAX_CONNECTIONS: int = 100
    CACHE_TIMEOUT: int = 300

    class Config:
        env_prefix = "FEATURE_"
```

## Nested Settings

```python
class DatabaseSettings(UnchainedSettings):
    URL: str
    PORT: int = 5432

class CacheSettings(UnchainedSettings):
    URL: str
    TIMEOUT: int = 300

class Settings(UnchainedSettings):
    DEBUG: bool = False
    DATABASE: DatabaseSettings
    CACHE: CacheSettings

    class Config:
        env_prefix = "APP_"
        env_nested_delimiter = "__"
        # APP_DATABASE__URL, APP_CACHE__TIMEOUT
```

## Validation

```python
from pydantic import validator

class Settings(UnchainedSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    @validator("PORT")
    def validate_port(cls, v):
        if v < 1024:
            raise ValueError("Port must be greater than 1024")
        return v

    @validator("HOST")
    def validate_host(cls, v):
        if v not in ["0.0.0.0", "127.0.0.1", "localhost"]:
            raise ValueError("Invalid host")
        return v
``` 