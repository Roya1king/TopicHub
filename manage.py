#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learn.settings")
    from django.core.management import execute_from_command_line

    # ✅ Set up Django
    import django
    django.setup()

    # ✅ Now safe to use ORM
    from django.contrib.auth import get_user_model
    from django.db.utils import OperationalError

    try:
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            print("✅ Superuser created: admin / admin")
    except OperationalError:
        print("⚠️  Database not ready, skipping superuser creation")

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
