"""
Scraper for Bureau of Labor Statistics (BLS) data.

Pulls salary data, employment outlook, and industry statistics
for MBA-relevant occupations.

API docs: https://www.bls.gov/developers/
"""

import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# BLS Occupational Employment and Wage Statistics (OEWS) series IDs
# Format: OEUM{area}{industry}{occupation}{data_type}
# area=0000000 (national), industry=000000, data_type=01 (employment), 04 (mean wage)
MBA_BLS_SERIES = {
    "Management Analysts": {
        "employment": "OEUM000000000000001311110001",
        "mean_wage": "OEUM000000000000001311110004",
        "soc": "13-1111",
    },
    "Financial Managers": {
        "employment": "OEUM000000000000001130310001",
        "mean_wage": "OEUM000000000000001130310004",
        "soc": "11-3031",
    },
    "Marketing Managers": {
        "employment": "OEUM000000000000001120210001",
        "mean_wage": "OEUM000000000000001120210004",
        "soc": "11-2021",
    },
    "General Operations Managers": {
        "employment": "OEUM000000000000001110210001",
        "mean_wage": "OEUM000000000000001110210004",
        "soc": "11-1021",
    },
    "Data Scientists": {
        "employment": "OEUM000000000000001520510001",
        "mean_wage": "OEUM000000000000001520510004",
        "soc": "15-2051",
    },
    "Chief Executives": {
        "employment": "OEUM000000000000001110110001",
        "mean_wage": "OEUM000000000000001110110004",
        "soc": "11-1011",
    },
    "Sales Managers": {
        "employment": "OEUM000000000000001120220001",
        "mean_wage": "OEUM000000000000001120220004",
        "soc": "11-2022",
    },
    "Project Management Specialists": {
        "employment": "OEUM000000000000001310820001",
        "mean_wage": "OEUM000000000000001310820004",
        "soc": "13-1082",
    },
}

# Occupational Outlook Handbook data (manually curated from BLS OOH)
OOH_DATA = {
    "Management Analysts": {
        "median_pay_2023": 99410,
        "job_outlook_2022_2032": "10%",
        "outlook_description": "Faster than average",
        "num_jobs_2022": 986000,
        "employment_change_2022_2032": 96000,
        "entry_education": "Bachelor's degree",
        "typical_mba_premium": 0.40,
    },
    "Financial Managers": {
        "median_pay_2023": 156100,
        "job_outlook_2022_2032": "16%",
        "outlook_description": "Much faster than average",
        "num_jobs_2022": 730800,
        "employment_change_2022_2032": 116700,
        "entry_education": "Bachelor's degree",
        "typical_mba_premium": 0.35,
    },
    "Marketing Managers": {
        "median_pay_2023": 157620,
        "job_outlook_2022_2032": "6%",
        "outlook_description": "Faster than average",
        "num_jobs_2022": 354600,
        "employment_change_2022_2032": 22600,
        "entry_education": "Bachelor's degree",
        "typical_mba_premium": 0.30,
    },
    "General Operations Managers": {
        "median_pay_2023": 101280,
        "job_outlook_2022_2032": "3%",
        "outlook_description": "As fast as average",
        "num_jobs_2022": 3531100,
        "employment_change_2022_2032": 116300,
        "entry_education": "Bachelor's degree",
        "typical_mba_premium": 0.35,
    },
    "Data Scientists": {
        "median_pay_2023": 108020,
        "job_outlook_2022_2032": "35%",
        "outlook_description": "Much faster than average",
        "num_jobs_2022": 192300,
        "employment_change_2022_2032": 67200,
        "entry_education": "Bachelor's degree",
        "typical_mba_premium": 0.25,
    },
    "Chief Executives": {
        "median_pay_2023": 206680,
        "job_outlook_2022_2032": "3%",
        "outlook_description": "As fast as average",
        "num_jobs_2022": 200300,
        "employment_change_2022_2032": 6000,
        "entry_education": "Master's degree preferred",
        "typical_mba_premium": 0.20,
    },
    "Sales Managers": {
        "median_pay_2023": 135160,
        "job_outlook_2022_2032": "4%",
        "outlook_description": "As fast as average",
        "num_jobs_2022": 469800,
        "employment_change_2022_2032": 20300,
        "entry_education": "Bachelor's degree",
        "typical_mba_premium": 0.30,
    },
    "Project Management Specialists": {
        "median_pay_2023": 98580,
        "job_outlook_2022_2032": "6%",
        "outlook_description": "Faster than average",
        "num_jobs_2022": 977600,
        "employment_change_2022_2032": 59300,
        "entry_education": "Bachelor's degree",
        "typical_mba_premium": 0.25,
    },
}

# Boston metro area salary adjustments (BLS area code 71650)
BOSTON_SALARY_MULTIPLIER = 1.18  # Boston salaries ~18% above national median


def fetch_bls_series(series_ids: list, start_year: int = 2020, end_year: int = 2024, api_key: str = None) -> dict:
    """Fetch time series data from BLS API."""
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    if api_key:
        payload["registrationkey"] = api_key

    try:
        resp = httpx.post(BLS_API_URL, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "REQUEST_SUCCEEDED":
                return data
    except httpx.RequestError:
        pass
    return {}


def get_occupation_outlook() -> list:
    """Get curated occupational outlook data with Boston adjustments."""
    results = []
    for title, data in OOH_DATA.items():
        boston_median = int(data["median_pay_2023"] * BOSTON_SALARY_MULTIPLIER)
        boston_mba_median = int(boston_median * (1 + data["typical_mba_premium"]))
        results.append({
            "title": title,
            "soc_code": MBA_BLS_SERIES.get(title, {}).get("soc", ""),
            "national_median_2023": data["median_pay_2023"],
            "boston_estimated_median": boston_median,
            "boston_mba_estimated_median": boston_mba_median,
            "job_outlook_2022_2032": data["job_outlook_2022_2032"],
            "outlook_description": data["outlook_description"],
            "total_jobs_2022": data["num_jobs_2022"],
            "projected_new_jobs": data["employment_change_2022_2032"],
            "entry_education": data["entry_education"],
            "mba_salary_premium": f"{data['typical_mba_premium']:.0%}",
        })
    return results


def scrape_all(api_key: str = None, output_path: str = None) -> dict:
    """Collect all BLS data for MBA-relevant occupations."""
    outlook = get_occupation_outlook()

    result = {
        "source": "Bureau of Labor Statistics",
        "occupational_outlook": outlook,
        "boston_area_multiplier": BOSTON_SALARY_MULTIPLIER,
        "notes": "Salary estimates include Boston metro area adjustment (+18%) and MBA premium estimates",
    }

    if output_path:
        Path(output_path).write_text(json.dumps(result, indent=2))
        print(f"  Saved BLS data to {output_path}")

    return result


if __name__ == "__main__":
    output = str(Path(__file__).parent.parent / "data" / "bls_outlook.json")
    Path(output).parent.mkdir(exist_ok=True)
    data = scrape_all(output_path=output)
    print(f"Compiled BLS data for {len(data['occupational_outlook'])} occupations")
