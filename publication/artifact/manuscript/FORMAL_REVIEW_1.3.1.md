# Formal review of the 1.3.1 corrections — artifact 1.3.1 (evidence frozen at 1.3.0)

Date: 2026-09-07. Object: the four statements that `manuscript/FORMAL_CORE.md`
version 1.3 changes with respect to version 1.2, plus the two wordings whose
scope was corrected in the same release (the conformal claim in the executed
design and the semantics of policy P3). Standard, as in
`FORMAL_REVIEW_1.3.0.md`: for every item, hypotheses, claim, argument line by
line, an explicit counterexample search against the *new* formulation, and a
permanent test wherever the statement can be decided by enumeration or
arithmetic. Scope rule of the release: nothing else was re-audited; the
statements not listed here are those of `FORMAL_REVIEW_1.3.0.md` and stand
unchanged. No experiment, kernel, job, seed, model or draw was executed.

Permanent tests added: `tests/test_workflow_state.py` (intervention
recomputation semantics; finite-shot counterexample of Proposition 7(iii)) and
`tests/test_manuscript_consistency.py` (abstract length, superseded headline
strings, conformal and P3 wording, interruption decomposition).

## 1. Definitions: primitive versus derived artifacts

- Hypotheses: the workflow is a fixed directed acyclic graph with primitive
  nodes $(X, P, C, E, \xi, g, f, y)$ and derived nodes
  $\tilde X, K_{\mathrm{sem}}, \hat K, K_{\mathrm{obs}}, \hat y, R$ in the
  topological order of Section 1 of the formal core.
- Claim: every derived node is a function of its parents; the state is
  determined by its primitives; the descendant relation is well defined.
- Argument: the parent map of Section 1 (table) is acyclic by construction;
  `descendants()` follows the topological order.
- Counterexample search: a cycle (e.g. $f$ depending on $R$ through model
  selection) would break determinacy. Excluded by hypothesis: $f$ is a
  primitive (the fitted predictor is an input to the evaluation run). A
  "derived" node with hidden randomness not in $\xi$ would break
  reproducibility of recomputation; excluded because $\xi$ is the only
  randomness by definition and is retained on recomputation.
- Test: `test_descendant_closure_follows_the_declared_graph`.

## 2. State semantics: interventions, fixed sets and recomputation

- Version 1.2 said "$T_y$ changes $y$ item-wise and leaves every other
  component fixed" while $R$, a component of the state, is a function of $y$.
  That is inconsistent: either $R$ is not fixed or $R$ is not a function of
  $y$.
- New claim: an intervention overwrites a declared node set $O$, keeps every
  node outside $O \cup \mathrm{desc}(O)$ fixed, and recomputes
  $\mathrm{desc}(O)$ with $\xi$ retained. Then "fixes everything else" is
  well defined (every non-descendant) and $R$ follows $y$.
- Argument: for $T_y$, $O = \{y\}$, $\mathrm{desc} = \{R\}$; $\tilde X$,
  the kernels and $\hat y$ are non-descendants, hence fixed, which is exactly
  the hypothesis of Corollary 1(a) (fixed $f$, fixed $\tilde X$). For a
  feature attack, $O = \{\tilde X\}$ (or $\{X\}$), $\mathrm{desc} =
  \{\hat y, R\}$. For a circuit attack, $O = \{C\}$, $\mathrm{desc} =
  \{K_{\mathrm{sem}}, \hat K, K_{\mathrm{obs}}, \hat y, R\}$. For
  estimation variation, $O = \{\xi\}$ or $\{E\}$, $\mathrm{desc} = \{\hat K,
  K_{\mathrm{obs}}, \hat y, R\}$ with $K_{\mathrm{sem}}$ fixed. For
  post-processing, $O = \{g\}$ or $\{K_{\mathrm{obs}}\}$, $\mathrm{desc} =
  \{\hat y, R\}$ (plus $K_{\mathrm{obs}}$ when $g$ is overwritten) with
  $K_{\mathrm{sem}}$ and $\hat K$ fixed.
- Counterexample search: (i) overwriting a derived node and also one of its
  parents (mixed set) — allowed by the definition; the class is reported as
  `mixed` and no proposition applies to it, stated. (ii) An intervention that
  overwrites $\tilde X$ but leaves $X$ untouched creates a state that no
  honest run produces ($\tilde X \ne P(X)$): this is intended, it is what
  "attack on the representation" means, and Proposition 6 is the statement
  about verifiers that would recompute $\tilde X$ from $X$. (iii) Does
  Corollary 1 still follow? Yes: with $O = \{y\}$ the view $V_{I_{XF}}$
  depends only on non-descendants.
- Test: `InterventionSemanticsTests` (label-only recomputes only $R$;
  feature attack recomputes $\hat y, R$ and leaves $X$ and $K_{\mathrm{sem}}$;
  circuit attack changes all three kernels; estimation variation keeps
  $K_{\mathrm{sem}}$; post-processing keeps $K_{\mathrm{sem}}$ and $\hat K$;
  mixed and unknown sets are named).

