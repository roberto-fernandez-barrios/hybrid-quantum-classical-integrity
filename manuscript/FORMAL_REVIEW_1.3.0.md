# Formal review of the core statements — artifact 1.3.0

Date: 2026-09-07. Object: `manuscript/FORMAL_CORE.md` version 1.2 (Lemma 1,
Propositions 1–7, Corollaries 1–3, counterexamples C1–C9). Standard: for every
statement, list the hypotheses, state the claim, check the proof line by line,
search explicitly for counterexamples (randomized inputs, ties, degenerate
batches, finite-sample boundaries), and, wherever the statement can be decided
by enumeration on small finite instances, add a permanent test. "Reviewed and
looks correct" is not an accepted disposition; every row names the test or the
argument that closes it.

Permanent tests: `tests/test_formal_core.py` (Lemma 1, Propositions 1–4, 6,
7, Corollaries 1–3, the AUC remark) and
`tests/test_family_calibration_exhaustive.py` (Proposition 5, every weak
ordering with ties for small $n$ and one to three sensors, random tied
configurations with up to ten sensors, the five-vector counterexample to the
1.2.0 rule).

## Lemma 1 (structural blindness)

- Hypotheses: $s_a \sim_{\mathcal I} s_0$; sensor deterministic and admissible
  in $\mathcal I$, or randomized with the seed in the view; for a fresh
  independent seed, equality in distribution only.
- Claim: $S(s_a) = S(s_0)$ (pointwise), or in distribution.
- Proof: function evaluated on identical arguments. Correct.
- Counterexample search: a sensor that reads anything outside the view
  (e.g. a wall-clock timestamp or the reference labels) is not admissible;
  the statement is about admissible sensors only. A randomized sensor with a
  fresh seed can differ pointwise; stated.
- Edge cases: empty batch (views equal trivially). Randomized sensors covered.
- Test: `test_lemma1_prop1_monotonicity_and_corollary1` (Counter-based views on
  enumerated label vectors).

## Proposition 1 (monotonicity under refinement)

