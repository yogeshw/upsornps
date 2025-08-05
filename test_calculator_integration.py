#!/usr/bin/env python3
"""
Integration test suite for UPS vs NPS Calculator
Tests complete calculator workflows and complex scenarios.

Copyright (C) 2025 Yogesh Wadadekar
This program is licensed under GPL v3. See LICENSE file for details.
"""

import subprocess
import sys
import os
import json
from typing import Dict, Any, List, Tuple
import io
import contextlib

# Import the Python calculator functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from upsnpscalculator import (
    calculate_final_salary,
    calculate_ups_monthly_pension,
    calculate_ups_lump_sum,
    calculate_nps_corpus,
    calculate_nps_monthly_pension,
    calculate_corpus_depletion_years,
    format_amount
)

class IntegrationTester:
    """Integration test class for complete calculator workflows"""
    
    def __init__(self):
        self.test_results = []
        self.tolerance = 1e-6
    
    def capture_console_output(self, func, *args, **kwargs):
        """Capture console output from a function"""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = func(*args, **kwargs)
        return result, f.getvalue()
    
    def test_complete_calculation_workflow(self):
        """Test a complete calculation workflow with realistic scenarios"""
        print("=== Testing Complete Calculation Workflows ===")
        
        # Test scenario 1: Standard government employee
        print("\nTest 1: Standard Government Employee")
        current_salary = 3600000  # 36L
        growth_rate = 0.07
        years = 7
        years_of_service = 32  # Joined at 28, retires at 60
        total_contrib_rate = 0.24  # 10% + 14%
        annual_return = 0.095
        existing_corpus = 12000000  # 120L
        annuity_rate = 0.07
        
        try:
            # Calculate all components
            final_salary = calculate_final_salary(current_salary, growth_rate, years)
            ups_monthly = calculate_ups_monthly_pension(final_salary, years_of_service)
            ups_lump_sum = calculate_ups_lump_sum(final_salary, years_of_service)
            nps_corpus = calculate_nps_corpus(current_salary, growth_rate, years, 
                                            total_contrib_rate, annual_return, existing_corpus)
            nps_monthly = calculate_nps_monthly_pension(nps_corpus, annuity_rate)
            nps_lump_sum = nps_corpus * 0.6
            
            # Test corpus depletion with captured output
            corpus_years, output = self.capture_console_output(
                calculate_corpus_depletion_years,
                nps_lump_sum, ups_monthly, nps_monthly, 20, 10, 0.05, 0.08, ups_lump_sum
            )
            
            print(f"  ✅ Final salary: {format_amount(final_salary)}")
            print(f"  ✅ UPS monthly pension: {format_amount(ups_monthly)}")
            print(f"  ✅ UPS lump sum: {format_amount(ups_lump_sum)}")
            print(f"  ✅ NPS corpus: {format_amount(nps_corpus)}")
            print(f"  ✅ NPS monthly pension: {format_amount(nps_monthly)}")
            print(f"  ✅ NPS lump sum: {format_amount(nps_lump_sum)}")
            print(f"  ✅ Corpus depletion years: {corpus_years}")
            print(f"  ✅ Console output captured: {len(output.split('\\n'))} lines")
            
            self.test_results.append(("Standard workflow", True, ""))
            
        except Exception as e:
            print(f"  ❌ Standard workflow failed: {e}")
            self.test_results.append(("Standard workflow", False, str(e)))
        
        # Test scenario 2: Edge case - very short service
        print("\nTest 2: Short Service Employee")
        try:
            short_service_years = 5
            ups_monthly_short = calculate_ups_monthly_pension(final_salary, short_service_years)
            ups_lump_sum_short = calculate_ups_lump_sum(final_salary, short_service_years)
            
            # Should be proportional to years of service
            expected_proportion = min(short_service_years / 25, 1.0)
            full_pension = calculate_ups_monthly_pension(final_salary, 25)
            expected_pension = full_pension * expected_proportion
            
            if abs(ups_monthly_short - expected_pension) < self.tolerance:
                print(f"  ✅ Short service pension calculation correct: {format_amount(ups_monthly_short)}")
                self.test_results.append(("Short service pension", True, ""))
            else:
                print(f"  ❌ Short service pension incorrect: got {ups_monthly_short}, expected {expected_pension}")
                self.test_results.append(("Short service pension", False, "Incorrect calculation"))
                
        except Exception as e:
            print(f"  ❌ Short service test failed: {e}")
            self.test_results.append(("Short service pension", False, str(e)))
        
        # Test scenario 3: Edge case - corpus never depletes
        print("\nTest 3: High Return Scenario (Corpus Never Depletes)")
        try:
            high_return_rate = 0.20  # 20% return
            corpus_years_high, output_high = self.capture_console_output(
                calculate_corpus_depletion_years,
                nps_lump_sum, ups_monthly, nps_monthly, 20, 10, 0.05, high_return_rate, ups_lump_sum
            )
            
            if corpus_years_high == float('inf'):
                print(f"  ✅ High return correctly shows infinite corpus life")
                self.test_results.append(("High return scenario", True, ""))
            else:
                print(f"  ❌ High return scenario incorrect: got {corpus_years_high}, expected inf")
                self.test_results.append(("High return scenario", False, "Should be infinite"))
                
        except Exception as e:
            print(f"  ❌ High return test failed: {e}")
            self.test_results.append(("High return scenario", False, str(e)))
    
    def test_edge_cases(self):
        """Test various edge cases and boundary conditions"""
        print("\n=== Testing Edge Cases ===")
        
        # Test 1: Zero corpus
        print("\nTest 1: Zero NPS Corpus")
        try:
            zero_corpus_years, _ = self.capture_console_output(
                calculate_corpus_depletion_years,
                0, 100000, 50000, 20, 10, 0.05, 0.08, 0
            )
            
            if zero_corpus_years == 0:
                print(f"  ✅ Zero corpus correctly depletes immediately")
                self.test_results.append(("Zero corpus", True, ""))
            else:
                print(f"  ❌ Zero corpus incorrect: got {zero_corpus_years}, expected 0")
                self.test_results.append(("Zero corpus", False, "Should deplete immediately"))
                
        except Exception as e:
            print(f"  ❌ Zero corpus test failed: {e}")
            self.test_results.append(("Zero corpus", False, str(e)))
        
        # Test 2: NPS pension higher than UPS
        print("\nTest 2: NPS Pension Higher Than UPS")
        try:
            high_nps_years, _ = self.capture_console_output(
                calculate_corpus_depletion_years,
                10000000, 50000, 100000, 20, 10, 0.05, 0.08, 0  # NPS higher than UPS
            )
            
            if high_nps_years == float('inf'):
                print(f"  ✅ Higher NPS pension correctly shows infinite corpus life")
                self.test_results.append(("High NPS pension", True, ""))
            else:
                print(f"  ❌ High NPS pension incorrect: got {high_nps_years}, expected inf")
                self.test_results.append(("High NPS pension", False, "Should be infinite"))
                
        except Exception as e:
            print(f"  ❌ High NPS pension test failed: {e}")
            self.test_results.append(("High NPS pension", False, str(e)))
        
        # Test 3: Maximum service years
        print("\nTest 3: Maximum Service Years (>25)")
        try:
            pension_25 = calculate_ups_monthly_pension(6000000, 25)
            pension_30 = calculate_ups_monthly_pension(6000000, 30)
            pension_40 = calculate_ups_monthly_pension(6000000, 40)
            
            # All should be the same (capped at 25 years)
            if abs(pension_25 - pension_30) < self.tolerance and abs(pension_25 - pension_40) < self.tolerance:
                print(f"  ✅ Service years correctly capped at 25: {format_amount(pension_25)}")
                self.test_results.append(("Service years cap", True, ""))
            else:
                print(f"  ❌ Service years cap failed: 25y={pension_25}, 30y={pension_30}, 40y={pension_40}")
                self.test_results.append(("Service years cap", False, "Not properly capped"))
                
        except Exception as e:
            print(f"  ❌ Service years cap test failed: {e}")
            self.test_results.append(("Service years cap", False, str(e)))
    
    def test_consistency_checks(self):
        """Test internal consistency of calculations"""
        print("\n=== Testing Consistency Checks ===")
        
        # Test 1: Proportional scaling
        print("\nTest 1: Proportional Scaling")
        try:
            base_salary = 3600000
            base_final = calculate_final_salary(base_salary, 0.07, 7)
            double_final = calculate_final_salary(base_salary * 2, 0.07, 7)
            
            if abs(double_final - base_final * 2) < self.tolerance:
                print(f"  ✅ Final salary scales proportionally")
                self.test_results.append(("Proportional scaling", True, ""))
            else:
                print(f"  ❌ Final salary scaling failed: {double_final} vs {base_final * 2}")
                self.test_results.append(("Proportional scaling", False, "Not proportional"))
                
        except Exception as e:
            print(f"  ❌ Proportional scaling test failed: {e}")
            self.test_results.append(("Proportional scaling", False, str(e)))
        
        # Test 2: NPS corpus consistency
        print("\nTest 2: NPS Corpus Consistency")
        try:
            # Test that existing corpus grows correctly
            base_corpus = calculate_nps_corpus(3600000, 0.07, 7, 0.24, 0.095, 1000000)
            zero_existing = calculate_nps_corpus(3600000, 0.07, 7, 0.24, 0.095, 0)
            expected_difference = 1000000 * (1.095 ** 7)
            actual_difference = base_corpus - zero_existing
            
            if abs(actual_difference - expected_difference) < 1:  # Allow 1 rupee tolerance for rounding
                print(f"  ✅ Existing corpus grows correctly")
                self.test_results.append(("NPS corpus consistency", True, ""))
            else:
                print(f"  ❌ Existing corpus growth failed: diff={actual_difference}, expected={expected_difference}")
                self.test_results.append(("NPS corpus consistency", False, "Incorrect growth"))
                
        except Exception as e:
            print(f"  ❌ NPS corpus consistency test failed: {e}")
            self.test_results.append(("NPS corpus consistency", False, str(e)))
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n=== Testing Error Handling ===")
        
        # Test 1: Negative inputs
        print("\nTest 1: Handling Negative Inputs")
        try:
            # These should still calculate but may give unexpected results
            neg_salary_result = calculate_final_salary(-1000000, 0.07, 5)
            neg_growth_result = calculate_final_salary(1000000, -0.1, 5)
            
            print(f"  ℹ️  Negative salary result: {neg_salary_result}")
            print(f"  ℹ️  Negative growth result: {neg_growth_result}")
            print(f"  ✅ Functions handle negative inputs (may produce negative results)")
            self.test_results.append(("Negative inputs", True, "Handled gracefully"))
            
        except Exception as e:
            print(f"  ❌ Negative input handling failed: {e}")
            self.test_results.append(("Negative inputs", False, str(e)))
        
        # Test 2: Zero values
        print("\nTest 2: Handling Zero Values")
        try:
            zero_tests = [
                ("Zero salary", calculate_final_salary, [0, 0.07, 5]),
                ("Zero growth", calculate_final_salary, [1000000, 0, 5]),
                ("Zero years", calculate_final_salary, [1000000, 0.07, 0]),
                ("Zero corpus", calculate_nps_monthly_pension, [0, 0.07]),
                ("Zero rate", calculate_nps_monthly_pension, [1000000, 0]),
            ]
            
            for test_name, func, args in zero_tests:
                result = func(*args)
                print(f"  ✅ {test_name}: {result}")
            
            self.test_results.append(("Zero values", True, "All handled"))
            
        except Exception as e:
            print(f"  ❌ Zero value handling failed: {e}")
            self.test_results.append(("Zero values", False, str(e)))
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("UPS vs NPS Calculator Integration Test Suite")
        print("=" * 60)
        
        self.test_complete_calculation_workflow()
        self.test_edge_cases()
        self.test_consistency_checks()
        self.test_error_handling()
        
        # Print summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'=' * 60}")
        print("INTEGRATION TEST SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\nFAILED TESTS:")
            print("-" * 30)
            for test_name, passed, error_msg in self.test_results:
                if not passed:
                    print(f"❌ {test_name}: {error_msg}")
        
        return failed_tests == 0

def main():
    """Main test runner"""
    print("Starting UPS vs NPS Calculator Integration Tests...")
    
    # Check if the calculator files exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    py_calc = os.path.join(script_dir, 'upsnpscalculator.py')
    
    if not os.path.exists(py_calc):
        print(f"❌ Error: Python calculator not found at {py_calc}")
        sys.exit(1)
    
    # Run tests
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()