r"""
Income-cap sensitivity engine: how far is a program's income cap from the income a
household needs to buy a recent home, and how much does that depend on assumptions?

Companion to assistance_sizing.py. That script asks "how many assistance dollars does
a household at income Y need for this home". This one inverts it: "what income does
the home require, given R dollars of principal reduction", and compares that with the
named caps. Governing document: ANALYSIS-PLAN.md.

Design choices that differ from assistance_sizing.py, on purpose:
  * Pure functions. Nothing here mutates downpayment_scenarios globals, so grids are
    safe to run in any order. Defaults are read from dps once, at Params creation.
  * Cash and income barriers are separate outputs. Required income assumes cash needs
    are met; the cash gap is reported alongside, never folded in.
  * Independent re-implementation of the financing math. tests/test_cap_sensitivity.py
    checks agreement with assistance_sizing.py and with closed-form amortization.

EXPLORATORY: every Compton result is exploratory (see ANALYSIS-PLAN.md). Rate, tax,
insurance, savings and closing-cost ranges below are PLACEHOLDERS until sourced.

Stdlib only. Python 3.9+.

Usage (Windows CMD, from the repo root):
    python analysis\cap_sensitivity.py
    python analysis\cap_sensitivity.py --rate 0.0740 --rate-date 2026-10-08
"""

import argparse
import itertools
import math
from dataclasses import dataclass, replace
from pathlib import Path

import downpayment_scenarios as dps


# ---------------------------------------------------------------------------
# Parameters

@dataclass(frozen=True)
class Params:
    rate: float = 0.0740                         # PMMS 2026-10-08, as in the repo
    term_months: int = 360
    tax_rate: float = dps.PROPERTY_TAX_RATE      # annual, of price
    insurance_monthly: float = dps.INSURANCE_MONTHLY
    closing_rate: float = dps.CLOSING_COST_RATE  # of price
    housing_dti: float = 0.30                    # front-end ratio only
    mi_scale: float = 1.0                        # credit multiplier on conventional MI
    savings: float = 10_000.0                    # PLACEHOLDER
    is_fha: bool = False
    down: float = 0.03


# ---------------------------------------------------------------------------
# Financing math (pure)

def payment_factor(rate, months):
    """Monthly principal and interest per $1 of loan."""
    r = rate / 12.0
    if r == 0:
        return 1.0 / months
    return r / (1.0 - (1.0 + r) ** -months)


def mi_rate(ltv, p):
    """Annual mortgage-insurance rate for a first mortgage at this LTV.

    Same banding as assistance_sizing.mi_rate_by_ltv: above 95% uses the 97 rate,
    90-95% the 95 rate, 80-90% the 90 rate, 80% or below none.
    """
    if p.is_fha:
        return dps.FHA_ANNUAL_MIP
    ltv = round(ltv, 6)
    if ltv > 0.95:
        base = dps.PMI_BY_LTV[0.97]
    elif ltv > 0.90:
        base = dps.PMI_BY_LTV[0.95]
    elif ltv > 0.80:
        base = dps.PMI_BY_LTV[0.90]
    else:
        return 0.0
    return base * p.mi_scale


def monthly_payment(price, base_loan, p):
    """Full PITI plus mortgage insurance for a first mortgage on a home at price."""
    loan = base_loan * (1.0 + dps.FHA_UPFRONT_MIP) if p.is_fha else base_loan
    return (loan * payment_factor(p.rate, p.term_months)
            + price * p.tax_rate / 12.0
            + p.insurance_monthly
            + loan * mi_rate(base_loan / price, p) / 12.0)


def start_loan(price, p):
    return price * (1.0 - p.down)


def cash_need(price, p):
    return price * (p.down + p.closing_rate)


def cash_gap(price, p):
    """Down payment plus closing costs not covered by savings."""
    return max(0.0, cash_need(price, p) - p.savings)


def surplus_savings(price, p):
    """Savings left after cash needs; the existing model applies it to principal."""
    return max(0.0, p.savings - cash_need(price, p))


