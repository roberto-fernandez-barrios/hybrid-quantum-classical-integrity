# Adversary and failure model — Paper 1.5 (release 1.3.4; evidence frozen at 1.3.0)

Release 1.3.4 corrects bibliography, wording and frozen-derived coverage
metadata; this model and all scientific evidence remain unchanged from 1.3.2.
Version 1.3 (2026-09-08, artifact 1.3.2) audits the reference semantics:
Class-A selected sensors use statistical aggregate comparisons against a
benchmark-protected clean same-item-set oracle without item pairing or
demonstrated deployed authentication; B/C are trusted aggregate/item-aligned
exact invariants. Version 1.2 (2026-09-07, artifact 1.3.1: reference levels named, quantum
rows annotated with the intervention class of Proposition 7 and the
observed-kernel anchor, Q5 aligned with the corrected Proposition 7(iii);
version 1.1 of the same day for artifact 1.3.0; version 1.0 for 1.2.0).
Supersedes the "capabilities evaluated" list of `THREAT_MODEL_CARD.md` 1.0;
the card is kept as the short reference and points here. Every row below
corresponds to an intervention class that is actually executed in the frozen
evidence, except the row marked *realised, not executed as a suite*, which is
named because the formal core predicts it and the executed rows realise it by
chance. Rates quoted are those of the conformal family rule of artifact 1.3.0
(Gate F) unless stated.

## Reading rule

The study does not call every intervention an attack. Four classes are
distinguished and every experimental mechanism is assigned to one of them:

| Class | Meaning | Who or what causes it | What the study claims |
|---|---|---|---|
| **Fault robustness** | Benign or accidental change without intent | numerical variation, pipeline defect, drift of the data source | whether the sensors react and whether the conclusion moves |
| **Integrity corruption** | Non-adaptive change of an asset by a party that does not model the auditor | corrupted store, buggy transformation, careless relabeling, untrusted upstream | which information regime can separate it and at what calibrated rate |
| **Adversarial attack** | Targeted change of an asset to alter the reported conclusion | party with write access to one boundary | which regime and trusted root are needed for identification |
| **Adaptive attacker** | Targeted change designed with knowledge of the auditor's sensors | as above, plus knowledge of the monitored statistics | which invariant it preserves and which root closes it |

Interventions approximate mechanisms of a hybrid chain as follows: the
evaluation-label classes stand for corruption of the ground-truth store or
of the label join between evaluation items and outcomes; feature-side
classes stand for corruption or drift of the acquisition/preprocessing path
that feeds both the classical and the quantum branch; the cluster-preserving
class stands for an attacker who knows which batch-level fingerprint the
auditor relies on; circuit and kernel classes stand for corruption of the
circuit/parameter store, the compiler output or the post-estimation kernel;
shot emulation stands for legitimate estimation uncertainty. None is an
estimate of prevalence.

## Per-class model

Fields: actor/cause; class; capability; point of access (boundary of
`THREAT_MODEL_CARD.md`); knowledge; objective; budget; alterable assets;
trusted roots it cannot control; information set that can identify it; claim
actually supported by the frozen evidence.

### L1 — Random evaluation-label flip (`label_flip_r`, r ∈ {0.02, 0.05, 0.10})

- Actor/cause: careless or corrupted relabeling; a compromised ground-truth store; a broken label join. Class: integrity corruption (non-adaptive).
- Capability: rewrite the label of a fraction $r$ of evaluation items, chosen at random. Access: B8 evaluation/report. Knowledge: none of the auditor.
- Objective: none specific (corruption); effect is a change of the reported metric in either direction.
- Budget: $r$ of the batch. Alterable assets: $y$ only. Roots it cannot control: $X$, $P$, $C$, $K$, $f$, the training routine, and (when declared) an item-aligned authenticated copy $y^{\star}$ of the labels.
- Identifying information: none in $\mathcal I_X$ or $\mathcal I_{XF}$ (Corollary 1a, exact); $\mathcal I_{Y_m}$ only through the class-count change, which at these rates and $n=128/256$ stays inside the batch-to-batch null (calibrated detection 0.00–0.01); $\mathcal I_{XFY}$ batch-level only through the confusion profile (0.00–0.01); exact under $\mathcal I_{XFY}^{\star}$.
- Claim: structurally invisible to feature and prediction evidence; not detected at the nominal budget by marginal or batch-level joint evidence at these rates; identified exactly with an item-aligned trusted reference; 1,800 rows, 1,558 with a changed conclusion.

### L2 — Prior-preserving evaluation-label flip (`label_flip_prior_preserving`, r ∈ {0.02, 0.05, 0.10})

