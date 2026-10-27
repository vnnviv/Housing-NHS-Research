# Findings

Dated log of results and corrections, newest first. BSR and coverage results are all from synthetic data.

---

## 2026-10-26: Income-cap sensitivity (Compton, exploratory)

- New `analysis/cap_sensitivity.py` and `ANALYSIS-PLAN.md`. The engine is pure (no module globals) and is tested against closed-form amortization values and against `assistance_sizing.py`. Compton results are exploratory: the data was seen before the plan existed. A held-out city is the confirmatory step.
- Base assumptions (7.40%, 3% down, 30% front-end ratio, 4-person caps): the 25th-percentile home ($559,482) requires $194,725 of income with no principal reduction, 1.46x the HUD low / HCD moderate cap of $133,250. With $100,000 of principal reduction it requires $149,120, 1.12x. Cash needs are assumed met and reported separately.
- The answer does not flip inside the placeholder ranges for the $133,250 cap. Rate would have to fall to 2.77% (others at base) to flip it. For the CalHFA flat $214,000 limit, required income stays below the cap across the 6% to 8% range and would cross it at 8.67%, above the tested range.
- Rate and the price-proxy multiplier give similar swings ($29,135 and $28,309 of required income). Both ranges are placeholders, so the ranking is not a finding.
- Limits: placeholder ranges, front-end ratio only (no debts), Assessor reset values as the price proxy, no count of households by income band. Direction-of-bias table in the output file.

---

## 2026-10-14: Assistance sizing (Compton scenarios)

- New `analysis/assistance_sizing.py`. Assistance needed = max(0, price + closing costs - first loan - savings), with the first loan capped by the housing-ratio budget.
- Median home $633,926, 3% down, 7.40%, $10,000 savings (placeholder): lower income $264,236, area median $355,046, very low $444,593. 91% to 94% of that is an income gap. The best usable program (GSFA Platinum, 5.5% of price) covers 8% to 13%.
- A $35,000 program opens at most about 1 in 20 of the 746 sales. Lower income range at the median across three assumption bundles: $181,647 to $274,236 (scenarios, not confidence intervals).
- Credit band doesn't change the amount here, since the first loan always ends at or below 80% of price. Credit's effect on the interest rate isn't modeled.
- Each extra $1 of price adds about $1.16 of assistance. Price is an Assessor-value proxy, so the benchmark problem applies.
- Limits: placeholder savings, closing costs and program amounts; one city; one household size. Details in `NHS-ASSISTANCE-SIZING.md`. No change to BSR or coverage results, and no disparity claim.

---

## 2026-10-05: Benchmark inventory for real data

- Candidates: recorded sale price, assessed value, appraised value, repeat-sales index, condition-controlled model. None run on real records yet.
- For recent sales the assessed value is close to the sale price (Prop 13 resets at transfer), and appraisals are reported to land at or above contract price in over 90% of GSE purchases (Fannie Mae; figure not checked against the original). The real-data class may hold fewer than two independent standards. If so, the BSR is undefined there and the coverage audit carries the analysis.
- Next: decide which candidates are independent enough, before any real-data run.

---

## 2026-10-02: Housekeeping

- READMEs now lead with the two-benchmark result (sale price vs assessed value, factor 3.05 to 4.95 across 50 draws). 7.97 is described as the original four-estimate output.
- `compton_sales_2025_2026.csv` holds Assessor assessed values, not recorded sale prices. The scenario analysis uses it as a price proxy and the BSR modules don't.
- "Not run on real parcel records" applies to the BSR and coverage modules only.

---

## 2026-09-08: Multi-seed robustness, and a limitation

- 50 seeds: BSR median 5.57 (IQR 5.22 to 6.39, range 4.00 to 9.38), sign flips in 50 of 50, median smallest |estimate| 0.026. The original seed's 7.97 sits inside the range.
- Coverage: group 0 median 94.5%, group 1 median 85.7% (below 88% in 48 of 50 seeds). The gap never falls below 4.8 points. Under-coverage means the model fails for that group. Over-coverage means wider, less precise intervals. Both are calibration failures.
- Limitation: `own model as truth` is the reciprocal of `sale price as truth` (`sale / pred - 1` vs `pred / sale - 1`), so the 100% sign flip is arithmetic. `log-space vs sale price` is the same comparison in log form (r = 0.994). Only two of the four choices ever set the ratio.
- BSR median by benchmark set: all four 5.57 (sign flips 100%); without `own model as truth` 4.54 (3.51 to 6.25, never); sale price vs assessed value only 3.76 (3.05 to 4.95, never).
- Revised claim: across 50 negative-control draws, two independently defensible reference standards gave disparity estimates differing by a factor of 3.05 to 4.95 on data with no disparity by construction.
- Planned: report three axes separately. Benchmark (BSR defined here only: sale price, assessed value, planned repeat-sales), functional form (level vs log) and direction (which quantity is the numerator).
- The demonstration is a negative control: zero disparity by construction, and the question is whether standard measurement choices produce one anyway.
- The per-seed CSV isn't tracked. Regenerate it with `--output-csv`.

---

## Related work

Notes on other fields that face the same problem (biostatistics, econometrics, accounting, metrology, psychometrics) are in [`docs/related-work.md`](docs/related-work.md).

## Reproducing

```bash
cd benchmark-sensitivity
pip install -e .
python examples/synthetic_demo.py                      # single seed
python examples/multi_seed.py --n-seeds 50             # distribution
python examples/multi_seed.py --n-seeds 50 --output-csv multi_seed_results.csv
pytest
```

The scenario analysis runs from the repo root: `python analysis/assistance_sizing.py` and `python -m pytest tests`.
