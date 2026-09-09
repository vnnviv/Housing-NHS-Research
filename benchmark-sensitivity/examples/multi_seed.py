"""Multi-seed robustness harness for the benchmark-sensitivity demonstration.

Runs the full pipeline — simulate, fit the misspecified AVM, compute the four
disparity estimates, run the BSR and the coverage audit — across many draws,
then reports the distribution of BSR, sign-flip rate, coverage, and the
benchmark-independence diagnostics described in FINDINGS.md.

Usage:
    python examples/multi_seed.py --n-seeds 50
    python examples/multi_seed.py --n-seeds 50 --output-csv multi_seed_results.csv
"""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

from bsr import coverage_audit, sensitivity_report

# ---------------------------------------------------------------------------
# Same simulation and AVM as synthetic_demo.py, parameterised by seed.
# ---------------------------------------------------------------------------

N = 4000


def simulate(n=N, seed=20260905):
    """Synthetic county with zero true disparity by construction."""
    rng = np.random.default_rng(seed)
    group = rng.integers(0, 2, n)
    sqft = rng.normal(1650 - 180 * group, 320, n).clip(600)
    age = rng.normal(48 + 14 * group, 18, n).clip(1)
    quality = rng.normal(-0.35 * group, 1.0, n)  # unobserved by the modeler
    true_value = np.exp(4.9 + 0.62 * np.log(sqft) - 0.004 * age + 0.11 * quality) * 1000
    sale_price = true_value * np.exp(rng.normal(0, 0.07 + 0.06 * group, n))
    assessed = true_value * np.exp(-0.11 - 0.09 * group + rng.normal(0, 0.05, n))
    return group, sqft, age, sale_price, assessed


