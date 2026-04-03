# We have to segment companies based on their financial behavior, which we will define using financial archetypes.
# We will use K-means clustering to identify these archetypes based on key financial metrics. This segmentation will allow us to build more tailored predictive models for each group, improving our ability to forecast stock performance relative to the S&P 500.

import numpy as np
import math
import re
import datetime
from financial_statement_pipeline.data import get_company_facts, extract_account_data, get_company_sic


def extract_company_account_data(company_facts, account_name, year):
    account_data = extract_account_data(company_facts, account_name)

    for date, value in account_data.items():
        if datetime.datetime.strptime(date, "%Y-%m-%d").year == year:
            return value

    return None

# Defining archetypes 
archetypes = [
    "Software/SaaS", # High GM, low CapEx, high R&D
    "Platform/Marketplace", # High GM, low inventory
    "Fabless Semiconductor", # High GM, low CapEx, high R&D
    "IDM Semiconductor/Foundry", # Moderate GM, high CapEx
    "Industrial Manufacturing", # Moderate GM, high CapEx, high inventory
    "Commodity Production", # Low GM, high CapEx, volatile margins
    "Retailer", # Low GM, high inventory, high inventory turnover
    "Consumer Brand", # Moderate GM, high SG&A expenses
    "Bank", # Interest income reliant 
    "Insurance", # Premiums reliant, Reserves reliant
    "Real Estate/Yield", # High assets, rental income reliant, FFO reliant
    "Biotech", # high R&D, negative earnings preprofit
    "Pharma" # high margins, high R&D
]

def extract_with_fallback(company_facts, tag_list, year):
    for tag in tag_list:
        value = extract_company_account_data(company_facts, tag, year)
        if value is not None:
            return value
    return None

# First, we will create rules to filter obvious archetypes. 
# We start with banks.

def is_bank(ticker, year):
    company_facts = get_company_facts(ticker)

    interest_fees_loans = extract_company_account_data(
        company_facts, "InterestAndFeeIncomeLoansAndLeases", year
    )

    noninterest_expense = extract_company_account_data(
        company_facts, "NoninterestExpense", year
    )

    interest_dividend_operating = extract_company_account_data(
        company_facts, "InterestAndDividendIncomeOperating", year
    )

    result = (
        interest_fees_loans is not None
        or (noninterest_expense is not None and interest_dividend_operating is not None)
    )

    print(f"{ticker}:{result}")
    return result

# We follow with real estate companies.

def is_REIT(ticker, year):
    result = get_company_sic(ticker) == 6798
    print(f"{ticker}: {result}")
    return result

# Next, identify insurance companies.

def is_insurance(ticker, year):
    company_facts = get_company_facts(ticker)

    premiums = extract_company_account_data(company_facts, "PremiumsEarnedNet", year)
    
    result = premiums is not None
    print(f"{ticker}:{result}")
    return result

# Business development companies, closed-end funds, and ETFs.



# Special purpose acquisition companies.

def is_SPAC(ticker, year):
    result = get_company_sic(ticker) == 6770
    print(f"{ticker}: {result}")
    return result

# Master limited partnerships.

def is_MLP(ticker, year):
    # MLPs have no dedicated SIC, identify via partnership-specific XBRL tag
    company_facts = get_company_facts(ticker)
    result = bool(extract_account_data(company_facts, "LimitedPartnersCapitalAccount"))
    print(f"{ticker}: {result}")
    return result

# Biotech companies.

def is_biotech(ticker, year):
    result = get_company_sic(ticker) in [2834, 2835, 2836, 8731]
    print(f"{ticker}: {result}")
    return result

# Mining, exploration companies.

def is_mining(ticker, year):
    result = get_company_sic(ticker) == 1040
    print(f"{ticker}: {result}")
    return result

# Utilities.

def is_utility(ticker, year):
    result = get_company_sic(ticker) in [4813, 4911, 4924, 4931]
    print(f"{ticker}: {result}")
    return result


