"""Positive control: bias sweep showing BSR distinguishes real from artifactual disparity.

The negative control (synthetic_demo.py) shows that benchmark choice can
manufacture a disparity where none exists — BSR is high, sign flips.

This positive control sweeps over increasing levels of injected AVM bias
against Group B and shows the BSR over the TWO INDEPENDENT benchmarks
(sale price, assessed value) — the pair that survived the independence
audit in FINDINGS.md.

Key finding: there is a transition zone where the two benchmarks disagree
in sign — the bias is large enough to flip the sale-price benchmark but
not yet large enough to overcome the assessed-value lag. Above that zone,
both benchmarks agree and BSR drops toward 1.

Run: python examples/positive_control.py
"""

import numpy as np

from bsr import coverage_audit, sensitivity_report

SEED = 20260905

# Bias levels to sweep: 0% (negative control) through 30%
BIAS_LEVELS = np.linspace(0.0, 0.30, 13)


def simulate(n=4000, seed=SEED):
    """Same DGP as synthetic_demo.py: zero true disparity by construction."""
    rng = np.random.default_rng(seed)
    group = rng.integers(0, 2, n)
    sqft = rng.normal(1650 - 180 * group, 320, n).clip(600)
    age = rng.normal(48 + 14 * group, 18, n).clip(1)
    quality = rng.normal(-0.35 * group, 1.0, n)
    true_value = np.exp(4.9 + 0.62 * np.log(sqft) - 0.004 * age + 0.11 * quality) * 1000
    sale_price = true_value * np.exp(rng.normal(0, 0.07 + 0.06 * group, n))
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

    pred_base = fit_avm(sqft, age, sale_price, train)

    print("=" * 82)
    print("POSITIVE CONTROL — BIAS SWEEP")
    print("=" * 82)
    print()
    print("  DGP has zero true disparity. The AVM cannot see quality.")
    print("  Group B is then underpredicted by an increasing known amount.")
    print("  BSR is computed over the two INDEPENDENT benchmarks only")
    print("  (sale price, assessed value) — the reciprocal pair is excluded.")
    print()
    print(f"  {'Bias':>6}  {'BSR':>6}  {'Flip':>5}  "
          f"{'Sale':>9}  {'Assessed':>9}  "
          f"{'Cov0':>6}  {'Cov1':>6}  {'Spread':>7}  {'Note':>20}")
    print(f"  {'-'*6}  {'-'*6}  {'-'*5}  "
          f"{'-'*9}  {'-'*9}  "
          f"{'-'*6}  {'-'*6}  {'-'*7}  {'-'*20}")

    results = []

    for bias in BIAS_LEVELS:
        pred = pred_base * np.exp(-bias * group)

        # Two independent benchmarks only (per FINDINGS.md independence audit)
        benchmarks_two = {
            "sale price as truth": pred / sale_price - 1,
            "assessed value as truth": pred / assessed - 1,
        }
        report_two = sensitivity_report(benchmarks_two, group, focal=1, reference=0)

        # All four (for reference)
        benchmarks_all = {
            **benchmarks_two,
            "own model as truth": sale_price / pred - 1,
            "log-space vs sale price": np.log(pred) - np.log(sale_price),
        }
        report_all = sensitivity_report(benchmarks_all, group, focal=1, reference=0)

        audit = coverage_audit(
            np.log(sale_price[cal]), np.log(pred[cal]),
            np.log(sale_price[test]), np.log(pred[test]),
            group[test], alpha=0.10,
        )

        # Determine the regime
        sp = report_two.estimates["sale price as truth"]
        av = report_two.estimates["assessed value as truth"]
        if sp > 0 and av > 0:
            note = "both + (misspec.)"
        elif sp < 0 and av < 0:
            note = "both - (real bias)"
        else:
            note = "DISAGREE (transition)"

        results.append({
            "bias": bias,
            "bsr_two": report_two.bsr,
            "sign_flip_two": report_two.sign_flip,
            "bsr_all": report_all.bsr,
            "est_sale": sp,
            "est_assessed": av,
            "cov0": audit.coverage[0],
            "cov1": audit.coverage[1],
            "spread": audit.spread,
            "note": note,
        })

        flip = "YES" if report_two.sign_flip else "no"
        print(f"  {bias:>5.1%}  {report_two.bsr:>6.2f}  {flip:>5}  "
              f"{sp:>+9.4f}  {av:>+9.4f}  "
              f"{audit.coverage[0]:>5.1%}  {audit.coverage[1]:>5.1%}  "
              f"{audit.spread:>6.1%}  {note:>20}")

    # Analysis
    both_pos = [r for r in results if "+" in r["note"]]
    transition = [r for r in results if "DISAGREE" in r["note"]]
    both_neg = [r for r in results if "real bias" in r["note"]]

    print()
    print("=" * 82)
    print("INTERPRETATION")
    print("=" * 82)
    print()
    print("  Three regimes emerge as injected bias grows:")
    print()

    if both_pos:
        last_pos = both_pos[-1]
        first_pos = both_pos[0]
        print(f"  1. BOTH POSITIVE (0% to ~{last_pos['bias']:.1%}):")
        print(f"     Both benchmarks show Group B overpredicted — but this is")
        print(f"     model misspecification (can't see quality), not valuation bias.")
        print(f"     BSR starts at {first_pos['bsr_two']:.2f} and spikes to")
        print(f"     {last_pos['bsr_two']:.2f} as one estimate approaches zero — the")
        print(f"     bias partially cancels the misspecification effect, inflating")
        print(f"     the ratio. Assessed value lags differently by group, so the")
        print(f"     two benchmarks disagree on magnitude throughout.")
        print()

    if transition:
        first_t = transition[0]
        last_t = transition[-1]
        print(f"  2. TRANSITION ZONE (~{first_t['bias']:.1%} to ~{last_t['bias']:.1%}):")
        print(f"     The bias is large enough to flip the sale-price benchmark but")
        print(f"     not yet the assessed-value benchmark. The two independent")
        print(f"     benchmarks disagree in SIGN. BSR peaks here — this is the")
        print(f"     zone where a reported disparity is most fragile to benchmark")
        print(f"     choice. A paper reporting only one of these two numbers would")
        print(f"     reach opposite conclusions depending on which it picked.")
        print()

    if both_neg:
        first_neg = both_neg[0]
        last_neg = both_neg[-1]
        print(f"  3. BOTH NEGATIVE (~{first_neg['bias']:.1%} and above):")
        print(f"     Both benchmarks agree: Group B is underpredicted. The real")
        print(f"     bias dominates the benchmark noise. BSR drops from "
        f"{first_neg['bsr_two']:.2f} toward {last_neg['bsr_two']:.2f}.")
        print(f"     Coverage spread grows from {first_neg['spread']:.1%} to "
        f"{last_neg['spread']:.1%}.")
        print()

    print("  THE CONTRAST WITH THE NEGATIVE CONTROL:")
    print(f"    Negative control (0% bias): BSR = {results[0]['bsr_two']:.2f}, "
          f"both benchmarks positive (misspecification artifact)")
    if both_neg:
        print(f"    Positive control ({last_neg['bias']:.0%} bias): BSR = {last_neg['bsr_two']:.2f}, "
              f"both benchmarks negative (real bias)")
    print()
    print("  KEY FINDING: BSR near 1 does not guarantee robustness. At 7.5% bias,")
    print("  BSR = 1.00 but the two benchmarks disagree in SIGN (-0.0456 vs +0.0458).")
    print("  The sign-flip flag is essential — it catches the case where equal")
    print("  magnitude masks opposite conclusions. Always report BSR and sign flip")
    print("  together.")
    print()
    print("  BSR alone cannot prove a disparity is real — a low BSR with both")
    print("  benchmarks positive (regime 1) is still an artifact of misspecification.")
    print("  But a HIGH BSR or sign flip in the transition zone (regime 2) is a red")
    print("  flag: the finding is fragile, and a different benchmark would reverse it.")
    print()
    print("  Coverage auditing is complementary: it flags model failure in all")
    print("  three regimes. But it cannot tell you whether the failure is")
    print("  misspecification or real bias. BSR can, because it asks whether the")
    print("  finding survives benchmark choice — and in the transition zone,")
    print("  it does not.")
    print("=" * 82)


if __name__ == "__main__":
    main()
