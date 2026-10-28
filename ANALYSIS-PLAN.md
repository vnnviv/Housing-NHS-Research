# Analysis plan: AMI-cap sensitivity (Compton, then one held-out city)

Status: DRAFT until you date and commit it. Amendments 1 (2026-10-27) and 2 (2026-10-28) are below. Once committed, changes go in a dated
"Amendments" section at the bottom, never as silent edits.

**What this plan is for.** To fix, before the confirmatory run, what is measured,
how the sample is filtered, and what counts as a conclusion. The Compton file
(`analysis/data/compton_sales_2025_2026.csv`, pulled 2026-09-18) and the
25th-percentile tables in `NHS-ASSISTANCE-SIZING.md` were seen before this plan
existed, so **every Compton result is exploratory**. Only a city that has not been
looked at can be confirmatory.

## 1. Question

How far is a program's income cap from the income a household needs to buy a recent
home at local prices, and how much does that answer depend on assumptions nobody can
observe (rate, price proxy, mortgage insurance, taxes, insurance)?

Not claimed: that AMI is "wrong" or "too low", that raising a cap raises ownership, or
anything about algorithmic bias in valuation models (that is Paper 2, a separate
project with a different estimand).

## 2. Estimands (primary)

1. **Required income** `Y*(price, R)`: the minimum annual income that carries the
   first mortgage on a home at `price` when `R` dollars of principal reduction (soft
   assistance beyond cash) are applied, with cash needs assumed met. Stated in dollars.
2. **Cap gap ratio** `Y* / cap` for each named cap. Greater than 1 means even a household
   at the cap cannot buy that home.
3. **Reach**: the share of recent sales that a household at income `cap` can buy at each `R`.
4. **Cash gap** `max(0, down + closing - savings)`, reported separately, never added into
   the income estimand.

Secondary: elasticities (change in `Y*` per +1 point of rate; per +10% price), and the
flip point on each axis (section 6).

## 3. Sample and filter (fixed before the confirmatory city is pulled)

- Source: LA County Assessor roll, parcels with `UseDescription='Single'`,
  `Roll_LandBaseYear = Roll_ImpBaseYear` in {2025, 2026}, `TaxRateCity` = the city
  (not `SitusCity`; unincorporated areas need a spatial join; check `returnCountOnly`
  first).
