# Benchmark Sensitivity Ratio

Diagnostics for disparity estimates that depend on a benchmark nobody can observe.

---

## The problem

There is no observable "true" value of a home. Every candidate benchmark is contested:

- **Sale price as truth** — sale prices themselves embed discrimination, so you measure deviation from an already-biased yardstick.
- **Appraised value as truth** — same problem, and appraisal bias is often the thing under investigation.
- **A model's own residuals** — now you are comparing someone else's model to yours, and any disparity may be your misspecification.

Each of those choices is individually defensible. Papers make all of them. The question this repository asks is what happens when you make all of them **on the same data**.

## The demonstration

`examples/synthetic_demo.py` builds a synthetic county in which two tract groups are drawn from an **identical** valuation process. Group B differs only in observable characteristics, in transaction noise (thinner markets produce noisier sales), and in how far assessed values lag. **The true disparity is exactly zero by construction.**

A deliberately misspecified AVM — it cannot see property quality, as no real AVM can — is then evaluated under four benchmarks:

| Benchmark | Measured disparity |
| --- | --- |
| Sale price as truth | **+0.0286** |
| Assessed value as truth | **+0.1357** |
| Own model as truth | **−0.0170** |
| Log-space vs sale price | **+0.0226** |

One dataset. No real disparity. Estimates spanning −1.7% to +13.6%, **and the sign flips.**

**BSR = 7.97.**

Any one of those four numbers, reported alone, is a publishable-looking finding about nothing.

## The diagnostic

For a disparity estimate `D` measured against benchmark `b` drawn from a class `B` of individually defensible benchmarks:

```
BSR = max_b |D(b)| / min_b |D(b)|
```

Report BSR alongside any disparity estimate, together with whether the **sign flips** across `B`.

- **BSR near 1** — the finding is about the world.
- **BSR large, or sign flips** — the finding is about the benchmark.

BSR does not tell you the disparity is fake. It tells you how much of what you are reporting is a property of your own analytical choice, which is a question every fairness estimate should have to answer before it is believed.

## Coverage auditing: measuring failure without a benchmark

The second module avoids the problem rather than quantifying it.

Instead of asking whether predictions are too low somewhere — which requires knowing what "correct" would have been — split conformal prediction produces calibrated intervals, and the audit asks whether those intervals actually contain the prices at which homes **did** sell, at the advertised rate, within each subgroup.

That question is answerable from realized transactions alone.

On the same synthetic data where every benchmark-based estimate was artifact:

| | Empirical coverage (target 90%) |
| --- | --- |
| Marginal | 87.5% |
| Group A | 93.2% |
| Group B | **81.7%** |

Subgroup spread: **11.5 points.**

The marginal guarantee looks nearly fine and conceals the gap. Split conformal guarantees *marginal* coverage under exchangeability and promises nothing per subgroup — which is precisely what makes the audit informative. Undercoverage in a subgroup is evidence of genuine model failure there, stated **without ever asserting what any house is worth.**

## Usage

```python
import numpy as np
from bsr import sensitivity_report, coverage_audit

# 1. How much does the disparity depend on the benchmark?
benchmarks = {
    "sale price as truth":     pred / sale_price - 1,
    "assessed value as truth": pred / assessed - 1,
    "own model as truth":      sale_price / pred - 1,
}
report = sensitivity_report(benchmarks, group, focal=1, reference=0)
print(report)
print(report.bsr, report.sign_flip, report.robust)

# 2. Where does the model actually fail, benchmark-free?
audit = coverage_audit(
    y_cal, pred_cal,          # calibration split (logs, for prices)
    y_test, pred_test,        # evaluation split
    group_test, alpha=0.10,
)
print(audit)
print(audit.spread, audit.worst_gap)
```

## Install

```bash
git clone https://github.com/<you>/benchmark-sensitivity.git
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py
pytest
```

Requires Python 3.9+ and NumPy. `pytest` for the test suite.

## Applying this to real data

The synthetic generator is a demonstration, not the research. To use this on real parcel data:

1. Replace the synthetic DGP with county Assessor records and recorded sales.
2. Replace the binary `group` with tract demographic shares — prefer a continuous specification over a binary split.
3. Expand the benchmark dictionary into a full **specification curve**: benchmark choice × functional form × sample restriction × winsorization rule. BSR is the headline; the curve is the evidence.
4. Compute coverage per tract and map it. Tracts with persistent undercoverage are where the model genuinely fails.
5. Add a **repeat-sales** restriction — same parcel, two transactions — to difference out fixed unobserved quality.

## Background

The construction follows the **Leakage Inflation Ratio** introduced in *Hybrid Quantitative ML Model for Financial Time Series Forecasting: A Two-Phase Empirical Diagnosis of Data Leakage and Metric Misuse* (Chan, Husain & Si), which applies the same idea to train/test split regimes: compute one metric under two or more regimes, and let the ratio expose that the metric was measuring the regime rather than the thing.

Related methods worth reading before using this seriously:

- Simonsohn, Simmons & Nelson — specification curve analysis, the formal engine under BSR.
- Manski, *Identification for Prediction and Decision*; Molinari, *Econometrics with Partial Identification* — reporting the range of estimates consistent with any benchmark in a class.
- The conformal equalized-coverage literature (2024–), on subgroup coverage guarantees and their cost.

## Status

Early. The API is not stable. The synthetic demonstration is verified and reproducible under seed `20260905`; nothing here has yet been run against real parcel data.

## License

MIT — see [LICENSE](LICENSE).
