# Housing Measurement Research

Methods and code for an ongoing research program on **how measurement choices manufacture findings** in housing policy and valuation.

The through-line across the work: an administratively neutral rule indexed to a number that has drifted from what it claims to measure will reproduce the drift as a finding, with no biased intent anywhere in the process.

---

## Contents

### [`benchmark-sensitivity/`](benchmark-sensitivity/)

Two diagnostics for disparity estimates that depend on a benchmark nobody can observe.

**Benchmark Sensitivity Ratio (BSR):** reports how much a measured disparity depends on which benchmark the analyst chose. On synthetic data where the true disparity is *exactly zero by construction*, two independently defensible reference standards, recorded sale price and county assessed value, produce disparity estimates that differ by a factor of 3.05 to 4.95 across 50 simulated draws. For seed `20260905` the estimates are +2.9% and +13.6%, a factor of about 4.7.

An earlier version of this demonstration reported a sign flip across four benchmarks (BSR 7.97). Two of those four were not independent of the others, so that figure is not used as the headline. [`FINDINGS.md`](FINDINGS.md) has the analysis.

**Conformal coverage auditing:** locates model failure without asserting any ground truth, by checking whether calibrated prediction intervals actually contain the prices at which homes *did* sell, subgroup by subgroup. On the same data (seed `20260905`), marginal coverage of 87.5% conceals 93.2% versus 81.7% across groups. Across 50 draws, median coverage is 94.5% for one group and 85.7% for the other, and the spread never falls below 4.8 percentage points.

See the [module README](benchmark-sensitivity/README.md) for the full argument, usage, and background.

```bash
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py
pytest
```

### Down-payment scenario analysis (repository root)

A separate affordability analysis for Compton, CA: a scenario workbook (`.xlsx`) and the data extract it uses, `compton_sales_2025_2026.csv`.

- The extract has 760 rows and five columns: `assessed_total`, `sqft_main`, `bedrooms`, `year_built`, `base_year`. Per the workbook's Assumptions sheet, it comes from the LA County Assessor roll, pulled 2026-09-18.
- **It contains Assessor base-year assessed values for 2025-26 transfers, not recorded sale prices**, despite the filename. The workbook uses them as a proxy for sale price after dropping 14 transfers under $200,000.
- This is scenario modeling. It is not a disparity estimate and makes no claim about algorithmic bias.

### Project notes
- [`STATUS.md`](STATUS.md): current state, limitations, next steps, and data sources.
- [`FINDINGS.md`](FINDINGS.md): dated log of results and corrections.
- [`sources/`](sources/): HUD income limit methodology (FY23, FY25, FY26) and the CFPB AVM quality control guide, converted to markdown.
---
## Status and scope

Early-stage and exploratory. The `benchmark-sensitivity` module's synthetic demonstration is verified and reproducible under seed `20260905`, and the module has not yet been run on real parcel data. The scenario analysis above uses real Assessor values for one city and is not an input to the module.

No empirical claim about algorithmic bias in any real housing market is made or implied by this repository.

Affiliation with Neighborhood Housing of LA County. 
## License

MIT. See [LICENSE](LICENSE). Code is free to use; please cite if it informs published work.
## Contact
Please reach out if you're interested on collaborating! We're expecting to open this to official collaboration on OpenLabs next semester, in hopes of publication.
