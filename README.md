# UPS vs NPS Pension Calculator

Copyright © 2025 Yogesh Wadadekar

A calculator to compare pension benefits between Universal Pension Scheme (UPS) and National Pension System (NPS). Available as both a web-based interface and Python command-line tool.

## Features

- Calculates final salary based on current salary and growth rate
- Estimates UPS monthly pension for employee and spouse (proportional to service years)
- Calculates and displays minimum return rate required for NPS corpus to last perpetually
- Calculates UPS lump sum amount at retirement.
- Projects the future value of the UPS lump sum if invested.
- Calculates NPS corpus accumulation with compound interest
- Estimates NPS monthly pension and lump sum amount
- Performs corpus depletion analysis (with post-tax investment returns if tax rate is specified)
- Provides year-by-year analysis of NPS corpus utilization, including NPS and UPS lump sum returns
- Considers both employee and spouse pension phases (spouse pension is 60% of employee's)
- Accounts for post-retirement growth in UPS pension

## Usage

### Browser Interface (Recommended)
1. Open `index.html` in a web browser
2. Enter your values or use the defaults
3. Click "Calculate Results" to see the analysis

### Command Line Interface
Run the Python script and follow the interactive prompts:

```bash
python upsnpscalculator.py
```

### Input Parameters

 - Current age and retirement age
 - Current basic salary (Basic + DA)
 - Expected salary growth rate
 - Existing NPS corpus (if any)
- NPS contribution rates (employee and employer)
- Expected returns on NPS investments (default: 9.5%)
- Annuity conversion rate without return of purchase price
- Age when you joined Government service (used to calculate years of service)
- Tax rate on investment returns (all corpus returns are post-tax if specified)
- Post-retirement parameters
  - UPS pension growth rate
  - NPS corpus return rate (before tax)
  - Life expectancy estimates

### Output Information

- Final basic salary at retirement
- Monthly pension estimates for both schemes
- UPS lump sum amount and its projected invested value (using post-tax returns if tax rate is specified).
- NPS corpus and lump sum calculations
- Detailed corpus depletion analysis (using post-tax returns if tax rate is specified)
- Year-by-year breakdown of pension differences, including NPS and UPS lump sum returns

## Default Values

 The calculator comes with sensible defaults:
 - Current age: 53 years
 - Retirement age: 60 years
 - Current annual salary: ₹36 lakhs
 - Salary growth rate: 7%
 - NPS contribution: Employee (10%) + Employer (14%)
 - Expected annual return on NPS: 9.5%
 - Annuity rate (without return of purchase price): 7%
 - Join age: 28 years

 ## License

GPL 3 License
