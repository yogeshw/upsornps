#!/usr/bin/env python3
"""
Main test runner for UPS vs NPS Calculator test suite.
Runs both unit tests (comparing Python vs JavaScript) and integration tests.

Copyright (C) 2025 Yogesh Wadadekar
This program is licensed under GPL v3. See LICENSE file for details.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --help       # Show help
"""

import sys
import argparse
import subprocess
import os
from datetime import datetime

def run_unit_tests():
    """Run unit tests comparing Python and JavaScript implementations"""
    print("🧪 Running Unit Tests (Python vs JavaScript comparison)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, 'test_calculator.py'
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run unit tests: {e}")
        return False

def run_integration_tests():
    """Run integration tests for calculator workflows"""
    print("🔄 Running Integration Tests (Complete workflows)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, 'test_calculator_integration.py'
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run integration tests: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking Dependencies...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 6):
        issues.append("Python 3.6 or higher is required")
    
    # Check if Node.js is available
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(f"  ✅ Node.js: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("Node.js is not available")
    
    # Check if required files exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        'upsnpscalculator.py',
        'upsnpscalculator.js',
        'test_calculator.py',
        'test_calculator_integration.py'
    ]
    
    for file in required_files:
        file_path = os.path.join(script_dir, file)
        if os.path.exists(file_path):
            print(f"  ✅ {file}")
        else:
            issues.append(f"Required file missing: {file}")
    
    if issues:
        print("\n❌ Dependency Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("  ✅ All dependencies satisfied")
    return True

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description="Run UPS vs NPS Calculator test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py              # Run all tests
  python run_tests.py --unit       # Run only unit tests  
  python run_tests.py --integration # Run only integration tests
        """
    )
    
    parser.add_argument('--unit', action='store_true',
                       help='Run only unit tests (Python vs JavaScript comparison)')
    parser.add_argument('--integration', action='store_true',
                       help='Run only integration tests (workflow validation)')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip dependency checks')
    
    args = parser.parse_args()
    
    print("🚀 UPS vs NPS Calculator Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check dependencies unless skipped
    if not args.skip_deps:
        if not check_dependencies():
            sys.exit(1)
        print()
    
    # Determine which tests to run
    run_unit = not args.integration  # Run unit tests unless --integration only
    run_integration = not args.unit  # Run integration tests unless --unit only
    
    if args.unit:
        run_unit = True
        run_integration = False
    elif args.integration:
        run_unit = False
        run_integration = True
    
    results = []
    
    # Run unit tests
    if run_unit:
        unit_success = run_unit_tests()
        results.append(("Unit Tests", unit_success))
        print()
    
    # Run integration tests
    if run_integration:
        integration_success = run_integration_tests()
        results.append(("Integration Tests", integration_success))
        print()
    
    # Print overall summary
    print("📊 OVERALL TEST SUMMARY")
    print("=" * 60)
    
    total_test_suites = len(results)
    passed_suites = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTest Suites: {passed_suites}/{total_test_suites} passed")
    print(f"Overall Status: {'✅ SUCCESS' if passed_suites == total_test_suites else '❌ FAILED'}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    sys.exit(0 if passed_suites == total_test_suites else 1)

if __name__ == "__main__":
    main()