def fit_avm(sqft, age, sale_price, train):
    """OLS on log price. Sees size and age; cannot see quality."""
    X = np.column_stack([np.ones(sqft.size), np.log(sqft), age])
    beta, *_ = np.linalg.lstsq(X[train], np.log(sale_price[train]), rcond=None)
    return np.exp(X @ beta)


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def run_one(seed):
    """Run the full pipeline for one seed. Returns a dict of results."""
    group, sqft, age, sale_price, assessed = simulate(seed=seed)
    n = group.size
    train = slice(0, n // 2)
    cal = slice(n // 2, n // 2 + n // 4)
    test = slice(n // 2 + n // 4, None)

    pred = fit_avm(sqft, age, sale_price, train)

    benchmarks = {
        "sale price as truth": pred / sale_price - 1,
        "assessed value as truth": pred / assessed - 1,
        "own model as truth": sale_price / pred - 1,
        "log-space vs sale price": np.log(pred) - np.log(sale_price),
    }

    report = sensitivity_report(benchmarks, group, focal=1, reference=0)

    # Coverage audit
    audit = coverage_audit(
        np.log(sale_price[cal]), np.log(pred[cal]),
        np.log(sale_price[test]), np.log(pred[test]),
        group[test], alpha=0.10,
    )

    # Benchmark-independence diagnostics
    ests = report.estimates
    sp = ests["sale price as truth"]
    om = ests["own model as truth"]
    reciprocal_ratio = om / sp if abs(sp) > 1e-12 else float("nan")

    # Correlation between log-space and sale-price benchmarks (per-observation)
    log_meas = benchmarks["log-space vs sale price"]
    sp_meas = benchmarks["sale price as truth"]
    if np.std(log_meas) > 0 and np.std(sp_meas) > 0:
        r = float(np.corrcoef(log_meas, sp_meas)[0, 1])
    else:
        r = float("nan")

    # Mean absolute difference between the two per-seed disparity estimates
    # (group-level means), not the per-observation measures.
    est_mad = float(abs(ests["log-space vs sale price"] - ests["sale price as truth"]))

    # Which benchmark is max / min (by absolute value)
    abs_ests = {k: abs(v) for k, v in ests.items()}
    argmax = max(abs_ests, key=abs_ests.get)
    argmin = min(abs_ests, key=abs_ests.get)

    # Recomputed BSR under alternative benchmark sets
    all_four = [abs(v) for v in ests.values()]
    bsr_all = max(all_four) / min(all_four) if min(all_four) > 1e-12 else float("nan")

    excl_own = [abs(v) for k, v in ests.items() if k != "own model as truth"]
    bsr_excl_own = max(excl_own) / min(excl_own) if min(excl_own) > 1e-12 else float("nan")

    two_only = [abs(ests["sale price as truth"]), abs(ests["assessed value as truth"])]
    bsr_two = max(two_only) / min(two_only) if min(two_only) > 1e-12 else float("nan")

    # Sign flips under alternative sets
    vals_all = list(ests.values())
    sign_flip_all = bool(min(vals_all) < 0 < max(vals_all))

    vals_excl_own = [v for k, v in ests.items() if k != "own model as truth"]
    sign_flip_excl_own = bool(min(vals_excl_own) < 0 < max(vals_excl_own))

    vals_two = [ests["sale price as truth"], ests["assessed value as truth"]]
    sign_flip_two = bool(min(vals_two) < 0 < max(vals_two))

    return {
        "seed": seed,
        # BSR (all four)
        "bsr": report.bsr,
        "sign_flip": report.sign_flip,
        # Disparity estimates
        "est_sale_price": sp,
        "est_assessed": ests["assessed value as truth"],
        "est_own_model": om,
        "est_log_space": ests["log-space vs sale price"],
        "bsr_denominator": min(all_four),
        # Benchmark independence
        "reciprocal_ratio": reciprocal_ratio,
        "log_sp_corr": r,
        "log_sp_est_mad": est_mad,
        "argmax": argmax,
        "argmin": argmin,
        # Alternative benchmark sets
        "bsr_all_four": bsr_all,
        "bsr_excl_own": bsr_excl_own,
        "bsr_two_only": bsr_two,
        "sign_flip_all": sign_flip_all,
        "sign_flip_excl_own": sign_flip_excl_own,
        "sign_flip_two": sign_flip_two,
        # Coverage
        "cov_marginal": audit.coverage.get("marginal", float("nan")),
        "cov_group0": audit.coverage.get(0, float("nan")),
        "cov_group1": audit.coverage.get(1, float("nan")),
        "cov_spread": audit.spread,
        "cov_worst_gap": audit.worst_gap,
    }


# ---------------------------------------------------------------------------
# Aggregation and reporting
# ---------------------------------------------------------------------------

def summarize(values):
    """Return median, IQR, and range as a dict."""
    arr = np.asarray(values, dtype=float)
    return {
        "median": float(np.median(arr)),
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def fmt_pct(x):
    return f"{x:.1%}"


def main():
    parser = argparse.ArgumentParser(description="Multi-seed robustness for BSR + coverage")
    parser.add_argument("--n-seeds", type=int, default=50, help="number of seeds to run")
    parser.add_argument("--output-csv", type=str, default=None, help="write per-seed results to CSV")
    args = parser.parse_args()

    seeds = range(20260905, 20260905 + args.n_seeds)
    results = []
    for i, s in enumerate(seeds):
        results.append(run_one(s))
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  seed {s} ... done ({i + 1}/{args.n_seeds})", file=sys.stderr)

    # --- CSV export --------------------------------------------------------
    if args.output_csv:
        path = Path(args.output_csv)
        fieldnames = list(results[0].keys())
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Per-seed results written to {path}", file=sys.stderr)

    # --- Aggregate ---------------------------------------------------------
    bsr_vals = [r["bsr"] for r in results]
    sign_flips = sum(1 for r in results if r["sign_flip"])
    denom_vals = [r["bsr_denominator"] for r in results]
    near_zero = sum(1 for r in results if r["bsr_denominator"] <= 1e-12)

    bsr_all_vals = [r["bsr_all_four"] for r in results]
    bsr_excl_vals = [r["bsr_excl_own"] for r in results]
    bsr_two_vals = [r["bsr_two_only"] for r in results]

    rec_ratio_vals = [r["reciprocal_ratio"] for r in results]
    rec_ratio_neg = sum(1 for r in results if r["reciprocal_ratio"] < 0)

    corr_vals = [r["log_sp_corr"] for r in results]
    mad_vals = [r["log_sp_est_mad"] for r in results]

    argmax_consistent = len(set(r["argmax"] for r in results)) == 1
    argmin_consistent = len(set(r["argmin"] for r in results)) == 1

    cov_marginal = [r["cov_marginal"] for r in results]
    cov_g0 = [r["cov_group0"] for r in results]
    cov_g1 = [r["cov_group1"] for r in results]
    cov_spread = [r["cov_spread"] for r in results]
    g1_below_88 = sum(1 for r in results if r["cov_group1"] < 0.88)

    bsr_s = summarize(bsr_vals)
    denom_s = summarize(denom_vals)
    bsr_all_s = summarize(bsr_all_vals)
    bsr_excl_s = summarize(bsr_excl_vals)
    bsr_two_s = summarize(bsr_two_vals)
    rec_s = summarize(rec_ratio_vals)
    cov_g0_s = summarize(cov_g0)
    cov_g1_s = summarize(cov_g1)
    spread_s = summarize(cov_spread)

    # --- Print -------------------------------------------------------------
    print("=" * 70)
    print(f"MULTI-SEED RESULTS  ({args.n_seeds} seeds)")
    print("=" * 70)

    print()
    print("BSR (all four benchmarks)")
    print(f"  median:   {bsr_s['median']:.2f}")
    print(f"  IQR:      [{bsr_s['p25']:.2f}, {bsr_s['p75']:.2f}]")
    print(f"  range:    [{bsr_s['min']:.2f}, {bsr_s['max']:.2f}]")
    print(f"  sign flips: {sign_flips} / {args.n_seeds} seeds")
    print(f"  median min |estimate| (denominator): {denom_s['median']:.4f}")
    print(f"  benchmarks within 1e-12 of zero: {near_zero}")

    print()
    print("Benchmark-independence diagnostics")
    print(f"  reciprocal ratio (own/sale) median: {rec_s['median']:.3f}")
    print(f"    negative in {rec_ratio_neg} / {args.n_seeds} seeds")
    print(f"  log-space vs sale-price correlation: r = {np.median(corr_vals):.3f} (median)")
    print(f"    mean abs difference (estimates): {np.median(mad_vals):.4f} (median)")
    print(f"  argmax consistent across seeds: {argmax_consistent}"
          + (f"  (always '{results[0]['argmax']}')" if argmax_consistent else ""))
    print(f"  argmin consistent across seeds: {argmin_consistent}"
          + (f"  (always '{results[0]['argmin']}')" if argmin_consistent else ""))

    print()
    print("Recomputed BSR under alternative benchmark sets")
    print(f"  {'Benchmark set':<40} {'BSR median':>12} {'Range':>22} {'Sign flip':>12}")
    print(f"  {'-'*40} {'-'*12} {'-'*22} {'-'*12}")
    sf_all = sum(r["sign_flip_all"] for r in results)
    sf_excl = sum(r["sign_flip_excl_own"] for r in results)
    sf_two = sum(r["sign_flip_two"] for r in results)

    row_all = f"  {'All four (as originally reported)':<40} {bsr_all_s['median']:>12.2f} {bsr_all_s['min']:.2f} – {bsr_all_s['max']:.2f}{'':>5} {sf_all}/{args.n_seeds}"
    row_excl = f"  {'Excluding own model as truth':<40} {bsr_excl_s['median']:>12.2f} {bsr_excl_s['min']:.2f} – {bsr_excl_s['max']:.2f}{'':>5} {sf_excl}/{args.n_seeds}"
    row_two = f"  {'Sale price vs assessed value only':<40} {bsr_two_s['median']:>12.2f} {bsr_two_s['min']:.2f} – {bsr_two_s['max']:.2f}{'':>5} {sf_two}/{args.n_seeds}"
    print(row_all)
    print(row_excl)
    print(row_two)

    print()
    print("Conformal coverage (target 90%)")
    print(f"  marginal coverage median:  {np.median(cov_marginal):.1%}")
    print(f"  Group 0 coverage median:   {cov_g0_s['median']:.1%}")
    print(f"  Group 1 coverage median:   {cov_g1_s['median']:.1%}")
    print(f"  Group 1 below 88%:          {g1_below_88} / {args.n_seeds} seeds")
    print(f"  subgroup spread min:       {spread_s['min']:.1%}")
    print(f"  subgroup spread median:    {spread_s['median']:.1%}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
