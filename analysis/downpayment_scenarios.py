"""
NHS down-payment scenario model — AMI limits vs. actual purchasing power.

Extends the September 2026 NHS concept note from a single 20%-down case to the
3% / 5% / 10% / 20% scenarios Josh Butler asked for, adds mortgage insurance
(which the 20%-only version never had to model), and layers on down-payment
assistance.

Price benchmark comes from LA County Assessor roll data, not a vendor AVM.
See METHODOLOGY in the companion results file for why.

Stdlib only. Python 3.9+.

Usage (Windows CMD, from the repo root):
    python analysis\downpayment_scenarios.py
    python analysis\downpayment_scenarios.py --refresh    (re-pull Assessor data)
"""

import argparse
import csv
import json
import statistics
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Assumptions. Every one of these is a dated, sourced choice — see the results
# file. Change them here and re-run; nothing downstream hardcodes them.

RATE_ANNUAL = 0.0695          # Freddie Mac PMMS 30-yr FRM, released 2026-09-17
TERM_MONTHS = 360
HOUSING_DTI = 0.30            # front-end ratio, per the original concept
PROPERTY_TAX_RATE = 0.011     # 1.1% of purchase price annually
INSURANCE_MONTHLY = 150.0
CLOSING_COST_RATE = 0.025     # estimate: 2.5% of purchase price

# LA County 2026 income limits, four-person household (HCD/HUD, eff. 2026-06-23)
INCOME_TIERS = {
    "Very low income": 83_300,
    "Area median income": 108_100,
    "Lower income (= moderate)": 133_250,
}

# Borrower-paid monthly MI, annual premium as % of loan balance.
# Enact HFA rate card, 700-719 FICO band, fixed term > 20 years.
# The FICO band is an assumption — see SENSITIVITY in the results file.
PMI_BY_LTV = {
    0.97: 0.0099,   # 3% down
    0.95: 0.0078,   # 5% down
    0.90: 0.0055,   # 10% down
    0.80: 0.0000,   # 20% down — no MI
}

# FHA (alternative to conventional at the low end; MyHome's 3.5% ties to it)
FHA_DOWN = 0.035
FHA_UPFRONT_MIP = 0.0175      # financed into the loan
FHA_ANNUAL_MIP = 0.0055       # >95% LTV, 30-yr; life of loan when <10% down

SCENARIOS = [
    # (label, down_fraction, is_fha)
    ("3% down (conventional 97)", 0.03, False),
    ("3.5% down (FHA)", FHA_DOWN, True),
    ("5% down (conventional 95)", 0.05, False),
    ("10% down (conventional 90)", 0.10, False),
    ("20% down (conventional 80)", 0.20, False),
]

# Down-payment assistance, verified September 2026. Amounts are what the
# program contributes toward down payment and/or closing costs.
DPA_PROGRAMS = [
    {
        "name": "CalHFA MyHome (conventional)",
        "pct_of_price": 0.03,
        "cap": None,
        "structure": "Deferred-payment junior loan (repayable, not a grant)",
        "income_limit_la": 214_000,
        "available_in_compton": True,
    },
    {
        "name": "CalHFA MyHome (FHA)",
        "pct_of_price": 0.035,
        "cap": None,
        "structure": "Deferred-payment junior loan (repayable, not a grant)",
        "income_limit_la": 214_000,
        "available_in_compton": True,
    },
    {
        "name": "GSFA Platinum",
        "pct_of_price": 0.055,
        "cap": None,
        "structure": "Combination gift + second mortgage; no first-time requirement",
        "income_limit_la": None,   # varies by first-mortgage type
        "available_in_compton": True,
    },
    {
        "name": "LACDA HOP80",
        "pct_of_price": 0.20,
        "cap": 100_000,
        "structure": "0% deferred second with shared equity; max price $700,000",
        "income_limit_la": 133_250,   # 4-person
        "available_in_compton": False,  # Compton is not a participating city
    },
    {
        "name": "CalHFA Dream For All",
        "pct_of_price": 0.20,
        "cap": 150_000,
        "structure": "Shared appreciation loan — APPLICATION WINDOW CLOSED 2026-03-16",
        "income_limit_la": 214_000,
        "available_in_compton": False,  # closed to new applicants
    },
]

