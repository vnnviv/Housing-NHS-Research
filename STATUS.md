# Status — 2026-09-08

A snapshot of where this work currently stands. Overwritten as things change;
`FINDINGS.md` is the dated log of how it got here.

## Research question

Estimates of disparity in automated property valuation are measured against a
reference standard that cannot be observed. There is no true value of a home.
Every candidate reference — recorded sale price, county assessed value, a
model's own residuals — is individually defensible and separately contestable,
and published work uses all of them.

The question is not whether valuation models produce disparities. That is
established. It is **how much of a reported disparity is a property of the
reference standard the analyst selected**, and whether that dependence can be
measured and reported as a matter of routine.

## Where things stand

Two diagnostics are implemented, tested, and reproducible:

**Benchmark Sensitivity Ratio (BSR)** — the ratio of the largest to the
smallest absolute disparity estimate across a class of defensible reference
standards, reported alongside whether the sign changes across that class.

**Conformal coverage auditing** — a benchmark-free check on where a model
fails, asking whether calibrated prediction intervals contain realized sale
prices at the advertised rate within each subgroup. Answerable from completed
transactions alone, without asserting any home's value.

Both are demonstrated on a **negative control**: a synthetic data-generating
process in which the true disparity is zero by construction, evaluated with a
deliberately misspecified valuation model that cannot observe property quality,
as no real model can.

### Current claim

> Across 50 negative-control draws, two independently defensible reference
> standards produced disparity estimates differing by a factor of 3.05 to 4.95
> on data containing no disparity by construction.

Coverage results on the same draws are stable: one group over-covered (median
94.5%), the other under-covered (median 85.7%), with a subgroup spread never
below 4.8 percentage points. Both directions are treated as calibration
failures — under-coverage exposes a group to unflagged model error,
over-coverage makes estimates for that group less precise.

### Known limitations

- **Nothing here has been run against real parcel records or recorded sales.**
  All results are from the synthetic negative control.
- Two of the four measurement choices in the current demonstration are not
  independent: one is the reciprocal of another, and a third is the same
  comparison in log form. The headline claim above is restricted to the two
  genuinely distinct reference standards. See `FINDINGS.md` for the analysis
  and the recomputed values.
- The API is not stable.

## Next steps

1. **Separate the collapsed axes.** Define the BSR over a benchmark axis
   (distinct reference standards) only, and report functional form and
   direction of comparison as their own sensitivities.
2. **Add a third independent reference standard.** A repeat-sales estimate on
   the same parcel differences out fixed unobserved quality and is not
   derivable from either current benchmark.
3. **Report mean interval width by group** alongside coverage. Coverage alone
   can be satisfied by widening intervals; width is what makes the rate
   interpretable.
4. **Document the denominator rule** for the BSR when an estimate approaches
   zero, and report the raw spread as a companion statistic, since the ratio
   discards both sign and magnitude.
5. **Move from the synthetic generator to public records** — county Assessor
   parcel data, recorded sales, and ACS tract demographics — with the
   identification strategy and disaggregation plan committed before outcomes
   are examined.

## Open questions

Questions where outside expertise would genuinely change the work:

- Under what assumptions is a disparity identifiable given several imperfect
  measures of a *continuous* latent value? The relevant literature appears to
  be measurement-error and errors-in-variables econometrics rather than the
  latent class models used for binary diagnostic tests, but the identification
  conditions have not been worked through here.
- What makes two reference standards independent enough to belong in the same
  benchmark class? The reciprocal pair found in the current demonstration shows
  the question is not trivial, and the answer determines what the BSR measures.
- Does unequal subgroup coverage constitute harm on its own, or only in
  combination with how the estimate is used? The synthetic design attributes
  the gap to the model rather than to group heterogeneity, but the normative
  step is not argued here.

## Data

**Public sources only.** No confidential or client-level data is used, and none
belongs in this repository.

| Source | State |
| --- | --- |
| Synthetic generator (`examples/synthetic_demo.py`) | In use; all current results |
| HUD Section 8 income limit methodology, FY23 / FY25 / FY26 | Converted to markdown in `sources/` |
| CFPB AVM quality control small entity compliance guide | Converted to markdown in `sources/` |
| County Assessor parcel records and recorded sales | Not yet obtained |
| ACS 5-year tract demographics | Not yet obtained |

Conversion from source PDFs is reproducible via `convert.py`.

## Reproducing

```bash
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py                       # single seed
python examples/multi_seed.py --n-seeds 50              # distribution
pytest
```
