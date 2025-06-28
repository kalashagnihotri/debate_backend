#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onlineDebatePlatform.settings")
django.setup()

from django.db import connection


def check_tables():
    cursor = connection.cursor()
    cursor.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'debates_%' ORDER BY tablename;"
    )
    tables = cursor.fetchall()
    print("Debates tables:")
    for table in tables:
        print(f"  {table[0]}")

    # Check columns for each table
    for table in tables:
        table_name = table[0]
        cursor.execute(
            f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position;"
        )
        columns = cursor.fetchall()
        print(f"\nColumns in {table_name}:")
        for col in columns:
            print(f"  {col[0]}")


if __name__ == "__main__":
    check_tables()
