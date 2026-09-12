# Paper 2 — Draft Limitations Prose

*September 12, 2026. Two subsections written to be dropped into the limitations or identification
section and then rewritten in the author's own voice. Citation placeholders marked `[cite]` must be
verified against the primary sources before use.*

---

## Selection into transaction

Any disparity estimate benchmarked against sale price is conditional on the property having sold.
This is not a peripheral caveat in the present setting, because the two regions being compared do
not transact at the same rate or for the same reasons. California's Proposition 13 caps the annual
growth of assessed value while a property remains in the same ownership and resets it to market at
transfer, creating a tax penalty for moving that rises with tenure. The resulting lock-in effect is
well documented [cite: Ferreira; Wasi & White] and is not distributed uniformly across Los Angeles
County: it binds hardest on long-tenured owners in appreciating submarkets, a description that fits
much of the San Gabriel Valley more closely than it fits South Los Angeles. The observed samples in
the two regions are therefore selected by different processes, and any measured differential in
valuation error confounds how homes are valued with which homes appear in the data at all.

The consequence is a standard sample-selection problem in the sense of Heckman (1979): the
estimating sample is drawn by a rule other than random sampling from the population of interest,
and the selection rule is plausibly correlated with the outcome. If, for example, homes that
transact in thinner or more distressed submarkets are systematically those whose characteristics
are least well captured by a hedonic specification, then a valuation model will appear less
accurate there for reasons that have nothing to do with the neighborhood's demographic composition.
The direction of the resulting bias is not signed a priori and depends on the correlation between
the unobservables driving selection and those driving valuation error.

This study does not attempt a formal correction. A selection model would require an exclusion
restriction — a determinant of the decision to transact that is credibly unrelated to valuation
error — and no such instrument is available in public parcel records. What is available, and what
is reported here, is a direct characterization of the selection margin: the distribution of tenure
length at time of sale in each region, the transaction rate per parcel-year, and the share of
recorded transfers that are arm's-length rather than intra-family, foreclosure, or trust
conveyances. Where these distributions diverge sharply between regions, the disparity estimate
should be read as descriptive of the transacting stock rather than of the housing stock, and that
restriction is stated wherever an estimate is reported. Reporting the selection margin is not a
substitute for correcting it, but it is the difference between a bounded claim and an
unacknowledged one.

---

## The direction of harm is not self-evident

A finding that valuation error is larger or more negative in some neighborhoods is often treated as
establishing harm to the residents of those neighborhoods. That inference requires an argument,
because a valuation error's welfare consequence depends on which side of a transaction the affected
party occupies.

For a seller, or for an owner seeking to refinance or to borrow against equity, an estimate below
market value is unambiguously costly: it reduces realizable proceeds, constrains loan-to-value, and
in the appraisal context triggers a reconsideration-of-value process whose burden falls on the
homeowner. For a purchaser, the same low estimate operates in the opposite direction. A valuation
below contract price provides leverage to renegotiate the price downward or to exit the contract,
and the empirical literature documents this channel directly, including estimates of the
information loss borne by borrowers who were not in a position to renegotiate [cite: Ding &
Nakamura; Fout & Yao]. Critics of the appraisal-bias literature have made precisely this point in
arguing that low appraisals carry a consumer benefit that disparity headlines omit [cite: AEI
Housing Center].

The resolution adopted here is to specify the affected party rather than to assume one. The
population of interest is existing owner-occupants, for whom the equity, refinancing, and
transfer-of-wealth channels dominate and for whom a downward valuation error is a cost. This is
also the population for which the low-turnover conditions described in the preceding subsection
bind most tightly: in neighborhoods where few homes transact in a given year, most residents
affected by a valuation model's behavior are owners rather than buyers, and the buyer-side offset
is correspondingly small. Where results bear on the purchase margin instead, that is noted and the
sign of the welfare interpretation is reversed accordingly. No aggregate welfare claim is made,
because netting the two channels would require the distribution of affected parties across both
sides of the market, which these data do not identify.

---

## Notes on the citations above

- **Heckman (1979)**, *Econometrica* 47(1), "Sample Selection Bias as a Specification Error" —
  verified; the standard reference for the framing used here.
- **Proposition 13 lock-in** — the effect is well established but the specific references above are
  placeholders. Ferreira (2010, *J. Public Economics*) and Wasi & White (2005, NBER) are the usual
  citations; confirm before use.
- **Ding & Nakamura; Fout & Yao** — both appear in Fannie Mae's literature review within *Contract
  Price Confirmation Bias: Evidence from Repeat Appraisals*. Pull the originals rather than citing
  them through that review.
- **AEI Housing Center** — the consumer-benefit-of-low-appraisals argument appears in the critique
  of Freddie Mac's appraisal-gap note. Cite the specific document, and characterize it as a critique
  in an ongoing dispute rather than as a settled result.