- Hypotheses: $V_{\mathcal I} = \pi \circ V_{\mathcal I'}$.
- Claim: $B_{\mathcal I'} \subseteq B_{\mathcal I}$, $G_{\mathcal I'} \subseteq G_{\mathcal I}$.
- Proof: apply $\pi$. Correct; the direction is the one that could not be
  reversed ($\pi$ need not be injective).
- Counterexample search: a non-injective $\pi$ (histogram of labels from the
  multiset of triples) — inclusion still holds; a pair of views with no
  refinement relation ($\mathcal I_{Y_m}$ versus $\mathcal I_X$) — not
  covered by the statement and not claimed.
- Boundary: the remark that calibrated power is not monotone (more sensors,
  higher union false-alarm rate) is a statement about sensors, not views.
- Test: `test_lemma1_prop1_monotonicity_and_corollary1` checks all five
  refinement pairs on every enumerated intervention.

## Corollary 1 (label-path boundaries)

- Hypotheses: $f$ fixed and deterministic (necessary: a stochastic predictor
  could change $\hat y$ without a label change).
- Claim: label-only changes are blind to $\mathcal I_X$ and $\mathcal I_{XF}$;
  prior-preserving ones also to $\mathcal I_{Y_m}$.
- Proof: definition of the classes plus Lemma 1. Correct.
- Test: same test, asserting both parts on every enumerated label vector.

## Proposition 2 (closing a blind region) and Corollary 2

- Hypotheses: none beyond the definitions; Corollary 2 needs $f$ fixed.
- Claim: $B_{\mathcal I \vee \mathcal W} = B_{\mathcal I} \cap B_{\mathcal W}$;
  complete separability iff $\mathcal W$ is baseline-separating on the orbit.
- Proof: a pair is equal iff both components are. Correct; the earlier
  "injective on the orbit" wording (1.2.0 draft) was replaced by
  baseline-separating, which is the exact condition.
- Counterexample search for Corollary 2: duplicated rows. Two states with
  identical $(\tilde x_i, \hat y_i)_i$ have the same multiset of triples iff
  the label vectors differ by a permutation within groups of identical
  $(\tilde x, \hat y)$; the test enumerates batches with duplicated rows and
  checks the iff in both directions.
- Test: `test_prop2_closure_and_corollary2`.

## Proposition 3 (materiality forces aggregate separability) and the metric remark

- Hypotheses: $R = g(M)$; $a \in T_y$.
- Claim: $\Delta_R \ne 0 \Rightarrow M(s_a) \ne M(s_0)$; hence separable in
  the confusion view and in $\mathcal I_{XFY}$.
- Proof: contrapositive. Correct. The hypothesis is essential: the test
  exhibits two label vectors with the same confusion matrix and different
  ROC-AUC, so the statement is false for AUC with $M$ as the aggregate, and
  true again with the score-label multiset as the aggregate (the remark).
- Edge cases: degenerate batches with one class (balanced accuracy defined
  with the 0/0 convention); the implication is unaffected because it only
  uses $M$ equal $\Rightarrow$ $g(M)$ equal.
- Tests: `test_prop3_materiality_forces_confusion_change_for_confusion_metrics`
  (balanced accuracy, accuracy, $F_1$),
  `test_prop3_remark_auc_is_not_a_function_of_the_confusion_matrix`.

## Proposition 4 (separability necessary; anchoring sufficient) and Corollary 3

- Hypotheses: (i) decision is a function of the view (seed in the view); (ii)
  metric $d$ with $d = 0$ iff equal; reference trusted (unaltered).
- Claim: (i) blind interventions produce the clean decision; (ii)
  reference-anchored detection is exact.
- Proof: Lemma 1 and the definition of a metric. Correct. A pseudo-metric
  would break (ii); stated.
- Corollary 3: (a) needs Proposition 3; (b) is the swap computation. The
  proof of (b) was re-derived: the two moves cancel in every cell of $M$ and
  in the histogram. Correct.
- Counterexample search: references finer than $M$ but still
  permutation-invariant within equal-prediction groups (per-class score
  histograms) remain blind to C1; the statement is restricted to references
  that factor through $M$, $\mathrm{hist}$ or $R$, so no overclaim.
- Tests: `test_corollary3_which_reference_certifies_which_integrity`,
  `test_prop4_reference_anchoring_is_exact`.

## Proposition 5 (union versus family calibration) — replaced in 1.3.0

- (a) Union bounds. Hypotheses: $p_j \le \alpha$. Claim:
  $\max_j p_j \le P(\cup) \le \min(1, \sum p_j)$; attainment by nested and
  disjoint events; independence formula. Proof: Boole. Correct. (The 1.2.0
  draft before the final review had claimed the upper bound under
  independence; corrected then.)
- (b) Adopted conformal rule. Hypotheses: exchangeability of the $n+1$ sensor
  vectors; ties counted against firing. Claim: deterministic counting bound
  $\#\{j : N_j \le k\} \le k$ for $k = \lfloor \alpha(n+1) \rfloor$, hence
  $P(\text{fire}) \le k/(n+1) \le \alpha$; equality for distinct scores;
  single-sensor coincidence with the 1.1.0 rule. Proof re-derived line by
  line: the score map is permutation-equivariant because each score depends
  on its own vector and the multiset of the others; the counting bound is
  the pigeonhole argument on the smallest score among $k+1$ candidates.
  Correct.
- Counterexample search for (b): every weak ordering (all tie patterns) of
  $n+1 \in \{3,\dots,7\}$ elements with one sensor, of $n+1 \in \{3,4,5\}$
  with two sensors (292,681 configurations at $n+1 = 5$), of $n+1 = 4$ with
  three sensors (421,875 configurations), random tied configurations with up
  to ten sensors and $n+1$ up to 21, at six levels of $\alpha$ including
  values where $\alpha(n+1)$ is an integer. No configuration violates the
  counting bound. Monte Carlo with dependent continuous sensors ($m = 10$,
  $n = 200$) at 0.05: within sampling error of the level.
- Finite-sample boundary: when $\alpha (n+1)$ is an integer the level equals
  $\alpha$ exactly for distinct scores (e.g. $\alpha = 0.2$, $n = 4$); when it
  is not, the level is strictly below $\alpha$ ($10/201$ at $0.05$, $n = 200$).
- What is not claimed: a conditional guarantee given the calibration set;
  independence of the audited draws of one cell; validity when the
  exchangeability premise fails (the executed design). All stated in (b)(iv).
- (c) The 1.2.0 rule. The five-vector configuration is enumerated in the
  test and fires for 3 of 5 audited members (0.60 > 0.40 > 0.20); random
  search over small tied configurations finds further violations of the
  published bound. On the frozen null draws the exchangeable re-splits show
  the 1.2.0 rule above $\alpha$ in $\mathcal I_X$, $\mathcal I_{XF}$ and
  $\mathcal I_{XFY}$ and the conformal rule below its level in every regime
  (`family_resplit_pooled.csv`; acceptance check F4).
- Tests: the whole of `tests/test_family_calibration_exhaustive.py` and the
  single-sensor and level tests in `tests/test_policy_layer.py`.

## Proposition 6 (no local authentication without an uncontrolled root)

- Hypotheses: honest completeness; joint control over the asset and every
  reference in the bundle.
- Claim: the substituted pair is accepted and is observationally an honest
  run of $s'$; a bundle component the class cannot write rejects every
  substitution it separates.
- Proof: acceptance is a function of the input, which equals an honest input.
  Correct. The proposition is about authenticity, not consistency; a
  verifier with a stored baseline value is excluded by the joint-control
  hypothesis and handled by the converse.
- Counterexample search: a verifier that rejects some honest states violates
  honest completeness (excluded); a verifier with access to an external
  channel violates the "nothing else" hypothesis (excluded and named).
- Test: `test_prop6_local_verifier_accepts_a_jointly_controlled_substitution`
  builds an honest-complete verifier on the confusion matrix, substitutes the
  asset and the reference jointly, and checks acceptance together with
  rejection by an uncontrolled root.

## Proposition 7 (the quantum lattice) — new in 1.3.0

- Hypotheses: collision-free hash on the circuits under study; $\Phi$ the
  semantic kernel map on a fixed probe set; $A$ and $f$ functions of $K$;
  $\hat K$ a non-degenerate estimator.
- Claim: (i) provenance refines semantics, approved rewrites lie in
  $B_K \setminus B_h$; (ii) algebra and outputs coarsen the kernel, the
  PSD-preserving substitution lies in $B_A \setminus B_K$; (iii) under shot
  noise the exact anchor has false-alarm probability one and must be
  replaced by a calibrated Level-A test, to which Proposition 5(b) applies.
- Proof: (i) and (ii) are Proposition 1 applied to the maps $\Phi \circ h^{-1}$,
  $A$ and $f$; the strictness statements are existence claims witnessed in
  the frozen gate; (iii) is the definition of a continuous estimator.
  Correct. No quantum mechanics enters; the proposition organises the
  quantum sensors on the lattice and names the two features that the
  classical branches lack.
- Counterexample search: a hash that is not canonical (whitespace
  differences) would make identical circuits hash differently — the
  provenance view would then be finer than the circuit, still refining
  semantics; a probe set on which two different circuits induce identical
  kernels makes $[C]$ larger than the intended class — the auditor's
  approved class is defined relative to the probe set, stated.
- Test: `QuantumLatticeTests` on the frozen 165-cell evidence: approved
  transpilation changes the hash and never the kernel; rows without a hash
  change on the circuit side have zero semantic delta; the PSD-preserving
  substitution changes the kernel with silent algebraic sensors; no row with
  an unchanged kernel changes a prediction; every finite-shot row has a
  non-zero repeated-estimation discrepancy.

## Counterexamples C1–C9

C1–C8 are minimal constructions; their witness counts are generated from
`counterexample_witnesses.csv` and checked by the verifier (W8 as an
acceptance check). C9 (cluster-preserving drift) is not a structural blind
region but the executed instance of sensor insufficiency against an adaptive
attacker; its measurements are Gate A. The distinction is stated in Section 5
of the formal core so that no reader takes C9 for a theorem.

## Disposition

Every statement of the formal core has a proof that was re-derived, an
explicit counterexample search, and, where decidable by enumeration, a
permanent test. Proposition 5(b) of artifact 1.2.0 was false and is replaced;
no other statement required weakening. Residual limits are those stated in
Section 7 of the formal core.
