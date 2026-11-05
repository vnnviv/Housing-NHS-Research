"""Q5: how far does the Prop 13 roll sit from market, by tract? (EXPLORATORY)

    python analysis/prop13_gap.py --cache q5_cache

Measures, per Census 2020 tract, for single-family parcels on the 2026 LA County roll:

  tenure        median land base year, share with base year <= 2000
  stock_ratio   median roll value of all SFR parcels / HMDA median property value
                (owner-occupied first-lien SFR purchase originations, 2024-25 pooled)
  held_ratio    the same, using only parcels whose base year is 2023 or earlier
  psf_ratio     median roll $/sqft of held parcels / median $/sqft of market-sale resets
                (2025-26, round-value filter) in the same tract. Same source, size-controlled.

Why: Paper 2 cannot use assessed value as a benchmark (PAPER2-CONTEXT-DELTA). This measures how
badly it would mislead, and whether the distortion differs between the two study regions, which
is the tenure confound in its own right.

Regions are provisional, set before looking at outcomes: study ZIPs below, then a tract rule
(SGV: non-Hispanic Asian >= 50%; South LA: non-Hispanic Black + Hispanic >= 50%). Tract
demographics come from LA County's ACS B03002 layer; its ACS year is not stated on the layer.

Data: LA County 'Assessor Parcel Data Roll 2026' (ArcGIS Online), TIGERweb 2020 tracts,
CFPB HMDA Data Browser. All public, no key. Writes Q5-PROP13-GAP.md and q5_tracts.csv.
"""
import argparse
import csv
import json
import random
import statistics as st
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import downpayment_scenarios as dps   # noqa: E402
import hmda_validation as hv          # noqa: E402

AGOL = "https://services.arcgis.com/RmCCgQtiZLDCtblq/ArcGIS/rest/services"
ROLL = AGOL + "/Assessor%20Parcel%20Data%20Roll%202026/FeatureServer/0/query"
ACS = (AGOL + "/ACS_Race_Internet_Connectivity_Median_Household_Income_School_Enrollment_"
       "Age_LA_County/FeatureServer/0/query")
TRACTS = hv.TIGER + "/Tracts_Blocks/MapServer/10/query"

ZIPS = {
    "SGV": ["91801", "91803", "91754", "91755", "91775", "91776", "91770", "91780", "91006",
            "91007", "91108", "91745", "91748", "91789", "91765", "91731", "91732", "91733"],
    "South LA": ["90001", "90002", "90003", "90008", "90011", "90016", "90018", "90037",
                 "90043", "90044", "90047", "90059", "90061", "90062", "90220", "90221", "90222"],
}
FIELDS = ("AIN,SitusZIP5,Roll_totLandImp,Roll_LandBaseYear,Roll_ImpBaseYear,SQFTmain,"
          "CENTER_LAT,CENTER_LON")
MIN_PARCELS, MIN_LOANS, MIN_RESETS = 50, 20, 10
HELD_MAX_BASE = 2023
ROLL_YEAR = 2026


def get(url, params, timeout=120):
    req = urllib.request.Request(url, urllib.parse.urlencode(params).encode())
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def cached(cache, name, fn):
    path = Path(cache) / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    data = fn()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def pull_parcels(region):
    zips = ",".join(f"'{z}'" for z in ZIPS[region])
    where = f"UseType='SFR' AND SitusZIP5 IN ({zips})"
    out, last = [], -1
    while True:   # keyset paging on OBJECTID: nothing is skipped or double-counted
        p = get(ROLL, {"where": f"{where} AND OBJECTID > {last}", "outFields": FIELDS + ",OBJECTID",
                       "orderByFields": "OBJECTID", "resultRecordCount": 1000,
                       "returnGeometry": "false", "f": "json"})
        if "error" in p:
            sys.exit(f"Roll service error: {p['error']}")
        feats = [f["attributes"] for f in p.get("features", [])]
        if not feats:
            break
        out += feats
        last = feats[-1]["OBJECTID"]
        print(f"  {region}: {len(out):,} parcels", end="\r", flush=True)
    print()
    return out


def pull_tracts():
    out, offset = [], 0
    while True:
        p = get(TRACTS, {"where": "STATE='06' AND COUNTY='037'", "outFields": "GEOID",
                         "returnGeometry": "true", "outSR": "4326",
                         "maxAllowableOffset": "0.00005", "resultOffset": offset,
                         "resultRecordCount": 500, "f": "json"})
        feats = p.get("features", [])
        out += [{"geoid": f["attributes"]["GEOID"], "rings": f["geometry"]["rings"]}
                for f in feats]
        if len(feats) < 500:
            return out
        offset += 500


