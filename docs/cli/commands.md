# Unchained CLI Commands

The Unchained framework provides a command-line interface for various tasks like running development servers, managing database migrations, creating superusers, and more.

## Command Structure

All commands use the `unchained` prefix and follow this pattern:

```
unchained [command] [subcommand] [options]
```

Many commands accept an `app_path` argument which specifies the location of your application in the format `module:instance`. If not provided, the CLI will attempt to automatically detect your app from:

1. `UNCHAINED_APP_PATH` environment variable
2. `pyproject.toml` file with `[tool.unchained]` section
3. Common app patterns in the current directory

## Main Commands

### `unchained start`

Run the development server using uvicorn.

```
unchained start [app_path] [options]
```

**Options:**
- `--host`, `-h`: Host to bind the server to (default: 127.0.0.1)
- `--port`, `-p`: Port to bind the server to (default: 8000)
- `--reload/--no-reload`: Enable/disable auto-reload for development (default: enabled)

**Example:**
```
unchained start
unchained start --port 8080
unchained start myapp:app --host 0.0.0.0 --no-reload
```

### `unchained collectstatic`

Collect static files for production deployment.

```
unchained collectstatic
```

### `unchained version`

Show the current version of Unchained.

```
unchained version
```

### `unchained createsuperuser`

Create a superuser account for the admin interface.

```
unchained createsuperuser [app_path] [username] [email] [noinput]
```

**Examples:**
```
unchained createsuperuser
```

### `unchained shell`

Start the Django shell with your application context loaded.

```
unchained shell [app_path]
```

## Database Migration Commands

Unchained provides a set of commands for managing database migrations under the `migrations` namespace.

### `unchained migrations create`

Create new database migrations based on model changes.

```
unchained migrations create 
```


### `unchained migrations apply`

Apply migrations to sync the database with your models.

```
unchained migrations apply [app_path] [app_label] [migration_name]
```

**Arguments:**
- `app_label`: App label to migrate (optional, migrates all apps if not specified)
- `migration_name`: Specific migration to apply (optional, requires app_label)

**Examples:**
```
unchained migrations apply                   # Apply all pending migrations
unchained migrations apply myapp             # Apply migrations for 'myapp' only
unchained migrations apply myapp 0002        # Apply specific migration
```

### `unchained migrations show`

Show the status of all database migrations.

```
unchained migrations show [app_path] [app_label]
```

**Arguments:**
- `app_label`: App label to show migrations for (optional, shows all apps if not specified)

**Examples:**
```
unchained migrations show
unchained migrations show myapp
```
