// Copyright (C) 2025 Yogesh Wadadekar
// This program is licensed under GPL v3. See LICENSE file for details.

// --- Constants ---
const UPS_PENSION_FACTOR = 0.5;
const NPS_ANNUITY_PORTION = 0.4;
const NPS_LUMP_SUM_PORTION = 0.6;
const MONTHS_PER_YEAR = 12;

function calculateFinalSalary(currentSalary, growthRate, years) {
    /**
     * Calculate the final basic salary at retirement based on compound growth.
     * @param {number} currentSalary - Current basic salary
     * @param {number} growthRate - Expected annual salary growth rate (e.g., 0.05 for 5%)
     * @param {number} years - Number of years until retirement
     * @returns {number} Estimated final basic salary
     */
    return currentSalary * Math.pow(1 + growthRate, years);
}

function calculateUPSMonthlyPension(finalSalary, yearsOfService) {
    /**
     * Calculate the monthly pension under UPS, proportionate to years of service.
     * @param {number} finalSalary - Final basic salary
     * @param {number} yearsOfService - Number of years worked (max 25 for full pension)
     * @returns {number} Monthly pension
     */
    const serviceFactor = Math.min(yearsOfService / 25, 1.0);
    const annualPension = serviceFactor * UPS_PENSION_FACTOR * finalSalary;
    return annualPension / MONTHS_PER_YEAR;
}

function formatAmount(amount) {
    /**
     * Format amount to show in lakhs if >= 1 lakh, otherwise in thousands
     * @param {number} amount - Amount to format
     * @returns {string} Formatted amount string
     */
    if (amount >= 100000) {
        return `${(amount/100000).toFixed(2)}L`;
    } else if (amount >= 1000) {
        return `${(amount/1000).toFixed(2)}K`;
    }
    return amount.toFixed(2);
}

function calculateCorpusDepletionYears(initialCorpus, upsMonthlyInitial, npsMonthly, 
                                     employeeLifeYears, spouseAdditionalYears,
                                     postRetGrowth = 0.05, corpusReturn = 0.08) {
    /**
     * Calculate how many years the NPS lump sum corpus will last while covering pension differences.
     * @param {number} initialCorpus - NPS lump sum corpus available.
     * @param {number} upsMonthlyInitial - Initial monthly UPS pension.
     * @param {number} npsMonthly - Monthly NPS annuity (remains constant).
     * @param {number} employeeLifeYears - Expected years employee will live after retirement.
     * @param {number} spouseAdditionalYears - Additional years spouse will live after employee's death.
     * @param {number} postRetGrowth - Annual growth rate of UPS pension.
     * @param {number} corpusReturn - Annual return on remaining corpus.
     * @returns {number} Number of years the corpus lasts, or Infinity if it never depletes.
     */
    let corpus = initialCorpus;
    let year = 0;
    let upsMonthly = upsMonthlyInitial;
    const totalYears = employeeLifeYears + spouseAdditionalYears;
    const yearlyNps = npsMonthly * MONTHS_PER_YEAR; // Calculate constant NPS yearly amount once
    
    console.log("\nYear-by-year NPS Corpus Analysis:");
    console.log("Year  UPS Monthly  NPS Monthly  Yearly Difference  Interest Earned    Corpus Balance  Phase");
    console.log("-".repeat(95));
    
    while (corpus > 0 && year < totalYears) {
        const isSpousePhase = year >= employeeLifeYears;
        const currentUps = upsMonthly * (isSpousePhase ? UPS_PENSION_FACTOR : 1.0); // Use constant
        const phase = isSpousePhase ? "Spouse" : "Employee";
        
        const yearlyUps = currentUps * MONTHS_PER_YEAR; // Use constant
        const yearlyDifference = yearlyUps - yearlyNps;
        const interestEarned = corpus * corpusReturn;
        
        console.log(
            `${year.toString().padStart(4)}  ` +
            `${formatAmount(currentUps).padStart(10)}  ` +
            `${formatAmount(npsMonthly).padStart(10)}  ` +
            `${formatAmount(yearlyDifference).padStart(16)}  ` +
            `${formatAmount(interestEarned).padStart(14)}  ` +
            `${formatAmount(corpus).padStart(14)}  ` +
            `${phase.padStart(7)}`
        );
        
        if (year === 0 && interestEarned >= yearlyDifference) { // Simplified check
            console.log("\nThe corpus will never deplete as the investment returns cover the pension difference perpetually!");
            return Infinity;
        }
        
        corpus = (corpus * (1 + corpusReturn)) - yearlyDifference;
        upsMonthly *= (1 + postRetGrowth);
        year++;
    }
    
    if (corpus <= 0) {
        console.log(`\nThe corpus is depleted after ${year} years.`);
    }
    
    return year;
}

