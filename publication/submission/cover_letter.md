Dear Editor-in-Chief,

Please consider the manuscript "Observational Indistinguishability and
Integrity Blind Regions Across the Evidence Boundaries of Hybrid
Quantum-Classical Kernel Workflows" as a Regular Paper for *IEEE Transactions
on Dependable and Secure Computing*.

The protected asset is the integrity of the evidence and conclusions produced
by a hybrid workflow. The paper addresses a basic assurance failure: an
intervention can change a reported conclusion while every sensor available at
the audited boundary is structurally invariant, a separable change can remain
undetected because the auditor holds no trusted anchor, and a detected change
can become undetected once the attacker learns what the sensor sees. We
formalize auditability as observational indistinguishability under an
explicit information set and explicit trusted references, derive blind
regions that are monotone under refinement and closed exactly by added
evidence that separates the intervention class, and treat the
evaluation-label path as a protected boundary: for a fixed predictor,
label-only changes leave feature and prediction evidence invariant,
prior-preserving changes also leave label marginals invariant, and any change
of the reported balanced accuracy changes the confusion matrix, so a material
label corruption is always separable in the joint view; a trusted aggregate
reference of the same batch detects it exactly, and an item-aligned reference
is needed only for relabelings that preserve every aggregate. The quantum
branch is placed on the same lattice of views.

The contribution is the integrated combination of (i) the observation model
with its monotonicity, closure and materiality results and minimal
counterexamples, (ii) an explicit adversary and failure model including an
executed adaptive attacker, (iii) validation over CICIDS2017, UNSW-NB15 and
ToN-IoT in eight fixed ID/OOD environments (11,400 deduplicated observations)
under preregistered null calibration, (iv) a decision-level calibration by a
conformal family rule with an exact finite-sample level, which brings the
multi-sensor regimes with feature evidence to 0.053–0.058 against
0.125–0.259 for the union of per-sensor rules (the label-marginal regime
stays at 0.048), (v) an offline end-to-end allow/hold/block evaluation on
24,000 frozen observations whose primary endpoint is the number of materially
changed results a policy would serve (4,365–4,496 of 7,008 for batch-level
regimes with feature evidence, all 7,008 for the label-marginal regime, none
for the trusted item-aligned regime) and whose cost endpoint shows that the
trusted regime interrupts 52 % of benign near-null variation, (vi) a
preregistered adversarial gate in which an attacker who preserves the tight
feature clusters that the batch-level sensors rely on cuts their detection of
drift from 0.96–1.00 to 0.01–0.66 while keeping 83–91 % of the conclusion
changes, and (vii) a bounded quantum-specific layer with a four-contract
executable response.

This positioning fits TDSC's interest in foundations, methodologies,
monitoring and measurement, experimental evaluation, software validation and
dependable and secure emerging technologies. Prior work establishes
information-relative detectability for controlled dynamics, proxy monitoring
under delayed labels, contract-based integrity for quantum stages and
conformal calibration of anomaly scores; our distinction is deriving blind
regions from views of a learning workflow whose protected boundaries include
the evaluation labels, separating structural from statistical blindness
through explicit trusted references, and composing the coverage into a
decision whose false-alarm level, unsafe-allow count, benign-interruption cost
and adaptive residual are measured.

All three preregistered gate sets (artifacts 1.1.0, 1.2.0 and 1.3.0) were
frozen before execution and are reported as executed, including two
corrections found during the audits: the earlier "harm-only" endpoint had
folded 433 label corruptions that raise the reported metric into "zero
impact" (now reported with sign), and the family-calibration rule of the
previous version had a false finite-sample guarantee (now replaced by a
conformal rule whose level is exact under exchangeability, with the earlier
numbers retained as comparison columns and the decomposition of their excess
into rule bias and design effect).

Three companion manuscripts by the authors are disclosed in Section II-E and
listed on the title page. They share datasets, monitors or vocabulary with this
article but none of its propositions, interventions, tables or experiments.

We make no claim of quantum advantage, complete lifecycle security,
physical-QPU coverage, calibrated device-noise coverage, provider
authentication, scheduling security, multi-tenancy protection, deployed
runtime services, context-conditioned runtime calibration under
non-stationarity, or operational Fleet Management. Code, tests, derived
evidence, vector figures, seven SHA-256 evidence manifests and the
preregistrations accompany the manuscript and are archived at Zenodo
under the concept DOI 10.5281/zenodo.22550852 (version 1.3.0; the version DOI
is recorded in the artifact metadata).

The manuscript is original, is not under consideration elsewhere, and has been
approved by all authors. Author identities, affiliations, ORCIDs, CRediT
roles, funding, competing interests (none), artifact licensing and the
related-manuscript disclosure are recorded on the title page.

Sincerely,

Roberto Fernández-Barrios (corresponding author)

Faculty of Engineering, University of Deusto, Bilbao, Spain

roberto.fernandez.b@deusto.es
