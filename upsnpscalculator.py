# Copyright (C) 2025 Yogesh Wadadekar
# This program is licensed under GPL v3. See LICENSE file for details.

from typing import Union

# --- Constants ---
UPS_PENSION_FACTOR: float = 0.5
NPS_ANNUITY_PORTION: float = 0.4
NPS_LUMP_SUM_PORTION: float = 0.6
MONTHS_PER_YEAR: int = 12

def calculate_final_salary(current_salary: float, growth_rate: float, years: int) -> float:
    """
    Calculate the final basic salary at retirement based on compound growth.
    
    Parameters:
      current_salary (float): Current basic salary.
      growth_rate (float): Expected annual salary growth rate (e.g., 0.05 for 5%).
      years (int): Number of years until retirement.
    
    Returns:
      float: Estimated final basic salary.
    """
    return current_salary * ((1 + growth_rate) ** years)

def calculate_ups_monthly_pension(final_salary: float) -> float:
    """
    Calculate the monthly pension under UPS.
    
    Parameters:
      final_salary (float): Final basic salary.
    
    Returns:
      float: Monthly pension (assuming 50% of final salary as annual pension).
    """
    annual_pension: float = UPS_PENSION_FACTOR * final_salary
    return annual_pension / MONTHS_PER_YEAR

def format_amount(amount: float) -> str:
    """
    Format amount to show in lakhs if >= 1 lakh, otherwise in thousands
    """
    if amount >= 100000:
        return f"{amount/100000:.2f}L"
    elif amount >= 1000:
        return f"{amount/1000:.2f}K"
    return f"{amount:.2f}"

def calculate_corpus_depletion_years(initial_corpus: float, ups_monthly_initial: float, nps_monthly: float, 
                                employee_life_years: int, spouse_additional_years: int,
                                post_ret_growth: float = 0.05, corpus_return: float = 0.08) -> Union[int, float]:
    """
    Calculate how many years the NPS lump sum corpus will last while covering pension differences.
    
    Parameters:
        initial_corpus (float): NPS lump sum corpus available.
        ups_monthly_initial (float): Initial monthly UPS pension.
        nps_monthly (float): Monthly NPS annuity (remains constant).
        employee_life_years (int): Expected years employee will live after retirement.
        spouse_additional_years (int): Additional years spouse will live after employee's death.
        post_ret_growth (float): Annual growth rate of UPS pension.
        corpus_return (float): Annual return on remaining corpus.
    
    Returns:
        Union[int, float]: Number of years the corpus lasts, or float('inf') if it never depletes.
    """
    corpus: float = initial_corpus
    year: int = 0
    ups_monthly: float = ups_monthly_initial
    total_years: int = employee_life_years + spouse_additional_years
    yearly_nps: float = nps_monthly * MONTHS_PER_YEAR # Calculate constant NPS yearly amount once
    
    print("\nYear-by-year NPS Corpus Analysis:")
    print("Year  UPS Monthly  NPS Monthly  Yearly Difference  Interest Earned    Corpus Balance  Phase")
    print("-" * 95)
    
    while corpus > 0 and year < total_years:
        is_spouse_phase: bool = year >= employee_life_years
        current_ups: float = ups_monthly * (UPS_PENSION_FACTOR if is_spouse_phase else 1.0) # Use constant
        phase: str = "Spouse" if is_spouse_phase else "Employee"
        
        yearly_ups: float = current_ups * MONTHS_PER_YEAR
        yearly_difference: float = yearly_ups - yearly_nps
        interest_earned: float = corpus * corpus_return
        
        print(f"{year:4d}  {format_amount(current_ups):>10}  {format_amount(nps_monthly):>10}  "
              f"{format_amount(yearly_difference):>16}  {format_amount(interest_earned):>14}  "
              f"{format_amount(corpus):>14}  {phase:>7}")
        
        if year == 0 and interest_earned >= yearly_difference: # Simplified check
            print("\nThe corpus will never deplete as the investment returns cover the pension difference perpetually!")
            return float('inf')
        
        corpus = (corpus * (1 + corpus_return)) - yearly_difference
        ups_monthly *= (1 + post_ret_growth)
        year += 1
    
    if corpus <= 0:
        print(f"\nThe corpus is depleted after {year} years.")
    
    return year

def calculate_nps_corpus(current_salary: float, growth_rate: float, years: int, 
                         total_contrib_rate: float, annual_return: float, 
                         existing_corpus: float = 0.0) -> float:
    """
    Calculate the NPS corpus accumulated over the years.
    
    Assumes contributions are made at the end of each year and compound at the annual_return.
    
    Parameters:
      current_salary (float): Current basic salary.
      growth_rate (float): Annual salary growth rate.
      years (int): Number of years of contributions.
      total_contrib_rate (float): Total contribution rate (employee + employer).
      annual_return (float): Expected annual return on contributions.
      existing_corpus (float): Already accumulated NPS corpus.
    
    Returns:
      float: Total corpus accumulated at retirement.
    """
    corpus: float = existing_corpus * ((1 + annual_return) ** years)
    
    for i in range(1, years + 1):
        salary_at_year: float = current_salary * ((1 + growth_rate) ** i)
        annual_contribution: float = total_contrib_rate * salary_at_year
        years_to_compound: int = years - i
        corpus += annual_contribution * ((1 + annual_return) ** years_to_compound)
    return corpus

def calculate_nps_monthly_pension(corpus: float, annuity_rate: float) -> float:
    """
    Calculate the estimated monthly pension from NPS.
    
    Uses a portion of the corpus to purchase an annuity based on NPS_ANNUITY_PORTION.
    
    Parameters:
      corpus (float): The total corpus accumulated.
      annuity_rate (float): The annuity conversion rate (annual).
    
    Returns:
      float: Estimated monthly pension.
    """
    annual_annuity_pension: float = NPS_ANNUITY_PORTION * corpus * annuity_rate
    return annual_annuity_pension / MONTHS_PER_YEAR

