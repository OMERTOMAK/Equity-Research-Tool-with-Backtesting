# We have to segment companies based on their financial behavior, which we will define using financial archetypes.
# Two companies have the same financial archetype if their standard metrics are compatible.

# First we will hardcode some financial archetypes using SIC numbers and XBRL tags.
# Them, we will use K-means clustering on the remainder of companies to determine their financial archetypes.

from financial_statement_pipeline.data import get_company_facts, get_company_sic, REVENUE_TAGS
from financial_statement_pipeline.tag_finder import get_last_year_for_tag_raw, get_last_value_for_tag, find_tags

# Hardcoding companies with incompatible standard metrics
ARCHETYPE_SIC_MAP = {
    "Bank": [
        6021, 6022, 6029,
        6035, 6036,
        6099,
        6111, 6141, 6153, 6159, 6162, 6163, 6172,
        6189, 6199,
    ],
    "Brokerage": [
        6200, 6211, 6221,
        6282,
    ],
    "Insurance": [
        6311, 6321, 6324, 6331,
        6351, 6361, 6399,
        6411,
    ],
    "REIT": [
        6798,
    ],
    "BDC": [
        6726,
    ],
    "Pre-revenue Biotech": [
        2835, 2836, 8731,
    ],
    "Exclude": [
        6770, 8888, 9721, 9995, 6799,
    ],
}

# Letting K-means cluster companies with compatible standard metrics
archetypes_kmeans = [
    "Software/SaaS",
    "Platform/Marketplace",
    "Fabless Semiconductor",
    "IDM Semiconductor/Foundry",
    "Industrial Manufacturing",
    "Commodity Production",      # mining, oil & gas will likely cluster here
    "Retailer",
    "Consumer Brand",
    "Pharma",
    "Telecom",
    "Healthcare Services",
    "Media/Entertainment",
    # utilities will either cluster alone or near industrials — let data decide
]

# Check that a company has an XBRL tag in a list of XBRL tags.
def extract_with_fallback(company_facts, tag_list):
    if company_facts is None:
        return None
    for tag in tag_list:
        value = get_last_value_for_tag(company_facts, tag)
        if value is not None:
            return value
    return None

MLP_TAGS = [
    "LimitedPartnersCapitalAccount",
    "PartnersCapital",
]

BDC_TAGS = [
    "InvestmentOwnedAtFairValue",
    "NetInvestmentIncome",
]

RD_TAGS = [
    "ResearchAndDevelopmentExpense",
    "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
]


def get_archetype(ticker, year):
    sic = get_company_sic(ticker)

    for archetype, sic_list in ARCHETYPE_SIC_MAP.items():
        if sic in sic_list:
            if archetype == "Pre-revenue Biotech":
                break  # fall through to revenue check below
            print(f"{ticker}: {archetype}")
            return archetype
        
    company_facts = get_company_facts(ticker)

    # MLP fallback
    if any(
        get_last_year_for_tag_raw(company_facts, tag) is not None
        and get_last_year_for_tag_raw(company_facts, tag) >= year - 2
        for tag in MLP_TAGS
    ):
        print(f"{ticker}: MLP")
        return "MLP"

    # BDC fallback
    if extract_with_fallback(company_facts, BDC_TAGS) is not None:
        print(f"{ticker}: BDC")
        return "BDC"

    # Pre-revenue biotech
    if sic in [2835, 2836, 8731]:
        revenue = extract_with_fallback(company_facts, REVENUE_TAGS)
        rd = extract_with_fallback(company_facts, RD_TAGS)
        if revenue is None or (rd is not None and rd > revenue):
            print(f"{ticker}: Pre-revenue Biotech")
            return "Pre-revenue Biotech"

    print(f"{ticker}: Standard")
    return "Standard"

features = [
    "gross_margin_pct",      # discriminates Software vs Retailer vs Commodity
    "operating_margin_pct",  # discriminates profitable vs not
    "rd_pct_revenue",        # discriminates Pharma/Semi/Software vs everyone else
    "sga_pct_revenue",       # discriminates Consumer Brand vs Industrial
    "capex_ev",              # discriminates capital intensive vs asset light
    "asset_turnover",        # discriminates Retailer vs Industrial vs Software
    "inventory_pct_revenue", # discriminates physical goods vs services
]


GROSS_PROFIT_TAGS = ["GrossProfit"]

COST_OF_REVENUE_TAGS = [
    "CostOfRevenue",
    "CostOfGoodsAndServicesSold",
    "CostOfGoodsSold",
    "CostOfServices",
    "FoodAndBeverageCostOfSales",
]

OPERATING_INCOME_TAGS = [
    "OperatingIncomeLoss",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
] # 97% coverage 

RD_TAGS = [
    "ResearchAndDevelopmentExpense"
] # 100% coverage

SGA_TAGS = [
    "SellingGeneralAndAdministrativeExpense",
    "SellingAndMarketingExpense",
    "GeneralAndAdministrativeExpense",
] # 93% coverage

CAPEX_TAGS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsToAcquireProductiveAssets",
    "PaymentsToAcquireOilAndGasPropertyAndEquipment",
] # 97% coveage

ASSET_TAGS = [
    "Assets"
] # 100% coverage

NET_INVENTORY_TAGS = [
    "InventoryNet"
] # 100% coverage


tickers = [
    # Mega cap tech
    "AAPL", "MSFT", "GOOG", "META", "AMZN", "NFLX", "CRM", "ADBE", "NOW", "SNOW",
    # Semiconductors
    "NVDA", "AMD", "INTC", "QCOM", "AVGO", "MU", "AMAT", "KLAC", "LRCX", "TXN",
    # Industrial
    "GE", "HON", "MMM", "CAT", "DE", "EMR", "ETN", "PH", "ROK", "ITW",
    # Consumer/Retail
    "WMT", "TGT", "COST", "HD", "LOW", "NKE", "SBUX", "MCD", "YUM", "CMG",
    # Energy
    "XOM", "CVX", "COP", "SLB", "HAL", "PSX", "VLO", "MPC", "OXY", "EOG",
    # Healthcare/Pharma
    "JNJ", "PFE", "MRK", "ABBV", "LLY", "BMY", "AMGN", "GILD", "REGN", "VRTX",
    # Financials (standard only)
    "BLK", "SPGI", "MCO", "ICE", "CME", "CBOE", "MSCI", "FDS", "BR", "TW",
    # Media/Telecom
    "DIS", "CMCSA", "T", "VZ", "CHTR", "PARA", "WBD", "FOXA", "OMC", "IPG",
    # Consumer brands
    "PG", "KO", "PEP", "CL", "EL", "CHD", "CLX", "KMB", "SJM", "HRL",
    # Aerospace/Defense
    "LMT", "RTX", "NOC", "GD", "BA", "TDG", "HII", "L", "LDOS", "SAIC",
]