- Drop assessed totals under $200,000 (partial interest / non-arm's-length). The
  threshold is the existing repo value and is not tuned on outcomes.
- **Known gaps, reported, not hidden:** (a) a reset is not necessarily an arm's-length
  sale (inheritance and trust transfers can reset); (b) condos and townhomes are excluded
  by the `Single` filter, so the sample leans toward the higher-priced segment;
  (c) base-year value is the price at the reset date, not today's price.
- Report, for every city: rows pulled, rows after each filter, final n.
- **Minimum n:** a percentile is reported only if the city has at least 100 retained
  parcels. Below that, report the range only and say so.

## 4. Fixed cases

| Item | Value | Status |
|---|---|---|
| Household size | 4 persons (a 2-person run is a pre-planned second case) | Fixed |
| Price points | 25th and 50th percentile; 75th as context | Fixed |
| Principal reduction `R` | $0, $25k, $50k, $100k, $150k | Fixed |
| Caps (4-person, dollars) | HUD very low $83,300; MFI $108,100 (reference, not a cap); HUD low = HCD moderate $133,250; CalHFA standard flat $214,000; Greenline $151,300 (2024 materials, possibly stale) | HUD/HCD verified; CalHFA relationship to AMI unexplained; Greenline unverified |
| Housing ratio (policy axis) | 0.28, 0.30, 0.33, 0.36 front-end | Policy choice, shown separately from uncertainty |

## 5. Uncertainty axes (rate is sourced; the other ranges are PLACEHOLDERS until sourced)

| Axis | Base | Range | Source to replace the placeholder |
|---|---|---|---|
| Mortgage rate | 7.40% (PMMS 2026-10-08, from repo) | 5.98% to 7.79% | **Sourced** (Amendment 1): Freddie Mac PMMS weekly min and max, 2023-01-05 to 2026-10-22, FRED MORTGAGE30US |
| Price proxy multiplier | 1.00 | 0.95 to 1.10 | Scenario; Assessor-reset vs sale gap is unmeasured |
| MI scale (credit) | 1.00 (700-719) | 0.59 to 1.67 | Rate card in repo (Enact HFA); credit effect on the *rate* is not modeled |
| Property tax rate | 1.10% | 1.00% to 1.25% | County tax bill for the city's tax rate area |
| Homeowners insurance / month | $150 | $100 to $300 | Quotes or CDI data; wildfire-area repricing is a risk |
| Savings | $10,000 | $0 to $25,000 | Placeholder until NHS shares typical client savings |
| Closing costs | 2.5% | 2.0% to 4.0% | Lender estimates |

Ranges must be anchored to observed history or a named source before the confirmatory
run. A range chosen to produce a result is a fork in the path.

## 6. Decision rules (what counts as a conclusion)

- **Do not report "share of the grid".** Report, for each price point, `R`, housing ratio
  and cap: the minimum and maximum `Y*` over the uncertainty axes, and one of three
  labels: *reachable in every cell*, *unreachable in every cell*, or *mixed*. The cell
  count is shown as description only; it is not a probability.
- **Flip points.** For each continuous axis, with the others at base, the value at which
  `Y*` equals the cap. State whether that value lies inside the stated range.
  "Unreachable unless rates fall to X%" is the headline form.
- **Tornado.** Swing in `Y*` from the low to high end of each uncertainty axis. If the
  price-proxy multiplier is the largest swing, the finding is "better sale data comes
  before debating the cap".
- **Direction of bias.** Every number is paired with the direction in which each
  omitted factor pushes it (section 7). The final claim is a lower bound on the income
  barrier, not a point estimate.
- **Confirmatory test.** The sign of "the cap household cannot reach the 25th-percentile
  sale at base assumptions" and its label (*every cell / mixed*) must match in the
  held-out city. A mismatch is reported as such.

## 7. Direction of bias for omitted or assumed factors

| Omitted or assumed | Effect on "a cap-level household cannot reach a recent sale" |
|---|---|
| Existing debts (none in ACS; front-end ratio only) | Understates the barrier |
| Unfinanceable fixers and cash-only sales inside the 25th percentile | Understates the barrier (a financeable entry price is higher) |
| Base-year price vs today's rates and prices | Depends on price change since reset; trend or restrict the window |
| Credit effect on the interest rate (not modeled) | Understates the barrier for lower scores |
| Wealth (unobserved) | Cash-barrier shares are unknowable; report only the cash gap |
| Non-arm's-length resets in the sample | Noise, likely biased low on price; filter |
| Assistance structure (grant vs repayable second) | Dollars counted equally here; repayable seconds with payments would raise `Y*` |

## 8. Population caveat

This engine computes what an income can buy. It does **not** estimate how many Compton
renter households sit in each income band (needs ACS tract tables, not yet pulled) or
whether recent buyers resembled local renters. Until that join exists, no sentence of the
form "X% of Compton households are excluded" is permitted.

## 9. Validation

- Unit tests against closed-form amortization values and against the existing
  `assistance_sizing.py` (parity), in `tests/test_cap_sensitivity.py`.
- External check: Atlanta Fed HOAM qualified income, run on LA County prices (mechanics
  check, not a Compton result). Set the tolerance before looking. Not yet done.
- Practitioner check of rate, ratio, mortgage insurance and closing-cost assumptions by a
  loan officer or NHS staff. Not yet done.

## 10. Order of work

1. Commit this plan. 2. Replace placeholder ranges with sourced ones. 3. Pull the
held-out city under section 3. 4. Run once. 5. Report both cities with the labels above.

### Held-out city selection (fixed before any candidate is pulled)

Eligible: an incorporated LA County city whose `TaxRateCity` returns at least 100 retained
parcels under section 3, working-class and renter-heavy like Compton, and not a city used
in any prior NHS analysis. Candidate list, fixed in alphabetical order so the choice does
not depend on outcomes: Baldwin Park, Bell Gardens, Lynwood, Pomona, South Gate. Run them in
that order and use the first that meets the minimum n. The candidates are named from
general knowledge; their n and incomes are unverified. Baldwin Park and Pomona sit in the
San Gabriel Valley, which overlaps Paper 2's geography; that is a separate project, so if
you want the threads kept apart, drop them from the list *before* running anything.
Run: `python analysis/pull_city.py "<CITY>" --out analysis/data/<city>_2025_2026.csv`, then
`cap_sensitivity.py --csv ... --label ... --status confirmatory`.

## Amendments

**Amendment 1, 2026-10-27 (before any held-out city was pulled).**
- Rate axis now 5.98% to 7.79% (PMMS weekly min and max, 2023-01-05 to 2026-10-22). Base stays
  7.40% (repo value, PMMS 2026-10-08); the latest reading is 7.32% (2026-10-22). The range was
  taken from observed history, not from any result. Compton results shifted only by the rate
  swing in the tornado ($29,135 to $26,248); the headline row did not change.
- Added a headline line to every report (25th percentile, R = 0, 30% ratio, HUD low cap, label)
  so the confirmatory comparison is on one pre-named line.
- Added the held-out city list and rule above, a `--csv/--label/--status` interface, and the
  n < 100 stop.
- Still PLACEHOLDER: tax rate, insurance, savings, closing costs, price multiplier. Tax: the 1%
  general levy is verified; Compton's total rate is not. Look up 2 to 3 Compton tax rate areas
  at the LA County Auditor-Controller before the confirmatory run.

**Amendment 2, 2026-10-28 (before any held-out city was pulled; after seeing HMDA for Compton).**
- Reason, stated plainly: public HMDA loans for Compton tracts showed that real buyers carry much
  higher housing ratios than the 30% base used for the headline (median implied front-end ratio
  0.39 in 2025 and 0.41 in 2024; most buyers at or below the cap had total DTI of 44% or more).
  At 43% the Compton 25th-percentile home needs about $136k, 1.02x the cap, and the label is
  *mixed*, not *unreachable*. The earlier headline was driven by the ratio assumption.
- Change: the headline and the confirmatory comparison are now reported at two front-end ratios,
  30% (conservative policy ratio) and 43% (near observed buyers). A confirmatory match requires
  the same label at both.
- Added `analysis/hmda_validation.py` and `HMDA-VALIDATION.md` as an external check. It is
  exploratory for Compton. The same script is run unchanged on the held-out city.
- This amendment was made after looking at HMDA for Compton, so it is post hoc for Compton. It
  was made before the held-out city was pulled, so it does not bias the confirmatory test.
- Interpretation rule: a household that "can" buy at 43% front-end carries a heavy housing cost
  burden. Reachability at 43% is not affordability. Report both, never one.
