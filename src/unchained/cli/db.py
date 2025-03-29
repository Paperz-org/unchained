from typing import Optional

import typer

from unchained.cli.utils import get_app_path_arg, load_app_module

app = typer.Typer(help="Database management commands")


@app.command(name="make")
def makemigration(
    app_path: Optional[str] = typer.Argument(None, help="Path to the app module and instance (module:instance)"),
    name: Optional[str] = None,
):
    from unchained.cli.utils import get_app_path_arg, load_app_module

    """Make migrations for database changes"""
    app_path_str = get_app_path_arg(app_path)

    # Lazy import django
    from django.conf import settings

    # Load app from the specified path
    _, _ = load_app_module(app_path_str)

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        typer.echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
        return

    from django.core.management import call_command

    args = [name] if name else []
    call_command("makemigrations", *args)


@app.command(name="apply")
def migrate(
    app_path: Optional[str] = typer.Argument(None, help="Path to the app module and instance (module:instance)"),
    app_label: Optional[str] = None,
    migration_name: Optional[str] = None,
):
    """Apply migrations to the database"""
    app_path_str = get_app_path_arg(app_path)

    from django.conf import settings

    # Load app from the specified path
    _, _ = load_app_module(app_path_str)

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        typer.echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
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
    app_path: Optional[str] = typer.Argument(None, help="Path to the app module and instance (module:instance)"),
    app_label: Optional[str] = None,
):
    """Show migration status"""
    app_path_str = get_app_path_arg(app_path)

    from django.conf import settings

    # Load app from the specified path
    _, _ = load_app_module(app_path_str)

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        typer.echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
        return

    from django.core.management import call_command

    args = [app_label] if app_label else []
    call_command("showmigrations", *args)
