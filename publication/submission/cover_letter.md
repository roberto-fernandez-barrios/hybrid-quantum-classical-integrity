Dear Editor-in-Chief,

Please consider the manuscript "Observational Indistinguishability and
Integrity Blind Regions in Hybrid Quantum-Classical Workflows" as a Regular Paper for *IEEE Transactions
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
label corruption is always separable in the joint view. The constructive
result is the minimum evidence granularity relative to the integrity claim: a
trusted aggregate commitment of the same batch certifies the reported
conclusion, whereas item-identity integrity requires item alignment. This
does not assume away the attacked label store: it avoids duplicating labels
item-wise when only conclusion integrity is claimed, while proving that some
root outside the adversary's rewrite class is unavoidable. The selected
batch sensors use statistically thresholded aggregate comparisons against a
benchmark-protected clean same-item-set oracle without item pairing; this is
not deployed authentication. The quantum branch is placed on the same lattice
with semantic, estimated and observed kernels kept apart.

The contribution is the integrated combination of (i) the observation model
with its monotonicity, closure and materiality results and minimal
counterexamples, (ii) an explicit adversary and failure model including an
executed adaptive attacker, (iii) validation over CICIDS2017, UNSW-NB15 and
ToN-IoT in eight fixed ID/OOD environments (11,400 deduplicated observations)
under preregistered null calibration, (iv) a decision-level calibration by a
conformal family rule whose finite-sample level holds under exchangeability;
in the executed, non-exchangeable design its observed false-alarm rates are
0.053–0.058 for the multi-sensor regimes with feature evidence against
0.125–0.259 for the union of per-sensor rules (the label-marginal regime
stays at 0.048), (v) an offline end-to-end allow/hold/block evaluation on
24,000 policy rows derived from the frozen grid—where inferential independence
resides at environment/split clusters, not row level—whose primary endpoint
is materially altered audit results served (4,365–4,496 of 7,008 for batch-level
regimes with feature evidence, all 7,008 for the label-marginal regime, none
for the trusted item-aligned regime) and whose cost endpoint shows that the
trusted regime interrupts 629 of 1,200 near-null synthetic controls. It
produces 85 gross exact-reference blocks, 46 of which overlap batch
I_XFY/P2 interruptions, so the net increase is 39/1,200 (3.25 percentage
points), (vi) a
preregistered adversarial gate in which an attacker who preserves the tight
feature clusters that the batch-level sensors rely on cuts their detection of
drift from 0.96–1.00 to 0.01–0.66 while keeping 83–91 % of the conclusion
changes; aggregate material served rates are 0.39/0.28/0.29 for I_X/I_XF/I_XFY,
with the matched-strength I_XFY profile spanning 0.22–0.90, and (vii) a bounded ideal-statevector and finite-shot-emulation quantum layer with a four-contract
executable response.

This positioning fits TDSC's interest in foundations, methodologies,
monitoring and measurement, experimental evaluation, software validation and
dependable and secure emerging technologies. We do not claim priority for
observation-relative detectability, monitor-aware drift evasion, authenticated
evaluation artifacts, conformal multiple testing, quantum provenance or
hardware-backed quantum-stage contracts. Hinder et al. establish the generic
adaptive-drift premise; VAMP authenticates evaluation artifacts; Max-Rank
provides dependence-aware conformal family control; QProv, QCIVET and
QML-PipeGuard cover quantum provenance and, for the latter two, stronger
QPU/hardware and runtime evidence. Our complementary result is
claim-relative minimum evidence granularity: which view and trusted reference
suffice for conclusion, aggregate or item-identity integrity, and what remains
indistinguishable under weaker evidence. Gate A is a concrete preregistered,
cluster-preserving instance against the declared sensor fingerprint. The
internal CSV name `unsafe_allow` denotes corrupted audit/report conclusions
served; it does not mean that the NIDS allowed a malicious network event.

All three preregistered gate sets (artifacts 1.1.0, 1.2.0 and 1.3.0) were
frozen before execution and are reported as executed, including two
corrections found during the audits: the earlier "harm-only" endpoint had
folded 433 label corruptions that raise the reported metric into "zero
impact" (now reported with sign), and the family-calibration rule of the
previous version had a false finite-sample guarantee (now replaced by a
conformal rule whose level holds under exchangeability, with the earlier
numbers retained as comparison columns and the decomposition of their excess
into rule bias and design effect). A formal review (version 1.3.1)
corrected the finite-shot statement of the quantum proposition, the
workflow-state semantics and the reference taxonomy without touching the
evidence. Version 1.3.2 then audited every selected sensor and corrected the
epistemic taxonomy; only reference/cost/profile tables were derived from the
already frozen outputs, and no experiment was rerun. Version 1.3.3 is a
bibliographic/editorial correction only: it verifies and updates bibliography,
metadata and positioning and applies one readability pass. No experiment,
kernel, draw, model, seed, intervention, policy decision or scientific
evidence was rerun or changed; methodology is unchanged from 1.3.2.

Three companion manuscripts by the authors are disclosed in Section II-E and
listed on the title page: Paper 1 studies target-domain quantum-kernel
advantage/certification, Paper 2 conditional validity under benign
systematics/estimation uncertainty, and Paper 3 adaptive IDS
promotion/comparability. They share datasets, kernels or monitors with this
Paper 1.5, whose contribution is workflow integrity, observational
indistinguishability, evidence granularity and policy. Planned Paper 2.5 will
study longitudinal operational QPU/context assurance and will not reuse the
present experimental claim. Copies of related manuscripts can be supplied to
the editor on request.

We make no claim of quantum advantage, complete lifecycle security,
physical-QPU coverage, calibrated device-noise coverage, provider
authentication, scheduling security, multi-tenancy protection, deployed
runtime services, context-conditioned runtime calibration under
non-stationarity, or operational Fleet Management. Code, tests, derived
evidence, vector figures, eight SHA-256 evidence manifests and the
preregistrations accompany the manuscript and are archived under the concept DOI 10.5281/zenodo.22550852 (version 1.3.3; the version DOI
is recorded in the artifact metadata); the experimental evidence is frozen at version
1.3.0 (version DOI 10.5281/zenodo.22648573).

The manuscript is original, is not under consideration elsewhere, and has been
approved by all authors. Author identities, affiliations, ORCIDs, CRediT
roles, funding, competing interests (none), artifact licensing and the
related-manuscript disclosure are recorded on the title page.

Sincerely,

Roberto Fernández-Barrios (corresponding author)

Faculty of Engineering, University of Deusto, Bilbao, Spain

roberto.fernandez.b@deusto.es
