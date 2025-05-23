# Copyright (C) 2025 Yogesh Wadadekar
# This program is licensed under GPL v3. See LICENSE file for details.

from typing import Union

# --- Constants ---
UPS_PENSION_FACTOR: float = 0.5
UPS_SPOUSE_FACTOR: float = 0.6
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

def calculate_ups_monthly_pension(final_salary: float, years_of_service: int) -> float:
    """
    Calculate the monthly pension under UPS, proportionate to years of service.
    
    Parameters:
      final_salary (float): Final basic salary.
      years_of_service (int): Number of years worked (max 25 for full pension).
    
    Returns:
      float: Monthly pension.
    """
    employee_factor: float = min(years_of_service / 25, 1.0) * UPS_PENSION_FACTOR
    annual_pension: float = employee_factor * final_salary
    return annual_pension / MONTHS_PER_YEAR

def calculate_ups_lump_sum(final_salary_annual: float, years_of_service: int) -> float:
    """
    Calculate the lump sum payment under UPS.

    The lump sum is 1/10th of the last drawn monthly basic pay (plus DA)
    for every completed six months of qualifying service.

    Parameters:
      final_salary_annual (float): Final annual basic salary (plus DA).
      years_of_service (int): Number of completed years of qualifying service.

    Returns:
      float: Calculated UPS lump sum amount.
    """
    last_monthly_salary: float = final_salary_annual / MONTHS_PER_YEAR
    # Number of completed six-month periods
    num_six_month_periods: int = years_of_service * 2
    lump_sum: float = (1/10) * last_monthly_salary * num_six_month_periods
    return lump_sum

def format_amount(amount: float) -> str:
    """
    Format amount to show in lakhs if >= 1 lakh, otherwise in thousands
    """
    if amount >= 100000:
        return f"{amount/100000:.2f}L"
    elif amount >= 1000:
        return f"{amount/1000:.2f}K"
    return f"{amount:.2f}"

