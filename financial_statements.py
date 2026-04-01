import pandas as pd
import matplotlib.pyplot as plt
import requests
import yfinance as yf

security = yf.Ticker("INTC")

# Can't access SEC data without this
headers = {
    "User-Agent": "Kagan Tomak omertomak@gmail.com"
}

# Accessing financial statements of selected company
# SEC stores stocks using CIK numbers, must retrieve CIK number first

def get_cik(security, headers=headers):
    url = "https://www.sec.gov/files/company_tickers.json"
    # Requesting access to SEC API, saving response in a variable
    # For future ref, SEC returns data in JSON text format; JSON text has the syntax of a Python dictionary; We convert JSON text into a JavaScript object, in our case a Python dict since we use Python
    response = requests.get(url, headers=headers)
    data = response.json()
    # Each item in the dictionary is key: {CIK, ticker, ...}. So, we're dealing with nested dictionaries.
    for item in data.values():
        if item["ticker"].upper() == security:
            # "cik_str" --> CIK number
            cik_str = str(item["cik_str"])
            # CIK numbers are 10 digits long but they almost always have leading zeroes, which are omitted by default in SEC API, which we must add back.
            # zfill(x) adds zeroes to the left until the length is x, very useful!
            cik_str = cik_str.zfill(10)
            return cik_str
    return None

# Now, we fetch

def get_financial_statements(cik, headers=headers):
    if cik is None:
        return None
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    # Saving company facts data in a variable, converting from JSON text to Python dict
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

company_facts = get_financial_statements(get_cik("INTC", headers), headers)

# 1: We want the accounts data, which can be found in either "us-gaap" or "ifrs-full".
# 2: We want only annual data, filtering by form type [10-K, 20-F, 40-F, 10-K/A, 20-F/A, 40-F/A].
# 3: We have to express values in correct currency.
# 4: We want to get the values for the last 3 years, or the company lifetime if < 3 years.

from datetime import datetime
from dateutil.relativedelta import relativedelta

current_day = datetime.now().date()
five_years_ago = current_day - relativedelta(years=5)


def extract_account_data(company_facts, account_name):
    account_data = {}
    accounting_rules = ["us-gaap", "ifrs-full"]
    form_types = ["10-K", "20-F", "40-F", "10-K/A", "20-F/A", "40-F/A"]
    for rule in accounting_rules:
        if rule in company_facts["facts"]:
            if account_name in company_facts["facts"][rule]:
                currency = next(iter(company_facts["facts"][rule][account_name]["units"]))
                for f in company_facts["facts"][rule][account_name]["units"][currency]:
                    if f["form"] in form_types:
                        if "end" in f and f["end"] is not None:
                            if five_years_ago <= datetime.strptime(f["end"], "%Y-%m-%d").date() <= current_day:
                                account_data[f["end"]] = f'{f["val"]} ({currency})'
    return account_data

def latest_value(account_name):
    account_data = extract_account_data(company_facts, account_name)
    if not account_data:
        return None
    latest_date = max(account_data.keys())
    return float(account_data[latest_date].split(" ")[0])

