# Related work across fields

The problem of estimating error against a reference standard that cannot be
observed has been treated independently in several literatures. Notes on what
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
not reveal. That is an independent instance of the concern this package measures.

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