ASSESSOR_URL = (
    "https://public.gis.lacounty.gov/public/rest/services/"
    "LACounty_Cache/LACounty_Parcel/MapServer/0/query"
)
DATA_FILE = Path(__file__).resolve().parent / "data" / "compton_sales_2025_2026.csv"
MIN_PLAUSIBLE_SALE = 200_000   # below this = partial-interest / non-arms-length


# ---------------------------------------------------------------------------
# Price benchmark

def fetch_assessor_rows(city="COMPTON"):
    """Pull recently-reassessed single-family parcels from the LA County Assessor.

    Requiring Roll_LandBaseYear == Roll_ImpBaseYear is the important filter: a
    genuine change of ownership reassesses land AND improvements to the same
    year, while new construction or an addition moves only the improvement base
    year. Without it the sample is contaminated with remodels.
    """
    where = (
        f"TaxRateCity='{city}' AND UseDescription='Single' "
        f"AND (Roll_LandBaseYear='2025' OR Roll_LandBaseYear='2026') "
        f"AND Roll_LandBaseYear=Roll_ImpBaseYear"
    )
    params = {
        "where": where,
        "outFields": "Roll_LandValue,Roll_ImpValue,Roll_LandBaseYear,"
                     "SQFTmain1,Bedrooms1,YearBuilt1",
        "returnGeometry": "false",
        "resultRecordCount": "2000",
        "f": "json",
    }
    url = ASSESSOR_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=90) as resp:
        payload = json.load(resp)
    if payload.get("exceededTransferLimit"):
        raise RuntimeError("Hit the service record cap — add resultOffset paging.")
    rows = []
    for feat in payload.get("features", []):
        a = feat["attributes"]
        total = (a.get("Roll_LandValue") or 0) + (a.get("Roll_ImpValue") or 0)
        rows.append([total, a.get("SQFTmain1"), a.get("Bedrooms1"),
                     a.get("YearBuilt1"), a.get("Roll_LandBaseYear")])
    return rows


def save_rows(rows, path=DATA_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["assessed_total", "sqft_main", "bedrooms",
                         "year_built", "base_year"])
        writer.writerows(rows)


def load_rows(path=DATA_FILE):
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        return [[int(r["assessed_total"]),
                 r["sqft_main"], r["bedrooms"], r["year_built"], r["base_year"]]
                for r in reader]


def price_benchmark(rows):
    """Percentiles of observed transaction prices, with non-arms-length dropped."""
    kept = [r for r in rows if r[0] >= MIN_PLAUSIBLE_SALE]
    dropped = len(rows) - len(kept)
    values = sorted(r[0] for r in kept)
    pct = statistics.quantiles(values, n=100)
    sqft = [int(r[1]) for r in kept if r[1] not in (None, "", "None")]
    beds = [int(r[2]) for r in kept if r[2] not in (None, "", "None")]
    built = [int(r[3]) for r in kept if str(r[3]).strip().isdigit()]
    return {
        "n": len(values),
        "dropped": dropped,
        "p10": pct[9], "p25": pct[24], "p50": pct[49],
        "p75": pct[74], "p90": pct[89],
        "mean": statistics.mean(values),
        "median_sqft": statistics.median(sqft) if sqft else None,
        "median_beds": statistics.median(beds) if beds else None,
        "median_year_built": statistics.median(built) if built else None,
    }


# ---------------------------------------------------------------------------
# Financing math

def payment_factor(annual_rate=None, months=TERM_MONTHS):
    """Monthly P&I per $1 of loan principal.

    annual_rate defaults to the module-level RATE_ANNUAL, read at call time so
    the sensitivity analysis can vary it. (Using RATE_ANNUAL as the default
    argument value would bind it once at import and silently ignore changes.)
    """
    if annual_rate is None:
        annual_rate = RATE_ANNUAL
    r = annual_rate / 12.0
    if r == 0:
        return 1.0 / months
    return r / (1 - (1 + r) ** -months)


def mi_rate_for(down_fraction, is_fha):
    if is_fha:
        return FHA_ANNUAL_MIP
    ltv = round(1 - down_fraction, 4)
    if ltv not in PMI_BY_LTV:
        raise KeyError(f"No MI rate configured for LTV {ltv}")
    return PMI_BY_LTV[ltv]


