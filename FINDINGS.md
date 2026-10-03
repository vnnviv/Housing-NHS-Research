# Findings

A running log of results and limitations for the benchmark-sensitivity work.
Newest entries first.

---

## 2026-10-02 — Housekeeping: public claims aligned with the revised result

No new results. Three corrections to how the repository describes itself.

- **Headline claim.** The root README and the module README previously led with
  the four-benchmark result (BSR 7.97, sign flips). The 2026-09-08 entry below
  shows that two of those four benchmarks are not independent of the others, so
  the sign flip is arithmetic. Both READMEs now lead with the two-benchmark
  result (sale price vs assessed value, factor 3.05 to 4.95 across 50 draws) and
  describe the 7.97 figure as the original four-estimate output.
- **What `compton_sales_2025_2026.csv` is.** Its columns are `assessed_total`,
  `sqft_main`, `bedrooms`, `year_built` and `base_year`. It holds Assessor
  base-year assessed values for 2025-26 transfers, not recorded sale prices, and
  the scenario workbook uses it as a proxy for sale price. It is not used by the
  BSR modules. Because the proxy is an assessed value, the benchmark problem this
  repository studies applies to it directly.
- **Status statements.** "Nothing has been run against real parcel records" now
  applies to the BSR and coverage modules only, since the repository root
  contains a separate scenario analysis built on real Assessor values.

The per-seed CSV mentioned below is not tracked, because `*.csv` is gitignored.
Regenerate it with the `--output-csv` command under "Reproducing these results."

---

## 2026-09-08 — Multi-seed robustness, and a benchmark-independence limitation

### Multi-seed results

The single-seed demonstration (`seed=20260905`) establishes reproducibility but
not stability. A multi-seed harness (`examples/multi_seed.py`) now runs the full
pipeline — simulate, fit the misspecified AVM, compute the four disparity
estimates, run the BSR and the coverage audit — across many draws.

Across 50 seeds:

| Quantity | Value |
| --- | --- |
| BSR median | 5.57 |
| BSR IQR | [5.22, 6.39] |
| BSR range | [4.00, 9.38] |
| Sign flips | 50 / 50 seeds |
| Median min \|estimate\| (BSR denominator) | 0.026 |
| Benchmarks within 1e-12 of zero | 0 across all seeds |

The original seed's BSR of 7.97 sits high in the distribution but inside the
observed range. The denominator stays well away from zero, so the ratio is not
inflated by a near-zero benchmark.

Conformal coverage is equally stable. Group 0 over-covers (median 94.5%) and
Group 1 under-covers (median 85.7%); Group 1 falls below 88% in 48 of 50 seeds,
and the subgroup spread never drops below 4.8 percentage points.

Both directions are calibration failures and are now reported as such. Under-
coverage means the model fails for that group. Over-coverage means intervals
are wider than advertised, so estimates there are less precise — a different
harm, not an absence of one.

Raw per-seed output can be exported to CSV for independent checking (the
file is not tracked in this repository; regenerate it with `--output-csv`).

### Limitation found: two of the four benchmarks are not independent

Re-examining the four measurement choices against the multi-seed output
surfaced a construction problem that materially changes how the headline result
should be stated.

**`own model as truth` is approximately the algebraic negative of
`sale price as truth`.**

```
sale price as truth:   pred / sale - 1
own model as truth:    sale / pred - 1      <- reciprocal transformation
```

These are reciprocal expressions of the same comparison. If one is +x, the
other is approximately -x before any data enters. The output confirms it: the
ratio between the two disparity estimates has median -0.674 and is negative in
50 of 50 seeds.

**The 100% sign-flip rate is therefore a mathematical consequence of including
a quantity and its reciprocal in the same comparison set, not an empirical
result about measurement.**

`log-space vs sale price` is also not an independent reference standard. It
correlates with `sale price as truth` at r = 0.994, with a mean absolute
difference of 0.0065 — the same comparison in a different functional form.

Finally, the ratio is determined by only two of the four choices. In all 50
seeds the maximum is `assessed value as truth` and the minimum is
`own model as truth`; the other two never bind.

#### Recomputed under alternative benchmark sets

| Benchmark set | BSR median | Range | Sign flip |
| --- | --- | --- | --- |
| All four (as originally reported) | 5.57 | 4.00 – 9.38 | 100% |
| Excluding `own model as truth` | 4.54 | 3.51 – 6.25 | Never |
| `sale price` vs `assessed value` only | 3.76 | 3.05 – 4.95 | Never |

