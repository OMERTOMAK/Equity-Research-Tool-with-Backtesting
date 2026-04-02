import pandas as pd
import yfinance as yf
from financial_statement_pipeline.data import extract_account_data, latest_value, latest_revenue, get_total_revenue, safe_divide


def yoy_growth(company_facts, account_name):
    if account_name == "Revenue":
        data = get_total_revenue(company_facts)
    else:
        data = extract_account_data(company_facts, account_name)

    if not data or len(data) < 2:
        return None

    sorted_dates = sorted(data.keys())
    current = float(data[sorted_dates[-1]].split(" ")[0])
    prior = float(data[sorted_dates[-2]].split(" ")[0])

    return safe_divide(current - prior, abs(prior))


def eps_yoy_growth(company_facts):
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

    return safe_divide(eps_current - eps_prior, abs(eps_prior))


def margin_change(company_facts, numerator_tag, denominator_tag):
    data_n = extract_account_data(company_facts, numerator_tag)
    data_d = extract_account_data(company_facts, denominator_tag)

    if not data_n or not data_d or len(data_n) < 2 or len(data_d) < 2:
        return None

    n_dates = sorted(data_n.keys())
    d_dates = sorted(data_d.keys())

    margin_current = safe_divide(float(data_n[n_dates[-1]].split(" ")[0]), float(data_d[d_dates[-1]].split(" ")[0]))
    margin_prior = safe_divide(float(data_n[n_dates[-2]].split(" ")[0]), float(data_d[d_dates[-2]].split(" ")[0]))

    return safe_divide(margin_current - margin_prior, abs(margin_prior))


def ebitda_yoy_growth(company_facts):
    ebit = extract_account_data(company_facts, "OperatingIncomeLoss")
    dep = extract_account_data(company_facts, "Depreciation")

    if not ebit or not dep or len(ebit) < 2 or len(dep) < 2:
        return None

    ebit_dates = sorted(ebit.keys())
    dep_dates = sorted(dep.keys())

    ebitda_current = float(ebit[ebit_dates[-1]].split(" ")[0]) + float(dep[dep_dates[-1]].split(" ")[0])
    ebitda_prior = float(ebit[ebit_dates[-2]].split(" ")[0]) + float(dep[dep_dates[-2]].split(" ")[0])

    return safe_divide(ebitda_current - ebitda_prior, abs(ebitda_prior))


def build_key_metrics(company_facts, ticker):
    security = yf.Ticker(ticker)

    key_metrics = {
        "net_income": latest_value(company_facts, "NetIncomeLoss"),
        "EBIT": latest_value(company_facts, "OperatingIncomeLoss"),
        "EBITDA": (latest_value(company_facts, "OperatingIncomeLoss") or 0)
                  + (latest_value(company_facts, "Depreciation") or 0)
                  + (latest_value(company_facts, "AmortizationOfIntangibleAssets") or 0),
        "Depreciation": latest_value(company_facts, "Depreciation"),
        "Amortization": latest_value(company_facts, "AmortizationOfIntangibleAssets"),
        "Basic EPS": safe_divide(
            (latest_value(company_facts, "NetIncomeLoss") - (latest_value(company_facts, "DividendsPreferredStock") or 0)),
            (latest_value(company_facts, "WeightedAverageNumberOfSharesOutstandingBasic") or 1)
        ),
        "Diluted EPS": safe_divide(
            (latest_value(company_facts, "NetIncomeLoss") - (latest_value(company_facts, "DividendsPreferredStock") or 0)),
            (latest_value(company_facts, "WeightedAverageNumberOfDilutedSharesOutstanding") or 1)
        ),
        "Trailing P/E": safe_divide(
            security.fast_info["last_price"],
            safe_divide(
                (latest_value(company_facts, "NetIncomeLoss") - (latest_value(company_facts, "DividendsPreferredStock") or 0)),
                (latest_value(company_facts, "WeightedAverageNumberOfDilutedSharesOutstanding") or 1)
            )
        ),
        "ROE": safe_divide(
            latest_value(company_facts, "NetIncomeLoss"),
            latest_value(company_facts, "StockholdersEquity")
        ),
        "Interest Coverage Ratio": safe_divide(
            latest_value(company_facts, "OperatingIncomeLoss"),
            latest_value(company_facts, "InterestExpense")
        ),
        "Operating Margin": safe_divide(
            latest_value(company_facts, "OperatingIncomeLoss"),
            latest_revenue(company_facts)
        )
    }

    return pd.Series(key_metrics)


def build_yoy_growth_metrics(company_facts):
    yoy_growth_rates = {
        "Revenue Growth": yoy_growth(company_facts, "Revenue"),
        "Gross Profit Growth": yoy_growth(company_facts, "GrossProfit"),
        "Net Income Growth": yoy_growth(company_facts, "NetIncomeLoss"),
        "EBIT Growth": yoy_growth(company_facts, "OperatingIncomeLoss"),
        "EBITDA Growth": ebitda_yoy_growth(company_facts),
        "ROE Growth": margin_change(company_facts, "NetIncomeLoss", "StockholdersEquity"),
        "EPS Growth": eps_yoy_growth(company_facts),
        "R&D Growth": yoy_growth(company_facts, "ResearchAndDevelopmentExpense"),
        "Operating Cash Flow Growth": yoy_growth(company_facts, "NetCashProvidedByUsedInOperatingActivities")
    }

    return pd.Series(yoy_growth_rates)