# Forming the balance sheet 
balance_sheet = {
    # Assets
        # Current Assets
    "cash": extract_account_data(company_facts, "CashAndCashEquivalentsAtCarryingValue"),
    "short_term_investments": extract_account_data(company_facts, "MarketableSecuritiesCurrent"),
    "accounts_receivable": extract_account_data(company_facts, "AccountsReceivableNetCurrent"),
    "other_receivables": extract_account_data(company_facts, "OtherReceivablesCurrent"),
    "total_net_inventory": extract_account_data(company_facts, "InventoryNet"),
    "raw_materials": extract_account_data(company_facts, "InventoryRawMaterials"),
    "wok_in_process": extract_account_data(company_facts, "InventoryWorkInProcess"),
    "finished_goods": extract_account_data(company_facts, "InventoryFinishedGoods"),
    "other_current_assets": extract_account_data(company_facts, "OtherAssetsCurrent"),
    "TOTAL_CURRENT_ASSETS": extract_account_data(company_facts, "AssetsCurrent"),
        # Non-Current Assets
    "PP&E": extract_account_data(company_facts, "PropertyPlantAndEquipmentNet"),
    "Buildings": extract_account_data(company_facts, "BuildingsNet"),
    "Land": extract_account_data(company_facts, "LandAndImprovements"),
    "Machinery": extract_account_data(company_facts, "MachineryNet"),
    "Accumulated_Depreciation": extract_account_data(company_facts, "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment"),
    "Long_term_investments": extract_account_data(company_facts, "LongTermInvestments"),
    "Investment_in_affiliates": extract_account_data(company_facts, "EquityMethodInvestments"),
    "Goodwill": extract_account_data(company_facts, "Goodwill"),
    "Net_intangible_assets_excluding_goodwill": extract_account_data(company_facts, "IntangibleAssetsNetExcludingGoodwill"),
    "Deferred_tax_assets": extract_account_data(company_facts, "DeferredTaxAssetsNet"),
    "Other_non_current_assets": extract_account_data(company_facts, "OtherAssetsNoncurrent"),
    "TOTAL_NONCURRENT_ASSETS": extract_account_data(company_facts, "AssetsNoncurrent"),
    "TOTAL_ASSETS": extract_account_data(company_facts, "Assets"),
    # Liabilities
        # Current Liabilities
    "short_term_debt": extract_account_data(company_facts, "ShortTermBorrowings"),
    "current_long_term_debt": extract_account_data(company_facts, "LongTermDebtCurrent"),
    "accounts_payable": extract_account_data(company_facts, "AccountsPayableCurrent"),
    "accrued_payroll": extract_account_data(company_facts, "AccruedLiabilitiesCurrent"),
    "income_taxes_payable": extract_account_data(company_facts, "TaxesPayableCurrent"),
    "other_current_liabilities": extract_account_data(company_facts, "OtherLiabilitiesCurrent"),
    "TOTAL_CURRENT_LIABILITIES": extract_account_data(company_facts, "LiabilitiesCurrent"),
        # Long_term Liabilities
    "long_term_debt": extract_account_data(company_facts, "LongTermDebtNoncurrent"),
    "lease_obligations": extract_account_data(company_facts, "OperatingLeaseLiabilityNoncurrent"),
    "deferred_taxes": extract_account_data(company_facts, "DeferredTaxLiabilitiesNet"),
    "deferred_income": extract_account_data(company_facts, "ContractWithCustomerLiabilityNoncurrent"),
    "other_long_term_liabilities": extract_account_data(company_facts, "OtherLiabilitiesNoncurrent"),
    "TOTAL_LONG_TERM_LIABILITIES": extract_account_data(company_facts, "LiabilitiesNoncurrent"),
    "TOTAL_LIABILITIES": extract_account_data(company_facts, "Liabilities"),
    # Equity
        # Common Equity
    "common_stock": extract_account_data(company_facts, "CommonStockValue"),
    "common_stock_APIC": extract_account_data(company_facts, "AdditionalPaidInCapital"),
    "retained_earnings": extract_account_data(company_facts, "RetainedEarningsAccumulatedDeficit"),
    "treasury_stock": extract_account_data(company_facts, "TreasuryStockValue"),
    "accumulated_other_comprehensive_income_or_loss": extract_account_data(company_facts, "AccumulatedOtherComprehensiveIncomeLoss"),
    "minority_interest": extract_account_data(company_facts, "MinorityInterest"),
    "total_equity": extract_account_data(company_facts, "StockholdersEquity"),
    "TOTAL_LIABILITIES_AND_STOCKHOLDERS_EQUITY": extract_account_data(company_facts, "LiabilitiesAndStockholdersEquity")
}

balance_sheet_df = pd.DataFrame(balance_sheet).T

# Revenue reporting can be very inconsistent across companies, so we have to check multiple tags.
REVENUE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet"
]

def get_total_revenue(facts):
    for tag in REVENUE_TAGS:
        for rule in ["us-gaap", "ifrs-full"]:
            if rule in facts["facts"] and tag in facts["facts"][rule]:
                data = extract_account_data(facts, tag)
                if data:
                    return data
    return None

def latest_revenue():
    data = get_total_revenue(company_facts)
    if not data:
        return None
    latest_date = max(data.keys())
    return float(data[latest_date].split(" ")[0])