## 3. Proposition 7: three kernels and class-indexed inclusions

- Version 1.2 used one symbol $K$ for the semantic kernel, the finite-shot
  estimate and the delivered matrix, and stated $B_h \subseteq B_K$ and
  $B_K \subseteq B_A$ without saying on which interventions. A PSD-preserving
  substitution of the delivered kernel does not change $C$, so $h(C)$ and
  $\Phi(C)$ are unchanged: the old text's "closed by the anchored comparison
  with $K_0$" was correct only because in the ideal-statevector gate the
  trusted probe and the delivered kernel have the same honest value, which
  the text did not say.
- New claim: (i) $B_h \subseteq B_{K_{\mathrm{sem}}}$ on class (a);
  (ii) $B_{K_{\mathrm{obs}}} \subseteq B_A$, $B_{K_{\mathrm{obs}}} \subseteq
  B_f$ on class (c), and a PSD-preserving substitution lies in
  $B_A \cap B_h \cap B_{K_{\mathrm{sem}}} \setminus B_{K_{\mathrm{obs}}}$;
  (iii) the finite-shot statement below; no inclusion across classes.
- Argument: (i) and (ii) are Proposition 1 applied to the maps
  $\Phi \circ h^{-1}$, $A$ and $f$, as before; the memberships in
  $B_h \cap B_{K_{\mathrm{sem}}}$ are the definition of class (c) (Section
  2 above).
- Counterexample search: could a class-(c) intervention change $h(C)$?
  Only if $C$ were a descendant of $g$ or $K_{\mathrm{obs}}$, which it is
  not. Could a class-(a) intervention leave $K_{\mathrm{obs}}$ unchanged
  while changing $K_{\mathrm{sem}}$? Yes if $g$ discards the information
  (e.g. $g$ constant); then $B_{K_{\mathrm{sem}}} \not\subseteq
  B_{K_{\mathrm{obs}}}$, which is why no inclusion between
  $K_{\mathrm{sem}}$ and $K_{\mathrm{obs}}$ is claimed. Could an approved
  rewrite change $K_{\mathrm{sem}}$? No, by definition of $[C]$.
- Test: `QuantumLatticeTests` (unchanged, on the frozen 165 cells:
  PSD-preserving rows have unchanged circuit hash, silent algebra and a
  firing anchored comparison; approved rewrites change the hash and not the
  kernel), plus `test_post_processing_substitution_changes_only_the_observed_kernel_branch`
  and `test_circuit_intervention_changes_semantic_estimated_and_observed_kernels`.

## 4. Proposition 7(iii): exact equality under finite-shot estimation

- Version 1.2 claimed $\Pr[\hat K = K_0] = 0$ for a non-degenerate estimator,
  hence false-alarm probability one for "fire iff $\hat K \ne K_0$". The
  argument ("for a continuous estimator") does not apply: a finite-shot
  fidelity estimate is discrete.
- Counterexample: $p = 1/2$, $N = 2$, $\hat p = X/2$ with
  $X \sim \mathrm{Binomial}(2, 1/2)$: $\Pr[\hat p = p] = \Pr[X = 1] = 1/2$,
  so the exact rule has false-alarm probability $1/2$, not one. Conversely
  $p = 1/3$, $N = 2$ gives zero mass at $p$ and false-alarm probability one;
  a degenerate entry gives zero.
- New claim: false-alarm probability
  $1 - \Pr[\hat K = K_{\mathrm{sem},0} \mid \text{honest}]$, which depends
  on the discrete support and may be large or equal to one but is not
  universally one. Consequences (unchanged in substance): exact equality is
  not an appropriate acceptance criterion; treat $d(\hat K,
  K_{\mathrm{sem},0})$ as a Level-A statistic with a null from repeated
  honest estimation; Proposition 5(b) applies when repeated and audited
  estimates are exchangeable; otherwise no statistical integrity claim.
- Argument: binomial mass function; independence across entries gives the
  product. The executed gate's 30/30 non-zero discrepancies are an empirical
  property of those cells (fidelities of a 64-row probe set at 256 and 1,024
  shots), not a law, and are now described as such in the article, the
  supplement, the formal core and `tests/test_formal_core.py`.
- Counterexample search against the new wording: is there a case where the
  new statement is false? It is an identity, so no; the only risk is
  over-reading "may be large or equal to one" as "is one", which the text
  avoids by giving the $1/2$ example.
- Test: `FiniteShotEqualityTests` (the $1/2$ counterexample; the value one
  off the support; zero for degenerate entries; exact binomial mass on the
  support for $N \in \{2, 4, 8, 16\}$; products over entries; the universal
  claim falsified on a grid).
- Regression guard: `test_prop7_never_claims_universal_false_alarm_one`
  forbids the strings "false-alarm probability one", "$\Pr[\hat K = K_0] =
  0$" and "never reproducing the exact kernel" in the article, the
  supplement, the formal core, the threat-model card and the adversary model.

## 5. Reference taxonomy

