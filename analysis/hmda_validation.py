"""External check of the cap-sensitivity engine against real buyers (HMDA).

    python analysis/hmda_validation.py --city Compton --years 2024 2025 --cache hmda_cache

HMDA (CFPB Data Browser) is public loan-level data: income, loan amount, property value,
rate, loan-to-value, loan type, census tract. It shows who actually bought, so it checks
the engine's mechanics and the ratio assumption. It is NOT a sample of people who tried
and failed (survivorship), and HMDA income is the applicants' combined income.

City tracts: Census 2020 tracts whose internal point falls inside the city's boundary
(TIGERweb). Tracts that only touch the city are excluded and counted as 'edge'.
Writes HMDA-VALIDATION.md. Needs network access to ffiec.cfpb.gov and tigerweb.geo.census.gov.
"""
import argparse
import csv
import json
import statistics as st
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cap_sensitivity as cs   # noqa: E402

TIGER = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb"
HMDA = ("https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?states=CA&counties=06037"
        "&years={y}&actions_taken=1&loan_purposes=1")
CAPS = {"HUD very low": 83_300, "MFI reference": 108_100, "HUD low = HCD moderate": 133_250,
        "Greenline": 151_300, "CalHFA flat": 214_000}


def _get(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    with urllib.request.urlopen(urllib.request.Request(url, body), timeout=120) as r:
        return json.load(r)


def point_in_rings(x, y, rings):
    inside = False
    for ring in rings:
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
    return inside


def city_tracts(city):
    pl = _get(f"{TIGER}/Places_CouSub_ConCity_SubMCD/MapServer/25/query",
              {"where": f"STATE='06' AND BASENAME='{city}'", "outFields": "NAME,GEOID",
               "returnGeometry": "true", "outSR": "4326", "f": "json"})
    if len(pl["features"]) != 1:
        sys.exit(f"Expected one incorporated place named {city!r}, found {len(pl['features'])}.")
    rings = pl["features"][0]["geometry"]["rings"]
    geom = json.dumps({"rings": rings, "spatialReference": {"wkid": 4326}})
    tr = _get(f"{TIGER}/Tracts_Blocks/MapServer/10/query",
              {"geometry": geom, "geometryType": "esriGeometryPolygon", "inSR": "4326",
               "spatialRel": "esriSpatialRelIntersects", "where": "STATE='06' AND COUNTY='037'",
               "outFields": "GEOID,INTPTLAT,INTPTLON", "returnGeometry": "false", "f": "json"})
    inside, edge = [], []
    for t in tr["features"]:
        a = t["attributes"]
        (inside if point_in_rings(float(a["INTPTLON"]), float(a["INTPTLAT"]), rings) else edge
         ).append(a["GEOID"])
    return set(inside), set(edge)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def pct(v, p):
    return st.quantiles(sorted(v), n=100)[p - 1] if len(v) >= 100 else None


def fetch(year, cache):
    path = Path(cache) / f"hmda_la_{year}.csv"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(HMDA.format(y=year), path)
    return path


def buyers(path, tracts):
    keep = []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            if (r["census_tract"] in tracts and r["occupancy_type"] == "1"
                    and r["lien_status"] == "1" and r["reverse_mortgage"] != "1"
                    and r["business_or_commercial_purpose"] != "1"
                    and r["derived_dwelling_category"].startswith("Single Family")):
                keep.append(r)
    return keep


def implied_front_end(r, tax_rate=0.011, insurance=150.0):
    inc, loan, rate, pv = (num(r[k]) for k in ("income", "loan_amount", "interest_rate", "property_value"))
    if not (inc and loan and rate and pv):
        return None
    ltv = loan / pv
    pi = loan * cs.payment_factor(rate / 100, int(num(r["loan_term"]) or 360))
    mi = 0.0 if ltv <= 0.8 else loan * cs.mi_rate(ltv, cs.Params()) / 12
    return (pi + mi + pv * tax_rate / 12 + insurance) * 12 / (inc * 1000)


def section(year, rows, label):
    out = [f"## {year}", ""]
    inc = [num(r["income"]) * 1000 for r in rows if num(r["income"])]
    pv = [num(r["property_value"]) for r in rows if num(r["property_value"])]
    rt = [num(r["interest_rate"]) for r in rows if num(r["interest_rate"])]
    fe = [x for x in (implied_front_end(r) for r in rows) if x is not None]
    out.append(f"{len(rows)} owner-occupied, first-lien, single-family purchase originations in "
               f"{label} tracts; income reported for {len(inc)}.\n")
    if min(len(inc), len(pv), len(fe)) < 100:
        out.append("Fewer than 100 usable loans; percentiles suppressed.\n")
        return out
    out.append("| Measure | p25 | median | p75 |\n|---|---|---|---|")
    out.append(f"| Applicant income | ${pct(inc, 25):,.0f} | ${pct(inc, 50):,.0f} | ${pct(inc, 75):,.0f} |")
    out.append(f"| Property value | ${pct(pv, 25):,.0f} | ${pct(pv, 50):,.0f} | ${pct(pv, 75):,.0f} |")
    out.append(f"| Interest rate | {pct(rt, 25):.2f}% | {pct(rt, 50):.2f}% | {pct(rt, 75):.2f}% |")
    out.append(f"| Implied front-end ratio* | {pct(fe, 25):.2f} | {pct(fe, 50):.2f} | {pct(fe, 75):.2f} |")
    out.append("\n*Own loan terms, 1.10% tax, $150/mo insurance, engine mortgage-insurance card. "
               "Total DTI from HMDA is a separate, higher number.\n")
    out.append("| Cap | Share of buyers with income at or below the cap |\n|---|---|")
    for name, cap in CAPS.items():
        out.append(f"| {name} (${cap:,}) | {sum(1 for x in inc if x <= cap) / len(inc):.0%} |")
    low = [r for r in rows if num(r["income"]) and num(r["income"]) * 1000 <= CAPS["HUD low = HCD moderate"]]
    lpv = [num(r["property_value"]) for r in low if num(r["property_value"])]
    ltv = [num(r["loan_to_value_ratio"]) for r in low if num(r["loan_to_value_ratio"])]
    coapp = sum(1 for r in low if r["co-applicant_age"] != "9999")
    out.append(f"\nBuyers at or below $133,250: n={len(low)}, median property value "
               f"${st.median(lpv):,.0f}, median LTV {st.median(ltv):.0f}, "
               f"{sum(1 for x in ltv if x >= 95) / len(ltv):.0%} with LTV at or above 95, "
               f"{coapp / len(low):.0%} with a co-applicant. Loan types "
               f"{dict(Counter(r['loan_type'] for r in low))} (1 conv, 2 FHA, 3 VA, 4 USDA). "
               f"Total DTI bins: {dict(Counter(r['debt_to_income_ratio'] for r in low).most_common(5))}.\n")
    ratios = []
    for r in rows:
        i, v, rate, l = (num(r[k]) for k in ("income", "property_value", "interest_rate", "loan_to_value_ratio"))
        if i and v and rate and l:
            p = cs.Params(rate=rate / 100, down=max(0.0, 1 - l / 100))
            ratios.append(cs.required_income(v, p, 0.0) / (i * 1000))
    out.append(f"Engine check: at each buyer's own price, rate and down payment and a 30% front-end "
               f"ratio, required income divided by actual income has median {pct(ratios, 50):.2f} "
               f"(p25 {pct(ratios, 25):.2f}, p75 {pct(ratios, 75):.2f}). If the engine's arithmetic "
               f"reproduces real loans this should be close to the buyers' median front-end ratio "
               f"divided by 0.30, which is {pct(fe, 50) / 0.30:.2f}.\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", default="Compton")
    ap.add_argument("--years", type=int, nargs="+", default=[2024, 2025])
    ap.add_argument("--cache", default="hmda_cache")
    ap.add_argument("--out", default="HMDA-VALIDATION.md")
    args = ap.parse_args()
    inside, edge = city_tracts(args.city)
    lines = [f"# HMDA check of the engine: {args.city} (EXPLORATORY)", "",
             "Real purchase loans, not a sample of people who tried and failed. Tracts: "
             f"{len(inside)} Census 2020 tracts with their internal point inside {args.city}; "
             f"{len(edge)} tracts that only touch the boundary are excluded. Income is the "
             "applicants' combined income and household size is unknown, so the 4-person caps are a "
             "rough comparison. Not a finding about NHS clients.", ""]
    for y in args.years:
        lines += section(y, buyers(fetch(y, args.cache), inside), args.city)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
