# Findings

Dated log of results and corrections, newest first. BSR and coverage results are all from synthetic data.

---

## 2026-10-28: HMDA check changes the headline (Compton, exploratory)

- Pulled public HMDA purchase originations for LA County (2024: 43,089; 2025: 42,498) and kept owner-occupied, first-lien, single-family loans in 24 Compton tracts (2024: 289; 2025: 363). Tracts are Census 2020 tracts whose internal point lies inside the city; 21 boundary-touching tracts are excluded.
- Real buyers: median income $150,000 (2024) and $153,500 (2025); median property value $655,000 in both years; median rate 6.50% and 6.28%. 32% (2024) and 28% (2025) of buyers had income at or below the $133,250 cap, and those buyers bought at a median value of $605,000, mostly with LTV near 95 and about 40% FHA or VA.
- **The 30% front-end ratio drove the old headline.** The median buyer's implied front-end ratio was 0.41 (2024) and 0.39 (2025), and most buyers at or below the cap had a total DTI of 44% or more. At 43% the 25th-percentile home needs $135,854, 1.02x the cap, and the label is mixed. At 30% it is $194,725, 1.46x, unreachable in every cell. The earlier sentence "unreachable in every cell" was a statement about a 30% ratio, not about Compton.
- The Assessor price proxy ran below HMDA property values: p25 $559,482 vs $605,000, median $633,926 vs $655,000 (about 3% to 8% low). That sits inside the 0.95 to 1.10 multiplier range and supports its upper half.
- The engine's arithmetic reproduces real loans: required income over actual income at each buyer's own terms has median 1.36 (2024) and 1.32 (2025), against 1.36 and 1.31 predicted from their ratios. This checks consistency of the formulas, not the tax and insurance assumptions.
- Limits: HMDA shows only people who bought (survivorship). Income is combined applicant income and household size is unknown, so the 4-person caps are a rough match. Half the buyers at or below the cap had a co-applicant. 2025 rates were lower than the 7.40% base. HMDA has no down payment assistance or seller-credit field.
- Consequence: the headline and the confirmatory test now use two ratios (Amendment 2). The claim that survives is narrower and more defensible: whether a cap-level household can buy depends mainly on how much of their income lenders let them spend on housing, and reaching a home at 43% means a heavy cost burden.

---

## 2026-10-27: Sourced rate range, headline line, held-out pipeline

- Rate range replaced with Freddie Mac PMMS history: 5.98% to 7.79% (weekly, 2023-01-05 to 2026-10-22; FRED MORTGAGE30US). Base 7.40% unchanged; latest reading 7.32%. Amendment 1 in `ANALYSIS-PLAN.md`.
- Compton headline (exploratory, unchanged): 25th-percentile home $559,482 needs $194,725 with no principal reduction, 1.46x the $133,250 cap, unreachable in every grid cell. The rate swing in the tornado is now $26,248 (was $29,135 on the placeholder range); price proxy $28,309 is now the largest swing, but its range is still a placeholder, so the ranking is not a finding.
- New: `pull_city.py` (run locally; the Assessor service blocks cloud IPs), `acs_renter_income.py` (needs a Census API key; gives bounds, never a point share), `make_figures.py`, `docs/novelty-search.md`. The held-out city is not yet pulled, so nothing is confirmed.
- Literature check: the income / asset barrier split already exists (Perkins et al., Cityscape 2020; JCHS). Only the combination is arguably new. Direct SSRN, NBER, JHE and Lewis Center searches are still to do.

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
