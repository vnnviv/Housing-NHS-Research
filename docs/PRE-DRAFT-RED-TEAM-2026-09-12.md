# Pre-Draft Red Team — Paper 2

*September 12, 2026. A pre-draft red team, written from the published record of prior work in this
exact area. The organizing question: which researchers believed they had a finding, published it,
and were then shown to have measured their own analytical choice?*

*Written as a review memo addressed to the author, and kept in that voice. It is a working document,
not a finished section; second person throughout refers to the repository owner.*

---

## 1. The single most useful thing in this document

**Zhu, Neal & Young's own results contain a direction reversal, and it is published.**

In Atlanta and Memphis, the *absolute dollar* magnitude of AVM error was **larger in majority-White
neighborhoods**. The disparity appears only when error is expressed as a **percentage of sale
price**, where it reverses and becomes larger in majority-Black neighborhoods. Same data, same
model, same benchmark — opposite headline depending on whether the denominator is there. Urban
states this plainly in the 2022 brief and the 2024 *Cityscape* article.

This matters more than anything else here because of what the repository currently is. The
benchmark-sensitivity module's headline BSR of 7.97 comes from a synthetic county, and the
`FINDINGS.md` entry of Sept 8 already retracted part of its interpretation — two of the four
benchmarks were a reciprocal pair, so the 100% sign-flip rate was arithmetic, not evidence. A
reviewer who reads only the README meets a striking number that the repository's own findings log
walks back.

**Recommendation:** lead the paper with the Zhu/Neal/Young reversal, not with the synthetic demo.
It is a real, peer-reviewed, non-simulated instance of exactly the thesis — a disparity estimate
whose sign is determined by a functional-form choice the analyst made — and it comes from the
paper closest to Paper 2's own design. The synthetic county then becomes the controlled
illustration that explains *why* it happens, which is its correct role. This costs nothing but
reordering, and it converts the paper's weakest exposure (all results are synthetic) into its
strongest opening.

---

## 2. The canonical "we were sure, and it did not hold" case

| | |
|---|---|
| **Claim** | Perry, Rothwell & Harshbarger (Brookings, 2018): homes in majority-Black neighborhoods are undervalued ~23% (~$48,000/home, $156B cumulative) after 23 controls for structure and neighborhood amenity. |
| **Reception** | Enormous. Cited by the interagency PAVE task force, NYT, CNN, and most subsequent appraisal-bias policy work. |
| **The critique** | AEI Housing Center (Pinto & Peter) replicated the analysis, kept all 23 original controls, and added **one** variable: neighborhood Equifax Risk Score. They report that ERS alone absorbs the entire measured devaluation. |
| **Brookings' reply** | Argue the objections do not survive scrutiny; note that adding income and education moves the estimate only from −22.7% to −21.7%, and that the critique's first version fails once rich and poor neighborhoods are both included. |
| **Status** | Unresolved. Both sides are still publishing. AEI testified to House Financial Services in March 2022 under the title "Faulty Evidence and Misdiagnosed Solutions." |

**Why this is Paper 2's problem, not just a citation.** The AEI critique is not about appraisals
specifically. It is a general claim: *a neighborhood-racial-composition coefficient survives your
controls because your controls omit creditworthiness and buying power, which are correlated with
race and with price.* That argument transfers to Paper 2 unchanged. San Gabriel Valley versus South
LA is a comparison across an enormous SES gradient. If the paper reports any SGV/South-LA
differential without a pre-committed answer to "did you control for neighborhood credit
conditions," the first informed reader supplies the AEI critique and the paper is done.

**What to do about it, cheaply.** The master brief's SGV-vs-South-LA design already claims to
"partially solve the identification problem" because one AVM misspecified similarly in both regions
makes a differential more defensible than a level. That reasoning is sound but incomplete: it
defends against *model* misspecification, not against *omitted-variable* confounding in the
comparison itself. Two additions close most of the gap and both are already within scope:

- Report the differential with and without a neighborhood credit/SES control, and treat the
  *movement* between the two as a reported quantity rather than a robustness footnote. This is the
  specification-curve logic already planned, applied to the axis that actually killed Brookings.
- State in the design section, before results, that a differential which vanishes under SES
  controls will be reported as such. The pre-commitment is what distinguishes this paper from the
  ones it critiques.

---

## 3. The circularity is already in print, in a good journal

*"Do appraiser and borrower race affect mortgage collateral valuation?"* — **Review of Finance**,
accepted July 2024, published Nov 6 2025, **corrected and typeset March 12 2026**.

The design: benchmark appraised values against an independent industry AVM that lenders did not
have at origination. The finding: appraisals are 5–12% above AVM values for all borrowers; minority
valuation discounts exist and **grow larger "after adjusting for potential bias in the AVM
estimates."**

Read that last clause carefully. A finance journal published a paper that measures appraisal bias
against an AVM, then adjusts for bias *in the AVM* — which requires a third standard that is never
itself validated. This is the benchmark regress, in print, at a venue Paper 2 would be lucky to
reach. It is the best possible motivating citation: the paper does not have to argue that
researchers *might* fall into this: it can show that the field's current best work is structured
this way and has no vocabulary for reporting it.