def loan_after_reduction(price, p, reduction):
    return max(0.0, start_loan(price, p) - reduction - surplus_savings(price, p))


def required_income(price, p, reduction=0.0):
    """Minimum annual income that carries the first mortgage after principal reduction.

    Cash needs are assumed met (see cash_gap for what that costs). reduction is soft
    assistance beyond cash, counted as dollar-for-dollar principal reduction.
    """
    loan = loan_after_reduction(price, p, reduction)
    return monthly_payment(price, loan, p) * 12.0 / p.housing_dti


def max_loan(price, income, p):
    """Largest first mortgage the housing-ratio budget carries. (loan, feasible)."""
    budget = income * p.housing_dti / 12.0
    if monthly_payment(price, 0.0, p) > budget:
        return 0.0, False
    lo, hi = 0.0, price
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if monthly_payment(price, mid, p) <= budget:
            lo = mid
        else:
            hi = mid
    return lo, True


def assistance_needed(price, income, p):
    """Total assistance (cash gap + principal reduction) for a household at income.

    Same identity as assistance_sizing.assistance_needed, written independently.
    """
    cap_loan, feasible = max_loan(price, income, p)
    reduction = start_loan(price, p) - min(start_loan(price, p), cap_loan)
    a_cash = cash_gap(price, p)
    a_income = max(0.0, reduction - surplus_savings(price, p))
    return {"cash": a_cash, "income": a_income, "total": a_cash + a_income,
            "feasible": feasible}


def reach_share(prices, income, p, reduction=0.0):
    """Share of the given prices a household at this income can buy."""
    ok = sum(1 for x in prices if required_income(x, p, reduction) <= income + 1e-9)
    return ok / len(prices)


# ---------------------------------------------------------------------------
# Axes, flips, tornado

# axis -> (low, high, provenance). PLACEHOLDER ranges unless noted; see ANALYSIS-PLAN.md.
UNCERTAINTY_AXES = {
    "rate":              (0.060, 0.080, "PLACEHOLDER: replace with PMMS 2023-2026 range"),
    "price_mult":        (0.95, 1.10, "scenario: Assessor-reset vs sale gap unmeasured"),
    "mi_scale":          (0.0058 / 0.0099, 0.0165 / 0.0099, "repo rate card: 760+ to 640-659"),
    "tax_rate":          (0.0100, 0.0125, "PLACEHOLDER: city tax rate area"),
    "insurance_monthly": (100.0, 300.0, "PLACEHOLDER: no quotes sourced"),
}

GRID = {
    "rate": [0.060, 0.065, 0.070, 0.074, 0.080],
    "price_mult": [0.95, 1.00, 1.05, 1.10],
    "mi_scale": [0.0058 / 0.0099, 1.0, 0.0165 / 0.0099],
    "tax_rate": [0.0100, 0.0110, 0.0125],
    "insurance_monthly": [100.0, 150.0, 300.0],
}

POLICY_DTI = [0.28, 0.30, 0.33, 0.36]
REDUCTIONS = [0, 25_000, 50_000, 100_000, 150_000]

# (name, 4-person dollars, status)
CAPS = [
    ("HUD very low", 83_300, "verified (HUD FY2026, LA)"),
    ("MFI (reference, not a cap)", 108_100, "verified (HUD FY2026, LA)"),
    ("HUD low = HCD moderate", 133_250, "verified (HCD 2026 memo)"),
    ("Greenline", 151_300, "2024 materials, possibly stale"),
    ("CalHFA standard (flat)", 214_000, "verified figure; relationship to AMI unexplained"),
]


def apply_axis(price, p, axis, x):
    """Return (price, params) with one axis set to x."""
    if axis == "price_mult":
        return price * x, p
    return price, replace(p, **{axis: x})


def required_at(price, p, reduction, axis=None, x=None):
    if axis is not None:
        price, p = apply_axis(price, p, axis, x)
    return required_income(price, p, reduction)


