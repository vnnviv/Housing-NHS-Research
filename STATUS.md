# Status: 2026-10-15

Where the work stands now. `FINDINGS.md` is the dated log.

## Research question

Disparity estimates for automated valuation models are measured against a reference standard nobody can observe. Every candidate (recorded sale price, assessed value, a model's own residuals) is defensible and contestable, and published work uses all of them.

The question is how much of a reported disparity comes from the benchmark the analyst picked, and whether that dependence can be measured and reported routinely.

## Where things stand

Two diagnostics are implemented, tested and reproducible:

- **Benchmark Sensitivity Ratio (BSR):** the largest over the smallest absolute disparity estimate across a class of defensible benchmarks, plus whether the sign changes.
- **Conformal coverage auditing:** a benchmark-free check of whether calibrated prediction intervals contain realized sale prices at the advertised rate within each subgroup.

Both are demonstrated on a synthetic negative control: true disparity is zero by construction and the valuation model is deliberately misspecified.

> Across 50 negative-control draws, two independently defensible reference standards produced disparity estimates differing by a factor of 3.05 to 4.95 on data containing no disparity by construction.

On the same draws, one group is over-covered (median 94.5%) and the other under-covered (median 85.7%), and the gap never falls below 4.8 points.

Separately, a Compton scenario analysis (real Assessor values, placeholder inputs) finds that at the median price 91% to 94% of the assistance a household needs is an income gap, not a cash gap. See `FINDINGS.md` (2026-10-14). It does not feed the BSR or coverage modules.

## Limitations

- The BSR and coverage modules have never been run on real parcel records or recorded sales.
- On county data the benchmark class may hold fewer than two independent standards. Recent assessed values sit close to sale prices, and appraisals are reported to anchor to contract price. If so, the BSR is undefined there and coverage carries the analysis.
- Two of the four original benchmarks weren't independent, so the headline uses two. See `FINDINGS.md` (2026-09-08).
- The scenario analysis uses placeholder savings and closing costs, dated program amounts, and Assessor values as a price proxy.
- The API is not stable.

## Next steps

1. Decide, in writing and before any run, which real-data benchmarks are independent enough to share a class (candidates are in `FINDINGS.md`, 2026-10-05).
2. Separate the collapsed axes: define the BSR over distinct reference standards only, and report functional form and direction as their own sensitivities.
3. Add a third independent standard, such as a repeat-sales estimate.
4. Report mean interval width by group next to coverage. Coverage alone can be met by widening intervals.
5. Document the denominator rule for estimates near zero, and report the raw spread beside the ratio.
6. Move to public records (Assessor parcels, recorded sales, ACS tract demographics), with the identification strategy and disaggregation plan committed before outcomes are examined.

## Open questions

- When is a disparity identifiable from several imperfect measures of a continuous latent value? This looks like errors-in-variables econometrics, not binary latent-class models, but the conditions haven't been worked out.
- What makes two reference standards independent enough to share a class?
- Is unequal subgroup coverage harmful on its own, or only through how the estimate is used?

## Data

Public sources only. No confidential or client-level data belongs in this repository.

| Source | State |
| --- | --- |
| Synthetic generator (`examples/synthetic_demo.py`) | In use; all BSR and coverage results |
| HUD income limit methodology (FY23, FY25, FY26) and CFPB AVM guide | Converted to markdown in `sources/` |
| Compton assessed values, 2025-26 transfers (`analysis/data/compton_sales_2025_2026.csv`) | Pulled 2026-09-18 from the LA County Assessor roll. Base-year assessed values, not sale prices. Scenario analysis only |
| Scenario workbook and assistance-sizing model | Built on the Compton data, HUD/HCD income limits, a Freddie Mac PMMS rate (7.40%, 2026-10-08) and mortgage insurance rate cards |
| Assessor parcels and recorded sales for the study regions | Not yet obtained |
| ACS 5-year tract demographics | Not yet obtained |

To convert source PDFs, run `python convert.py <pdf paths>` (needs `pip install pymupdf`). The PDFs themselves aren't stored here.

## Reproducing

```bash
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py                       # single seed
python examples/multi_seed.py --n-seeds 50              # distribution
pytest
```

Scenario analysis, from the repo root: `python analysis/assistance_sizing.py` and `python -m pytest tests`.
