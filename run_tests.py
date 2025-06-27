#!/usr/bin/env python
"""
Test runner script for the Online Debate Platform.

This script provides an easy way to run all tests with proper
configuration and coverage reporting.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'onlineDebatePlatform.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run all tests
    failures = test_runner.run_tests([
        "users.tests",
        "debates.tests", 
        "notifications.tests",
        "tests"
    ])
    
    if failures:
        sys.exit(bool(failures))