- Actor/cause: a party that knows the class prior is monitored and rewrites labels by pairwise swaps. Class: adaptive attacker (the marginal-preserving constraint is the adaptation).
- Capability: swap the labels of $r n / 2$ pairs of opposite-class items. Access: B8. Knowledge: that the auditor monitors label marginals; no knowledge of the predictor is needed.
- Objective: change the reported conclusion while leaving class counts invariant.
- Budget: $r$ of the batch. Alterable assets: $y$. Roots it cannot control: as L1, including $y^{\star}$ when declared.
- Identifying information: none in $\mathcal I_X$, $\mathcal I_{XF}$, $\mathcal I_{Y_m}$ (Corollary 1, exact; conformal rules fire 0/1,800); $\mathcal I_{XFY}$ batch-level 0.00–0.01; exact under $\mathcal I_{XFY}^{\star}$. Proposition 3: every material instance changes the confusion matrix; Corollary 2: no view factoring through $(\tilde X, \hat y, \mathrm{hist}(y))$ can separate it.
- Claim: the executed instance of the exact blind region of Propositions 1–2; 1,800 rows, 1,059 with a changed conclusion; closed by a trusted reference of the same batch (aggregate confusion reference for every material instance, Corollary 3a; item-aligned reference for aggregate-preserving swaps, Corollary 3b).

### L3 — Confusion-preserving relabeling (*realised, not executed as a suite*)

- Actor/cause: adaptive attacker who knows the confusion profile is monitored and swaps labels only between items with identical predictions. Class: adaptive attacker.
- Effect: invariant marginal, confusion matrix and conclusion; only item identity changes (counterexample C1). 808 of the executed random and prior-preserving flips realise this pattern by chance (witness W1 = W10).
- Decision (1.3.0, recorded in the preregistration before execution): not executed as a controlled suite, because it would reproduce C1 by construction and could change no conclusion: a trusted aggregate reference is exactly blind to it (Corollary 3b), an item-aligned reference detects it exactly, and every batch-level policy serves it as an immaterial row, which is not an unsafe allow.
- Claim: an item-identity violation with no aggregate or conclusion impact; visible only to an item-aligned reference; it is the reason item-identity, aggregate and conclusion integrity are reported as separate notions.

### F1 — Feature sign flip (`feature_sign_flip_p`, p ∈ {0.02, 0.05, 0.10})

- Actor/cause: corrupted feature store or transport; malicious tampering of evaluation features. Class: integrity corruption.
- Capability: negate a fraction $p$ of entries of $\tilde X$ (post-projection). Access: B1/B2 acquisition–preprocessing of evaluation data. Knowledge: none.
- Objective: none specific; may flip predictions and change the conclusion in either direction.
- Alterable assets: $\tilde X$ (and through $f$, $\hat y$ and $R$). Roots it cannot control: the training data and fitted model, the reference features when declared.
- Identifying information: distributional feature sensors in $\mathcal I_X$ (conformal detection 0.09/0.47/0.72 by strength); prediction sensors add power in $\mathcal I_{XF}$ (0.13/0.52/0.84); exact under item-aligned reference (0.79–0.91, where predictions change).
- Claim: partially separable at the batch level; the residual is strength-dependent; 1,800 rows, 1,464 with a changed conclusion, of which 685 are still served under $\mathcal I_{XF}$/P2.

### F2 — Feature-wise mean shift and scaling drift (`mean_shift_pf_delta`, `scaling_drift_alpha`)

- Actor/cause: sensor miscalibration, unit or scaling change, preprocessing drift. Class: fault robustness (benign drift) or non-adaptive corruption.
- Capability: additive shift or multiplicative scaling of all evaluation features. Access: B1/B2. Knowledge: none.
- Identifying information: the generated `AdvDetCtrlIXMin/Max` and `AdvDetCtrlHeadlineMin/Max` macros report the per-regime and two-regime matched-control ranges. This design-specific response is driven by tight clusters in the standardized projected features (69–87% of rows within 0.01 SD in some feature): an in-place perturbation smears the cluster, while a fresh clean batch reproduces it. Item-aligned prediction changes 0.36–0.67.
- Claim: detected in this design by a fragile fingerprint; the adaptive attacker F5 that preserves the clusters reduces response against that declared fingerprint (executed in 1.3.0). 3,600 rows, 1,848 with a changed conclusion, 6 served under $\mathcal I_{XF}$/P2.

### F3 — Feature dropout with median imputation (`feature_dropout_p`)