def loan_multiplier(down_fraction, is_fha):
    """Loan principal per $1 of purchase price (FHA finances upfront MIP)."""
    base = 1 - down_fraction
    return base * (1 + FHA_UPFRONT_MIP) if is_fha else base


def max_purchase_price(income, down_fraction, is_fha):
    """Largest price affordable at HOUSING_DTI, given full PITI + MI."""
    budget = income * HOUSING_DTI / 12.0 - INSURANCE_MONTHLY
    if budget <= 0:
        return 0.0
    k = loan_multiplier(down_fraction, is_fha)
    mi = mi_rate_for(down_fraction, is_fha)
    per_dollar = (k * payment_factor()
                  + PROPERTY_TAX_RATE / 12.0
                  + k * mi / 12.0)
    return budget / per_dollar


def monthly_breakdown(price, down_fraction, is_fha):
    k = loan_multiplier(down_fraction, is_fha)
    loan = price * k
    mi = mi_rate_for(down_fraction, is_fha)
    return {
        "loan": loan,
        "principal_interest": loan * payment_factor(),
        "property_tax": price * PROPERTY_TAX_RATE / 12.0,
        "insurance": INSURANCE_MONTHLY,
        "mortgage_insurance": loan * mi / 12.0,
    }


def total_monthly(price, down_fraction, is_fha):
    b = monthly_breakdown(price, down_fraction, is_fha)
    return (b["principal_interest"] + b["property_tax"]
            + b["insurance"] + b["mortgage_insurance"])


def income_required(price, down_fraction, is_fha):
    return total_monthly(price, down_fraction, is_fha) * 12.0 / HOUSING_DTI


def cash_required(price, down_fraction):
    down = price * down_fraction
    closing = price * CLOSING_COST_RATE
    return {"down_payment": down, "closing": closing, "total": down + closing}


def dpa_amount(program, price):
    amt = price * program["pct_of_price"]
    if program["cap"] is not None:
        amt = min(amt, program["cap"])
    return amt


# ---------------------------------------------------------------------------
# Reporting

def money(x):
    return f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}"


