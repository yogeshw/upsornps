#!/usr/bin/env python3
"""
Test suite for UPS vs NPS Calculator
Compares Python and JavaScript implementations to ensure they produce identical outputs.

Copyright (C) 2025 Yogesh Wadadekar
This program is licensed under GPL v3. See LICENSE file for details.
"""

import json
import subprocess
import sys
import os
from typing import Dict, List, Tuple, Any, Optional
import math

# Import the Python calculator functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from upsnpscalculator import (
    calculate_final_salary,
    calculate_ups_monthly_pension,
    calculate_ups_lump_sum,
    calculate_nps_corpus,
    calculate_nps_monthly_pension,
    format_amount
)

class TestResult:
    """Class to store test results and comparisons"""
    def __init__(self, test_name: str, python_result: Any, js_result: Any, 
                 passed: bool, error_msg: str = ""):
        self.test_name = test_name
        self.python_result = python_result
        self.js_result = js_result
        self.passed = passed
        self.error_msg = error_msg

class CalculatorTester:
    """Main test class for comparing Python and JavaScript calculator implementations"""
    
    def __init__(self, tolerance: float = 1e-6):
        self.tolerance = tolerance
        self.test_results: List[TestResult] = []
        self.js_test_script = self._create_js_test_script()
    
    def _create_js_test_script(self) -> str:
        """Create a JavaScript test script that can be executed by Node.js"""
        return """
// Load the calculator functions
const fs = require('fs');
const calcCode = fs.readFileSync('upsnpscalculator.js', 'utf8');

// Remove main execution to avoid console output
const lines = calcCode.split('\\n');
const cleanLines = [];
let skipMainExecution = false;

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.includes('// For Node.js environments, only run if this is the entry point')) {
        skipMainExecution = true;
    }
    if (!skipMainExecution) {
        cleanLines.push(line);
    }
}

const cleanCode = cleanLines.join('\\n');

// Execute the calculator code in the global context
eval(cleanCode);

// Test runner function
function runTest(functionName, args) {
    try {
        let result;
        switch(functionName) {
            case 'calculateFinalSalary':
                result = calculateFinalSalary(args[0], args[1], args[2]);
                break;
            case 'calculateUPSMonthlyPension':
                result = calculateUPSMonthlyPension(args[0], args[1]);
                break;
            case 'calculateUPSLumpSum':
                result = calculateUPSLumpSum(args[0], args[1]);
                break;
            case 'calculateNPSCorpus':
                result = calculateNPSCorpus(args[0], args[1], args[2], args[3], args[4], args[5] || 0.0);
                break;
            case 'calculateNPSMonthlyPension':
                result = calculateNPSMonthlyPension(args[0], args[1]);
                break;
            case 'formatAmount':
                result = formatAmount(args[0]);
                break;
            default:
                throw new Error(`Unknown function: ${functionName}`);
        }
        return { success: true, result: result };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Read test input from stdin
const input = process.argv[2];
if (input) {
    const testData = JSON.parse(input);
    const result = runTest(testData.function, testData.args);
    console.log(JSON.stringify(result));
} else {
    console.log(JSON.stringify({ success: false, error: "No test data provided" }));
}
"""
    
    def _run_js_function(self, function_name: str, args: List[Any]) -> Tuple[bool, Any]:
        """Execute a JavaScript function with given arguments"""
        try:
            # Write the JS test script to a temporary file
            js_script_path = '/tmp/js_test_runner.js'
            with open(js_script_path, 'w') as f:
                f.write(self.js_test_script)
            
            # Prepare test data
            test_data = {
                'function': function_name,
                'args': args
            }
            
            # Run the JavaScript test
            result = subprocess.run([
                'node', js_script_path, json.dumps(test_data)
            ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
            
            if result.returncode != 0:
                return False, f"JS execution error: {result.stderr}"
            
            # Parse the result
            try:
                js_result = json.loads(result.stdout.strip())
                if js_result['success']:
                    return True, js_result['result']
                else:
                    return False, js_result['error']
            except json.JSONDecodeError as e:
                return False, f"JSON parse error: {e}, output: {result.stdout}"
                
        except Exception as e:
            return False, f"Exception running JS: {e}"
    
    def _compare_results(self, python_result: Any, js_result: Any) -> Tuple[bool, str]:
        """Compare Python and JavaScript results with appropriate tolerance"""
        if isinstance(python_result, (int, float)) and isinstance(js_result, (int, float)):
            if math.isnan(python_result) and math.isnan(js_result):
                return True, ""
            if math.isinf(python_result) and math.isinf(js_result):
                return True, ""
            if abs(python_result - js_result) <= self.tolerance:
                return True, ""
            else:
                return False, f"Numerical difference: Python={python_result}, JS={js_result}, diff={abs(python_result - js_result)}"
        elif isinstance(python_result, str) and isinstance(js_result, str):
            if python_result == js_result:
                return True, ""
            else:
                return False, f"String difference: Python='{python_result}', JS='{js_result}'"
        else:
            if python_result == js_result:
                return True, ""
            else:
                return False, f"Type/value difference: Python={python_result} ({type(python_result)}), JS={js_result} ({type(js_result)})"
    
    def test_function(self, test_name: str, python_func, js_func_name: str, 
                     test_cases: List[Tuple[str, List[Any]]]) -> None:
        """Test a specific function with multiple test cases"""
        print(f"\n=== Testing {test_name} ===")
        
        for case_name, args in test_cases:
            try:
                # Run Python function
                python_result = python_func(*args)
                
                # Run JavaScript function
                js_success, js_result = self._run_js_function(js_func_name, args)
                
                if not js_success:
                    test_result = TestResult(
                        f"{test_name} - {case_name}",
                        python_result,
                        None,
                        False,
                        f"JS execution failed: {js_result}"
                    )
                    self.test_results.append(test_result)
                    print(f"  ❌ {case_name}: JS execution failed - {js_result}")
                    continue
                
                # Compare results
                passed, error_msg = self._compare_results(python_result, js_result)
                
                test_result = TestResult(
                    f"{test_name} - {case_name}",
                    python_result,
                    js_result,
                    passed,
                    error_msg
                )
                self.test_results.append(test_result)
                
                if passed:
                    print(f"  ✅ {case_name}: Python={python_result}, JS={js_result}")
                else:
                    print(f"  ❌ {case_name}: {error_msg}")
                    
            except Exception as e:
                test_result = TestResult(
                    f"{test_name} - {case_name}",
                    None,
                    None,
                    False,
                    f"Python execution failed: {e}"
                )
                self.test_results.append(test_result)
                print(f"  ❌ {case_name}: Python execution failed - {e}")
    
    def run_all_tests(self) -> None:
        """Run all tests for calculator functions"""
        print("UPS vs NPS Calculator Test Suite")
        print("=" * 50)
        print("Comparing Python and JavaScript implementations...")
        
        # Test calculate_final_salary
        self.test_function(
            "calculate_final_salary",
            calculate_final_salary,
            "calculateFinalSalary",
            [
                ("regular_case", [3600000, 0.07, 7]),
                ("zero_growth", [3600000, 0.0, 7]),
                ("zero_years", [3600000, 0.07, 0]),
                ("high_growth", [3600000, 0.15, 10]),
                ("small_salary", [100000, 0.05, 5]),
                ("large_salary", [10000000, 0.03, 15]),
                ("negative_years", [3600000, 0.07, -1]),  # Edge case
            ]
        )
        
        # Test calculate_ups_monthly_pension
        self.test_function(
            "calculate_ups_monthly_pension",
            calculate_ups_monthly_pension,
            "calculateUPSMonthlyPension",
            [
                ("regular_25_years", [6000000, 25]),
                ("regular_32_years", [6000000, 32]),  # More than 25 years
                ("partial_service", [6000000, 15]),
                ("minimum_service", [6000000, 1]),
                ("zero_service", [6000000, 0]),
                ("large_salary", [50000000, 25]),
                ("small_salary", [500000, 25]),
                ("negative_service", [6000000, -1]),  # Edge case
            ]
        )
        
        # Test calculate_ups_lump_sum
        self.test_function(
            "calculate_ups_lump_sum",
            calculate_ups_lump_sum,
            "calculateUPSLumpSum",
            [
                ("regular_25_years", [6000000, 25]),
                ("regular_32_years", [6000000, 32]),
                ("partial_service", [6000000, 15]),
                ("minimum_service", [6000000, 1]),
                ("zero_service", [6000000, 0]),
                ("large_salary", [50000000, 25]),
                ("small_salary", [500000, 25]),
                ("negative_service", [6000000, -1]),  # Edge case
            ]
        )
        
        # Test calculate_nps_corpus
        self.test_function(
            "calculate_nps_corpus",
            calculate_nps_corpus,
            "calculateNPSCorpus",
            [
                ("regular_case", [3600000, 0.07, 7, 0.24, 0.095, 12000000]),
                ("zero_existing", [3600000, 0.07, 7, 0.24, 0.095, 0]),
                ("zero_contrib", [3600000, 0.07, 7, 0.0, 0.095, 12000000]),
                ("zero_return", [3600000, 0.07, 7, 0.24, 0.0, 12000000]),
                ("high_return", [3600000, 0.07, 7, 0.24, 0.20, 12000000]),
                ("long_period", [3600000, 0.07, 30, 0.24, 0.095, 12000000]),
                ("short_period", [3600000, 0.07, 1, 0.24, 0.095, 12000000]),
                ("zero_years", [3600000, 0.07, 0, 0.24, 0.095, 12000000]),
            ]
        )
        
        # Test calculate_nps_monthly_pension
        self.test_function(
            "calculate_nps_monthly_pension",
            calculate_nps_monthly_pension,
            "calculateNPSMonthlyPension",
            [
                ("regular_corpus", [50000000, 0.07]),
                ("small_corpus", [1000000, 0.07]),
                ("large_corpus", [200000000, 0.07]),
                ("zero_corpus", [0, 0.07]),
                ("zero_rate", [50000000, 0.0]),
                ("high_rate", [50000000, 0.15]),
                ("negative_rate", [50000000, -0.05]),  # Edge case
            ]
        )
        
        # Test format_amount
        self.test_function(
            "format_amount",
            format_amount,
            "formatAmount",
            [
                ("lakhs", [1500000]),
                ("thousands", [50000]),
                ("hundreds", [500]),
                ("zero", [0]),
                ("exactly_1_lakh", [100000]),
                ("exactly_1000", [1000]),
                ("decimal", [156789.45]),
                ("large_number", [50000000]),
                ("negative", [-1500000]),  # Edge case
            ]
        )
    
    def print_summary(self) -> None:
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'=' * 50}")
        print("TEST SUMMARY")
        print(f"{'=' * 50}")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\nFAILED TESTS:")
            print("-" * 30)
            for result in self.test_results:
                if not result.passed:
                    print(f"❌ {result.test_name}")
                    print(f"   {result.error_msg}")
        
        return failed_tests == 0

def main():
    """Main test runner"""
    print("Starting UPS vs NPS Calculator Test Suite...")
    
    # Check if Node.js is available
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Node.js is not available. Please install Node.js to run JavaScript tests.")
        sys.exit(1)
    
    # Check if the calculator files exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    py_calc = os.path.join(script_dir, 'upsnpscalculator.py')
    js_calc = os.path.join(script_dir, 'upsnpscalculator.js')
    
    if not os.path.exists(py_calc):
        print(f"❌ Error: Python calculator not found at {py_calc}")
        sys.exit(1)
    
    if not os.path.exists(js_calc):
        print(f"❌ Error: JavaScript calculator not found at {js_calc}")
        sys.exit(1)
    
    # Run tests
    tester = CalculatorTester()
    tester.run_all_tests()
    
    # Print summary and exit with appropriate code
    success = tester.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()