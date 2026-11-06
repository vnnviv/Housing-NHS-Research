# Status: 2026-11-05

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

Since 2026-10-28, work on real public data:

- **HMDA cross-check (`HMDA-VALIDATION.md`).** The Assessor price proxy ran below HMDA property values for Compton. Most of that gap was non-market rows (partial-interest or blended reassessments). A round-value filter now drops them in every script. After filtering, the proxy is about 2% to 4% low. The 25th-percentile Compton home is $580,700 (was $559,482), and at a 43% ratio it needs 1.06x the income cap (was 1.02x). See `FINDINGS.md` (2026-11-05).
- **Q5, roll versus market by tract (`Q5-PROP13-GAP.md`).** 221,709 single-family parcels on the 2026 roll, 93 San Gabriel Valley and 222 South LA tracts. South LA's roll sits further below market on every measure: 0.05 lower per sqft against same-tract resets, 0.13 lower against HMDA values. The gap holds inside every base-year cohort except 2020-23, so it is mainly faster appreciation since purchase, not tenure. An assessed-value benchmark would show a 5 to 13 point "undervaluation" of South LA with no valuation content.

## Questions resolved (2026-11-05)

| Question | Answer |
|---|---|
| Does public HMDA include credit scores? | No. CFPB's public data excludes credit score, AUS result, denial reasons and property address. DTI and CLTV are public, in ranges. Credit enters any affordability figure only as an assumption. |
| Which LA County CalHFA income limit applied in 2022-25? | First mortgage and MyHome: $180,000 (June 2022), $194,000 (July 2023 and June 2024), $211,000 (June 2025, from a search snippet). Dream For All is separate and lower: $155,000 (June 2024), about $168,000 (2025, snippet). Limits apply by reservation date. |
| Why did Assessor values sit about 5% below HMDA? | About half came from non-market rows, now filtered. The remaining 2% to 4% cannot be separated with public data. Candidates are appraisal-based HMDA values and different buyer mixes; timing points the other way. |
| Does the roll-to-market gap differ between the two study regions? | Yes (Q5). The difference comes mostly from appreciation paths, not tenure. |

## Limitations

- The BSR and coverage modules have never been run on real parcel records or recorded sales.
- Q5 shows assessed value is not usable as a benchmark, feature or target for the study regions, even with tenure matched. Any benchmark class built from Assessor data needs an explicit model of the price path.
- On county data the benchmark class may hold fewer than two independent standards. Recent assessed values sit close to sale prices, and appraisals are reported to anchor to contract price. If so, the BSR is undefined there and coverage carries the analysis.
- Two of the four original benchmarks weren't independent, so the headline uses two. See `FINDINGS.md` (2026-09-08).
- The scenario analysis uses placeholder savings and closing costs, dated program amounts, and filtered Assessor values as a price proxy. The round-value filter is a heuristic and should be reported with and without.
- Q5's study regions are ZIP lists plus a 50% tract rule, set before outcomes but not preregistered. The county ACS layer used for tract demographics does not state its survey year.
- The API is not stable.

## Next steps

In order. Items 1 to 3 are short and unblock the rest.

1. **Confirm the 2026 limit.** Which CalHFA program the $214,000 figure (effective 2026-06-30) belongs to, first mortgage or Dream For All. Every share-of-buyers number depends on it.
2. **Verify the ACS layer's survey year** before citing any Q5 demographics.
3. **Test the renovation explanation for Q5.** Use the roll's `EffectiveYearBuilt` to flag renovated resales. If South LA's reset reference drops once they're excluded, part of the gap is quality, not appreciation.
4. **Q3: buyer income versus resident income by tract** (HMDA buyer income over ACS owner-household income). State in the first line that HMDA excludes cash and investor buyers.
5. **Q1, one reading:** is there any public CalHFA report on when funds ran out or reservations by income band? If not, it becomes one question for practitioner review and ends.
6. **Only if time remains, Q2:** do buyer incomes bunch just under the limit? Test both cutoffs (first mortgage and Dream For All). Cut this first.
7. Benchmark design, carried over: decide in writing which real-data benchmarks are independent enough to share a class; define the BSR over distinct reference standards only; add a repeat-sales standard; report interval width beside coverage; document the near-zero denominator rule.
8. Commit the identification strategy and disaggregation plan before modeling outcomes on recorded sales.

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
| HMDA 2024-25 loan-level data, LA County | In use (`HMDA-VALIDATION.md`, Q5). Downloaded by the scripts, not stored |
| 2026 Assessor roll, single-family parcels in the study ZIPs | In use for Q5. Pulled from LA County's ArcGIS Online layer by `analysis/prop13_gap.py`; tract results in `analysis/data/q5_tracts.csv` |
| ACS B03002 tract race and ethnicity | In use for Q5, from LA County's ACS layer (survey year not stated; verify) |
| Recorded sale prices for the study regions | Not yet obtained |

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

Q5, from the repo root: `python analysis/prop13_gap.py` (pulls about 222,000 parcels; caches to `q5_cache/`, which is git-ignored).
