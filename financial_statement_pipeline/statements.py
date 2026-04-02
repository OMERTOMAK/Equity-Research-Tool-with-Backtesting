import pandas as pd
from financial_statement_pipeline.data import extract_account_data, get_total_revenue


def build_balance_sheet(company_facts):
    balance_sheet = {
        "cash": extract_account_data(company_facts, "CashAndCashEquivalentsAtCarryingValue"),
        "short_term_investments": extract_account_data(company_facts, "MarketableSecuritiesCurrent"),
        "accounts_receivable": extract_account_data(company_facts, "AccountsReceivableNetCurrent"),
        "other_receivables": extract_account_data(company_facts, "OtherReceivablesCurrent"),
        "total_net_inventory": extract_account_data(company_facts, "InventoryNet"),
        "raw_materials": extract_account_data(company_facts, "InventoryRawMaterials"),
        "work_in_process": extract_account_data(company_facts, "InventoryWorkInProcess"),
        "finished_goods": extract_account_data(company_facts, "InventoryFinishedGoods"),
        "other_current_assets": extract_account_data(company_facts, "OtherAssetsCurrent"),
        "TOTAL_CURRENT_ASSETS": extract_account_data(company_facts, "AssetsCurrent"),

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

        "short_term_debt": extract_account_data(company_facts, "ShortTermBorrowings"),
        "current_long_term_debt": extract_account_data(company_facts, "LongTermDebtCurrent"),
        "accounts_payable": extract_account_data(company_facts, "AccountsPayableCurrent"),
        "accrued_payroll": extract_account_data(company_facts, "AccruedLiabilitiesCurrent"),
        "income_taxes_payable": extract_account_data(company_facts, "TaxesPayableCurrent"),
        "other_current_liabilities": extract_account_data(company_facts, "OtherLiabilitiesCurrent"),
        "TOTAL_CURRENT_LIABILITIES": extract_account_data(company_facts, "LiabilitiesCurrent"),

        "long_term_debt": extract_account_data(company_facts, "LongTermDebtNoncurrent"),
        "lease_obligations": extract_account_data(company_facts, "OperatingLeaseLiabilityNoncurrent"),
        "deferred_taxes": extract_account_data(company_facts, "DeferredTaxLiabilitiesNet"),
        "deferred_income": extract_account_data(company_facts, "ContractWithCustomerLiabilityNoncurrent"),
        "other_long_term_liabilities": extract_account_data(company_facts, "OtherLiabilitiesNoncurrent"),
        "TOTAL_LONG_TERM_LIABILITIES": extract_account_data(company_facts, "LiabilitiesNoncurrent"),
        "TOTAL_LIABILITIES": extract_account_data(company_facts, "Liabilities"),

        "common_stock": extract_account_data(company_facts, "CommonStockValue"),
        "common_stock_APIC": extract_account_data(company_facts, "AdditionalPaidInCapital"),
        "retained_earnings": extract_account_data(company_facts, "RetainedEarningsAccumulatedDeficit"),
        "treasury_stock": extract_account_data(company_facts, "TreasuryStockValue"),
        "accumulated_other_comprehensive_income_or_loss": extract_account_data(company_facts, "AccumulatedOtherComprehensiveIncomeLoss"),
        "minority_interest": extract_account_data(company_facts, "MinorityInterest"),
        "total_equity": extract_account_data(company_facts, "StockholdersEquity"),
        "TOTAL_LIABILITIES_AND_STOCKHOLDERS_EQUITY": extract_account_data(company_facts, "LiabilitiesAndStockholdersEquity")
    }

    return pd.DataFrame(balance_sheet).T


