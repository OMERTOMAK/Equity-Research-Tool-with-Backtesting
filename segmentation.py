# We have to segment companies based on their financial behavior, which we will define using financial archetypes.
# Two companies have the same financial archetype if their standard metrics are compatible.

# First we will hardcode some financial archetypes using SIC numbers and XBRL tags.
# Them, we will use K-means clustering on the remainder of companies to determine their financial archetypes.

from financial_statement_pipeline.data import get_company_facts, get_company_sic, REVENUE_TAGS
from financial_statement_pipeline.tag_finder import get_last_year_for_tag_raw, get_last_value_for_tag

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
    for tag in tag_list:
        value = get_last_value_for_tag(company_facts, tag)  # should be this
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

if __name__ == "__main__":
    year = 2024

    # Banks
    print(get_archetype("JPM", year))
    print(get_archetype("BAC", year))
    print(get_archetype("WFC", year))

    # Brokerages
    print(get_archetype("GS", year))
    print(get_archetype("MS", year))
    print(get_archetype("SCHW", year))

    # Insurance
    print(get_archetype("BRK-B", year))
    print(get_archetype("PGR", year))
    print(get_archetype("MET", year))

    # REITs
    print(get_archetype("PLD", year))
    print(get_archetype("AMT", year))
    print(get_archetype("EQIX", year))

    # BDCs
    print(get_archetype("ARCC", year))
    print(get_archetype("MAIN", year))

    # MLPs
    print(get_archetype("ET", year))
    print(get_archetype("EPD", year))
    print(get_archetype("MPLX", year))

    # Pre-revenue Biotech
    print(get_archetype("BEAM", year))
    print(get_archetype("CRSP", year))
    print(get_archetype("FATE", year))

    # Standard Biotech with revenue (should be Standard)
    print(get_archetype("BIIB", year))
    print(get_archetype("MRNA", year))

    # Standard
    print(get_archetype("AAPL", year))
    print(get_archetype("MSFT", year))
    print(get_archetype("AMZN", year))
    print(get_archetype("OKE", year))
    print(get_archetype("KMI", year))