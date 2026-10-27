# Novelty check: has anyone audited an AMI cap against local purchasing power?

Status: first-pass, bounded (about 15 searches, run 2026-10). It supports one narrow
sentence and no stronger claim. **"I did not find X" means exactly that.** Do not write
"no one has done this" anywhere (paper, brief, email) until the open items below are done.

## What was found

| Work | What it does | How this project differs |
|---|---|---|
| Perkins, Rieger, Spader et al., Cityscape 22(1), 2020 | Splits public-housing residents into income / asset / debt barriers to a home at 3.5% down on the county median | The barrier-decomposition idea **already exists**. It is about a population, not about a program's cap |
| McCue, Hanifa, Herbert (JCHS), 2023 | Tests how far $25k of down payment assistance closes Black and Hispanic homeownership gaps under FHA underwriting | Asks what assistance does for a population, not whether the eligibility cap itself reaches local sales |
| Ward (JCHS), 2021 | Design choices for a national down payment program | Program design, no cap-vs-price audit |
| Shoag, Romem, Garcia (Terner Center), 2023 | Net-worth-to-price ratio explains much of California's ownership gap | Statewide, wealth framing, not a program cap |
| Teles, Su, Oneto (Urban Institute), 2023, "Calculating AMI" | Explains how HUD builds AMI and notes programs may adjust it | Describes the benchmark; does not test a cap against prices. It is the policy hook for this project |
| Linneman and Wachter (1989); Gyourko, Linneman, Wachter (1999); Acolin et al. | Wealth vs income constraints on ownership | Foundational; population level |
| Orange County housing element (2020) | Tables of affordable price at 80% and 120% AMI | Same arithmetic, but a single deterministic table, no uncertainty ranges or flip points |

## The one sentence this supports

"In the sources searched, I did not find a study that takes a specific program's income
cap, computes the income needed for recent local sales across stated assumption ranges,
and reports where the conclusion would flip."

What is arguably new here is the **combination**: the program-specific cap as the unit,
the cash/income split, uncertainty reported as min/max with flip points, and a held-out
city. The decomposition itself is not new and must be credited to Perkins et al. and JCHS.

## Not searched (absence of coverage, not absence of literature)

NBER and SSRN title search; Journal of Housing Economics; UCLA Lewis Center; Google
Scholar; HUD PD&R Evidence Matters; CalHFA and HCD evaluations; GSE evaluations of
AMI-capped products. **Do these before claiming novelty to anyone.** Full texts of
Linneman/Wachter, Gyourko et al. and Acolin et al. were not opened.

## Policy context (context only, not a claim)

California's November 2026 ballot includes Proposition 37, which concerns income limits
tied to AMI (reported as a 200%-of-AMI ceiling). Check the official ballot text before
describing it; this project takes no position on it and its numbers do not evaluate it.
NHS is a nonprofit and any public statement about a ballot measure is its decision.

## Open item

LACDA and Habitat LA 2026 tables could not be mapped to tiers from excerpts. The repo
already treats HUD low = HCD moderate = $133,250 (4-person) as verified from the HUD/HCD
methodology files in `sources/`; keep citing those, not the excerpts.