function calculateNPSCorpus(currentSalary, growthRate, years, totalContribRate, annualReturn, existingCorpus = 0.0) {
    /**
     * Calculate the NPS corpus accumulated over the years
     * @param {number} currentSalary - Current basic salary
     * @param {number} growthRate - Annual salary growth rate
     * @param {number} years - Number of years of contributions
     * @param {number} totalContribRate - Total contribution rate (employee + employer)
     * @param {number} annualReturn - Expected annual return on contributions
     * @param {number} existingCorpus - Already accumulated NPS corpus
     * @returns {number} Total corpus accumulated at retirement
     */
    let corpus = existingCorpus * Math.pow(1 + annualReturn, years);
    
    for (let i = 1; i <= years; i++) {
        const salaryAtYear = currentSalary * Math.pow(1 + growthRate, i);
        const annualContribution = totalContribRate * salaryAtYear;
        const yearsToCompound = years - i;
        corpus += annualContribution * Math.pow(1 + annualReturn, yearsToCompound);
    }
    return corpus;
}

function calculateNPSMonthlyPension(corpus, annuityRate) {
    /**
     * Calculate the estimated monthly pension from NPS.
     * Uses a portion of the corpus to purchase an annuity based on NPS_ANNUITY_PORTION.
     * @param {number} corpus - The total corpus accumulated
     * @param {number} annuityRate - The annuity conversion rate (annual)
     * @returns {number} Estimated monthly pension
     */
    const annualAnnuityPension = NPS_ANNUITY_PORTION * corpus * annuityRate; // Use constant
    return annualAnnuityPension / MONTHS_PER_YEAR; // Use constant
}

function promptWithDefault(question, defaultValue) {
    const input = prompt(question, defaultValue);
    return input === "" ? defaultValue : input;
}

