"""Demonstration on synthetic data where the true disparity is exactly zero.

Two tract groups are generated from an IDENTICAL valuation process. Group B
differs only in observable characteristics and in transaction noise -- thinner
markets produce noisier sales -- and in how far assessed values lag. Nothing in
the data-generating process mispricing anything by group.

A deliberately misspecified AVM (it cannot see property quality, as no real AVM
can) is then evaluated under four benchmarks, each of which has appeared in
published work. The disparity estimates disagree in magnitude and in sign.

Run: python examples/synthetic_demo.py
"""

import numpy as np

from bsr import coverage_audit, sensitivity_report

SEED = 20260905


def simulate(n=4000, seed=SEED):
    """Synthetic county with zero true disparity by construction."""
    rng = np.random.default_rng(seed)

    group = rng.integers(0, 2, n)
    sqft = rng.normal(1650 - 180 * group, 320, n).clip(600)
    age = rng.normal(48 + 14 * group, 18, n).clip(1)
    quality = rng.normal(-0.35 * group, 1.0, n)  # unobserved by the modeler

    # Same valuation function for both groups. No discrimination in the DGP.
    true_value = np.exp(4.9 + 0.62 * np.log(sqft) - 0.004 * age + 0.11 * quality) * 1000

    # Sales are unbiased but noisier in the thinner group-B market.
    sale_price = true_value * np.exp(rng.normal(0, 0.07 + 0.06 * group, n))

    # Assessed values lag the market, and lag further in group B. An
    # administrative fact, not valuation discrimination.
    assessed = true_value * np.exp(-0.11 - 0.09 * group + rng.normal(0, 0.05, n))

    return group, sqft, age, sale_price, assessed


def fit_avm(sqft, age, sale_price, train):
    """OLS on log price. Sees size and age; cannot see quality."""
    X = np.column_stack([np.ones(sqft.size), np.log(sqft), age])
    beta, *_ = np.linalg.lstsq(X[train], np.log(sale_price[train]), rcond=None)
    return np.exp(X @ beta)


def main():
    group, sqft, age, sale_price, assessed = simulate()
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

    print("=" * 70)
    print("TRUE disparity in the data-generating process: 0.0000 (by construction)")
    print("=" * 70)
    report = sensitivity_report(benchmarks, group, focal=1, reference=0)
    print(report)
    print()
    print("  BSR near 1        -> the finding is about the world.")
    print("  BSR large or flip -> the finding is about the benchmark.")
    print(f"  robust by the built-in heuristic: {report.robust}")
    print()

    print("=" * 70)
    print("CONFORMAL COVERAGE AUDIT (no benchmark required)")
    print("=" * 70)
    audit = coverage_audit(
        np.log(sale_price[cal]), np.log(pred[cal]),
        np.log(sale_price[test]), np.log(pred[test]),
        group[test], alpha=0.10,
    )
    print(audit)
    print()
    print("  The marginal guarantee holds roughly, and hides the subgroup gap.")
    print("  Undercoverage is verifiable misspecification -- checked against")
    print("  sales that actually happened, so no 'true value' is assumed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