def pull_acs():
    """ACS polygons with B03002 counts. The layer's tracts are not all 2020 tracts
    (about 2,000 of 2,399 GEOIDs match), so demographics are joined spatially, not by GEOID."""
    out, offset = [], 0
    while True:
        p = get(ACS, {"where": "1=1", "returnGeometry": "true", "outSR": "4326",
                      "maxAllowableOffset": "0.00005", "resultOffset": offset,
                      "outFields": "GEOID,B03002_001E,B03002_004E,B03002_006E,B03002_012E",
                      "resultRecordCount": 500, "f": "json"})
        feats = p.get("features", [])
        for f in feats:
            a = f["attributes"]
            out.append({"geoid": a["GEOID"], "rings": f["geometry"]["rings"],
                        "acs": [a["B03002_001E"], a["B03002_004E"], a["B03002_006E"],
                                a["B03002_012E"]]})
        if len(feats) < 500:
            return out
        offset += 500


def tract_demographics(by_tract, acs_polys):
    """Each 2020 tract takes the ACS polygon holding most of its parcels."""
    lookup = {a["geoid"]: a["acs"] for a in acs_polys}
    out, share = {}, []
    for g, ps in by_tract.items():
        placed, _ = assign(ps, acs_polys)
        if not placed:
            continue
        best = max(placed, key=lambda k: len(placed[k]))
        out[g] = lookup[best]
        share.append(len(placed[best]) / len(ps))
    return out, share


