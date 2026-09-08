# Neighborhood Housing Services LA Research

Methods and code for an ongoing research on **how measurement choices manufacture findings** in housing policy and valuation.

The through-line across the work: an administratively neutral rule indexed to a number that has drifted from what it claims to measure will reproduce the drift as a finding, with no biased intent anywhere in the process.

---

## Contents

### [`benchmark-sensitivity/`](benchmark-sensitivity/)

Two diagnostics for disparity estimates that depend on a benchmark nobody can observe.

**Benchmark Sensitivity Ratio (BSR)**  ┈➤ reports how much a measured disparity depends on which benchmark the analyst chose. On synthetic data where the true disparity is *exactly zero by construction*, four benchmarks each used in published work yield estimates from −1.7% to +13.6% that disagree in sign, for a BSR of **7.97**.

**Conformal coverage auditing**  ┈➤ locates model failure without asserting any ground truth, by checking whether calibrated prediction intervals actually contain the prices at which homes *did* sell, subgroup by subgroup. On the same data, marginal coverage of 87.5% conceals 93.2% versus 81.7% across groups.

See the [module README](benchmark-sensitivity/README.md) for the full argument, usage, and background.

```bash
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py
pytest
```

---

## Background

The BSR construction follows the **Leakage Inflation Ratio** introduced in *Hybrid Quantitative ML Model for Financial Time Series Forecasting: A Two-Phase Empirical Diagnosis of Data Leakage and Metric Misuse* (Chan, Husain & Si), which applies the same idea to train/test split regimes: compute one metric under two or more regimes, and let the ratio expose that the metric was measuring the regime rather than the thing.