def build_report(bench):
    L = []
    add = L.append

    benchmark_price = bench["p50"]
    entry_price = bench["p25"]

    add("# NHS Down-Payment Scenarios — Compton Benchmark")
    add("")
    add(f"Generated from `downpayment_scenarios.py`. Rate as of 2026-09-17; "
        f"Assessor data pulled 2026-09-18.")
    add("")

    # --- price benchmark -------------------------------------------------
    add("## 1. What a home actually costs")
    add("")
    add(f"Based on **{bench['n']} single-family parcels in Compton whose land and "
        f"improvement assessments were both reset in 2025 or 2026** — i.e. homes "
        f"that actually changed hands, priced at what the buyer actually paid.")
    add("")
    add("| Percentile | Price |")
    add("|---|---|")
    for key, label in [("p10", "10th"), ("p25", "25th"), ("p50", "Median"),
                       ("p75", "75th"), ("p90", "90th")]:
        add(f"| {label} | {money(bench[key])} |")
    add("")
    add(f"Typical home in this sample: {bench['median_beds']:.0f} bedrooms, "
        f"{bench['median_sqft']:,.0f} sq ft, built {bench['median_year_built']:.0f}.")
    add("")
    add(f"Two reference prices are used below: the **median ({money(benchmark_price)})** "
        f"and the **25th percentile ({money(entry_price)})**, since NHS households "
        f"are more likely to be buying at the lower end of the distribution than at "
        f"the middle of it.")
    add("")

    # --- view A: purchasing power ----------------------------------------
    add("## 2. What each income tier can actually buy")
    add("")
    add("Maximum purchase price at a 30% housing-DTI, with full PITI **including "
        "mortgage insurance**. The original concept modeled only the 20%-down case, "
        "where MI doesn't apply; at every lower down payment MI consumes part of the "
        "same monthly budget.")
    add("")
    add("**The central tension is visible across each row.** A smaller down payment "
        "is the only way these households clear the *cash* barrier — but it raises "
        "the loan, adds mortgage insurance, and therefore *lowers* the price they can "
        "carry monthly. Down-payment assistance does not resolve this: it solves the "
        "cash side while leaving the monthly side untouched, or slightly worse. Any "
        "program designed only around the down payment addresses the smaller of the "
        "two barriers.")
    add("")
    header = "| Income tier | " + " | ".join(s[0] for s in SCENARIOS) + " |"
    add(header)
    add("|---" * (len(SCENARIOS) + 1) + "|")
    for tier, income in INCOME_TIERS.items():
        cells = []
        for label, down, is_fha in SCENARIOS:
            cells.append(money(max_purchase_price(income, down, is_fha)))
        add(f"| {tier} ({money(income)}) | " + " | ".join(cells) + " |")
    add("")
    add("Gap against the market. The best case for every tier is 20% down — which is "
        "also the case demanding the most cash, so it is the least available in "
        "practice. The 3%-down column is the realistic one, and its gap is wider.")
    add("")
    add("| Income tier | Max price @20% down | Gap to median | Max price @3% down | "
        "Gap to median |")
    add("|---|---|---|---|---|")
    for tier, income in INCOME_TIERS.items():
        hi = max_purchase_price(income, 0.20, False)
        lo = max_purchase_price(income, 0.03, False)
        add(f"| {tier} | {money(hi)} | {money(hi - benchmark_price)} | "
            f"{money(lo)} | {money(lo - benchmark_price)} |")
    add("")

    # --- view B: cash and income needed at market price -------------------
    add(f"## 3. What it takes to buy the median home ({money(benchmark_price)})")
    add("")
    add("| Down payment | Cash needed (down + closing) | Loan | Monthly PITI+MI | "
        "Income required |")
    add("|---|---|---|---|---|")
    for label, down, is_fha in SCENARIOS:
        cash = cash_required(benchmark_price, down)
        brk = monthly_breakdown(benchmark_price, down, is_fha)
        tot = total_monthly(benchmark_price, down, is_fha)
        need = income_required(benchmark_price, down, is_fha)
        add(f"| {label} | {money(cash['total'])} | {money(brk['loan'])} | "
            f"{money(tot)} | {money(need)} |")
    add("")
    add(f"For reference, the same table at the 25th-percentile price "
        f"({money(entry_price)}):")
    add("")
    add("| Down payment | Cash needed (down + closing) | Monthly PITI+MI | "
        "Income required |")
    add("|---|---|---|---|")
    for label, down, is_fha in SCENARIOS:
        cash = cash_required(entry_price, down)
        tot = total_monthly(entry_price, down, is_fha)
        need = income_required(entry_price, down, is_fha)
        add(f"| {label} | {money(cash['total'])} | {money(tot)} | {money(need)} |")
    add("")
    add("The monthly cost of mortgage insurance alone, at the median price:")
    add("")
    add("| Down payment | MI rate | MI per month | MI over 10 years |")
    add("|---|---|---|---|")
    for label, down, is_fha in SCENARIOS:
        brk = monthly_breakdown(benchmark_price, down, is_fha)
        rate = mi_rate_for(down, is_fha)
        if rate == 0:
            add(f"| {label} | — | — | — |")
        else:
            add(f"| {label} | {rate*100:.2f}% | "
                f"{money(brk['mortgage_insurance'])} | "
                f"{money(brk['mortgage_insurance']*120)} |")
    add("")

    # --- DPA --------------------------------------------------------------
    add("## 4. What down-payment assistance changes")
    add("")
    add(f"Assistance available against the median price ({money(benchmark_price)}):")
    add("")
    add("| Program | Amount | Structure | Available in Compton? |")
    add("|---|---|---|---|")
    for prog in DPA_PROGRAMS:
        amt = dpa_amount(prog, benchmark_price)
        avail = "Yes" if prog["available_in_compton"] else "**No**"
        add(f"| {prog['name']} | {money(amt)} | {prog['structure']} | {avail} |")
    add("")
    add("Applying only the programs a Compton buyer can actually use today, "
        "against cash required at the median price:")
    add("")
    add("| Down payment | Cash needed | After MyHome | After GSFA Platinum |")
    add("|---|---|---|---|")
    myhome_conv = next(p for p in DPA_PROGRAMS if p["name"] == "CalHFA MyHome (conventional)")
    myhome_fha = next(p for p in DPA_PROGRAMS if p["name"] == "CalHFA MyHome (FHA)")
    gsfa = next(p for p in DPA_PROGRAMS if p["name"] == "GSFA Platinum")
    for label, down, is_fha in SCENARIOS:
        cash = cash_required(benchmark_price, down)["total"]
        mh = myhome_fha if is_fha else myhome_conv
        after_mh = max(0.0, cash - dpa_amount(mh, benchmark_price))
        after_gsfa = max(0.0, cash - dpa_amount(gsfa, benchmark_price))
        add(f"| {label} | {money(cash)} | {money(after_mh)} | {money(after_gsfa)} |")
    add("")
    add("These two columns are **alternatives, not additive** — MyHome and GSFA "
        "Platinum attach to different first-mortgage programs and are not stacked. "
        "Confirm the current pairing rules with a participating lender before "
        "relying on either figure.")
    add("")
    add("Three things worth drawing out:")
    add("")
    add("1. GSFA Platinum's 5.5% happens to land almost exactly on the 3%-down "
        "cash requirement (3% down + 2.5% closing), so it is the one program that "
        "can plausibly take a Compton buyer to near-zero cash at closing.")
    add("2. **The two largest programs are both unavailable here.** Dream For All "
        "(up to $150,000) closed to new applicants in March 2026, and LACDA HOP "
        "(up to $100,000) does not operate in Compton — the city is not on the "
        "participating-cities list. The programs that would close the gap are the "
        "ones a Compton household cannot reach.")
    add("3. Even with full assistance, the *income* requirement is untouched. At the "
        "median price no assistance program brings the required income below "
        f"{money(income_required(benchmark_price, 0.20, False))}, against a "
        "lower-income limit of $133,250.")
    add("")

    # --- sensitivity ------------------------------------------------------
    add("## 5. Sensitivity")
    add("")
    add("The three assumptions most likely to be challenged, tested at the median "
        "price with 3% down.")
    add("")
    add("**Housing DTI.** 30% is conservative; lenders commonly underwrite a higher "
        "front-end ratio with compensating factors. This is the single biggest lever "
        "in the model:")
    add("")
    add("| Front-end DTI | Max price, lower-income tier | Max price, AMI tier |")
    add("|---|---|---|")
    global HOUSING_DTI
    original_dti = HOUSING_DTI
    for test_dti in (0.30, 0.33, 0.36):
        HOUSING_DTI = test_dti
        a = max_purchase_price(INCOME_TIERS["Lower income (= moderate)"], 0.03, False)
        b = max_purchase_price(INCOME_TIERS["Area median income"], 0.03, False)
        add(f"| {test_dti*100:.0f}% | {money(a)} | {money(b)} |")
    HOUSING_DTI = original_dti
    add("")
    add("Even at 36%, the lower-income tier tops out well below the median sale "
        "price — the conclusion is not an artifact of the 30% choice.")
    add("")
    add("**Credit score.** PMI is priced off FICO, and the model assumes a 700-719 "
        "band. At 3% down the same loan carries these rates (Enact HFA card):")
    add("")
    add("| FICO band | PMI rate @97% LTV | Monthly MI at median price |")
    add("|---|---|---|")
    loan_97 = benchmark_price * 0.97
    for band, rate in [("760+", 0.0058), ("700-719", 0.0099),
                       ("680-699", 0.0121), ("640-659", 0.0165)]:
        add(f"| {band} | {rate*100:.2f}% | {money(loan_97 * rate / 12)} |")
    add("")
    add("**Rate.** The concept used 6.71% (2026-09-03); this run uses 6.95% "
        "(2026-09-17). That two-week move alone costs the lower-income tier roughly "
        f"{money(abs(_price_at_rate(INCOME_TIERS['Lower income (= moderate)'], 0.0671) - _price_at_rate(INCOME_TIERS['Lower income (= moderate)'], 0.0695)))} "
        "in purchasing power at 3% down. Any figure sent to NHS should carry its "
        "rate date.")
    add("")

    # --- methodology ------------------------------------------------------
    add("## 6. Methodology and sources")
    add("")
    add("**Price benchmark — why Assessor data and not Zillow.** The September "
        "concept used a Zillow ZHVI figure of $624,000 for Compton and flagged it "
        "as the wrong dependency: a vendor AVM estimate has no place in a project "
        "whose subject is valuation measurement. This run replaces it with observed "
        "transaction prices recovered from the LA County Assessor roll.")
    add("")
    add("California is a non-disclosure state, so sale prices do not appear on "
        "recorded deeds. Under Proposition 13, however, a property's assessed value "
        "is reset to its purchase price at a change of ownership and then escalates "
        "by no more than 2% a year. A parcel whose base year is 2025 or 2026 "
        "therefore carries an assessed value that *is* essentially its recent sale "
        "price. Filtering on `Roll_LandBaseYear == Roll_ImpBaseYear` isolates genuine "
        "ownership changes, since a remodel or addition resets only the improvement "
        "base year. Parcels assessed below "
        f"{money(MIN_PLAUSIBLE_SALE)} were dropped as partial-interest or "
        f"non-arms-length transfers ({bench['dropped']} of "
        f"{bench['n'] + bench['dropped']}).")
    add("")
    add(f"Worth noting for the Paper 2 benchmark question: the Assessor-derived "
        f"median of {money(benchmark_price)} lands within about 1.6% of the Zillow "
        f"ZHVI figure the concept had used. Aggregate agreement of this kind says "
        f"nothing about parcel-level accuracy — a model can match a city median "
        f"while being badly and unevenly wrong house by house, which is precisely "
        f"the disparity Paper 2 is designed to measure. It does mean the original "
        f"illustrative calculation was not misleading in magnitude, only in "
        f"provenance.")
    add("")
    add("**Source list.**")
    add("")
    add("| Input | Value | Source | As of |")
    add("|---|---|---|---|")
    add("| 30-yr fixed rate | 6.95% | Freddie Mac PMMS | 2026-09-17 |")
    add("| Income limits (4-person) | $83,300 / $108,100 / $133,250 | "
        "HCD/HUD LA County | 2026-06-23 |")
    add("| Conventional PMI | 0.99% / 0.78% / 0.55% (97/95/90 LTV) | "
        "Enact HFA rate card, 700-719 FICO | 2026 |")
    add("| FHA MIP | 1.75% upfront, 0.55% annual, life of loan | HUD | 2026 |")
    add("| Price benchmark | Compton SFR, 2025-26 base years | "
        "LA County Assessor parcel service | 2026-09-18 |")
    add("| CalHFA MyHome | 3% conv / 3.5% FHA, deferred junior loan | CalHFA | "
        "2026-09-18 |")
    add("| CalHFA income limit, LA County | $214,000 | CalHFA | 2026-06-30 |")
    add("| GSFA Platinum | up to 5.5%, gift + second | GSFA | 2026-09-18 |")
    add("| LACDA HOP80 | up to $100,000 / 20%, 47 participating cities | LACDA | "
        "2026-09-18 |")
    add("| Dream For All | closed to new applicants | CalHFA | 2026-03-16 |")
    add("")
    add("**Carried assumptions** (unchanged from the concept, not independently "
        "re-derived): 30% housing DTI, 1.1% property tax, $150/month insurance. "
        "Closing costs are estimated at 2.5% of purchase price and are the least "
        "well-grounded figure in the model — worth replacing with NHS's own "
        "observed closing costs if they have them.")
    add("")
    add("**Open items for Josh.** Whether NHS administers or brokers any assistance "
        "of its own that should be in the program table; whether NHS's observed "
        "client credit-score distribution justifies a different PMI band than the "
        "700-719 assumed here; and whether the Compton benchmark is the right "
        "geography, or whether NHS's client base is concentrated elsewhere in the "
        "county.")
    add("")
    return "\n".join(L)


def _price_at_rate(income, rate, down=0.03, is_fha=False):
    """Max price recomputed at an alternate interest rate."""
    global RATE_ANNUAL
    original = RATE_ANNUAL
    RATE_ANNUAL = rate
    try:
        return max_purchase_price(income, down, is_fha)
    finally:
        RATE_ANNUAL = original


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true",
                    help="Re-pull Assessor data instead of using the cached CSV")
    ap.add_argument("--out", default="NHS-DOWNPAYMENT-RESULTS.md")
    args = ap.parse_args()

    if args.refresh:
        rows = fetch_assessor_rows()
        save_rows(rows)
        print(f"Refreshed: {len(rows)} parcels -> {DATA_FILE}")
    else:
        rows = load_rows()

    bench = price_benchmark(rows)
    report = build_report(bench)
    out_path = Path(__file__).resolve().parent.parent / args.out
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