def flip_point(axis, lo, hi, price, p, reduction, cap, iters=100):
    """Value of axis in [lo, hi] where required income crosses cap, others at base.

    Returns {"value": v} if the cap is crossed inside the range, otherwise
    {"value": None, "side": "above"|"below"} saying where required income sits
    relative to the cap across the whole range.
    """
    def above(x):
        return required_at(price, p, reduction, axis, x) > cap
    a_lo, a_hi = above(lo), above(hi)
    if a_lo == a_hi:
        return {"value": None, "side": "above" if a_lo else "below"}
    left, right = lo, hi
    for _ in range(iters):
        mid = (left + right) / 2.0
        if above(mid) == a_lo:
            left = mid
        else:
            right = mid
    return {"value": (left + right) / 2.0}


def tornado(price, p, reduction):
    """Swing in required income across each uncertainty axis, others at base."""
    rows = []
    for axis, (lo, hi, prov) in UNCERTAINTY_AXES.items():
        y_lo = required_at(price, p, reduction, axis, lo)
        y_hi = required_at(price, p, reduction, axis, hi)
        rows.append({"axis": axis, "low": lo, "high": hi, "y_low": y_lo,
                     "y_high": y_hi, "swing": abs(y_hi - y_lo), "prov": prov})
    rows.sort(key=lambda r: r["swing"], reverse=True)
    return rows


def grid_cells():
    keys = list(GRID)
    for combo in itertools.product(*(GRID[k] for k in keys)):
        yield dict(zip(keys, combo))


def grid_summary(price, p, reduction, dti, caps):
    """min / max required income over the grid and a label per cap."""
    base = replace(p, housing_dti=dti)
    ys = []
    for cell in grid_cells():
        q = replace(base, rate=cell["rate"], mi_scale=cell["mi_scale"],
                    tax_rate=cell["tax_rate"], insurance_monthly=cell["insurance_monthly"])
        ys.append(required_income(price * cell["price_mult"], q, reduction))
    out = {"min": min(ys), "max": max(ys), "n": len(ys), "labels": {}}
    for name, cap, _ in caps:
        n_ok = sum(1 for y in ys if y <= cap)
        if n_ok == len(ys):
            label = "reachable in every cell"
        elif n_ok == 0:
            label = "unreachable in every cell"
        else:
            label = f"mixed ({n_ok} of {len(ys)} cells)"
        out["labels"][name] = label
    return out


# ---------------------------------------------------------------------------
# Report

def money(x):
    return dps.money(x)


def pct(x):
    return f"{x * 100:.0f}%"


BIAS_TABLE = [
    ("Existing debts (none in ACS; front-end ratio only)", "Understates the barrier"),
    ("Unfinanceable fixers and cash-only sales inside the 25th percentile",
     "Understates the barrier (a financeable entry price is higher)"),
    ("Base-year price vs today's rates and prices",
     "Depends on price change since reset; trend or restrict the window"),
    ("Credit effect on the interest rate (not modeled)", "Understates the barrier for lower scores"),
    ("Wealth (unobserved)", "Cash-barrier shares unknowable; only the cash gap is reported"),
    ("Non-arm's-length resets in the sample", "Noise, likely biased low on price; filter"),
    ("Assistance structure (grant vs repayable second)",
     "Dollars counted equally; repayable seconds with payments would raise required income"),
]


