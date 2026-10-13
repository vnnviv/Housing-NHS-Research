r"""
NHS assistance-sizing model: how much assistance moves a "mortgage ready"
household to a home that actually exists in the market?

Builds on downpayment_scenarios.py (same financing math, same Assessor price
benchmark, same assumptions) and answers the question that script leaves open:
not "what can each income tier afford", but "how many dollars of assistance
close the gap to a real recent sale, and which barrier do those dollars close".

The accounting is one identity. For a home at price P with closing costs C and
a household holding S in savings, the first mortgage can be no larger than
Lt (the largest loan whose full payment, including taxes, insurance and mortgage
insurance, fits the DTI budget). Everything else must come from somewhere:

    outside funding needed = P + C - min(starting loan, Lt)
    assistance needed      = max(0, outside funding - S)

It splits into two parts:
  * cash barrier   - down payment + closing costs the household cannot cover
  * income barrier - principal reduction needed so the monthly payment fits

Stdlib only. Python 3.9+. Reads analysis/data/compton_sales_2025_2026.csv.

Usage (Windows CMD, from the repo root):
    python analysis\assistance_sizing.py
    python analysis\assistance_sizing.py --rate 0.0740 --rate-date 2026-10-08
    python analysis\assistance_sizing.py --sales-csv my_sales.csv --sales-col price
"""

import argparse
import csv
import statistics
from pathlib import Path

import downpayment_scenarios as dps

BASELINE_SAVINGS = 10_000          # PLACEHOLDER - replace with NHS client data
SAVINGS_GRID = [0, 10_000, 25_000]
REACH_CAPS = [0, 20_000, 35_000, 50_000, 100_000, 150_000, 250_000, 350_000]
PRICE_PERCENTILES = [("p10", "10th"), ("p25", "25th"), ("p50", "Median"),
                     ("p75", "75th")]
CONV_3 = (0.03, False)
FHA_35 = (dps.FHA_DOWN, True)


# ---------------------------------------------------------------------------
# Core model
# ---------------------------------------------------------------------------

def mi_rate_by_ltv(ltv, is_fha):
    """Mortgage-insurance rate for an arbitrary first-mortgage LTV.

    downpayment_scenarios.py only prices four fixed LTVs. Assistance can leave
    the first mortgage at any LTV, so rates are banded: above 95% uses the 97
    rate, 90-95% the 95 rate, 80-90% the 90 rate, and 80% or below none. The
    80-85% range is therefore priced at the 90-LTV rate, which is conservative.
    Reproduces dps.mi_rate_for exactly at 97 / 95 / 90 / 80.
    """
    if is_fha:
        return dps.FHA_ANNUAL_MIP
    ltv = round(ltv, 6)   # guard against 0.8000000000000002 style float noise
    if ltv > 0.95:
        return dps.PMI_BY_LTV[0.97]
    if ltv > 0.90:
        return dps.PMI_BY_LTV[0.95]
    if ltv > 0.80:
        return dps.PMI_BY_LTV[0.90]
    return 0.0


def monthly_payment(price, base_loan, is_fha):
    """Full PITI + MI for a first mortgage of base_loan on a home at price."""
    loan = base_loan * (1 + dps.FHA_UPFRONT_MIP) if is_fha else base_loan
    mi = mi_rate_by_ltv(base_loan / price, is_fha)
    return (loan * dps.payment_factor()
            + price * dps.PROPERTY_TAX_RATE / 12.0
            + dps.INSURANCE_MONTHLY
            + loan * mi / 12.0)


def max_base_loan(price, income, is_fha):
    """Largest first mortgage the DTI budget carries on this home.

    Returns (loan, feasible). Payment is non-decreasing in loan size, so
    bisection on "payment <= budget" finds the threshold exactly. Not feasible
    means taxes and insurance alone exceed the budget.
    """
    budget = income * dps.HOUSING_DTI / 12.0
    if monthly_payment(price, 0.0, is_fha) > budget:
        return 0.0, False
    lo, hi = 0.0, price
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if monthly_payment(price, mid, is_fha) <= budget:
            lo = mid
        else:
            hi = mid
    return lo, True


def assistance_needed(price, income, down, is_fha, savings):
    start_loan = price * (1 - down)
    cap, feasible = max_base_loan(price, income, is_fha)
    target = min(start_loan, cap)
    reduction = start_loan - target                    # income barrier
    cash_need = price * (down + dps.CLOSING_COST_RATE)  # cash barrier, gross
    a_cash = max(0.0, cash_need - savings)
    surplus = max(0.0, savings - cash_need)
    a_income = max(0.0, reduction - surplus)
    return {
        "price": price, "cash_need": cash_need, "reduction": reduction,
        "a_cash": a_cash, "a_income": a_income, "total": a_cash + a_income,
        "feasible": feasible,
    }