def main():
    print("Pension Scheme Comparison: UPS vs NPS")
    print("-------------------------------------")
    print("Hit enter to use default values in [brackets]")
    
    # User inputs with defaults
    try:
        current_age_input = input("Enter your current age [53]: ")
        current_age = 53 if current_age_input == "" else int(current_age_input)
        
        retirement_age_input = input("Enter your expected retirement age [60]: ")
        retirement_age = 60 if retirement_age_input == "" else int(retirement_age_input)
        
        current_salary_input = input("Enter your current (Basic + DA) annual amount in lakhs [36.00]: ")
        current_salary = 3600000 if current_salary_input == "" else float(current_salary_input) * 100000
        
        growth_rate_input = input("Enter expected annual salary growth rate [0.07 for 7%]: ")
        growth_rate = 0.07 if growth_rate_input == "" else float(growth_rate_input)
        
        existing_corpus_input = input("Enter your current NPS corpus amount in lakhs [120.00]: ")
        existing_corpus = 12000000 if existing_corpus_input == "" else float(existing_corpus_input) * 100000
        
        print("\nFor NPS, specify contribution rates:")
        employee_rate_input = input("  Enter your contribution rate [0.10 for 10%]: ")
        employee_rate = 0.10 if employee_rate_input == "" else float(employee_rate_input)
        
        employer_rate_input = input("  Enter employer's contribution rate [0.14 for 14%]: ")
        employer_rate = 0.14 if employer_rate_input == "" else float(employer_rate_input)
        total_contrib_rate = employee_rate + employer_rate
        
        annual_return_input = input("Enter expected annual return on NPS contributions [0.08 for 8%]: ")
        annual_return = 0.08 if annual_return_input == "" else float(annual_return_input)
        
        annuity_rate_input = input("Enter the annuity conversion rate at retirement [0.05 for 5%]: ")
        annuity_rate = 0.05 if annuity_rate_input == "" else float(annuity_rate_input)
        
        post_ret_growth_input = input("Enter expected post-retirement UPS pension growth rate [0.05 for 5%]: ")
        post_ret_growth = 0.05 if post_ret_growth_input == "" else float(post_ret_growth_input)
        
        corpus_return_input = input("Enter expected return on remaining NPS corpus post-retirement [0.08 for 8%]: ")
        corpus_return = 0.08 if corpus_return_input == "" else float(corpus_return_input)
        
        employee_life_input = input("Enter expected years of life after retirement [20]: ")
        employee_life_years = 20 if employee_life_input == "" else int(employee_life_input)
        
        spouse_additional_input = input("Enter additional years spouse may live after employee's death [10]: ")
        spouse_additional_years = 10 if spouse_additional_input == "" else int(spouse_additional_input)
        
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return
    
    years_to_retirement = retirement_age - current_age
    if years_to_retirement <= 0:
        print("Retirement age must be greater than current age.")
        return
    
    # Calculate UPS pension
    final_salary = calculate_final_salary(current_salary, growth_rate, years_to_retirement)
    ups_monthly = calculate_ups_monthly_pension(final_salary)
    
    # Calculate NPS corpus and pension
    corpus = calculate_nps_corpus(current_salary, growth_rate, years_to_retirement, 
                                total_contrib_rate, annual_return, existing_corpus)
    nps_monthly = calculate_nps_monthly_pension(corpus, annuity_rate)
    
    # Calculate how long the 60% corpus will last
    lump_sum = corpus * NPS_LUMP_SUM_PORTION  # Use constant
    depletion_years = calculate_corpus_depletion_years(lump_sum, ups_monthly, nps_monthly,
                                                      employee_life_years, spouse_additional_years,
                                                      post_ret_growth, corpus_return)
    
    # Output the results
    print("\nEstimated Results at Retirement:")
    print(f"  Final basic salary: {format_amount(final_salary)}")
    print(f"  UPS estimated monthly pension (employee): {format_amount(ups_monthly)}")
    print(f"  UPS estimated monthly pension (spouse): {format_amount(ups_monthly * 0.5)}")
    print(f"  NPS accumulated corpus: {format_amount(corpus)}")
    print(f"  NPS estimated monthly pension (constant for both): {format_amount(nps_monthly)}")
    print(f"  NPS lump sum amount (60%): {format_amount(lump_sum)}")
    
    # Life expectancy analysis
    print("\nLife Expectancy Analysis:")
    print(f"  Employee expected to live for {employee_life_years} years after retirement")
    print(f"  Spouse expected to live for additional {spouse_additional_years} years")
    total_coverage_needed = max(employee_life_years, employee_life_years + spouse_additional_years)
    print(f"  Total years of pension coverage needed: {total_coverage_needed}")
    if spouse_additional_years < 0:
        print("  Note: Since spouse's additional years is negative, coverage is needed only until employee's death")
    
    # Post-retirement analysis
    print("\nPost-Retirement Analysis:")
    if depletion_years == float('inf'):
        print("  The NPS corpus will NEVER deplete as the investment returns")
        print("  cover the pension difference perpetually!")
    else:
        print(f"  The NPS corpus will last approximately {depletion_years:.1f} years")
        if depletion_years < total_coverage_needed:
            shortfall_years = total_coverage_needed - depletion_years
            print(f"  WARNING: This is {shortfall_years:.1f} years short of the total needed coverage period!")
        print("  while covering the difference between UPS and NPS pensions")

if __name__ == '__main__':
    main()
