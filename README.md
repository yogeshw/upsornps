# UPS vs NPS Pension Calculator

Copyright © 2025 Yogesh Wadadekar

A Python-based calculator to compare pension benefits between Universal Pension Scheme (UPS) and National Pension System (NPS).

## Features

- Calculates final salary based on current salary and growth rate
- Estimates UPS monthly pension for employee and spouse
- Calculates NPS corpus accumulation with compound interest
- Estimates NPS monthly pension and lump sum amount
- Performs corpus depletion analysis
- Provides year-by-year analysis of NPS corpus utilization
- Considers both employee and spouse pension phases
- Accounts for post-retirement growth in UPS pension

## Usage

Run the script and follow the interactive prompts:

```bash
python upsnpscalculator.py
```

### Input Parameters

- Current age and retirement age
- Current basic salary (Basic + DA)
- Expected salary growth rate
- Existing NPS corpus (if any)
- NPS contribution rates (employee and employer)
- Expected returns on NPS investments
- Annuity conversion rate
- Post-retirement parameters
  - UPS pension growth rate
  - NPS corpus return rate
  - Life expectancy estimates

### Output Information

- Final basic salary at retirement
- Monthly pension estimates for both schemes
- NPS corpus and lump sum calculations
- Detailed corpus depletion analysis
- Year-by-year breakdown of pension differences

## Default Values

The calculator comes with sensible defaults:
- Current age: 53 years
- Retirement age: 60 years
- Current annual salary: ₹36 lakhs
- Salary growth rate: 7%
- NPS contribution: Employee (10%) + Employer (14%)
- Investment return: 8%
- Annuity rate: 5%

## License

GPL 3 License
