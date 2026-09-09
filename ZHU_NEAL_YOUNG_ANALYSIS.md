# Zhu, Neal & Young — Novelty Assessment and Specification Axis Mapping

*September 8, 2026. References the Cityscape paper and the 2025 Urban Institute follow-up.*

---

## The paper

**Zhu, L., Neal, M., & Young, C.** "Racial Disparities in Automated Valuation Models: New Evidence Using Property Condition and Machine Learning." *Cityscape* 26(1), HUD, 2024. Atlanta and Memphis, 2018 transactions.

Preceded by Neal, Strochak, Zhu & Young (2020), Urban Institute working paper — Atlanta, Memphis, and Washington DC. Followed by Zhu, Axelrod & Zinn (2025), Urban Institute — Atlanta and Memphis, individual homeowner level.

## Design

| Element | Detail |
|---|---|
| Cities | Atlanta-Sandy Springs-Alpharetta, GA; Memphis, TN-MS-AR |
| Data | 2018 single-family home sale transactions |
| Benchmark | Sale price (AVM estimate compared to actual sales price) |
| Racial classification | ACS tract racial composition; majority-Black vs majority-White tracts. The 2025 follow-up uses fBISG (fully Bayesian Improved Surname Geocoding) for individual homeowner race. |
| AVM models | OLS baseline; LightGBM (beats OLS by 5.8pp RMSE) |
| Condition ratings | Exterior condition from computer vision on aerial imagery |
| Synthetic control | Neighborhood race manipulated via synthetic control construction |

## The three error metrics — a ready-made specification axis

The paper uses three functional forms of the AVM-vs-sale-price comparison. These are exactly the "functional form axis" that the BSR specification curve should sweep:

1. **Directional inaccuracy** — signed error: AVM estimate minus sale price. Measures whether the AVM systematically over- or under-predicts. This is the sale-price benchmark with sign preserved.

2. **Magnitude** — absolute dollar difference: |AVM - sale price|. Measures the size of the error regardless of direction. This is the sale-price benchmark with sign discarded.

3. **Percentage magnitude** — absolute error as a fraction of sale price: |AVM - sale price| / sale price. Measures proportional error, which matters more for lower-priced homes. This is the sale-price benchmark in ratio form.

All three are transforms of the same underlying comparison (AVM vs sale price). They are not independent benchmarks — they are the same benchmark in different functional forms. This is precisely the "functional form axis" that FINDINGS.md plans to separate from the benchmark axis.

## Headline results

- Percentage magnitude of error roughly 2× as large in majority-Black neighborhoods vs majority-White
- ~3.5pp survives condition controls
- ~5.0pp attributed to racial composition via synthetic control
- LightGBM beats OLS by 5.8pp RMSE
- Even with condition data and ML, disparity persists
- 2025 follow-up: 3.4pp higher error for Black homeowners; ~5% systematic undervaluation of Black-owned properties

## What this means for Paper 2

### The empirical result is not the contribution

Zhu/Neal/Young already established that AVMs produce larger percentage errors in majority-Black neighborhoods, using sale price as the benchmark, with property condition controls and ML. Paper 2 cannot claim this as a novel finding.

### The benchmark sensitivity of that result IS the contribution

Zhu/Neal/Young use sale price as the sole benchmark. They do not test whether their finding survives a change of benchmark. Paper 2's contribution is showing that the headline result — 2× error in majority-Black neighborhoods — is itself a function of benchmark choice, and that the BSR quantifies that dependence.

### The three error metrics are a specification axis

Zhu/Neal/Young's three metrics (directional, magnitude, percentage) are a ready-made functional-form axis for the specification curve. The BSR can be computed over these three forms of the same benchmark, showing how much the disparity estimate depends on which functional form the analyst chose — even holding the benchmark fixed.

### The condition ratings are a model-input axis

Their computer-vision condition ratings are a model-input axis: does the disparity survive when the model can see condition? Zhu/Neal/Young show it shrinks but persists. Paper 2 can add the benchmark axis: does it survive when you change what "correct" means?

## What Paper 2 must do

1. **Cite and distinguish before the November design memo.** Discovery by a reviewer instead would be damaging. The distinction is: they measure disparity against one benchmark; we measure how much that disparity depends on the benchmark.
2. **Map their three error metrics as a functional-form specification axis.** This is free empirical structure — their metrics are already defined and published.
3. **Position the BSR as answering a question they did not ask.** They ask "is there a disparity?" and answer yes. Paper 2 asks "how much of that disparity is a property of the benchmark?" and shows the answer is non-trivial.
4. **Note the 2025 follow-up.** Zhu, Axelrod & Zinn (2025) moves to individual homeowner level with fBISG. This raises the bar for the racial classification strategy — tract-level composition is now clearly superseded for individual-level claims, though it remains defensible for neighborhood-level disparity.
5. **Acknowledge that sale price is their benchmark and the contested one.** The BSR critique applies directly: sale price embeds discrimination, so measuring AVM error against sale price inherits that bias. This is stated in the BSR module README but must be made explicit in the paper's positioning relative to Zhu/Neal/Young.

## Sources

- Zhu, Neal & Young, *Cityscape* 26(1) — https://www.huduser.gov/portal/periodicals/cityscape/vol26num1/ch15.pdf
- Urban Institute (2022) — https://www.urban.org/research/publication/revisiting-automated-valuation-model-disparities-majority-black-neighborhoods
- Urban Institute (2025) — https://www.urban.org/research/publication/do-automated-valuation-models-reinforce-disparities-home-values
- Neal, Strochak, Zhu & Young (2020) — https://www.urban.org/research/publication/how-automated-valuation-models-can-disproportionately-affect-majority-black-neighborhoods
