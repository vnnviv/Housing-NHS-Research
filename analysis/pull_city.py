"""Pull recently reset single-family parcels for one city (ANALYSIS-PLAN.md section 3).

Run this on YOUR machine; the Assessor GIS service blocks cloud IP ranges.

    python analysis/pull_city.py "BALDWIN PARK" --out analysis/data/baldwin_park_2025_2026.csv

It prints the row counts after every filter (the plan requires reporting them), pages
through the service so nothing is silently truncated, and refuses to write a file with
fewer than 100 retained parcels. Run it ONCE for the confirmatory city and do not look
at prices before the plan is committed.
"""

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

URL = ("https://public.gis.lacounty.gov/public/rest/services/"
       "LACounty_Cache/LACounty_Parcel/MapServer/0/query")
FIELDS = ("Roll_LandValue,Roll_ImpValue,Roll_LandBaseYear,Roll_ImpBaseYear,"
          "SQFTmain1,Bedrooms1,YearBuilt1")
MIN_ASSESSED = 200_000     # same threshold as downpayment_scenarios.MIN_PLAUSIBLE_SALE
MIN_N = 100
PAGE = 1000


def query(where, offset):
    params = {"where": where, "outFields": FIELDS, "returnGeometry": "false",
              "resultOffset": str(offset), "resultRecordCount": str(PAGE),
              "orderByFields": "OBJECTID", "f": "json"}
    with urllib.request.urlopen(URL + "?" + urllib.parse.urlencode(params), timeout=90) as r:
        return json.load(r)


def pull(city):
    city = city.upper().replace("'", "''")
    where = (f"TaxRateCity='{city}' AND UseDescription='Single' "
             "AND (Roll_LandBaseYear='2025' OR Roll_LandBaseYear='2026')")
    raw, offset = [], 0
    while True:
        payload = query(where, offset)
        if "error" in payload:
            sys.exit(f"Service error: {payload['error']}")
        feats = payload.get("features", [])
        raw += [f["attributes"] for f in feats]
        if not payload.get("exceededTransferLimit") and len(feats) < PAGE:
            break
        offset += PAGE
    return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("city", help="TaxRateCity value, e.g. 'BALDWIN PARK'")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = pull(args.city)
    reset = [a for a in raw if a.get("Roll_LandBaseYear") == a.get("Roll_ImpBaseYear")]
    rows = []
    for a in reset:
        total = (a.get("Roll_LandValue") or 0) + (a.get("Roll_ImpValue") or 0)
        rows.append([total, a.get("SQFTmain1"), a.get("Bedrooms1"),
                     a.get("YearBuilt1"), a.get("Roll_LandBaseYear")])
    kept = [r for r in rows if r[0] >= MIN_ASSESSED]
    print(f"{args.city}: pulled {len(raw)}; land base year = improvement base year "
          f"{len(reset)}; assessed >= ${MIN_ASSESSED:,} {len(kept)}")
    if len(kept) < MIN_N:
        sys.exit(f"Only {len(kept)} retained parcels (< {MIN_N}). Per the plan, report the "
                 "range only and move to the next city on the list. No file written.")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["assessed_total", "sqft_main", "bedrooms", "year_built", "base_year"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}. Next: python analysis/cap_sensitivity.py "
          f"--csv {out} --label \"{args.city.title()}\" --status confirmatory "
          f"--out NHS-CAP-SENSITIVITY-{args.city.upper().replace(' ', '-')}.md")


if __name__ == "__main__":
    main()