# Forming the income statement
income_statement = {
    # Going from the top line to the bottom line, first subtracting COGS from sales to get gross profit.
    "revenues": get_total_revenue(company_facts),
    "cost_of_goods_sold": extract_account_data(company_facts, "CostOfGoodsSold"),
    "gross_profit": extract_account_data(company_facts, "GrossProfit"),
    # Now, we subtract operating expenses (Depreciation & Amortization, SG&A, R&D) from gross profit to get operating income (EBIT).
    "depreciation_and_amortization": extract_account_data(company_facts, "DepreciationAndAmortization"),
    "depreciation": extract_account_data(company_facts, "Depreciation"),
    "amortization": extract_account_data(company_facts, "AmortizationOfIntangibleAssets"),
    "sg_and_a": extract_account_data(company_facts, "SellingGeneralAndAdministrativeExpense"),
    "r_and_d": extract_account_data(company_facts, "ResearchAndDevelopmentExpense"),
    "operating_income_or_ebit": extract_account_data(company_facts, "OperatingIncomeLoss"),
    # Now, we add/subtract non-operating income/expense to/from EBIT to get EBT.
    # First non-operating income/expenses.
    "net_nonoperating_income_or_expense": extract_account_data(company_facts, "NonoperatingIncomeExpense"),
    "interest_income": extract_account_data(company_facts, "InterestIncome"),
    "other_non_operating_income_or_expense": extract_account_data(company_facts, "OtherNonoperatingIncomeExpense"),
    # Then, interest expenses.
    "interest_expense": extract_account_data(company_facts, "InterestExpense"),
    "capitalized_interest": extract_account_data(company_facts, "InterestCapitalized"),
    # Then, unusual expenses.
    "impairments": extract_account_data(company_facts, "AssetImpairmentCharges"),
    "goodwill_impairment": extract_account_data(company_facts, "ImpairmentOfGoodwill"),
    "restructuring_charges": extract_account_data(company_facts, "RestructuringCharges"),
        # Unrealized valuation gains/losses.
    "unrealized_gain_loss_on_investments": extract_account_data(company_facts, "UnrealizedGainLossOnInvestments"),
    "unrealized_gain_loss_on_derivatives": extract_account_data(company_facts, "UnrealizedGainLossOnDerivatives"),
        # Exceptional charges - others. 
    "debt_restructuring_charges": extract_account_data(company_facts, "GainLossOnDebtExtinguishment"),
    # Now, we have subtracted all operating and non-operating expenses from EBIT, we can get EBT.
    "pretax_income_or_ebt": extract_account_data(company_facts, "IncomeBeforeIncomeTaxes"),
    "income_tax_expense_benefit": extract_account_data(company_facts, "IncomeTaxExpenseBenefit"),
    "income_loss_from_equity_method_investments": extract_account_data(company_facts, "IncomeLossFromEquityMethodInvestments"),
    # Finally, we subtract income tax expense from EBT to get net income.
    "net_income": extract_account_data(company_facts, "NetIncomeLoss"),
    "noncontrolling_interest_net_income_loss": extract_account_data(company_facts, "NetIncomeLossAttributableToNoncontrollingInterest"),
    "common_stockholders_net_income_loss": extract_account_data(company_facts, "NetIncomeLossAvailableToCommonStockholders")
}

income_statement_df = pd.DataFrame(income_statement).T

