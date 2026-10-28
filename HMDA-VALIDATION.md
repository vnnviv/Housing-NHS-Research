# HMDA check of the engine: Compton (EXPLORATORY)

Real purchase loans, not a sample of people who tried and failed. Tracts: 24 Census 2020 tracts with their internal point inside Compton; 21 tracts that only touch the boundary are excluded. Income is the applicants' combined income and household size is unknown, so the 4-person caps are a rough comparison. Not a finding about NHS clients.

## 2024

289 owner-occupied, first-lien, single-family purchase originations in Compton tracts; income reported for 287.

| Measure | p25 | median | p75 |
|---|---|---|---|
| Applicant income | $127,000 | $150,000 | $178,000 |
| Property value | $605,000 | $655,000 | $705,000 |
| Interest rate | 6.00% | 6.50% | 6.99% |
| Implied front-end ratio* | 0.35 | 0.41 | 0.45 |

*Own loan terms, 1.10% tax, $150/mo insurance, engine mortgage-insurance card. Total DTI from HMDA is a separate, higher number.

| Cap | Share of buyers with income at or below the cap |
|---|---|
| HUD very low ($83,300) | 2% |
| MFI reference ($108,100) | 9% |
| HUD low = HCD moderate ($133,250) | 32% |
| Greenline ($151,300) | 53% |
| CalHFA flat ($214,000) | 90% |

Buyers at or below $133,250: n=93, median property value $605,000, median LTV 95, 60% with LTV at or above 95, 42% with a co-applicant. Loan types {'1': 52, '2': 37, '3': 4} (1 conv, 2 FHA, 3 VA, 4 USDA). Total DTI bins: {'50%-60%': 33, '49': 16, '48': 11, '46': 6, '45': 5}.

Engine check: at each buyer's own price, rate and down payment and a 30% front-end ratio, required income divided by actual income has median 1.36 (p25 1.14, p75 1.50). If the engine's arithmetic reproduces real loans this should be close to the buyers' median front-end ratio divided by 0.30, which is 1.36.

## 2025

363 owner-occupied, first-lien, single-family purchase originations in Compton tracts; income reported for 362.

| Measure | p25 | median | p75 |
|---|---|---|---|
| Applicant income | $129,000 | $153,500 | $189,000 |
| Property value | $605,000 | $655,000 | $725,000 |
| Interest rate | 5.99% | 6.28% | 6.75% |
| Implied front-end ratio* | 0.33 | 0.39 | 0.45 |

*Own loan terms, 1.10% tax, $150/mo insurance, engine mortgage-insurance card. Total DTI from HMDA is a separate, higher number.

| Cap | Share of buyers with income at or below the cap |
|---|---|
| HUD very low ($83,300) | 3% |
| MFI reference ($108,100) | 11% |
| HUD low = HCD moderate ($133,250) | 28% |
| Greenline ($151,300) | 48% |
| CalHFA flat ($214,000) | 86% |

Buyers at or below $133,250: n=102, median property value $605,000, median LTV 94, 48% with LTV at or above 95, 49% with a co-applicant. Loan types {'2': 34, '3': 7, '1': 61} (1 conv, 2 FHA, 3 VA, 4 USDA). Total DTI bins: {'50%-60%': 28, '49': 23, '48': 11, '44': 9, '45': 7}.

Engine check: at each buyer's own price, rate and down payment and a 30% front-end ratio, required income divided by actual income has median 1.32 (p25 1.11, p75 1.47). If the engine's arithmetic reproduces real loans this should be close to the buyers' median front-end ratio divided by 0.30, which is 1.31.