- Version 1.2 described Level A as "no stored value of the baseline view"
  and the article as "batch-level statistical evidence, with no stored
  baseline value". The experimental batch-level sensors do use stored
  references: the 200 calibration draws of each cell, the training-fitted
  projection and scaler, the null score distributions. The description was
  too strong.
- New taxonomy: Level A = statistical or historical reference (null
  distribution, training or reference population, calibration sample,
  baseline score distribution; no authenticated value of the same batch);
  Level B = trusted aggregate same-batch reference; Level C = trusted
  item-aligned same-batch reference. The distinction that carries
  Propositions 3–4 and Corollary 3 is between a statistical baseline and an
  authenticated same-batch anchor.
- Check that no proof depended on the old wording: Proposition 4(i) uses
  only that the decision is a function of the view (a Level-A auditor's
  decision is a function of the view and of the calibration sample, which
  is fixed across the baseline and the intervened state); Proposition 4(ii)
  and Corollary 3 use only that $\rho = V_J(s_0)$ is a trusted same-batch
  value (Levels B, C). Nothing changes.
- Counterexample search: a calibration sample that happens to contain the
  audited batch would be a same-batch value; excluded by the disjoint
  calibration/evaluation halves of Gate N (design fact, stated in the
  supplement).
- Test: `test_reference_taxonomy_is_named_consistently` (the wording is
  present in the article, the supplement and the formal core; the
  superseded "no stored baseline" wording is absent).

## 6. Conformal claim in the executed design

- Property: Proposition 5(b) gives finite-sample level
  $\lfloor \alpha(n+1) \rfloor/(n+1) \le \alpha$ under exchangeability of
  the $n+1$ draws. Executed design: overlapping draws within a pool half,
  calibration and evaluation halves that are different rows of one table, E1
  with one disjoint batch per half. The premise does not hold; the observed
  decision false-alarm rates are 0.056 / 0.058 / 0.048 / 0.053.
- Corrected wording everywhere (abstract, contributions, related work,
  results, conclusion, claims matrix, README, cover letter, highlights): the
  rule *has* finite-sample level $\le \alpha$ under exchangeability; *in the
  executed non-exchangeable design the observed rates are* 0.048–0.058. No
  text says or implies that the experiment is exactly calibrated.
- Counterexample search: any sentence with "exact level" lacking its
  premise. Enforced by `test_exact_level_is_always_tied_to_exchangeability`
  (every sentence containing "exact ... level" must contain "exchangeab" or
  "premise") and `test_no_exactly_calibrated_experiment`.

## 7. Policy P3: coverage-complete abstaining

- Version 1.2/1.3.0 called P3 "strict fail-closed / abstaining". Its rule is:
  hold iff a mandatory boundary has neither exact nor declared statistical
  coverage under the regime. The rule is silent about the power of the
  coverage that exists, so "fail-closed" invited the reading "P3 never
  serves an unsafe allow when a sensor exists", which is false: in
  $\mathcal I_{XFY}$ P3 coincides with P2 and serves 4,390 material
  observations.
- New name and definition: *coverage-complete abstaining* (fail-closed on
  missing coverage), with the explicit statement that P3 guarantees no
  minimum detection power and that low-power but nominally covered sensors
  remain a limitation of every policy; abstention conditioned on the
  validity of the calibration itself (out-of-support context) is outside
  this layer (Paper 2.5). Decisions and results are unchanged: the policy
  identifier `family_calibrated_strict` and every decision table are those
  of 1.3.0; only the `policy_class` label was regenerated.
- Test: `test_abstaining_policy_serves_a_nominally_covered_boundary_of_any_power`
  (P3 = P2 on covered regimes), `test_policy_taxonomy_is_declared`,
  `test_no_minimum_power_claim_for_p3` (no active document lets a sentence
  with "P3" and "guarantee" stand without the negation), the evidence-table
  check that `policy_class` carries the new name.

## 8. Interruption decomposition of the trusted regime

- 1.3.0 attributed "about half" of the benign interruption to exact
  provenance. The table `policy_metrics.csv` gives, for the trusted regime
  under the calibrated policy, 544 statistical holds and 85 exact-reference
  blocks, 629 of 1,200 in total (0.524); P2 already holds 590–654 of the
  same controls in the batch regimes.
- Corrected wording: total 629, holds 544, blocks 85; the exact anchor adds
  85 to a statistical cost the calibrated policy already pays; the controls
  are synthetic near-null variation, not operational benign traffic.
- Test: `test_trusted_interruption_decomposition_sums` (macros), the
  verifier's `policy_trusted_benign_*` counts (544, 85, 629) and
  `test_policy_metrics_are_internally_consistent`.

## Disposition

Every corrected statement has an argument that was re-derived, an explicit
counterexample search against its new formulation, and a permanent test. The
formal core of version 1.3 is consistent with the implementation
(`src/integrity/workflow_state.py`, `src/hsaas/policy.py`,
`src/integrity/family_calibration.py`) and with the frozen evidence. Stop
rule applied: no other statement was reopened, and no new "opportunity" is
recorded here; anything beyond these items belongs to Paper 2.5.