- Actor/cause: pipeline fault: features silently missing and imputed. Class: fault robustness / integrity corruption of the pipeline.
- Capability: replace a fraction $p$ of entries by the training median. Access: B2 preprocessing. Knowledge: none.
- Identifying information: nearly invisible to batch-level distributional sensors (0.00–0.03 conformal in $\mathcal I_{XF}$) because imputed values fall inside the clusters; prediction changes visible item-wise in 49–76% of cells.
- Claim: the executed instance of a material feature-side change that is separable in $\mathcal I_{XF}$ (predictions differ) yet statistically undetectable with a level-A (statistical) reference only; 1,800 rows, 1,079 with a changed conclusion, 1,057 served under $\mathcal I_{XF}$/P2.

### F4 — Near-null in-place variation (`sham_tiny_gaussian_sigma_0.001`, `sham_tiny_scaling_alpha_0.001`)

- Actor/cause: harmless numerical variation. Class: fault robustness (specificity control).
- Identifying information: the KS sensor reacts in 40–64% of cells (conformal rule) through the cluster fingerprint; predictions change in 4–10% of cells.
- Claim: a specificity cost of the cluster fingerprint, reported as the interruption rate of every policy and regime on these near-null synthetic controls (Gate D); not an attack and not operational benign traffic. The trusted same-batch regime under P2 interrupts 629/1,200. It produces 85 gross exact-reference blocks; 46 overlap the 590 batch `I_XFY`/P2 interruptions, so the net increase is 39/1,200 (3.25 percentage points).

### F5 — Cluster-preserving mean shift and scaling drift (`cluster_preserving_*`, executed in Gate A, artifact 1.3.0)

