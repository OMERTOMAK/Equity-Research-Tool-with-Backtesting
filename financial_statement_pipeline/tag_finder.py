from data import get_company_facts, extract_account_data
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

if __name__ == "__main__":
    print(find_tags(get_company_facts("WFC"), "Revenues"))
    print(find_tags(get_company_facts("GS"), "Revenues"))
    print(find_tags(get_company_facts("MS"), "Revenues"))

    print(get_last_year_for_tag_raw(get_company_facts("WFC"), "Revenues"))
    print(get_last_year_for_tag_raw(get_company_facts("GS"), "Revenues"))
    print(get_last_year_for_tag_raw(get_company_facts("MS"), "Revenues"))

    print(get_last_year_for_tag_raw(get_company_facts("WFC"), "RevenuesNetOfInterestExpense"))
    print(get_last_year_for_tag_raw(get_company_facts("GS"), "RevenuesNetOfInterestExpense"))
    print(get_last_year_for_tag_raw(get_company_facts("MS"), "RevenuesNetOfInterestExpense"))