# Forming the cash flow statement
cash_flow_statement = {
    # Cash flows from operating activities
    "net_income": extract_account_data(company_facts, "NetIncomeLoss"),
    "depreciation_depletion_and_amortization": extract_account_data(company_facts, "DepreciationDepletionAndAmortization"),
    "depreciation": extract_account_data(company_facts, "Depreciation"),
    "depletion": extract_account_data(company_facts, "Depletion"),
    "amortization": extract_account_data(company_facts, "AmortizationOfIntangibleAssets"),
    "deferred_income_tax_expense_benefit": extract_account_data(company_facts, "DeferredIncomeTaxExpenseBenefit"),
        # Changes in working capital accounts
    "receivables": extract_account_data(company_facts, "IncreaseDecreaseInAccountsAndOtherReceivables"),
    "inventories": extract_account_data(company_facts, "IncreaseDecreaseInInventories"),
    "accounts_payable": extract_account_data(company_facts, "IncreaseDecreaseInAccountsPayable"),
    "other_assets_and_liabilities": extract_account_data(company_facts, "IncreaseDecreaseInOtherOperatingAssetsAndLiabilities"),
    "net_cash_from_operating_activities": extract_account_data(company_facts, "NetCashProvidedByUsedInOperatingActivities"),
    # Cash flows from investing activities
    "capital_expenditures": extract_account_data(company_facts, "PaymentsToAcquirePropertyPlantAndEquipment"),
    "net_assets_from_acquisitions": extract_account_data(company_facts, "PaymentsToAcquireBusinessesNetOfCashAcquired"),
    "proceeds_from_sale_of_PPE": extract_account_data(company_facts, "ProceedsFromSaleOfPropertyPlantAndEquipment"),
    "proceeds_from_sale_of_business": extract_account_data(company_facts, "ProceedsFromSaleOfBusiness"),
    "purchase_of_investments": extract_account_data(company_facts, "PaymentsToAcquireAvailableForSaleSecurities"),
    "sale_or_maturity_of_investments": extract_account_data(company_facts, "ProceedsFromSaleAndMaturityOfAvailableForSaleSecurities"),
    "net_cash_from_investing_activities": extract_account_data(company_facts, "NetCashProvidedByUsedInInvestingActivities"),
    # Cash flows from financing activities
    "cash_dividends_paid": extract_account_data(company_facts, "PaymentsOfDividends"),
    "common_dividends": extract_account_data(company_facts, "PaymentsOfDividendsCommonStock"),
    "treasury_stock_purchase": extract_account_data(company_facts, "PaymentsForRepurchaseOfCommonStock"),
    "sale_of_common_stock": extract_account_data(company_facts, "ProceedsFromIssuanceOfCommonStock"),
    "stock_options_proceeds": extract_account_data(company_facts, "ProceedsFromStockOptionsExercised"),
    "issuance_of_long_term_debt": extract_account_data(company_facts, "ProceedsFromIssuanceOfLongTermDebt"),
    "reduction_in_long_term_debt": extract_account_data(company_facts, "RepaymentsOfLongTermDebt"),
    "net_cash_from_financing_activities": extract_account_data(company_facts, "NetCashProvidedByUsedInFinancingActivities"),
    # All activities
    "exchange_rate_effect": extract_account_data(company_facts, "EffectOfExchangeRateOnCashAndCashEquivalents"),
    "net_change_in_cash": extract_account_data(company_facts, "CashAndCashEquivalentsPeriodIncreaseDecrease")
}

cash_flow_statement_df = pd.DataFrame(cash_flow_statement).T

# Now that the financial statements are ready, we can calculate important metrics for the LAST YEAR and determine the viability of an investment in this stock.
# We have already calculated some of these, but we will initialize them here once more. 

