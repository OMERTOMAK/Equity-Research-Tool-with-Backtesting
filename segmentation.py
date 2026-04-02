# We have to segment companies based on their financial behavior, which we will define using financial archetypes.
# We will use K-means clustering to identify these archetypes based on key financial metrics. This segmentation will allow us to build more tailored predictive models for each group, improving our ability to forecast stock performance relative to the S&P 500.

import numpy as np
import math
import re
import datetime
from financial_statement_pipeline.data import get_company_facts, extract_account_data


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

def missing(x):
    return x is None or (isinstance(x, float) and math.isnan(x))

def to_number(x):
    if x is None:
        return None

    if isinstance(x, (int, float)):
        return float(x)

    if isinstance(x, str):
        x = x.strip()

        match = re.search(r'-?\d+(?:,\d{3})*(?:\.\d+)?', x)
        if not match:
            return None

        num_str = match.group(0).replace(",", "")
        return float(num_str)

    return None

def safe_div(a, b):
    a = to_number(a)
    b = to_number(b)

    if a is None or b is None or b == 0:
        return None
    return a / b

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def extract_with_fallback(company_facts, tag_list, year):
    for tag in tag_list:
        value = extract_company_account_data(company_facts, tag, year)
        if value is not None:
            return value
    return None

# First, we will create rules to filter obvious archetypes. 
# We start with banks.

# Interest income and revenues have a lot of variation in how they are tagged.

INTEREST_INCOME_TAGS = [
    "InterestAndDividendIncomeOperating",
    "InterestIncome",
    "InterestIncomeOperating",
    "InterestAndFeeIncomeLoans",
]

REVENUE_TAGS = [
    "Revenues",
    "RevenuesNetOfInterestExpense",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet"
]

def is_bank(ticker, year):
    company_facts = get_company_facts(ticker)

    print()
    # Interest Income / Revenue
    interest_income_ratio = safe_div(extract_with_fallback(company_facts, INTEREST_INCOME_TAGS, year), extract_with_fallback(company_facts, REVENUE_TAGS, year))
    print(f"Interest Income Ratio: {interest_income_ratio}")
    if interest_income_ratio is None:
        print(f"interest_income: {extract_with_fallback(company_facts, INTEREST_INCOME_TAGS, year)}, revenue: {extract_with_fallback(company_facts, REVENUE_TAGS, year)}")
    # Deposits / Liabilities
    deposits_to_liabilities_ratio = safe_div(extract_company_account_data(company_facts, "Deposits", year), extract_company_account_data(company_facts, "Liabilities", year))
    print(f"Deposits to Liabilities Ratio: {deposits_to_liabilities_ratio}")
    # Leverage (Assets / Equity)
    leverage = safe_div(extract_company_account_data(company_facts, "Assets", year), extract_company_account_data(company_facts, "StockholdersEquity", year))
    print(f"Leverage: {leverage}")

    if (
    missing(interest_income_ratio) or
    missing(deposits_to_liabilities_ratio) or
    missing(leverage)
):
        print(False)
        return False
    
    else:
        
        score = score = (
        3 * interest_income_ratio +
        2 * deposits_to_liabilities_ratio +
        1 * leverage
    )

        p_bank = sigmoid(score - 3)
        print(f"{ticker} - Bank Score: {score:.2f}, P(Bank): {p_bank:.2f}")

        print(p_bank > 0.7)
        return p_bank > 0.7

# We follow with real estate companies.

REAL_ESTATE_TAGS = [
    "RealEstateInvestmentsNet",
    "RealEstateInvestmentPropertyNet",
    "InvestmentPropertyNet"
]

PROPERTY_REIT_TAGS = [
    "RealEstateInvestmentsNet",
    "RealEstateInvestmentPropertyNet",
    "InvestmentPropertyNet"
]

INFRASTRUCTURE_ASSET_TAGS = [
    "PropertyPlantAndEquipmentNet"
]

def is_reit(ticker, year):
    company_facts = get_company_facts(ticker)

    assets = extract_company_account_data(company_facts, "Assets", year)
    revenue = extract_with_fallback(company_facts, REVENUE_TAGS, year)
    equity = extract_company_account_data(company_facts, "StockholdersEquity", year)

    property_assets = extract_with_fallback(company_facts, PROPERTY_REIT_TAGS, year)
    infrastructure_assets = extract_with_fallback(company_facts, INFRASTRUCTURE_ASSET_TAGS, year)

    property_asset_ratio = safe_div(property_assets, assets)
    infrastructure_asset_ratio = safe_div(infrastructure_assets, assets)
    asset_to_revenue_ratio = safe_div(assets, revenue)
    leverage = safe_div(assets, equity)

    print(f"Property Asset Ratio: {property_asset_ratio}")
    print(f"Infrastructure Asset Ratio: {infrastructure_asset_ratio}")
    print(f"Asset to Revenue Ratio: {asset_to_revenue_ratio}")
    print(f"Leverage: {leverage}")

    # Classic property REITs: PLD, SPG, O, PSA, AVB, etc.
    property_reit = (
        not missing(property_asset_ratio) and property_asset_ratio > 0.5 and
        not missing(asset_to_revenue_ratio) and asset_to_revenue_ratio > 4
    )

    # Infrastructure REITs: AMT, EQIX, DLR-like names
    infrastructure_reit = (
        missing(property_asset_ratio) and
        not missing(infrastructure_asset_ratio) and infrastructure_asset_ratio > 0.5 and
        not missing(asset_to_revenue_ratio) and asset_to_revenue_ratio > 3 and
        not missing(leverage) and leverage > 1.5
    )

    result = property_reit or infrastructure_reit
    print(result)
    return result

is_reit("PLD", 2022)   # Prologis (industrial/logistics)
is_reit("AMT", 2022)   # American Tower (cell towers)
is_reit("EQIX", 2022)  # Equinix (data centers)
is_reit("SPG", 2022)   # Simon Property (malls)
is_reit("O", 2022)     # Realty Income (net lease)