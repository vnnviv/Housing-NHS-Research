"""Bounded share of renter households under each income cap (ANALYSIS-PLAN.md section 8).

Needs a free Census API key: https://api.census.gov/data/key_signup.html

    export CENSUS_API_KEY=...
    python analysis/acs_renter_income.py --place "Compton city, California"

Table B25118 (tenure by household income), ACS 5-year. The table has fixed income bins,
not the caps, so each cap lands INSIDE a bin. We report a lower bound (full bins below the
cap) and an upper bound (through the bin containing the cap). We never interpolate to a
point estimate. B25118 is all household sizes; the caps are 4-person, so this is a rough
population context and not a clean match. The ACS 5-year dollars are in the survey's
inflation-adjusted year, not 2026.
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

YEAR = 2023
# B25118: _014E renter total; _015E.._025E renter income bins (variable order per Census docs).
BINS = [  # (upper bound in dollars (exclusive), variable)
    (5_000, "B25118_015E"), (10_000, "B25118_016E"), (15_000, "B25118_017E"),
    (20_000, "B25118_018E"), (25_000, "B25118_019E"), (35_000, "B25118_020E"),
    (50_000, "B25118_021E"), (75_000, "B25118_022E"), (100_000, "B25118_023E"),
    (150_000, "B25118_024E"), (float("inf"), "B25118_025E"),
]
CAPS = {"HUD very low": 83_300, "MFI reference": 108_100,
        "HUD low = HCD moderate": 133_250, "Greenline": 151_300, "CalHFA flat": 214_000}


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def main():
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("Set CENSUS_API_KEY first (free key at api.census.gov/data/key_signup.html).")
    ap = argparse.ArgumentParser()
    ap.add_argument("--place", default="Compton city, California")
    args = ap.parse_args()

    names = ",".join(["NAME", "B25118_014E"] + [v for _, v in BINS])
    base = f"https://api.census.gov/data/{YEAR}/acs/acs5"
    rows = get(f"{base}?get={names}&for=place:*&in=state:06&key={key}")
    head, data = rows[0], rows[1:]
    match = [r for r in data if r[0] == args.place]
    if len(match) != 1:
        sys.exit(f"Expected one place named {args.place!r}, found {len(match)}.")
    rec = dict(zip(head, match[0]))
    total = int(rec["B25118_014E"])
    print(f"{args.place}: {total:,} renter households (ACS {YEAR} 5-year, B25118)\n")
    print("| Cap | Lower bound | Upper bound |\n|---|---|---|")
    for name, cap in CAPS.items():
        lo = sum(int(rec[v]) for ub, v in BINS if ub <= cap)
        lower = lo
        upper = lo + next(int(rec[v]) for ub, v in BINS if ub > cap)
        print(f"| {name} (${cap:,}) | {lower / total:.0%} | {upper / total:.0%} |")
    print("\nBounds are shares of renter households with income below the cap. "
          "Moe is not shown; consult the *M variables before quoting any number.")


if __name__ == "__main__":
    main()
