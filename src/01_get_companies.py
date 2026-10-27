import requests
import pandas as pd
import time
from io import StringIO
from config import SEC_USER_AGENT

HEADERS = {"User-Agent": SEC_USER_AGENT}

url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=1731&start=0&count=100"
response = requests.get(url, headers=HEADERS, timeout=30)
print(response.status_code)

tables = pd.read_html(StringIO(response.text))
companies = tables[0]
companies["CIK"] = companies["CIK"].astype(str).str.zfill(10)
print(companies.shape)

def get_filing_summary(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code != 200:
        print(f"{cik}: status {response.status_code}")
        return {"CIK": cik, "status": response.status_code}
    data = response.json()
    pages = [pd.DataFrame(data["filings"]["recent"])]
    for f in data["filings"]["files"]:
        older_url = f"https://data.sec.gov/submissions/{f['name']}"
        older = requests.get(older_url, headers=HEADERS, timeout=30)
        if older.status_code == 200:
            pages.append(pd.DataFrame(older.json()))
        time.sleep(0.15)
    filings = pd.concat(pages, ignore_index=True)
    annual = filings[filings["form"].isin(["10-K", "10-K405", "10-KSB"])]
    return {
        "CIK": cik,
        "ticker": data["tickers"][0] if data["tickers"] else None,
        "n_10k": len(annual),
        "first_10k": annual["filingDate"].min(),
        "last_10k": annual["filingDate"].max(),
        "last_filing": filings["filingDate"].max(),
        "filed_form_15": filings["form"].str.startswith("15").any(),
    }

results = []
for cik in companies["CIK"]:
    results.append(get_filing_summary(cik))
    time.sleep(0.15)

summary = pd.DataFrame(results)
companies = companies.merge(summary, on="CIK")
companies.to_csv("data/silver/companies_1731.csv", index=False)
print(companies.sort_values("n_10k", ascending=False))