def build_report(bench, prices, rate, rate_date):
    p = Params(rate=rate)
    pts = [("25th", bench["p25"]), ("Median", bench["p50"]), ("75th", bench["p75"])]
    L = []
    add = L.append

    add("# Income-cap sensitivity: Compton (EXPLORATORY)")
    add("")
    add("**Exploratory.** The Compton data and earlier tables were seen before "
        "`ANALYSIS-PLAN.md` existed, so nothing here is confirmatory. Ranges for rate, "
        "tax, insurance, savings and closing costs are placeholders until sourced. "
        "Not a finding about NHS clients, and no statement about algorithmic bias.")
    add("")
    add(f"Generated by `cap_sensitivity.py`. Rate {rate * 100:.2f}% (Freddie Mac PMMS, "
        f"{rate_date}). Price proxy: {bench['n']} Compton single-family parcels, Assessor "
        f"base-year values for 2025-26 resets, **not recorded sale prices**. 4-person "
        f"caps. Front-end ratio {p.housing_dti * 100:.0f}% unless stated. 3% down, "
        f"conventional, 700-719 credit band.")
    add("")

    add("## 1. Income a home requires vs the caps")
    add("")
    add("Required income assumes cash needs are met and that `R` dollars of soft "
        "assistance reduce the first mortgage dollar for dollar. A household at the cap "
        "is the best-off eligible household: if it cannot buy, no eligible household can.")
    add("")
    cap_names = [c[0] for c in CAPS]
    add("| Home | Price | R | Required income | " + " | ".join(cap_names) + " |")
    add("|---|---|---|---|" + "---|" * len(CAPS))
    for label, price in pts[:2]:
        for R in REDUCTIONS:
            y = required_income(price, p, R)
            ratios = " | ".join(f"{y / c[1]:.2f}x" for c in CAPS)
            add(f"| {label} | {money(price)} | {money(R)} | **{money(y)}** | {ratios} |")
    add("")
    add("Ratios above 1.00x mean even a household at that cap cannot carry the loan. "
        "The CalHFA flat limit is a county number, not a household-size schedule, so its "
        "ratio is not comparable with the HUD rows.")
    add("")

    add("## 2. Cash gap, reported separately")
    add("")
    add("| Home | Down payment | Cash needed (down + closing) | Gap at $0 savings | "
        "Gap at $10,000 | Gap at $25,000 |")
    add("|---|---|---|---|---|---|")
    for label, price in pts[:2]:
        for down in (0.03, 0.05, 0.10, 0.20):
            q = replace(p, down=down)
            need = cash_need(price, q)
            gaps = [max(0.0, need - s) for s in (0, 10_000, 25_000)]
            add(f"| {label} ({money(price)}) | {pct(down)} | {money(need)} | "
                + " | ".join(money(g) for g in gaps) + " |")
    add("")
    add("Savings below the cash need change the cash gap but not required income. That is "
        "why savings show zero swing in the tornado below.")
    add("")

    add("## 3. Reach: share of recent sales a household at the cap can buy")
    add("")
    add(f"Out of {len(prices)} retained parcels; base assumptions.")
    add("")
    add("| Cap | " + " | ".join(money(R) for R in REDUCTIONS) + " |")
    add("|---|" + "---|" * len(REDUCTIONS))
    for name, cap, _ in CAPS:
        cells = [pct(reach_share(prices, cap, p, R)) for R in REDUCTIONS]
        add(f"| {name} ({money(cap)}) | " + " | ".join(cells) + " |")
    add("")

    add("## 4. Reverse stress test: where does the answer flip?")
    add("")
    add("One axis moves at a time, others at base. Home: 25th percentile, `R` = $0. "
        "'Cap' column shows the dollar cap tested. A flip value outside the stated range "
        "means the conclusion does not flip inside plausible values.")
    add("")
    add("| Axis | Tested range | Cap | Result |")
    add("|---|---|---|---|")
    price25 = bench["p25"]
    wide = {"rate": (0.0, 0.12), "price_mult": (0.3, 1.5), "mi_scale": (0.0, 3.0),
            "tax_rate": (0.0, 0.03), "insurance_monthly": (0.0, 1_000.0)}
    for axis, (lo, hi, _) in UNCERTAINTY_AXES.items():
        for name, cap, _s in CAPS:
            if name.startswith("MFI"):
                continue
            inside = flip_point(axis, lo, hi, price25, p, 0.0, cap)
            if inside["value"] is not None:
                res = f"flips inside range at {_fmt_axis(axis, inside['value'])}"
            else:
                wl, wh = wide[axis]
                far = flip_point(axis, wl, wh, price25, p, 0.0, cap)
                where = ("no flip inside the range; required income stays "
                         + ("above" if inside["side"] == "above" else "below") + " the cap")
                if far["value"] is not None:
                    where += f"; it would flip at {_fmt_axis(axis, far['value'])}"
                res = where
            add(f"| {axis} | {_fmt_axis(axis, lo)} to {_fmt_axis(axis, hi)} | "
                f"{name} ({money(cap)}) | {res} |")
    add("")

    add("## 5. Which assumption moves required income most")
    add("")
    add("25th-percentile home, `R` = $0, swing across each axis' range. Placeholders are "
        "flagged; a ranking built on placeholder ranges is a ranking of the placeholders.")
    add("")
    add("| Axis | Low | High | Required income (low) | (high) | Swing | Range source |")
    add("|---|---|---|---|---|---|---|")
    for r in tornado(price25, p, 0.0):
        add(f"| {r['axis']} | {_fmt_axis(r['axis'], r['low'])} | "
            f"{_fmt_axis(r['axis'], r['high'])} | {money(r['y_low'])} | "
            f"{money(r['y_high'])} | **{money(r['swing'])}** | {r['prov']} |")
    add("")
    base_y = required_income(price25, p, 0.0)
    d_rate = (required_at(price25, p, 0.0, "rate", p.rate + 0.01) - base_y)
    d_price = (required_at(price25, p, 0.0, "price_mult", 1.10) - base_y)
    add(f"**Elasticities (25th percentile, `R` = $0).** +1 point of rate adds "
        f"{money(d_rate)} of required income; +10% price adds {money(d_price)}.")
    add("")

    add("## 6. Every cell of the grid")
    add("")
    add(f"Grid: {len(list(grid_cells()))} cells over rate, price multiplier, MI scale, "
        "tax and insurance. Housing ratio is a policy choice, so it is a separate row "
        "dimension, not part of the grid. Labels describe the grid; the cell count is "
        "not a probability.")
    add("")
    short = [c for c in CAPS if not c[0].startswith("MFI")]
    add("| Home | R | Ratio | Min required | Max required | " + " | ".join(c[0] for c in short) + " |")
    add("|---|---|---|---|---|" + "---|" * len(short))
    for label, price in pts[:2]:
        for R in (0, 50_000, 100_000):
            for dti in POLICY_DTI:
                g = grid_summary(price, p, R, dti, short)
                add(f"| {label} | {money(R)} | {dti * 100:.0f}% | {money(g['min'])} | "
                    f"{money(g['max'])} | " + " | ".join(g["labels"][c[0]] for c in short) + " |")
    add("")

    add("## 7. Direction of bias")
    add("")
    add("| Omitted or assumed | Effect on 'a cap-level household cannot reach a recent sale' |")
    add("|---|---|")
    for a, b in BIAS_TABLE:
        add(f"| {a} | {b} |")
    add("")
    add("Most omissions push toward understating the barrier, so the defensible reading of "
        "section 1 is a lower bound on the income barrier, not a point estimate.")
    add("")

    add("## 8. What this does not show")
    add("")
    add("- No count of Compton renter households by income band (needs ACS tract tables); "
        "so no statement that a share of households is excluded.")
    add("- Recent buyers need not resemble local renters. Reach is a share of sales, not of people.")
    add("- The `Single` filter drops condos and townhomes, which raises the 25th percentile.")
    add("- One city, one household size (4 persons), front-end ratio only.")
    add("- Held-out city not yet pulled; nothing here is confirmed.")
    add("")
    return "\n".join(L)


def _fmt_axis(axis, x):
    if axis in ("rate", "tax_rate"):
        return f"{x * 100:.2f}%"
    if axis == "insurance_monthly":
        return f"${x:,.0f}/mo"
    return f"{x:.2f}x" if axis in ("price_mult", "mi_scale") else f"{x}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=float, default=0.0740)
    ap.add_argument("--rate-date", default="2026-10-08")
    ap.add_argument("--out", default="NHS-CAP-SENSITIVITY.md")
    args = ap.parse_args()

    rows = dps.load_rows()
    bench = dps.price_benchmark(rows)
    prices = sorted(r[0] for r in rows if r[0] >= dps.MIN_PLAUSIBLE_SALE)
    report = build_report(bench, prices, args.rate, args.rate_date)
    out_path = Path(__file__).resolve().parent.parent / args.out
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