**[Resolved 2026-09-12]** Full citation: Lopez, Luis A., "Do appraiser and borrower race affect
mortgage collateral valuation?", *Review of Finance* 30(2), 2026, pp. 639-679, DOI
10.1093/rof/rfaf046 (University of Illinois Chicago). Single-authored. No erratum is attached; the
"corrected and typeset, 12 March 2026" line on the landing page is a production-stage label, not a
post-publication correction. Note the sample period: national refinanced mortgages, 2000-2007, which
predates both the HVCC appraisal-independence reforms and modern AVM products. Cite it for its
benchmarking *structure*, not for its magnitudes.

---

## 4. A benchmark you are treating as independent probably is not

**Fannie Mae, "Contract Price Confirmation Bias: Evidence from Repeat Appraisals."** For at least
two decades, appraisals have come in at or above purchase price on **over ninety percent** of GSE
transactions.

The consequence for the BSR benchmark class is direct. `FINDINGS.md` already documents that "own
model as truth" is the algebraic reciprocal of "sale price as truth," and that "log-space vs sale
price" correlates with sale price at r = 0.994 — leaving only two genuinely distinct standards, of
which "assessed value as truth" always binds the maximum. But in real data, **appraised value is
mechanically anchored to contract price in nine of ten transactions.** Any benchmark derived from
appraisal is therefore substantially a transformation of sale price too, not an independent
reference standard.

This is the same non-independence failure discovered synthetically, recurring in the real data —
and it is an argument *for* the paper, not against it. It also raises the stakes on the repeat-sales
benchmark (`hpiR`), already ranked #2 in the September priority list: after this, repeat-sales is
not merely the third independent standard, it may be the only genuinely independent one available.

California adds a second, separate reason to distrust assessed value — Proposition 13 means
assessed value tracks tenure length, not market value — which the context delta already flags.
Both reasons point the same way: **the real-data benchmark class may be smaller than two.** If it
is, the BSR is undefined on LA County data and the coverage audit carries the paper. That is a
finding worth stating explicitly rather than discovering in month nine.

---

## 5. Recent work that must be in the lit review

| Work | Why it matters |
|---|---|
| Urban Institute, **Oct 2025**, "Do AVMs Reinforce Disparities in Home Values?" | Newest in the line. Uses **BIRDiE** for race imputation, applied at **ZIP code** level because of computational cost. The aggregation choice is itself a MAUP exposure worth a sentence. |
| Zhu, Axelrod & Zinn (2025), Urban Institute | Moves to individual homeowner level via fBISG surname/geocoding imputation. Imputed race is a measurement-error problem layered on top of the benchmark problem. |
| Howell & Korver-Glenn, UAD study (FHFA data, 32M appraisals 2013–2021) | The largest appraisal dataset analysis in existence; the advocacy community treats it as settled. Any paper questioning disparity measurement must engage it directly rather than around it. |
| Gallin, Nielsen, Molloy, Smith & Sommer (Federal Reserve Board, NBER CRIW) | Uses AVMs to measure aggregate housing wealth; explicitly discusses AVM error distributions and the requirement that errors be unbiased *by geography*. A macro-side statement of the same measurement concern. |

---

## 6. Two threats not yet in the project docs

**Selection into transaction.** Every sale-price benchmark conditions on the home having sold. If
turnover differs across SGV and South LA — and under Prop 13 it certainly does — the two regional
samples are selected differently, and a measured differential partly reflects *which* homes
transact rather than how they are valued. This is Heckman selection, it is econometrics-native, and
naming it correctly is cheap credibility with an economics audience. The September priority list
already includes measuring tenure-length distribution across the two regions (#4); that measurement
is the input to this argument, so run it early and report it as a sample-selection diagnostic, not
only as a Prop 13 check.

**The welfare sign is not obvious.** The paper's harm channel runs through reconsideration of
value. But AEI's critique notes, correctly, that a low valuation gives a *buyer* substantial
leverage to renegotiate the contract downward — and Fannie Mae's literature review points to work
(Ding & Nakamura; Fout & Yao) on information loss to borrowers who could have renegotiated or
walked away. A low AVM estimate harms the seller and can benefit the buyer. Since homeowners in the
studied tracts are on both sides depending on the transaction, "undervaluation is harm" needs one
paragraph of argument rather than assumption. An economics reviewer will notice if it is assumed.

---

## 7. Ordered by value per hour, before the draft

1. Reorder the paper to open on the Zhu/Neal/Young published sign reversal; demote the synthetic
   county to illustration. **Cost: an afternoon. Largest single gain.**
2. Write the AEI/Brookings exchange into the design section as the named threat, with the SES
   pre-commitment stated before results. **Cost: two hours.**
3. Add the contract-price-confirmation finding to the benchmark-independence argument, and state
   plainly that the real-data benchmark class may contain fewer than two independent standards.
   **Cost: an hour, and it strengthens rather than weakens the contribution.**
4. ~~Pull the *Review of Finance* correction notice.~~ Done 2026-09-12 — see section 3; no
   erratum exists.
5. Add the Oct 2025 Urban brief and Howell & Korver-Glenn to the lit review. **Cost: an hour.**
6. Add selection-into-transaction and the welfare-sign paragraph. **Cost: two hours.**

Everything above is writing and reading. None of it requires the parcel data, which is the point —
these are the things that can be fixed before the data arrives, and each one is a place where a
prior researcher was confident and wrong.