### Revised claim

Recorded sale price and county assessed value are two genuinely distinct
reference standards, both used in published work, neither derivable from the
other. Restricting the comparison to those two:

> Across 50 negative-control draws, two independently defensible reference
> standards produced disparity estimates differing by a factor of 3.05 to 4.95
> on data containing no disparity by construction.

This is a weaker headline than the sign-flip framing and a considerably more
defensible one.

### Planned restructure

The module README already describes the full version as a specification curve
over benchmark choice x functional form x sample restriction x winsorization.
The current demonstration collapses three of those axes into one list. They
will be separated:

- **Benchmark axis** — distinct reference standards: sale price, assessed
  value, and (planned) a repeat-sales estimate. The BSR is defined over this
  axis only.
- **Functional form axis** — level vs log. Reported as its own sensitivity.
- **Direction axis** — which quantity is the numerator. Reported separately,
  with the reciprocal relationship disclosed.

### Terminology

The synthetic demonstration is a **negative control**: the data-generating
process contains zero disparity by construction, and the question is whether
established measurement choices manufacture one anyway. Framing it as a
negative control rather than as a simulation states the design more precisely.

---

## Related work across fields

The problem — estimating error against a reference standard that cannot be
observed — has been treated independently in several literatures. Notes on what
does and does not transfer.

**Diagnostic testing without a gold standard (biostatistics).** Hui-Walter
latent class models identify test accuracy from multiple imperfect tests across
populations with differing prevalence. These models require *binary* outcomes
and a dichotomous latent state, so they do not port directly to a continuous
latent value.

More relevant is their documented fragility. Where an unmodeled additional
latent state exists, reported simulations find sensitivity estimated at 0.27
against a true 0.88, coverage of 90% credible intervals collapsing toward zero,
and posterior predictive checks detecting the misfit in only about 7% of
simulations at N=225 and 23% at N=1000. A method built to operate without a
gold standard can be badly wrong in a way its own goodness-of-fit procedures do
not reveal — an independent instance of the concern this package measures.

- https://pmc.ncbi.nlm.nih.gov/articles/PMC8440412/
- https://pubmed.ncbi.nlm.nih.gov/22017371/
- https://onlinelibrary.wiley.com/doi/abs/10.1002/sim.6218

**Measurement error and errors-in-variables (econometrics).** The appropriate
home for a continuous latent true value observed through several imperfect
indicators, and the natural companion to the partial identification literature
already cited in the module README. Open question: under what assumptions is a
disparity identifiable given several imperfect benchmarks of a continuous
latent quantity?

- https://www.sciencedirect.com/science/article/abs/pii/S0304407617300830
- https://arxiv.org/html/2512.02970

**Fair value measurement (accounting).** Under ASC 820 and IFRS 13, assets
without an observable market price are classified Level 3, and the holder must
disclose the valuation technique, the unobservable inputs, and a sensitivity
analysis over alternative assumptions. A disclosure obligation of that shape,
applied to automated valuation models, is close to what reporting a benchmark
sensitivity statistic would accomplish.

- https://dart.deloitte.com/USDART/home/codification/broad-transactions/asc820-10/roadmap-fair-value-measurements-disclosures/chapter-8-fair-value-hierarchy/8-4-level-3-inputs

**Metrology.** Where no primary standard exists, measurement science uses a
consensus value together with an explicit uncertainty budget decomposing total
uncertainty into named components. The BSR is naturally read as one line item
in such a budget: uncertainty attributable to choice of reference standard.

- https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2156.pdf
- https://www.eurachem.org/images/stories/Guides/pdf/ECTRC_2019_EN_P1.pdf

**Psychometrics.** The criterion problem and construct validity address
measuring an unobservable construct with no criterion available for validation,
and long predate the machine learning treatment of the same difficulty.

- https://en.wikipedia.org/wiki/Criterion_validity

---

## Reproducing these results

```bash
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py                      # single seed
python examples/multi_seed.py --n-seeds 50             # distribution
python examples/multi_seed.py --n-seeds 50 --output-csv multi_seed_results.csv
pytest
```

## Status

Every result reported in this log is from synthetic data generated by
`examples/synthetic_demo.py`. The repository root also contains a separate
down-payment scenario analysis that uses real Assessor assessed values for
Compton; it is not part of the results above. The API is not stable.
