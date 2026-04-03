from financial_statement_pipeline.data import get_company_facts, FORM_TYPES
from datetime import datetime

def find_tags(company_facts, keyword):
    matches = []

    for rule in ["us-gaap", "ifrs-full"]:
        if rule in company_facts["facts"]:
            for tag in company_facts["facts"][rule].keys():
                if keyword.lower() in tag.lower():
                    matches.append(tag)

    return matches


def get_last_year_for_tag_raw(company_facts, tag):
    years = []

    for rule in ["us-gaap", "ifrs-full"]:
        if rule in company_facts["facts"] and tag in company_facts["facts"][rule]:
            units = company_facts["facts"][rule][tag]["units"]

            for unit, observations in units.items():
                for obs in observations:
                    if obs.get("end"):
                        try:
                            year = datetime.strptime(obs["end"], "%Y-%m-%d").year
                            years.append(year)
                        except:
                            continue

    return max(years) if years else None

def get_last_value_for_tag(company_facts, tag):
    best = None  # (year, value)

    for rule in ["us-gaap", "ifrs-full"]:
        if rule in company_facts["facts"] and tag in company_facts["facts"][rule]:
            units = company_facts["facts"][rule][tag]["units"]

            for unit, observations in units.items():
                for obs in observations:
                    if obs.get("end") and obs.get("form") in FORM_TYPES:
                        try:
                            year = datetime.strptime(obs["end"], "%Y-%m-%d").year
                            if best is None or year > best[0]:
                                best = (year, obs["val"])
                        except:
                            continue

    return best[1] if best else None

if __name__ == "__main__":
    print(get_last_year_for_tag_raw(get_company_facts("MPLX"), "PartnersCapital"))
    print(get_last_year_for_tag_raw(get_company_facts("PAA"), "PartnersCapital"))
    print(get_last_year_for_tag_raw(get_company_facts("DKL"), "PartnersCapital"))

# And verify it doesn't create false positives on negatives
    print(get_last_year_for_tag_raw(get_company_facts("OKE"), "PartnersCapital"))
    print(get_last_year_for_tag_raw(get_company_facts("KMI"), "PartnersCapital"))
    print(get_last_year_for_tag_raw(get_company_facts("AAPL"), "PartnersCapital"))
