#!/usr/bin/env python
"""
Test script to validate sample data fixtures.

This script checks that all fixture files are properly formatted
and contain valid JSON data.
"""

import json
import os
import sys
from pathlib import Path


def validate_fixture(fixture_path):
    """Validate a single fixture file."""
    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"✓ {fixture_path.name}: {len(data)} records")

        # Basic validation
        if not isinstance(data, list):
            print(f"  ⚠ Warning: Expected list, got {type(data)}")
            return False

        for i, record in enumerate(data):
            if not isinstance(record, dict):
                print(f"  ✗ Error: Record {i} is not a dict")
                return False

            required_fields = ["model", "pk", "fields"]
            for field in required_fields:
                if field not in record:
                    print(f"  ✗ Error: Record {i} missing '{field}'")
                    return False

        return True

    except json.JSONDecodeError as e:
        print(f"✗ {fixture_path.name}: JSON decode error - {e}")
        return False
    except FileNotFoundError:
        print(f"✗ {fixture_path.name}: File not found")
        return False
    except Exception as e:
        print(f"✗ {fixture_path.name}: Unexpected error - {e}")
        return False


def main():
    """Main validation function."""
    fixtures_dir = Path(__file__).parent
    fixture_files = [
        "sample_users.json",
        "sample_topics.json",
        "sample_sessions.json",
        "sample_participation.json",
        "sample_messages.json",
        "sample_votes.json",
        "sample_notifications.json",
    ]

    print("Validating sample data fixtures...")
    print("=" * 40)

    all_valid = True
    for fixture_file in fixture_files:
        fixture_path = fixtures_dir / fixture_file
        if not validate_fixture(fixture_path):
            all_valid = False

    print("=" * 40)
    if all_valid:
        print("✓ All fixtures are valid!")
        return 0
    else:
        print("✗ Some fixtures have errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