def best_available_program(price):
    """Largest listed program a Compton buyer can use today (dollars)."""
    return max(dps.dpa_amount(p, price) for p in dps.DPA_PROGRAMS
               if p["available_in_compton"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def money(x):
    return dps.money(x)


def pct(x):
    return f"{x * 100:.0f}%"


def load_external_prices(path, column):
    with open(path, newline="") as fh:
        vals = []
        for row in csv.DictReader(fh):
            try:
                vals.append(float(str(row[column]).replace(",", "").replace("$", "")))
            except (KeyError, ValueError):
                continue
    if len(vals) < 20:
        raise SystemExit(f"Only {len(vals)} usable prices in {path}:{column}; need >= 20.")
    return sorted(vals)


def parcel_prices(rows):
    return sorted(r[0] for r in rows if r[0] >= dps.MIN_PLAUSIBLE_SALE)


def with_rate(rate, fn):
    original = dps.RATE_ANNUAL
    dps.RATE_ANNUAL = rate
    try:
        return fn()
    finally:
        dps.RATE_ANNUAL = original


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def build_report(bench, prices, rate, rate_date, savings, external):
    L = []
    add = L.append
    tiers = dps.INCOME_TIERS
    p = {k: bench[k] for k, _ in PRICE_PERCENTILES}
    n = len(prices)

    add("# NHS Assistance Sizing - Compton")
    add("")
    add(f"Generated by `assistance_sizing.py`. Rate {rate * 100:.2f}% "
        f"(Freddie Mac PMMS, {rate_date}). Price benchmark: {n} Compton "
        f"single-family parcels in the LA County Assessor roll whose land and "
        f"improvement base years were both reset in 2025-26. Household savings "
        f"assumed: {money(savings)} (**placeholder - not NHS client data**).")
    add("")
    add("**Illustrative, not a finding about NHS clients.** The savings level, the "
        "closing-cost rate, and the program amounts are assumptions or dated "
        "lookups. Read these as a structure for the answer, with dollar figures "
        "that move when the inputs are replaced.")
    add("")

    # --- 1. headline ---------------------------------------------------
    add("## 1. Assistance needed to buy a home that exists")
    add("")
    add("3% down, conventional. Each row is a household at that income tier "
        "buying at that point of the recent-sales price distribution. The "
        "percentile is also the share of recent Compton sales priced at or "
        "below that home.")
    add("")
    add("**Cash part** is the down payment and closing costs the household "
        "cannot cover from savings. **Income part** is the principal reduction "
        "needed before the monthly payment fits the DTI budget. A down-payment "
        "program can only address the first.")
    add("")
    add("| Income tier | Home (percentile) | Price | Assistance needed | Cash part | "
        "Income part | Needed as % of price | Same home, FHA 3.5% |")
    add("|---|---|---|---|---|---|---|---|")
    for tier, income in tiers.items():
        for key, label in PRICE_PERCENTILES:
            r = assistance_needed(p[key], income, *CONV_3, savings)
            f = assistance_needed(p[key], income, *FHA_35, savings)
            add(f"| {tier} ({money(income)}) | {label} | {money(p[key])} | "
                f"**{money(r['total'])}** | {money(r['a_cash'])} | "
                f"{money(r['a_income'])} | {pct(r['total'] / p[key])} | "
                f"{money(f['total'])} |")
    add("")

    # --- 2. versus programs --------------------------------------------
    add("## 2. What the listed programs cover")
    add("")
    add("Best program a Compton buyer can use today (GSFA Platinum, 5.5% of "
        "price; CalHFA MyHome is smaller; Dream For All is closed and LACDA "
        "HOP does not operate in Compton). Amounts as looked up 2026-09-18 "
        "and carried in `downpayment_scenarios.py`; not re-verified for this run.")
    add("")
    add("| Income tier | Home | Assistance needed | Best available program | "
        "Gap left after program | Program covers |")
    add("|---|---|---|---|---|---|")
    for tier, income in tiers.items():
        for key, label in PRICE_PERCENTILES[1:3]:
            r = assistance_needed(p[key], income, *CONV_3, savings)
            prog = best_available_program(p[key])
            gap = max(0.0, r["total"] - prog)
            add(f"| {tier} | {label} ({money(p[key])}) | {money(r['total'])} | "
                f"{money(prog)} | {money(gap)} | "
                f"{pct(min(1.0, prog / r['total'])) if r['total'] else 'n/a'} |")
    add("")
    add("Programs of this type fund the down payment and closing costs. They do "
        "not reduce the first mortgage below what the lender would otherwise "
        "write, so they close the cash part and leave the income part in place.")
    add("")

    # --- 3. reach ------------------------------------------------------
    add("## 3. What a given assistance level opens up")
    add("")
    add(f"Share of the {n} recent Compton sales a household at each income tier "
        f"could buy, 3% down, with {money(savings)} in savings, at each level of "
        f"assistance. This is the table for setting a program cap: read across to "
        f"the dollar amount that reaches the share of the market you want.")
    add("")
    add("| Income tier | " + " | ".join(money(c) for c in REACH_CAPS) + " |")
    add("|---|" + "---|" * len(REACH_CAPS))
    for tier, income in tiers.items():
        needs = [assistance_needed(x, income, *CONV_3, savings)["total"] for x in prices]
        cells = [pct(sum(1 for v in needs if v <= c) / n) for c in REACH_CAPS]
        add(f"| {tier} | " + " | ".join(cells) + " |")
    add("")

    # --- 4. savings sensitivity ----------------------------------------
    add("## 4. How much the savings assumption matters")
    add("")
    add("Total assistance needed, 3% down, by household savings.")
    add("")
    add("| Income tier | Home | " + " | ".join(f"Savings {money(s)}" for s in SAVINGS_GRID) + " |")
    add("|---|---|" + "---|" * len(SAVINGS_GRID))
    for tier, income in tiers.items():
        for key, label in PRICE_PERCENTILES[1:3]:
            cells = [money(assistance_needed(p[key], income, *CONV_3, s)["total"])
                     for s in SAVINGS_GRID]
            add(f"| {tier} | {label} | " + " | ".join(cells) + " |")
    add("")
    add("Savings move the answer one dollar for one dollar, so a $10,000 change "
        "in what a typical client holds changes every figure by $10,000. It does "
        "not change how large the income part is.")
    add("")

    # --- 5. benchmark sensitivity --------------------------------------
    add("## 5. How much the price benchmark matters")
    add("")
    add("The conclusion about the size of the gap depends on which price "
        "benchmark stands in for \"something that exists in the market\". Median "
        "home, 3% down, lower-income and area-median tiers.")
    add("")
    lower = tiers["Lower income (= moderate)"]
    ami = tiers["Area median income"]
    bench_rows = [("Assessor 2025-26 resets, as observed", p["p50"])]
    for mult in (1.05, 1.10):
        bench_rows.append((f"Assessor +{(mult - 1) * 100:.0f}% (stress: assumes reset values lag sale prices)",
                           p["p50"] * mult))
    bench_rows.append(("Zillow ZHVI median from the September concept "
                       "(flagged there as the wrong dependency; shown for comparison)", 624_000.0))
    if external:
        ext_med = statistics.median(external)
        bench_rows.append((f"Supplied sales file (n={len(external)}, median)", ext_med))
    add("| Price benchmark | Median price | Lower-income tier | Area-median tier |")
    add("|---|---|---|---|")
    for label, price in bench_rows:
        a = assistance_needed(price, lower, *CONV_3, savings)["total"]
        b = assistance_needed(price, ami, *CONV_3, savings)["total"]
        add(f"| {label} | {money(price)} | {money(a)} | {money(b)} |")
    add("")
    dP = 0.05 * p["p50"]
    el = [(assistance_needed(p["p50"] + dP, inc, *CONV_3, savings)["total"]
           - assistance_needed(p["p50"], inc, *CONV_3, savings)["total"]) / dP
          for inc in (lower, ami)]
    if abs(el[0] - el[1]) < 0.005:
        slope = f"${el[0]:.2f}"
    else:
        slope = f"${el[0]:.2f} (lower-income) or ${el[1]:.2f} (area-median)"
    add(f"**Sensitivity.** Each extra $1 of price adds {slope} of required "
        f"assistance, because a higher price also raises the property-tax share "
        f"of the monthly budget and shrinks the loan the household can carry. A 5% "
        f"error in the benchmark price ({money(dP)}) is therefore a larger error "
        f"in the assistance figure.")
    add("")
    add("The Assessor benchmark is not a vendor estimate, but it is not a recorded "
        "sale price either. For parcels reassessed in 2025-26 it should sit close "
        "to the purchase price; the stress rows are there to show what happens if "
        "it does not, not to claim that it does. A recent-sales file (`--sales-csv`) "
        "would replace the stress rows with a measured comparison.")
    add("")

    # --- 6. rate sensitivity -------------------------------------------
    add("## 6. Interest rate")
    add("")
    add("The rate moved sharply between the two earlier runs and today. Median "
        "home, 3% down, same savings.")
    add("")
    add("| Rate | Date | Lower-income tier | Area-median tier |")
    add("|---|---|---|---|")
    rate_rows = [(0.0671, "2026-09-03", "September concept"),
                 (0.0695, "2026-09-17", "previous run"),
                 (rate, rate_date, "this run")]
    seen = set()
    for r_, d_, note in rate_rows:
        if (r_, d_) in seen:
            continue
        seen.add((r_, d_))
        a = with_rate(r_, lambda: assistance_needed(p["p50"], lower, *CONV_3, savings)["total"])
        b = with_rate(r_, lambda: assistance_needed(p["p50"], ami, *CONV_3, savings)["total"])
        add(f"| {r_ * 100:.2f}% | {d_} ({note}) | {money(a)} | {money(b)} |")
    add("")

    # --- 6b. underwriting ratio ----------------------------------------
    add("## 7. Underwriting ratio")
    add("")
    add("The 30% front-end ratio is the largest single lever in the earlier "
        "analysis. Total assistance needed, 3% down, by ratio.")
    add("")
    add("| Income tier | Home | 30% | 33% | 36% |")
    add("|---|---|---|---|---|")
    original_dti = dps.HOUSING_DTI
    try:
        for tier, income in tiers.items():
            for key, label in PRICE_PERCENTILES[1:3]:
                cells = []
                for dti in (0.30, 0.33, 0.36):
                    dps.HOUSING_DTI = dti
                    cells.append(money(assistance_needed(p[key], income, *CONV_3, savings)["total"]))
                add(f"| {tier} | {label} | " + " | ".join(cells) + " |")
    finally:
        dps.HOUSING_DTI = original_dti
    add("")
    add("Raising the ratio shrinks the gap but does not close it for any tier at "
        "the median price. Higher ratios also raise default risk, so this is a "
        "sensitivity, not a recommendation.")
    add("")

    # --- 8. structure / what it does not model -------------------------
    add("## 8. What this does not model")
    add("")
    add("- **Structure of the assistance.** Dollars are counted the same whether "
        "they are a grant, a forgivable second, or a repayable deferred second. "
        "Structure decides what a program costs to run, not how many dollars a "
        "household needs.")
    add("- **Lending limits.** No combined loan-to-value cap is checked. A second "
        "lien large enough to close the income part may not be permitted under "
        "existing programs, which is a design question, not a modeling one.")
    add("- **Mortgage insurance** is banded by first-mortgage LTV from one rate "
        "card at 700-719 FICO; 80-85% LTV is priced at the 90-LTV rate.")
    add("- **Down-payment choice drops out of the total** once the income part is "
        "positive: assistance reduces the loan to the same size regardless of "
        "the starting down payment. Only the split between cash and income parts "
        "depends on it. FHA differs slightly through its financed upfront premium.")
    add("- **One geography, one household size.** Compton only; four-person "
        "income limits only; flat 1.1% property tax.")
    add("- **Closing costs** at 2.5% of price are the least grounded input.")
    add("")
    add("**Questions for Josh:** typical client savings and credit band; actual "
        "closing costs on NHS purchases; whether NHS clients are concentrated in "
        "Compton; which assistance instruments NHS can actually deploy.")
    add("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=float, default=0.0740,
                    help="30-yr fixed rate as a decimal (default 0.0740)")
    ap.add_argument("--rate-date", default="2026-10-08",
                    help="date label for the rate (Freddie Mac PMMS Thursday)")
    ap.add_argument("--savings", type=float, default=BASELINE_SAVINGS)
    ap.add_argument("--sales-csv", help="optional recent sales file for a benchmark comparison")
    ap.add_argument("--sales-col", default="price")
    ap.add_argument("--out", default="NHS-ASSISTANCE-SIZING.md")
    args = ap.parse_args()

    dps.RATE_ANNUAL = args.rate
    rows = dps.load_rows()
    bench = dps.price_benchmark(rows)
    prices = parcel_prices(rows)
    external = load_external_prices(args.sales_csv, args.sales_col) if args.sales_csv else None

    report = build_report(bench, prices, args.rate, args.rate_date, args.savings, external)
    out_path = Path(__file__).resolve().parent.parent / args.out
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