- Actor/cause: adaptive attacker who knows the batch-level sensor definitions and the cluster fingerprint and applies the drift mechanisms of F2 only to the entries outside the tight clusters. Class: adaptive attacker.
- Capability: on the audited batch, leave every entry untouched whose value is shared (within 0.01 batch standard deviations) by at least $\lceil 0.05 n \rceil$ rows, and apply the F2 mechanism to the remaining 32% of entries on average (16–47% by environment, branch and dimension). Access: B1/B2. Knowledge: the batch, the sensor definitions and the fingerprint; not the thresholds. Strengths 0.02, 0.05, 0.10 (matched to F2) and 0.25, 0.50.
- Objective: change the conclusion while keeping the feature distribution inside the between-batch null.
- Alterable assets: $\tilde X$ (and through $f$, $\hat y$ and $R$). Roots it cannot control: the training data and fitted model; the item-aligned prediction reference when declared.
- Identifying information: conformal detection at matched strengths is 0.01/0.08/0.34 (mean shift) and 0.05/0.35/0.56 (scaling) in $\mathcal I_X$, and 0.06/0.24/0.48 and 0.23/0.47/0.66 in $\mathcal I_{XF}$; the generated `AdvDetAdaptiveHeadlineMin/Max` and `AdvDetCtrlHeadlineMin/Max` macros provide the adaptive and matched-control headline ranges across those two feature-bearing regimes. Detection is 0.76–0.90 at 0.25–0.50 and exact under $\mathcal I_{XFY}^{\star}$ for every material row (a changed conclusion with fixed labels requires a changed prediction).
- Claim: a stress test of a fragile, cluster-dependent fingerprint—not defeat of a generally powerful drift detector. High matched-control response, near-null sensitivity and response reduction against the declared monitored fingerprint are consequences of the same cluster structure. Across 6,000 rows, 3,418 change conclusion (83–91% of F2's material fraction at matched strengths), of which P2 serves 1,328 / 959 / 1,006 in $\mathcal I_X$ / $\mathcal I_{XF}$ / $\mathcal I_{XFY}$ (F2 in the same runs: 0 / 6 / 10 of 1,848); the classical branch produces lower response than the quantum branch because its scaler moves the unclustered entries less relative to the null. Calibration controls false alarms; only a protected reference closes this region.

### Q1 — Data-dependent circuit-parameter mutation (`parameterized_rz_alpha` 0.02 / 0.10) and feature-map repetition change (class (a), circuit-side)

- Actor/cause: corrupted parameter store, compromised compilation output, malicious circuit substitution. Class: adversarial attack (targeted change of the quantum program).
- Capability: insert data-dependent RZ rotations or change the feature-map depth before execution. Access: B3/B4 circuit design and transpilation. Knowledge: the circuit interface.
- Objective: change the kernel semantics while producing a plausible circuit.
- Alterable assets: $C$ and hence $K_{\mathrm{sem}}$, $\hat K$, $K_{\mathrm{obs}}$, $\hat y$, $R$. Roots it cannot control: the canonical reference circuit hash and the trusted semantic probe $K_{\mathrm{sem},0} = \Phi(C_0)$.
- Identifying information: circuit hash and semantic probe comparison detect 15/15 cells; algebraic checks pass; output changes in 0/15, 2/15 and 11/15 cells.
- Claim: identified by reference-anchored provenance and semantics; invisible to output monitoring unless a decision boundary is crossed (Proposition 7(i)–(ii)).

### Q2 — Benign transpilation (level 1) and common-unitary rewrite (negative controls; class (a))

- Actor/cause: approved compiler pass. Class: fault robustness (approved equivalence).
- Identifying information: circuit hash changes in 15/15 cells; semantic kernel, algebra and outputs unchanged.
- Claim: separability in the provenance view is not harm; the policy needs the approved-equivalence class $[C_0]$ of Proposition 7(i). A hash mismatch is evidence for adjudication, not proof of harm.

### Q3 — Asymmetric and diagonal-eroded kernel edits (class (c), post-processing)

- Actor/cause: faulty aggregation or malicious post-processing of the estimated kernel. Class: integrity corruption (non-adaptive).
- Access: B6 kernel/post-processing. Alterable assets: $K_{\mathrm{obs}}$ after estimation ($C$, $K_{\mathrm{sem}}$ and $\hat K$ fixed). Roots: reference kernel, algebraic invariants.
- Identifying information: algebraic checks (symmetry, unit diagonal) detect 15/15; the circuit hash is unchanged; no prediction changes at the tested severity.
- Claim: detected by structural algebraic invariants of the observed kernel;
  no trusted same-batch anchor is needed for these malformed edits.

### Q4 — PSD-preserving kernel substitution (`kernel_psd_preserving_mix`; class (c))

- Actor/cause: adaptive attacker who knows that symmetry, diagonal and PSD are checked and substitutes a valid-looking kernel. Class: adaptive attacker.
- Access: B6. Alterable assets: $K_{\mathrm{obs}}$ ($C$, $K_{\mathrm{sem}}$ and $\hat K$ fixed). Roots it cannot control: the trusted reference on the observed kernel.
- Identifying information: algebraic checks are exactly blind in 15/15 cells; the circuit hash is unchanged in 15/15 (the circuit was not touched); the kernel hash and the anchored comparison of the delivered kernel against the trusted reference detect 15/15; output changes in 1/15.
- Claim: the executed instance of sensor-level blindness closed only by a trusted reference on $K_{\mathrm{obs}}$ itself; the semantic probe of the unchanged circuit cannot see it (Proposition 7(ii)). In the ideal-statevector gate the reference on $K_{\mathrm{obs}}$ and the semantic probe have the same honest value, which is why one anchored comparison against $\Phi(C_0)$ serves both roles there.

### Q5 — Binomial shot emulation (256 and 1,024 shots; class (b), estimation variation)

- Actor/cause: legitimate finite-shot estimation uncertainty. Class: fault robustness (approved stochastic execution).
- Identifying information: repeated-estimation discrepancy is non-zero in 15/15 cells of each condition (an empirical property of these cells, not a law); outputs change in 7/15 and 3/15 cells.
- Claim: the contract holds the result for adjudication rather than allowing or blocking it; Proposition 7(iii) states that exact equality with the ideal kernel is not an appropriate acceptance criterion under finite-shot estimation (its false-alarm probability is $1 - \Pr[\hat K = K_{\mathrm{sem},0} \mid \text{honest}]$, which depends on the discrete support and is not universally one) and that the discrepancy needs a calibrated null from repeated honest estimation; without one no statistical integrity claim is made. Not hardware or calibrated-noise evidence.

### E1 — Post-hoc modification of the audit envelope

- Actor/cause: a party that edits stored evidence after the decision. Class: adversarial attack on the record.
- Identifying information: the SHA-256 chain exposes any modification of a recorded contract (tamper-evident).
- Claim: tamper evidence only. A party controlling both the artifact and the verifier can replace the whole chain (Proposition 6): no identity, signature or non-repudiation is claimed.

## Trusted computing base and roots

The frozen evidence trusts: the local Python/Qiskit/scikit-learn runtime and
host; the training data and fitted model artifact; the reference input array
and preprocessing declaration; the reference circuit/kernel probes; SHA-256
collision resistance; the item-level label reference $y^{\star}$ *only where
the regime $\mathcal I_{XFY}^{\star}$ is declared*; the code that builds and
verifies the envelope. Every "exact" claim in the article is conditional on
the corresponding root being outside the intervention class.

## Explicitly outside this study (Paper 2.5 or other ATHENA components)

Compromise of the operating system, runtime or verifier; provider identity,
forged job or calibration metadata, key theft and real provider attestation;
malicious scheduler, physical mapping attacks and unapproved compiler passes
on real hardware; calibrated device noise, crosstalk, multi-tenant
interference and QPU faults; timing, power or network side channels and
circuit confidentiality; denial of service, availability, billing and access
control; adaptive attackers with a model of the sensors other than the
executed cluster-preserving one; the operational Fleet Management System;
attack prevalence.
