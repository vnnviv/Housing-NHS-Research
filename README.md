# Housing Measurement Research

Code and notes on how measurement choices manufacture findings in housing policy and valuation. When a rule is indexed to a number that has drifted from what it claims to measure, the rule reproduces the drift as a finding, with no biased intent anywhere.

The Compton scenario analysis was built working with Neighborhood Housing Services of LA County (NHS). 

---

## benchmark-sensitivity/

Two diagnostics for disparity estimates that depend on a benchmark nobody can observe. Full argument and usage: [module README](benchmark-sensitivity/README.md).

**Benchmark Sensitivity Ratio (BSR)** measures how much a disparity estimate depends on the benchmark chosen. On synthetic data with zero true disparity by construction, recorded sale price and county assessed value give estimates that differ by a factor of 3.05 to 4.95 across 50 draws (seed `20260905`: +2.9% vs +13.6%). An earlier four-benchmark version (BSR 7.97, sign flip) is not the headline, because two of the four benchmarks were not independent. See [`FINDINGS.md`](FINDINGS.md).

**Conformal coverage auditing** checks, without assuming any true value, whether calibrated prediction intervals contain the prices homes actually sold for, by subgroup. Same seed: 87.5% marginal coverage hides 93.2% vs 81.7% by group. Across 50 draws, median coverage is 94.5% and 85.7%, and the gap never falls below 4.8 points.

```bash
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py
pytest
```

## Down-payment scenario analysis (repository root)

A separate affordability analysis for Compton, CA. It is scenario modeling, not a disparity estimate, and makes no claim about algorithmic bias.

- **Data:** `analysis/data/compton_sales_2025_2026.csv`, 760 rows from the LA County Assessor roll, pulled 2026-09-18. These are base-year assessed values for 2025-26 transfers, **not recorded sale prices**. They serve as a price proxy after dropping 14 transfers under $200,000.
- **Code:** `analysis/downpayment_scenarios.py` (scenario model, with `NHS-Downpayment-Scenarios.xlsx`) and `analysis/assistance_sizing.py` (how much assistance a household needs, split into a cash part and an income part). Tests are in `tests/`.
- **Results:** [`NHS-ASSISTANCE-SIZING.md`](NHS-ASSISTANCE-SIZING.md).

## Notes

- [`STATUS.md`](STATUS.md): current state, limitations, next steps, data sources.
- [`FINDINGS.md`](FINDINGS.md): dated log of results and corrections.
- [`sources/`](sources/): HUD income limit methodology (FY23, FY25, FY26) and the CFPB AVM quality control guide, as markdown.

## Status

Early-stage. The synthetic demonstration is reproducible under seed `20260905`. The BSR and coverage modules have not been run on real parcel data, and the scenario analysis does not feed them. No empirical claim about algorithmic bias in any real housing market is made or implied.

## License

MIT. See [LICENSE](LICENSE). Please cite if it informs published work.