def safe_divide(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b

key_metrics = {
    "net_income": latest_value("NetIncomeLoss"),
    "EBIT": latest_value("OperatingIncomeLoss"),
    "EBITDA": (latest_value("OperatingIncomeLoss") or 0) + (latest_value("Depreciation") or 0)  + (latest_value("AmortizationOfIntangibleAssets") or 0),
    "Depreciation": latest_value("Depreciation"),
    "Amortization": latest_value("AmortizationOfIntangibleAssets"),
    # Basic EPS = Net Income - Preferred Dividends/ Weighted Avg Common Shares Outstanding
    # Weighted Avg Common Shares Outstanding = (Beginning Common Shares Outstanding + Ending Common Shares Outstanding) / 2
    "Basic Earnings Per Share (EPS)": safe_divide((latest_value("NetIncomeLoss") - (latest_value("DividendsPreferredStock") or 0)), (latest_value("WeightedAverageNumberOfSharesOutstandingBasic") or 1)),
    # Diluted EPS = Net Income - Preferred Dividends/ Weighted Avg Common Shares Outstanding + Dilutive Potential Common Shares
    "Diluted Earnings Per Share (EPS)": safe_divide((latest_value("NetIncomeLoss") - (latest_value("DividendsPreferredStock") or 0)), (latest_value("WeightedAverageNumberOfDilutedSharesOutstanding") or 1)),
    # We use Diluted EPS to calculate P/E ratio. 
    # It must be noted that the P/E ratio continually changes as the stock price changes and is semi-periodic. 
    "Trailing P/E": safe_divide(security.fast_info["last_price"], safe_divide((latest_value("NetIncomeLoss") - (latest_value("DividendsPreferredStock") or 0)), (latest_value("WeightedAverageNumberOfDilutedSharesOutstanding") or 1))),
    "ROE": safe_divide(latest_value("NetIncomeLoss"), latest_value("StockholdersEquity")),
    "Interest Coverage Ratio": safe_divide(latest_value("OperatingIncomeLoss"), latest_value("InterestExpense")),
    "Operating Margin": safe_divide(latest_value("OperatingIncomeLoss"), latest_revenue())
}

key_metrics_df = pd.Series(key_metrics).T

def yoy_growth(account_name):
    if account_name == "Revenue":
        data = get_total_revenue(company_facts)
    else:
        data = extract_account_data(company_facts, account_name)
    if not data or len(data) < 2:
        return None
    sorted_dates = sorted(data.keys())
    current = float(data[sorted_dates[-1]].split(" ")[0])
    prior = float(data[sorted_dates[-2]].split(" ")[0])
    return safe_divide((current - prior), abs(prior)) 

def eps_yoy_growth():
    ni = extract_account_data(company_facts, "NetIncomeLossAvailableToCommonStockholders")
    shares = extract_account_data(company_facts, "WeightedAverageNumberOfDilutedSharesOutstanding")
    if not ni:
        ni = extract_account_data(company_facts, "NetIncomeLoss")
    if not ni or not shares or len(ni) < 2 or len(shares) < 2:
        return None
    ni_dates = sorted(ni.keys())
    sh_dates = sorted(shares.keys())
    eps_current = safe_divide(float(ni[ni_dates[-1]].split(" ")[0]), float(shares[sh_dates[-1]].split(" ")[0]))
    eps_prior = safe_divide(float(ni[ni_dates[-2]].split(" ")[0]), float(shares[sh_dates[-2]].split(" ")[0]))
    return safe_divide((eps_current - eps_prior), abs(eps_prior))

def margin_change(numerator_tag, denominator_tag):
    data_n = extract_account_data(company_facts, numerator_tag)
    data_d = extract_account_data(company_facts, denominator_tag)
    if not data_n or not data_d or len(data_n) < 2 or len(data_d) < 2:
        return None
    n_dates = sorted(data_n.keys())
    d_dates = sorted(data_d.keys())
    margin_current = safe_divide(float(data_n[n_dates[-1]].split(" ")[0]), float(data_d[d_dates[-1]].split(" ")[0]))
    margin_prior = safe_divide(float(data_n[n_dates[-2]].split(" ")[0]), float(data_d[d_dates[-2]].split(" ")[0]))
    return safe_divide((margin_current - margin_prior), abs(margin_prior))

def ebitda_yoy_growth():
    ebit = extract_account_data(company_facts, "OperatingIncomeLoss")
    da = extract_account_data(company_facts, "Depreciation")
    if not ebit or not da or len(ebit) < 2 or len(da) < 2:
        return None
    ebit_dates = sorted(ebit.keys())
    da_dates = sorted(da.keys())
    ebitda_current = float(ebit[ebit_dates[-1]].split(" ")[0]) + float(da[da_dates[-1]].split(" ")[0])
    ebitda_prior = float(ebit[ebit_dates[-2]].split(" ")[0]) + float(da[da_dates[-2]].split(" ")[0])
    return safe_divide((ebitda_current - ebitda_prior), abs(ebitda_prior))

yoy_growth_rates = {
    "Revenue Growth": yoy_growth("Revenue"),
    "Gross Profit Growth": yoy_growth("GrossProfit"), 
    "Net Income Growth": yoy_growth("NetIncomeLoss"),
    "EBIT Growth": yoy_growth("OperatingIncomeLoss"),
    "EBITDA Growth": ebitda_yoy_growth(),
    "ROE Growth": margin_change("NetIncomeLoss", "StockholdersEquity"),
    "EPS Growth": eps_yoy_growth(),  # EPS growth is essentially net income growth, since the number of shares outstanding doesn't change much year over year.
    "R&D Growth": yoy_growth("ResearchAndDevelopmentExpense"),
    "Operating Cash Flow Growth": yoy_growth("NetCashProvidedByUsedInOperatingActivities")
}
yoy_growth_rates_df = pd.Series(yoy_growth_rates).T

pd.set_option('display.float_format', lambda x: f'{x:,.0f}')
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 120)

print(key_metrics_df)
print(yoy_growth_rates_df)
 


