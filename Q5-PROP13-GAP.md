# Q5: How far the Prop 13 roll sits from market, by tract (EXPLORATORY)

Exploratory. Regions were defined in code before outcomes were computed, but nothing here is preregistered. Descriptive only: no statement about valuation bias, and assessed value is not a benchmark for Paper 2.

**Data.** LA County Assessor 2026 roll, single-family parcels (`UseType = 'SFR'`) in the study ZIPs, placed in Census 2020 tracts by parcel centroid. HMDA 2024-25 owner-occupied, first-lien, single-family purchase originations by tract. Tract race and ethnicity from LA County's ACS B03002 layer (ACS year not stated on the layer; verify).

**Counts.** SGV parcels: 125,734 (26 unplaced); SGV ACS match: median 100% of a tract's parcels fall in its assigned ACS polygon; South LA parcels: 95,975 (32 unplaced); South LA ACS match: median 100% of a tract's parcels fall in its assigned ACS polygon; ACS join: 410 of 410 tracts (spatial); SGV study tracts: 93; South LA study tracts: 222.

**Ratios.** `stock` = median roll value of all SFR parcels / HMDA median property value. `held` = the same for parcels with base year 2023 or earlier. `psf` = median roll $/sqft of held parcels / median $/sqft of round-value 2025-26 resets in the same tract (one source, size-controlled). 1.00 = roll equals market.

| Measure (tract medians) | SGV | South LA | SGV minus South LA (95% bootstrap) |
|---|---|---|---|
| SFR parcels per tract (tracts: 93, 222) | 855 [461-1,228] | 306 [189-577] | +549 (+432 to +681) |
| Median base year (tracts: 93, 222) | 2003 [2002-2004] | 2006 [2005-2009] | -3 (-4 to -3) |
| Share with base year 2000 or earlier (tracts: 93, 222) | 42% [40%-45%] | 35% [32%-38%] | +0.073 (+0.060 to +0.089) |
| HMDA median property value (tracts: 53, 72) | $1,055,000 [$915,000-$1,365,000] | $690,000 [$655,000-$805,000] | +365,000 (+280,000 to +495,000) |
| Median roll value (tracts: 93, 222) | $524,415 [$452,032-$643,976] | $279,505 [$254,304-$315,361] | +244,910 (+214,944 to +282,271) |
| stock ratio (tracts: 53, 72) | 0.54 [0.49-0.60] | 0.41 [0.39-0.43] | +0.13 (+0.10 to +0.15) |
| held ratio (tracts: 53, 72) | 0.51 [0.46-0.56] | 0.38 [0.36-0.41] | +0.13 (+0.10 to +0.15) |
| psf ratio (tracts: 80, 141) | 0.44 [0.40-0.48] | 0.39 [0.36-0.41] | +0.05 (+0.04 to +0.08) |

Brackets are the interquartile range across tracts. Bootstrap resamples tracts (2,000 draws, seed 20261105), so it reflects tract-to-tract spread, not parcel sampling.

## Same base year, different gap

Roll $/sqft over same-tract reset $/sqft, all parcels in study tracts with at least 10 resets, pooled by base-year cohort. Holding the base year fixed removes tenure mix; what is left is how much prices rose since purchase.

| Base year | SGV | South LA |
|---|---|---|
| 1989 or earlier | 0.21 (n=18,094) | 0.10 (n=17,828) |
| 1990-99 | 0.36 (n=13,528) | 0.31 (n=9,659) |
| 2000-07 | 0.47 (n=14,590) | 0.42 (n=14,222) |
| 2008-12 | 0.61 (n=7,628) | 0.40 (n=8,776) |
| 2013-19 | 0.72 (n=12,231) | 0.58 (n=14,691) |
| 2020-23 | 0.84 (n=8,684) | 0.88 (n=10,438) |

## What this says

**Go/no-go: go.** The plan said to stop if the ratio barely varies between regions. It does vary. On every measure the South LA roll sits further below market than the SGV roll.

**The size depends on the yardstick.** The SGV-minus-South LA gap is 0.13 against HMDA values and 0.05 against same-tract resets on a per-square-foot basis. HMDA medians are not size-matched to the stock, so the per-square-foot figure is the more careful one. The spread between the two is the benchmark problem in miniature: the same roll, two reasonable market references, and a disparity that changes by a factor of about 2.5.

**It is not tenure.** SGV owners have held longer (median base year 2003 vs 2006; 42% vs 35% with base year 2000 or earlier). That alone would put the SGV roll *further* from market. Within every base-year cohort except 2020-23, South LA parcels sit further below market than SGV parcels. The widest cohort gap is 2008-12 (0.61 vs 0.40), purchases near the post-crash low. The regional gap is mostly differential appreciation since purchase, and tenure mix partly offsets it. This revises the hypothesis in `PAPER2-CONTEXT-DELTA` that an assessed-value disparity would be "a map of tenure": here it is mainly a map of price paths.

**For Paper 2.** An assessed-value benchmark would show South LA as more "undervalued" by roughly 5 to 13 points of market value, with no valuation content at all. Matching on base year does not remove it, because the cohort table shows the gap inside each cohort. This confirms the rule that assessed value cannot be a benchmark, a feature, or a target without modeling the price path.

**Competing explanation not ruled out.** The market reference (2025-26 resets) could be pulled up in South LA if more of those sales are renovated resales. That would make South LA's ratio look lower for reasons of quality, not appreciation. The roll has `EffectiveYearBuilt`, which could flag renovations; that check is not done here.

**Limits.** Regions are study ZIPs plus a 50% tract rule, set in code before outcomes were computed but not preregistered. Tract demographics are joined spatially from a county ACS layer whose ACS year is not stated (verify before citing). HMDA covers financed owner-occupants only, and its values are often appraisals. Bootstrap intervals reflect tract-to-tract spread only. Roll values include any new-construction additions on top of the base-year value.