function main() {
    console.log("Pension Scheme Comparison: UPS vs NPS");
    console.log("-------------------------------------");
    
    try {
        // User inputs with defaults
        const currentAge = parseInt(promptWithDefault("Enter your current age [53]: ", "53"));
        const retirementAge = parseInt(promptWithDefault("Enter your expected retirement age [60]: ", "60"));
        const currentSalary = parseFloat(promptWithDefault("Enter your current (Basic + DA) annual amount in lakhs [36.00]: ", "36.00")) * 100000;
        const growthRate = parseFloat(promptWithDefault("Enter expected annual salary growth rate [0.07 for 7%]: ", "0.07"));
        const existingCorpus = parseFloat(promptWithDefault("Enter your current NPS corpus amount in lakhs [120.00]: ", "120.00")) * 100000;
        const employeeRate = parseFloat(promptWithDefault("  Enter your contribution rate [0.10 for 10%]: ", "0.10"));
        const employerRate = parseFloat(promptWithDefault("  Enter employer's contribution rate [0.14 for 14%]: ", "0.14"));
        const totalContribRate = employeeRate + employerRate;
        const annualReturn = parseFloat(promptWithDefault("Enter expected annual return on NPS contributions [0.08 for 8%]: ", "0.08"));
        const annuityRate = parseFloat(promptWithDefault("Enter the annuity conversion rate at retirement [0.05 for 5%]: ", "0.05"));
        const postRetGrowth = parseFloat(promptWithDefault("Enter expected post-retirement UPS pension growth rate [0.05 for 5%]: ", "0.05"));
        const corpusReturn = parseFloat(promptWithDefault("Enter expected return on remaining NPS corpus post-retirement [0.08 for 8%]: ", "0.08"));
        const employeeLifeYears = parseInt(promptWithDefault("Enter expected years of life after retirement [20]: ", "20"));
        const spouseAdditionalYears = parseInt(promptWithDefault("Enter additional years spouse may live after employee's death [10]: ", "10"));
        
        // Ask the age when user joined government service and compute years of service
        const joinAge = parseInt(promptWithDefault("At what age did you join Government service [28]: ", "28"));
        const yearsOfService = retirementAge - joinAge;
        if (yearsOfService < 0) {
            console.log("Join age must be less than or equal to retirement age.");
            return;
        }

        const yearsToRetirement = retirementAge - currentAge;
        if (yearsToRetirement <= 0) {
            console.log("Retirement age must be greater than current age.");
            return;
        }
        
        // Calculate UPS pension
        const finalSalary = calculateFinalSalary(currentSalary, growthRate, yearsToRetirement);
        const upsMonthly = calculateUPSMonthlyPension(finalSalary, yearsOfService);
        
        // Calculate NPS corpus and pension
        const corpus = calculateNPSCorpus(currentSalary, growthRate, yearsToRetirement, 
                                        totalContribRate, annualReturn, existingCorpus);
        const npsMonthly = calculateNPSMonthlyPension(corpus, annuityRate);
        
        // Calculate how long the lump sum corpus will last
        const lumpSum = corpus * NPS_LUMP_SUM_PORTION; // Use constant
        const depletionYears = calculateCorpusDepletionYears(lumpSum, upsMonthly, npsMonthly,
                                                          employeeLifeYears, spouseAdditionalYears,
                                                          postRetGrowth, corpusReturn);
        
        // Output the results
        console.log("\nEstimated Results at Retirement:");
        console.log(`  Final basic salary: ${formatAmount(finalSalary)}`);
        console.log(`  UPS estimated monthly pension (employee): ${formatAmount(upsMonthly)}`);
        console.log(`  UPS estimated monthly pension (spouse): ${formatAmount(upsMonthly * UPS_PENSION_FACTOR)}`); // Use constant
        console.log(`  NPS accumulated corpus: ${formatAmount(corpus)}`);
        console.log(`  NPS estimated monthly pension (constant for both): ${formatAmount(npsMonthly)}`);
        console.log(`  NPS lump sum amount (${NPS_LUMP_SUM_PORTION * 100}%): ${formatAmount(lumpSum)}`); // Use constant
        
        // Life expectancy analysis
        console.log("\nLife Expectancy Analysis:");
        console.log(`  Employee expected to live for ${employeeLifeYears} years after retirement`);
        console.log(`  Spouse expected to live for additional ${spouseAdditionalYears} years`);
        const totalCoverageNeeded = Math.max(employeeLifeYears, employeeLifeYears + spouseAdditionalYears); // Corrected logic
        console.log(`  Total years of pension coverage needed: ${totalCoverageNeeded}`);
        if (spouseAdditionalYears < 0) {
            console.log("  Note: Since spouse's additional years is negative, coverage is needed only until employee's death");
        }
        
        // Post-retirement analysis
        console.log("\nPost-Retirement Analysis:");
        if (depletionYears === Infinity) {
            console.log("  The NPS corpus will NEVER deplete as the investment returns");
            console.log("  cover the pension difference perpetually!");
        } else {
            console.log(`  The NPS corpus will last approximately ${depletionYears.toFixed(1)} years`);
            if (depletionYears < totalCoverageNeeded) {
                const shortfallYears = totalCoverageNeeded - depletionYears;
                console.log(`  WARNING: This is ${shortfallYears.toFixed(1)} years short of the total needed coverage period!`);
            }
            console.log("  while covering the difference between UPS and NPS pensions");
        }
    } catch (error) {
        console.error("Invalid input. Please enter numeric values.", error);
    }
}

// For browser environments
if (typeof window !== 'undefined') {
    window.runCalculator = main;
} else {
    // For Node.js environments
    main();
}