def calculate_corpus_depletion_years(
    initial_corpus: float,
    ups_monthly_initial: float,
    nps_monthly: float,
    employee_life_years: int,
    spouse_additional_years: int,
    post_ret_growth: float = 0.05,
    corpus_return: float = 0.08,
    ups_lump_sum: float = 0.0
) -> Union[int, float]:
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
        ups_lump_sum (float): UPS lump sum corpus invested to earn returns.
    Returns:
      Union[int, float]: Number of years the corpus lasts, or float('inf') if it never depletes.
    """
    corpus: float = initial_corpus
    year: int = 0
    ups_monthly: float = ups_monthly_initial
    total_years: int = employee_life_years + spouse_additional_years
    yearly_nps: float = nps_monthly * MONTHS_PER_YEAR # Calculate constant NPS yearly amount once
    
    print("\nYear-by-year Corpus Analysis with Returns:")
    print("Year  UPS Pension  UPS Return  Total UPS   NPS Annuity  NPS Return  Total NPS   Diff(UPS-NPS)  Corpus Balance  Phase")
    print("-" * 120)
    
    post_tax_corpus_return = corpus_return

    while corpus > 0 and year < total_years:
        is_spouse_phase: bool = year >= employee_life_years
        current_ups: float = ups_monthly * (UPS_SPOUSE_FACTOR if is_spouse_phase else 1.0)
        phase: str = "Spouse" if is_spouse_phase else "Employee"

        yearly_ups: float = current_ups * MONTHS_PER_YEAR
        ups_return: float = ups_lump_sum * post_tax_corpus_return
        total_ups_income: float = yearly_ups + ups_return
        nps_return: float = corpus * post_tax_corpus_return
        yearly_nps: float = nps_monthly * MONTHS_PER_YEAR
        total_nps_income: float = yearly_nps + nps_return
        yearly_difference: float = total_ups_income - total_nps_income

        print(
            f"{year:4d}  {format_amount(yearly_ups):>10}  {format_amount(ups_return):>10}  {format_amount(total_ups_income):>10}  "
            f"{format_amount(yearly_nps):>11}  {format_amount(nps_return):>10}  {format_amount(total_nps_income):>10}  "
            f"{format_amount(yearly_difference):>13}  {format_amount(corpus):>14}  {phase:>7}"
        )

        # Correct corpus update: corpus grows by post-tax return, then is reduced by (UPS+UPS return)-(NPS+NPS return) if UPS+UPS return > NPS+NPS return
        corpus -= max(0, total_ups_income - total_nps_income)
        corpus = corpus * (1 + post_tax_corpus_return)

        # Perpetual check: if NPS annuity + NPS corpus return >= UPS pension + UPS lump sum return, corpus will never deplete
        if year == 0 and total_nps_income >= total_ups_income:
            print("\nThe corpus will never deplete as the post-tax investment returns and NPS annuity cover the UPS pension plus UPS lump sum returns perpetually!")
            return float('inf')

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
      annuity_rate (float): The annuity conversion rate (annual) without return of purchase price.

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
        
        annual_return_input = input("Enter expected annual return on NPS contributions [0.095 for 9.5%]: ")
        annual_return = 0.095 if annual_return_input == "" else float(annual_return_input)
        
        annuity_rate_input = input("Enter the annuity conversion rate at retirement without return of purchase price [0.07 for 7%]: ")
        annuity_rate = 0.07 if annuity_rate_input == "" else float(annuity_rate_input)
        
        post_ret_growth_input = input("Enter expected post-retirement UPS pension growth rate [0.05 for 5%]: ")
        post_ret_growth = 0.05 if post_ret_growth_input == "" else float(post_ret_growth_input)
        
        corpus_return_input = input("Enter expected return on remaining NPS corpus post-retirement [0.08 for 8%]: ")
        corpus_return = 0.08 if corpus_return_input == "" else float(corpus_return_input)
        
        employee_life_input = input("Enter expected years of life after retirement [20]: ")
        employee_life_years = 20 if employee_life_input == "" else int(employee_life_input)
        
        spouse_additional_input = input("Enter additional years spouse may live after employee's death [10]: ")
        spouse_additional_years = 10 if spouse_additional_input == "" else int(spouse_additional_input)
        
        # Ask age when the user joined government service and compute service years
        join_age_input = input("Enter your age when you joined Government service [28]: ")
        join_age = 28 if join_age_input == "" else int(join_age_input)
        years_of_service = retirement_age - join_age
        if years_of_service < 0:
            print("Join age must be less than or equal to retirement age.")
            return

        # Tax rate input removed; all returns are now pre-tax
        
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return
    
    years_to_retirement = retirement_age - current_age
    if years_to_retirement <= 0:
        print("Retirement age must be greater than current age.")
        return
    
    # Calculate UPS pension and lump sum
    final_salary = calculate_final_salary(current_salary, growth_rate, years_to_retirement)
    ups_monthly = calculate_ups_monthly_pension(final_salary, years_of_service)
    ups_lump_sum_amount = calculate_ups_lump_sum(final_salary, years_of_service)

    # Calculate NPS corpus and pension
    corpus = calculate_nps_corpus(current_salary, growth_rate, years_to_retirement, 
                                total_contrib_rate, annual_return, existing_corpus)
    nps_monthly = calculate_nps_monthly_pension(corpus, annuity_rate)
    
    # NPS lump sum (60% of corpus)
    nps_lump_sum = corpus * NPS_LUMP_SUM_PORTION

    # Calculate total pension coverage period needed
    total_coverage_needed = max(employee_life_years, employee_life_years + spouse_additional_years)
    
    # Output the results
    print("\nEstimated Results at Retirement:")
    print(f"  Final basic salary: {format_amount(final_salary)}")
    print(f"  UPS estimated monthly pension (employee): {format_amount(ups_monthly)}")
    print(f"  UPS estimated monthly pension (spouse): {format_amount(ups_monthly * UPS_SPOUSE_FACTOR)}")
    print(f"  UPS lump sum amount: {format_amount(ups_lump_sum_amount)}")
    if ups_lump_sum_amount > 0 and total_coverage_needed > 0 and corpus_return > 0:
        projected_ups_lump_sum = ups_lump_sum_amount * ((1 + corpus_return) ** total_coverage_needed)
        print(f"    (Projected value after {total_coverage_needed} years if invested at {corpus_return:.2%}: {format_amount(projected_ups_lump_sum)})")
    print(f"  Yearly UPS return on investment: {format_amount(ups_lump_sum_amount * corpus_return)}")

    print(f"  NPS accumulated corpus: {format_amount(corpus)}")
    print(f"  NPS estimated monthly pension (constant for both): {format_amount(nps_monthly)}")
    print(f"  NPS lump sum amount (60%): {format_amount(nps_lump_sum)})")
    
    # Life expectancy analysis (display values used for total_coverage_needed)
    print("\nLife Expectancy Analysis:")
    print(f"  Employee expected to live for {employee_life_years} years after retirement")
    print(f"  Spouse expected to live for additional {spouse_additional_years} years")
    print(f"  Total years of pension coverage needed: {total_coverage_needed}") # Displaying it
    if spouse_additional_years < 0:
        print("  Note: Since spouse's additional years is negative, coverage is needed only until employee's death")
    
    # Calculate how long the NPS 60% corpus will last
    # Calculate how long the NPS 60% corpus will last, including UPS lump sum investment
    depletion_years = calculate_corpus_depletion_years(
        nps_lump_sum,
        ups_monthly,
        nps_monthly,
        employee_life_years,
        spouse_additional_years,
        post_ret_growth,
        corpus_return,
        ups_lump_sum_amount
    )
    
    # Post-retirement analysis for NPS lump sum
    print("\nPost-Retirement Analysis (for NPS lump sum):")
    if depletion_years == float('inf'):
        print("  The NPS corpus will NEVER deplete as the post-tax investment returns")
        print("  cover the pension difference perpetually!")
    else:
        print(f"  The NPS corpus will last approximately {depletion_years:.1f} years")
        if depletion_years < total_coverage_needed:
            shortfall_years = total_coverage_needed - depletion_years
            print(f"  WARNING: This is {shortfall_years:.1f} years short of the total needed coverage period!")
        print("  while covering the difference between UPS and NPS pensions")
        # Calculate minimum post-tax return rate on 60% corpus to last perpetually
        yearly_ups = ups_monthly * MONTHS_PER_YEAR
        yearly_nps = nps_monthly * MONTHS_PER_YEAR
        difference = yearly_ups - yearly_nps
        # Ensure nps_lump_sum is not zero to avoid division by zero error
        if nps_lump_sum > 0:
            min_return_rate = difference / nps_lump_sum
            print(f"  Minimum post-tax return rate on the NPS 60% corpus to last perpetually: {min_return_rate:.2%}")
        else:
            print("  NPS lump sum is zero, cannot calculate minimum return rate for perpetuity.")

if __name__ == '__main__':
    main()
