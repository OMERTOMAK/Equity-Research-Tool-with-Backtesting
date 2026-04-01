# We have to segment companies based on their financial behavior, which we will define using financial archetypes.
# We will use K-means clustering to identify these archetypes based on key financial metrics. This segmentation will allow us to build more tailored predictive models for each group, improving our ability to forecast stock performance relative to the S&P 500.

import numpy as np
import re
import math
from financial_statements import get_cik
from financial_statements import get_financial_statements
from financial_statements import extract_account_data
import datetime 

def extract_company_account_data(ticker, account_name, year):
    cik = get_cik (ticker)
    financial_statements = get_financial_statements(cik)
    account_data = extract_account_data(financial_statements, account_name)

    for date in account_data.keys():
        if datetime.datetime.strptime(date, "%Y-%m-%d").year == year:
            return account_data[date]

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

# First, we will create rules to filter obvious archetypes. 
# We start with banks.

BANK_TICKERS = [
    "JPM", "BAC", "WFC", "C",
    "GS", "MS",
    "BK", "STT",
    "USB", "PNC", "TFC", "COF",
    "RF", "FITB", "KEY", "HBAN",
    "CFG", "MTB", "ZION", "CMA"
]


def is_bank(ticker, year):
    
    print(extract_company_account_data(ticker, "InterestAndDividendIncomeOperating", year))
    print(extract_company_account_data(ticker, "Revenues", year))
    interest_income_ratio = safe_div(extract_company_account_data(ticker, "InterestAndDividendIncomeOperating", year), extract_company_account_data(ticker, "Revenues", year))
    print(interest_income_ratio)
    print()
    print(extract_company_account_data(ticker, "PaymentsForOriginationAndPurchasesOfLoansHeldForSale", year))
    print(extract_company_account_data(ticker, "Assets", year))
    loans_to_assets_ratio = safe_div(extract_company_account_data(ticker, "PaymentsForOriginationAndPurchasesOfLoansHeldForSale", year), extract_company_account_data(ticker, "Assets", year))
    print(loans_to_assets_ratio)
    print()
    print(extract_company_account_data(ticker, "Deposits", year))
    print(extract_company_account_data(ticker, "Liabilities", year))
    deposits_to_liabilities_ratio = safe_div(extract_company_account_data(ticker, "Deposits", year), extract_company_account_data(ticker, "Liabilities", year))
    print(deposits_to_liabilities_ratio)
    print()
    print(extract_company_account_data(ticker, "Assets", year))
    print(extract_company_account_data(ticker, "StockholdersEquity", year))
    leverage = safe_div(extract_company_account_data(ticker, "Assets", year), extract_company_account_data(ticker, "StockholdersEquity", year))
    print(leverage)

    if (
    missing(interest_income_ratio) or
    missing(loans_to_assets_ratio) or
    missing(deposits_to_liabilities_ratio) or
    missing(leverage)
):
        print(False)
        return False
    
    else:
        
        score = score = (
        3 * interest_income_ratio +
        2 * loans_to_assets_ratio +
        2 * deposits_to_liabilities_ratio +
        1 * leverage
    )

        p_bank = sigmoid(score - 3)
        print(f"{ticker} - Bank Score: {score:.2f}, P(Bank): {p_bank:.2f}")

        print(p_bank > 0.7)
        return p_bank > 0.7

is_bank("BAC", 2022)
is_bank("MU", 2022)