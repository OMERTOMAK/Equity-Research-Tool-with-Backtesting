import pandas as pd
from financial_statement_pipeline.data import get_company_facts
from financial_statement_pipeline.statements import build_balance_sheet, build_income_statement, build_cash_flow_statement
from financial_statement_pipeline.metrics import build_key_metrics, build_yoy_growth_metrics

pd.set_option('display.float_format', lambda x: f'{x:,.0f}')
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 120)

ticker = "INTC"
company_facts = get_company_facts(ticker)

balance_sheet_df = build_balance_sheet(company_facts)
income_statement_df = build_income_statement(company_facts)
cash_flow_statement_df = build_cash_flow_statement(company_facts)

key_metrics = build_key_metrics(company_facts, ticker)
yoy_growth = build_yoy_growth_metrics(company_facts)

print(balance_sheet_df)
print()
print(income_statement_df)
print()
print(cash_flow_statement_df)
print()
print(key_metrics)
print()
print(yoy_growth)