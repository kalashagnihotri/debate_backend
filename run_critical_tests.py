"""
Comprehensive test runner for critical endpoints.

This script runs all critical endpoint tests and generates
detailed reports for the Online Debate Platform.
"""

import os
import sys
import time
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(message, color=Colors.ENDC):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.ENDC}")


def print_header(title):
    """Print formatted header."""
    print_colored("=" * 60, Colors.HEADER)
    print_colored(f"  {title}", Colors.HEADER + Colors.BOLD)
    print_colored("=" * 60, Colors.HEADER)
    print()


def print_section(title):
    """Print formatted section header."""
    print_colored(f"\n{'-' * 40}", Colors.OKBLUE)
    print_colored(f"  {title}", Colors.OKBLUE + Colors.BOLD)
    print_colored(f"{'-' * 40}", Colors.OKBLUE)


def run_test_suite(test_labels, description):
    """Run a specific test suite and return results."""
    print_section(f"Running {description}")
    
    start_time = time.time()
    
    # Capture output
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineDebatePlatform.test_settings')
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, keepdb=True)
    
    try:
        # Run tests
        failures = test_runner.run_tests(test_labels)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if failures == 0:
            print_colored(f"✓ {description} completed successfully in {duration:.2f}s", Colors.OKGREEN)
            return True, duration, 0
        else:
            print_colored(f"✗ {description} completed with {failures} failures in {duration:.2f}s", Colors.FAIL)
            return False, duration, failures
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print_colored(f"✗ {description} failed with error: {str(e)}", Colors.FAIL)
        return False, duration, 1


def main():
    """Main test runner function."""
    print_header("Online Debate Platform - Critical Endpoint Tests")
    
    # Test suites to run
    test_suites = [
        {
            'labels': ['tests.test_critical_endpoints'],
            'description': 'Critical Authentication & Core Endpoints'
        },
        {
            'labels': ['tests.test_api_validation'],
            'description': 'API Validation & Error Handling'
        },
        {
            'labels': ['tests.test_performance_edge_cases'],
            'description': 'Performance & Edge Cases'
        },
        {
            'labels': ['users.tests'],
            'description': 'User Management Tests'
        },
        {
            'labels': ['debates.tests'],
            'description': 'Debate System Tests'
        },
        {
            'labels': ['notifications.tests'],
            'description': 'Notification System Tests'
        },
        {
            'labels': ['tests.test_core'],
            'description': 'Core System Tests'
        }
    ]
    
    # Results tracking
    total_start_time = time.time()
    results = []
    total_failures = 0
    
    # Run each test suite
    for test_suite in test_suites:
        success, duration, failures = run_test_suite(
            test_suite['labels'],
            test_suite['description']
        )
        
        results.append({
            'description': test_suite['description'],
            'success': success,
            'duration': duration,
            'failures': failures
        })
        
        total_failures += failures
    
    # Print summary
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    print_header("Test Results Summary")
    
    successful_suites = sum(1 for r in results if r['success'])
    total_suites = len(results)
    
    print_colored(f"Total Test Suites: {total_suites}", Colors.OKBLUE)
    print_colored(f"Successful: {successful_suites}", Colors.OKGREEN)
    print_colored(f"Failed: {total_suites - successful_suites}", Colors.FAIL if total_suites - successful_suites > 0 else Colors.OKGREEN)
    print_colored(f"Total Failures: {total_failures}", Colors.FAIL if total_failures > 0 else Colors.OKGREEN)
    print_colored(f"Total Duration: {total_duration:.2f}s", Colors.OKBLUE)
    
    print_section("Detailed Results")
    
    for result in results:
        status_color = Colors.OKGREEN if result['success'] else Colors.FAIL
        status_symbol = "✓" if result['success'] else "✗"
        
        print_colored(
            f"{status_symbol} {result['description']:<40} "
            f"({result['duration']:.2f}s, {result['failures']} failures)",
            status_color
        )
    
    # Performance analysis
    print_section("Performance Analysis")
    
    slowest_suite = max(results, key=lambda x: x['duration'])
    fastest_suite = min(results, key=lambda x: x['duration'])
    
    print_colored(f"Slowest Suite: {slowest_suite['description']} ({slowest_suite['duration']:.2f}s)", Colors.WARNING)
    print_colored(f"Fastest Suite: {fastest_suite['description']} ({fastest_suite['duration']:.2f}s)", Colors.OKGREEN)
    
    # Recommendations
    print_section("Recommendations")
    
    if total_failures == 0:
        print_colored("🎉 All tests passed! Your API endpoints are working correctly.", Colors.OKGREEN)
        print_colored("✓ Authentication system is secure", Colors.OKGREEN)
        print_colored("✓ Data validation is working properly", Colors.OKGREEN)
        print_colored("✓ Error handling is implemented correctly", Colors.OKGREEN)
        print_colored("✓ Performance is within acceptable limits", Colors.OKGREEN)
    else:
        print_colored("⚠️  Some tests failed. Please review the following:", Colors.WARNING)
        
        for result in results:
            if not result['success']:
                print_colored(f"  • Fix issues in: {result['description']}", Colors.FAIL)
    
    # Additional recommendations
    print_colored("\n📋 Additional Testing Recommendations:", Colors.OKBLUE)
    print_colored("  • Run tests regularly during development", Colors.OKCYAN)
    print_colored("  • Add integration tests for new features", Colors.OKCYAN)
    print_colored("  • Monitor test performance over time", Colors.OKCYAN)
    print_colored("  • Consider adding load testing for production", Colors.OKCYAN)
    
    # Exit with appropriate code
    if total_failures > 0:
        print_colored(f"\n❌ Test suite completed with {total_failures} failures", Colors.FAIL)
        sys.exit(1)
    else:
        print_colored(f"\n✅ All tests passed successfully!", Colors.OKGREEN)
        sys.exit(0)


def run_specific_test_category():
    """Run specific category of tests based on command line argument."""
    if len(sys.argv) < 2:
        return False
    
    category = sys.argv[1].lower()
    
    categories = {
        'auth': {
            'labels': ['tests.test_critical_endpoints.CriticalAuthenticationTestCase'],
            'description': 'Authentication Tests Only'
        },
        'validation': {
            'labels': ['tests.test_api_validation'],
            'description': 'Validation Tests Only'
        },
        'performance': {
            'labels': ['tests.test_performance_edge_cases.PerformanceTestCase'],
            'description': 'Performance Tests Only'
        },
        'security': {
            'labels': ['tests.test_critical_endpoints.CriticalSecurityTestCase'],
            'description': 'Security Tests Only'
        },
        'integration': {
            'labels': ['tests.test_critical_endpoints.CriticalIntegrationTestCase'],
            'description': 'Integration Tests Only'
        }
    }
    
    if category in categories:
        print_header(f"Running {categories[category]['description']}")
        success, duration, failures = run_test_suite(
            categories[category]['labels'],
            categories[category]['description']
        )
        
        if failures == 0:
            print_colored(f"✅ {categories[category]['description']} completed successfully!", Colors.OKGREEN)
            sys.exit(0)
        else:
            print_colored(f"❌ {categories[category]['description']} completed with {failures} failures", Colors.FAIL)
            sys.exit(1)
    
    return False


if __name__ == "__main__":
    print_colored("🚀 Starting Critical Endpoint Test Suite...", Colors.OKBLUE)
    
    # Check if specific category requested
    if not run_specific_test_category():
        # Run full test suite
        main()
