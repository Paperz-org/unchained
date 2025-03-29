from typing import Optional

from typer import Argument, Typer, echo

from unchained.cli.utils import get_app_path_arg, load_app_module

app = Typer(help="Database management commands for schema migrations and maintenance")


@app.command(name="create")
def makemigration(
    app_path: Optional[str] = Argument(None, help="Path to the app module and instance in the format module:instance"),
    name: Optional[str] = Argument(None, help="Name for the migration file (optional)"),
):
    """
    Create new database migrations based on model changes.

    Detects changes in your models and generates migration files to apply
    those changes to your database schema. If a name is provided, it will
    be used as a prefix for the migration file.
    """
    from unchained.cli.utils import get_app_path_arg, load_app_module

    app_path_str = get_app_path_arg(app_path)

    # Lazy import django
    from django.conf import settings

    # Load app from the specified path
    _, _ = load_app_module(app_path_str)

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
        return

    from django.core.management import call_command

    args = [name] if name else []
    call_command("makemigrations", *args)


@app.command(name="apply")
def migrate(
    app_path: Optional[str] = Argument(None, help="Path to the app module and instance in the format module:instance"),
    app_label: Optional[str] = Argument(
        None, help="App label to migrate (optional, migrates all apps if not specified)"
    ),
    migration_name: Optional[str] = Argument(None, help="Specific migration to apply (optional, requires app_label)"),
):
    """
    Apply migrations to sync the database with your models.

    Updates your database schema to match your current models and previous
    migrations. Can target specific apps or migrations if needed.

    Examples:
      unchained migrations apply                   # Apply all pending migrations
      unchained migrations apply myapp             # Apply migrations for 'myapp' only
      unchained migrations apply myapp 0002        # Apply specific migration
    """
    app_path_str = get_app_path_arg(app_path)

    from django.conf import settings

    # Load app from the specified path
    _, _ = load_app_module(app_path_str)

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
        return

    from django.core.management import call_command

    args = []
    if app_label:
        args.append(app_label)
        if migration_name:
            args.append(migration_name)

    call_command("migrate", *args)


@app.command(name="show")
def showmigration(
    app_path: Optional[str] = Argument(None, help="Path to the app module and instance in the format module:instance"),
    app_label: Optional[str] = Argument(
        None, help="App label to show migrations for (optional, shows all apps if not specified)"
    ),
):
    """
    Show the status of all database migrations.

    Displays which migrations have been applied and which are pending,
    helping you track the state of your database schema. Can be filtered
    to show information for a specific app.
    """
    app_path_str = get_app_path_arg(app_path)

    from django.conf import settings

    # Load app from the specified path
    _, _ = load_app_module(app_path_str)

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
        return

    from django.core.management import call_command

    args = [app_label] if app_label else []
    call_command("showmigrations", *args)
