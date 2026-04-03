import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

headers = {
    "User-Agent": "Kagan Tomak omertomak@gmail.com"
}

REVENUE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet"
]

FORM_TYPES = ["10-K", "20-F", "40-F", "10-K/A", "20-F/A", "40-F/A"]
ACCOUNTING_RULES = ["us-gaap", "ifrs-full"]


def get_cik(ticker, headers=headers):
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=headers)
    data = response.json()

    for item in data.values():
        if item["ticker"].upper() == ticker.upper():
            return str(item["cik_str"]).zfill(10)
    return None


def get_company_facts(ticker, headers=headers):
    cik = get_cik(ticker, headers)
    if cik is None:
        return None

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    return response.json()

def get_company_sic(ticker, headers=headers):
    cik = get_cik(ticker, headers)
    if cik is None:
        return None
    
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    sic = response.json().get("sic", None)
    
    if not sic:
        return None
    
    return int(sic)

def extract_account_data(company_facts, account_name, years=5):
    if company_facts is None:
        return {}

    current_day = datetime.now().date()
    cutoff_day = current_day - relativedelta(years=years)

    account_data = {}

    for rule in ACCOUNTING_RULES:
        if rule in company_facts["facts"] and account_name in company_facts["facts"][rule]:
            units = company_facts["facts"][rule][account_name]["units"]

            for currency, facts_list in units.items():
                for f in facts_list:
                    if f.get("form") in FORM_TYPES and f.get("end"):
                        end_date = datetime.strptime(f["end"], "%Y-%m-%d").date()
                        if cutoff_day <= end_date <= current_day:
                            account_data[f["end"]] = f'{f["val"]} ({currency})'

    return account_data


def latest_value(company_facts, account_name):
    account_data = extract_account_data(company_facts, account_name)
    if not account_data:
        return None

    latest_date = max(account_data.keys())
    return float(account_data[latest_date].split(" ")[0])


def get_total_revenue(company_facts):
    if company_facts is None:
        return None

    for tag in REVENUE_TAGS:
        for rule in ACCOUNTING_RULES:
            if rule in company_facts["facts"] and tag in company_facts["facts"][rule]:
                data = extract_account_data(company_facts, tag)
                if data:
                    return data
    return None


def latest_revenue(company_facts):
    data = get_total_revenue(company_facts)
    if not data:
        return None

    latest_date = max(data.keys())
    return float(data[latest_date].split(" ")[0])


def safe_divide(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b