def build_income_statement(company_facts):
    income_statement = {
        "revenues": get_total_revenue(company_facts),
        "cost_of_goods_sold": extract_account_data(company_facts, "CostOfGoodsSold"),
        "gross_profit": extract_account_data(company_facts, "GrossProfit"),
        "depreciation_and_amortization": extract_account_data(company_facts, "DepreciationAndAmortization"),
        "depreciation": extract_account_data(company_facts, "Depreciation"),
        "amortization": extract_account_data(company_facts, "AmortizationOfIntangibleAssets"),
        "sg_and_a": extract_account_data(company_facts, "SellingGeneralAndAdministrativeExpense"),
        "r_and_d": extract_account_data(company_facts, "ResearchAndDevelopmentExpense"),
        "operating_income_or_ebit": extract_account_data(company_facts, "OperatingIncomeLoss"),
        "net_nonoperating_income_or_expense": extract_account_data(company_facts, "NonoperatingIncomeExpense"),
        "interest_income": extract_account_data(company_facts, "InterestIncome"),
        "other_non_operating_income_or_expense": extract_account_data(company_facts, "OtherNonoperatingIncomeExpense"),
        "interest_expense": extract_account_data(company_facts, "InterestExpense"),
        "capitalized_interest": extract_account_data(company_facts, "InterestCapitalized"),
        "impairments": extract_account_data(company_facts, "AssetImpairmentCharges"),
        "goodwill_impairment": extract_account_data(company_facts, "ImpairmentOfGoodwill"),
        "restructuring_charges": extract_account_data(company_facts, "RestructuringCharges"),
        "unrealized_gain_loss_on_investments": extract_account_data(company_facts, "UnrealizedGainLossOnInvestments"),
        "unrealized_gain_loss_on_derivatives": extract_account_data(company_facts, "UnrealizedGainLossOnDerivatives"),
        "debt_restructuring_charges": extract_account_data(company_facts, "GainLossOnDebtExtinguishment"),
        "pretax_income_or_ebt": extract_account_data(company_facts, "IncomeBeforeIncomeTaxes"),
        "income_tax_expense_benefit": extract_account_data(company_facts, "IncomeTaxExpenseBenefit"),
        "income_loss_from_equity_method_investments": extract_account_data(company_facts, "IncomeLossFromEquityMethodInvestments"),
        "net_income": extract_account_data(company_facts, "NetIncomeLoss"),
        "noncontrolling_interest_net_income_loss": extract_account_data(company_facts, "NetIncomeLossAttributableToNoncontrollingInterest"),
        "common_stockholders_net_income_loss": extract_account_data(company_facts, "NetIncomeLossAvailableToCommonStockholders")
    }

    return pd.DataFrame(income_statement).T


def build_cash_flow_statement(company_facts):
    cash_flow_statement = {
        "net_income": extract_account_data(company_facts, "NetIncomeLoss"),
        "depreciation_depletion_and_amortization": extract_account_data(company_facts, "DepreciationDepletionAndAmortization"),
        "depreciation": extract_account_data(company_facts, "Depreciation"),
        "depletion": extract_account_data(company_facts, "Depletion"),
        "amortization": extract_account_data(company_facts, "AmortizationOfIntangibleAssets"),
        "deferred_income_tax_expense_benefit": extract_account_data(company_facts, "DeferredIncomeTaxExpenseBenefit"),
        "receivables": extract_account_data(company_facts, "IncreaseDecreaseInAccountsAndOtherReceivables"),
        "inventories": extract_account_data(company_facts, "IncreaseDecreaseInInventories"),
        "accounts_payable": extract_account_data(company_facts, "IncreaseDecreaseInAccountsPayable"),
        "other_assets_and_liabilities": extract_account_data(company_facts, "IncreaseDecreaseInOtherOperatingAssetsAndLiabilities"),
        "net_cash_from_operating_activities": extract_account_data(company_facts, "NetCashProvidedByUsedInOperatingActivities"),
        "capital_expenditures": extract_account_data(company_facts, "PaymentsToAcquirePropertyPlantAndEquipment"),
        "net_assets_from_acquisitions": extract_account_data(company_facts, "PaymentsToAcquireBusinessesNetOfCashAcquired"),
        "proceeds_from_sale_of_PPE": extract_account_data(company_facts, "ProceedsFromSaleOfPropertyPlantAndEquipment"),
        "proceeds_from_sale_of_business": extract_account_data(company_facts, "ProceedsFromSaleOfBusiness"),
        "purchase_of_investments": extract_account_data(company_facts, "PaymentsToAcquireAvailableForSaleSecurities"),
        "sale_or_maturity_of_investments": extract_account_data(company_facts, "ProceedsFromSaleAndMaturityOfAvailableForSaleSecurities"),
        "net_cash_from_investing_activities": extract_account_data(company_facts, "NetCashProvidedByUsedInInvestingActivities"),
        "cash_dividends_paid": extract_account_data(company_facts, "PaymentsOfDividends"),
        "common_dividends": extract_account_data(company_facts, "PaymentsOfDividendsCommonStock"),
        "treasury_stock_purchase": extract_account_data(company_facts, "PaymentsForRepurchaseOfCommonStock"),
        "sale_of_common_stock": extract_account_data(company_facts, "ProceedsFromIssuanceOfCommonStock"),
        "stock_options_proceeds": extract_account_data(company_facts, "ProceedsFromStockOptionsExercised"),
        "issuance_of_long_term_debt": extract_account_data(company_facts, "ProceedsFromIssuanceOfLongTermDebt"),
        "reduction_in_long_term_debt": extract_account_data(company_facts, "RepaymentsOfLongTermDebt"),
        "net_cash_from_financing_activities": extract_account_data(company_facts, "NetCashProvidedByUsedInFinancingActivities"),
        "exchange_rate_effect": extract_account_data(company_facts, "EffectOfExchangeRateOnCashAndCashEquivalents"),
        "net_change_in_cash": extract_account_data(company_facts, "CashAndCashEquivalentsPeriodIncreaseDecrease")
    }

    return pd.DataFrame(cash_flow_statement).T