def assign(parcels, tracts):
    """Point-in-polygon with a bounding-box prefilter. Returns {geoid: [parcel, ...]}."""
    boxes = []
    for t in tracts:
        xs = [x for ring in t["rings"] for x, _ in ring]
        ys = [y for ring in t["rings"] for _, y in ring]
        boxes.append((min(xs), max(xs), min(ys), max(ys), t))
    cell = 0.02
    grid = {}
    for b in boxes:
        for i in range(int(b[0] // cell), int(b[1] // cell) + 1):
            for j in range(int(b[2] // cell), int(b[3] // cell) + 1):
                grid.setdefault((i, j), []).append(b)
    out, missed = {}, 0
    for p in parcels:
        x, y = p.get("CENTER_LON"), p.get("CENTER_LAT")
        if x is None or y is None:
            missed += 1
            continue
        for b in grid.get((int(x // cell), int(y // cell)), []):
            if b[0] <= x <= b[1] and b[2] <= y <= b[3] and hv.point_in_rings(x, y, b[4]["rings"]):
                out.setdefault(b[4]["geoid"], []).append(p)
                break
        else:
            missed += 1
    return out, missed


def hmda_by_tract(cache, years):
    vals = {}
    for y in years:
        with open(hv.fetch(y, cache), newline="") as fh:
            for r in csv.DictReader(fh):
                if (r["occupancy_type"] == "1" and r["lien_status"] == "1"
                        and r["reverse_mortgage"] != "1"
                        and r["business_or_commercial_purpose"] != "1"
                        and r["derived_dwelling_category"].startswith("Single Family")):
                    v = hv.num(r["property_value"])
                    if v:
                        vals.setdefault(r["census_tract"], []).append(v)
    return vals


def year(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def tract_row(geoid, region, parcels, loans, acs):
    vals = [p["Roll_totLandImp"] for p in parcels if p.get("Roll_totLandImp")]
    bases = [year(p["Roll_LandBaseYear"]) for p in parcels if year(p["Roll_LandBaseYear"])]
    held = [p for p in parcels if (year(p["Roll_LandBaseYear"]) or 9999) <= HELD_MAX_BASE
            and p.get("Roll_totLandImp")]
    resets = reset_psf(parcels)
    held_psf = [p["Roll_totLandImp"] / p["SQFTmain"] for p in held if (p.get("SQFTmain") or 0) > 300]
    tot, blk, asn, hsp = acs.get(geoid, [None] * 4)
    hm = st.median(loans) if len(loans) >= MIN_LOANS else None
    return {
        "geoid": geoid, "region": region, "n_parcels": len(parcels), "n_loans": len(loans),
        "n_resets": len(resets),
        "pct_asian": round(asn / tot, 3) if tot else None,
        "pct_black_latino": round((blk + hsp) / tot, 3) if tot else None,
        "median_base_year": st.median(bases) if bases else None,
        "share_base_le_2000": round(sum(b <= 2000 for b in bases) / len(bases), 3) if bases else None,
        "median_roll_value": st.median(vals) if vals else None,
        "hmda_median_value": hm,
        "stock_ratio": round(st.median(vals) / hm, 3) if hm and vals else None,
        "held_ratio": round(st.median([p["Roll_totLandImp"] for p in held]) / hm, 3)
        if hm and held else None,
        "psf_ratio": round(st.median(held_psf) / st.median(resets), 3)
        if len(resets) >= MIN_RESETS and held_psf else None,
    }


COHORTS = [(0, 1989, "1989 or earlier"), (1990, 1999, "1990-99"), (2000, 2007, "2000-07"),
           (2008, 2012, "2008-12"), (2013, 2019, "2013-19"), (2020, 2023, "2020-23")]


def reset_psf(parcels):
    out = []
    for p in parcels:
        b = year(p["Roll_LandBaseYear"])
        if (b in (2025, 2026) and p["Roll_LandBaseYear"] == p["Roll_ImpBaseYear"]
                and (p.get("Roll_totLandImp") or 0) >= dps.MIN_PLAUSIBLE_SALE
                and (p.get("SQFTmain") or 0) > 300):
            price = dps.market_price(p["Roll_totLandImp"], b, ROLL_YEAR)
            if price:
                out.append(price / p["SQFTmain"])
    return out


def cohort_ratios(by_tract, study_geoids):
    """Roll $/sqft over same-tract reset $/sqft, pooled by base-year cohort.
    Holding the base year fixed separates appreciation since purchase from tenure mix."""
    out = {lab: [] for _, _, lab in COHORTS}
    for g, ps in by_tract.items():
        if g not in study_geoids:
            continue
        resets = reset_psf(ps)
        if len(resets) < MIN_RESETS:
            continue
        market = st.median(resets)
        for p in ps:
            b, sq, v = year(p["Roll_LandBaseYear"]), p.get("SQFTmain") or 0, p.get("Roll_totLandImp")
            if b and sq > 300 and v:
                for lo, hi, lab in COHORTS:
                    if lo <= b <= hi:
                        out[lab].append(v / sq / market)
    return out


def in_study(row):
    if row["n_parcels"] < MIN_PARCELS or row["pct_asian"] is None:
        return False
    if row["region"] == "SGV":
        return row["pct_asian"] >= 0.5
    return row["pct_black_latino"] >= 0.5


def boot_diff(a, b, reps=2000, seed=20261105):
    """Difference in medians (a - b) with a percentile bootstrap over tracts."""
    rng = random.Random(seed)
    d = sorted(st.median(rng.choices(a, k=len(a))) - st.median(rng.choices(b, k=len(b)))
               for _ in range(reps))
    return st.median(a) - st.median(b), d[int(0.025 * reps)], d[int(0.975 * reps)]


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * (len(v) - 1) + 0.5))]


def report(rows, counts, cohorts=None):
    out = ["# Q5: How far the Prop 13 roll sits from market, by tract (EXPLORATORY)", "",
           "Exploratory. Regions were defined in code before outcomes were computed, but nothing "
           "here is preregistered. Descriptive only: no statement about valuation bias, and "
           "assessed value is not a benchmark for Paper 2.", "",
           "**Data.** LA County Assessor 2026 roll, single-family parcels (`UseType = 'SFR'`) in "
           "the study ZIPs, placed in Census 2020 tracts by parcel centroid. HMDA 2024-25 "
           "owner-occupied, first-lien, single-family purchase originations by tract. Tract "
           "race and ethnicity from LA County's ACS B03002 layer (ACS year not stated on the "
           "layer; verify).", "",
           "**Counts.** " + "; ".join(f"{k}: {v}" for k, v in counts.items()) + ".", "",
           "**Ratios.** `stock` = median roll value of all SFR parcels / HMDA median property "
           f"value. `held` = the same for parcels with base year {HELD_MAX_BASE} or earlier. "
           "`psf` = median roll $/sqft of held parcels / median $/sqft of round-value 2025-26 "
           "resets in the same tract (one source, size-controlled). 1.00 = roll equals market.", ""]
    reg = {r: [x for x in rows if x["region"] == r] for r in ZIPS}
    out += ["| Measure (tract medians) | SGV | South LA | SGV minus South LA (95% bootstrap) |",
            "|---|---|---|---|"]
    for key, label, fmt in [("n_parcels", "SFR parcels per tract", "{:,.0f}"),
                            ("median_base_year", "Median base year", "{:.0f}"),
                            ("share_base_le_2000", "Share with base year 2000 or earlier", "{:.0%}"),
                            ("hmda_median_value", "HMDA median property value", "${:,.0f}"),
                            ("median_roll_value", "Median roll value", "${:,.0f}"),
                            ("stock_ratio", "stock ratio", "{:.2f}"),
                            ("held_ratio", "held ratio", "{:.2f}"),
                            ("psf_ratio", "psf ratio", "{:.2f}")]:
        a = [x[key] for x in reg["SGV"] if x[key] is not None]
        b = [x[key] for x in reg["South LA"] if x[key] is not None]
        if len(a) < 10 or len(b) < 10:
            out.append(f"| {label} | n={len(a)} | n={len(b)} | too few tracts |")
            continue
        d, lo, hi = boot_diff(a, b)
        cell = (lambda v: fmt.format(v))
        diff = (f"{d:+.2f} ({lo:+.2f} to {hi:+.2f})" if "ratio" in key
                else f"{d:+.3f} ({lo:+.3f} to {hi:+.3f})" if key == "share_base_le_2000"
                else f"{d:+,.0f} ({lo:+,.0f} to {hi:+,.0f})")
        out.append(f"| {label} (tracts: {len(a)}, {len(b)}) | {cell(st.median(a))} "
                   f"[{cell(q(a, .25))}-{cell(q(a, .75))}] | {cell(st.median(b))} "
                   f"[{cell(q(b, .25))}-{cell(q(b, .75))}] | {diff} |")
    out += ["", "Brackets are the interquartile range across tracts. Bootstrap resamples tracts "
            "(2,000 draws, seed 20261105), so it reflects tract-to-tract spread, not parcel "
            "sampling.", ""]
    if cohorts:
        out += ["## Same base year, different gap", "",
                "Roll $/sqft over same-tract reset $/sqft, all parcels in study tracts with at "
                f"least {MIN_RESETS} resets, pooled by base-year cohort. Holding the base year fixed "
                "removes tenure mix; what is left is how much prices rose since purchase.", "",
                "| Base year | SGV | South LA |", "|---|---|---|"]
        for _, _, lab in COHORTS:
            a, b = cohorts["SGV"][lab], cohorts["South LA"][lab]
            out.append(f"| {lab} | {st.median(a):.2f} (n={len(a):,}) | "
                       f"{st.median(b):.2f} (n={len(b):,}) |")
        out.append("")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="q5_cache")
    ap.add_argument("--years", type=int, nargs="+", default=[2024, 2025])
    ap.add_argument("--out", default="Q5-PROP13-GAP.md")
    ap.add_argument("--csv", default="analysis/data/q5_tracts.csv")
    args = ap.parse_args()

    tracts = cached(args.cache, "tracts_2020.json", pull_tracts)
    acs_polys = cached(args.cache, "acs_b03002_polys.json", pull_acs)
    loans = hmda_by_tract(args.cache, args.years)
    rows, counts, assigned = [], {}, {}
    for region in ZIPS:
        parcels = cached(args.cache, f"roll_{region.replace(' ', '_')}.json",
                         lambda r=region: pull_parcels(r))
        by_tract, missed = assign(parcels, tracts)
        assigned[region] = by_tract
        acs, share = tract_demographics(by_tract, acs_polys)
        counts[f"{region} parcels"] = f"{len(parcels):,} ({missed:,} unplaced)"
        counts[f"{region} ACS match"] = (f"median {st.median(share):.0%} of a tract's parcels "
                                         f"fall in its assigned ACS polygon")
        for g, ps in by_tract.items():
            rows.append(tract_row(g, region, ps, loans.get(g, []), acs))
    counts["ACS join"] = f"{sum(r['pct_asian'] is not None for r in rows)} of {len(rows)} tracts (spatial)"
    study = [r for r in rows if in_study(r)]
    for region in ZIPS:
        counts[f"{region} study tracts"] = sum(r["region"] == region for r in study)
    with open(args.csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) + ["in_study"])
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["region"], r["geoid"])):
            w.writerow(r | {"in_study": in_study(r)})
    cohorts = {region: cohort_ratios(assigned[region],
                                     {r["geoid"] for r in study if r["region"] == region})
               for region in ZIPS}
    text = "\n".join(report(study, counts, cohorts)) + "\n"
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
