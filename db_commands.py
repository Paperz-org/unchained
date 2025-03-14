import sys
from unchained import Unchained

# Initialize Django with a virtual app to avoid circular imports
app = Unchained()

# Import Django modules (now safe after initialization)
from django.core.management import execute_from_command_line

def makemigrations():
    """Create new migrations based on models changes."""
    sys.argv = ['manage.py', 'makemigrations']
    execute_from_command_line(sys.argv)

def migrate():
    """Apply migrations to the database."""
    sys.argv = ['manage.py', 'migrate']
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_commands.py [makemigrations|migrate]")
        sys.exit(1)
        
    command = sys.argv[1]
    if command == "makemigrations":
        makemigrations()
    elif command == "migrate":
        migrate()
    else:
        print("Unknown command. Use 'makemigrations' or 'migrate'")
        sys.exit(1) 