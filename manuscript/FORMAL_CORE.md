# Formal core — observational indistinguishability and integrity blind regions (release 1.3.6; scientific evidence frozen)

Release 1.3.6 corrects Proposition 4(i) to the pathwise equality supported by
Lemma 1 and repairs the omitted $K_{\mathrm{obs}}$ dependency in the proof of
Corollary 1(a). It also makes the $R_0$/$M_0$/item-aligned reference
granularity explicitly claim-relative. No other theorem is changed and no
scientific evidence is re-executed or modified. The model retains separate
primitive and derived artifacts, distinct semantic, estimated and observed
kernels, provenance/granularity/decision reference dimensions, and the exact
exchangeability premise of the conformal family rule. This document is the complete
statement, with proofs, of the formal section of the TDSC article. The
article prints the definitions and the propositions; the supplement
reproduces the proofs. Every witness count quoted here is generated from the
manifested table `counterexample_witnesses.csv` (Gate D) and printed in the
article through `publication/tdsc/tables/policy_macros.tex`. The
formal statements are guarded by the finite-state enumerations in
`tests/test_formal_core.py`, the exhaustive family-calibration tests, and the
workflow-state counterexamples in `tests/test_workflow_state.py`. The
executable counterpart of Section 1 is `src/integrity/workflow_state.py`.

The formal contribution makes exact which evidence separates which class of
intervention, so that the empirical gates test statements rather than
intuitions. Every statement below is pointwise
(for a fixed baseline state and a fixed finite batch) unless it says
"in distribution" or names a probability.

## 1. Objects

**States.** A workflow state separates the artifacts that are *stored* from
those the workflow *derives* from them. The primitive artifacts of one
evaluation run are $s = (X, P, C, E, \xi, g, f, y) \in \mathcal S$: acquired
features $X$, preprocessing $P$, circuit/feature map $C$, execution context
$E$ (shots, backend, declared metadata), estimation randomness $\xi$,
post-processing map $g$, fitted predictor $f$ and evaluation labels $y$. The
derived artifacts are recomputed from the primitives by the workflow:

| Derived artifact | Definition | Parents |
|---|---|---|
| $\tilde X = P(X)$ | evaluation representation | $P, X$ |
| $K_{\mathrm{sem}} = \Phi(C)$ | ideal semantic kernel induced by the circuit on a fixed probe set | $C$ |
| $\hat K = \mathrm{est}(K_{\mathrm{sem}}, E, \xi)$ | finite-shot estimate produced by execution | $K_{\mathrm{sem}}, E, \xi$ |
| $K_{\mathrm{obs}} = g(\hat K)$ | kernel object delivered to downstream processing after estimation, transmission and post-processing | $g, \hat K$ |
| $\hat y = f(\tilde X, K_{\mathrm{obs}})$ | predictions, indexed by item identity $i = 1, \dots, n$ | $f, \tilde X, K_{\mathrm{obs}}$ |
| $R = r(\hat y, y)$ | reported result (balanced accuracy) | $\hat y, y$ |

In the classical branch $f$ ignores $K_{\mathrm{obs}}$; in the
ideal-statevector gates $\mathrm{est}$ is the identity in law and $g$ is the
identity, so $K_{\mathrm{obs}} = \hat K = K_{\mathrm{sem}}$ on the honest path.

**Interventions.** An intervention $a$ *overwrites* a declared set of nodes
(primitive or derived), *keeps fixed* every node that is not a descendant of an
overwritten node, and *recomputes* the descendants of the overwritten nodes
through the workflow with $\xi$ retained (a stochastic descendant is
recomputed with the same randomness unless $\xi$ itself is overwritten). The
baseline state is $s_0$, the intervened state $s_a = a(s_0)$; an intervention
class $\mathcal A$ is a set of such maps. "Fixes everything else" therefore
means "fixes every non-descendant"; a derived node such as $R$ follows its
parents. Classes used in the study and what each recomputes:

- $T_y$ (label-only): overwrites $y$ item-wise; $\tilde X$, the kernels and
  $\hat y$ are fixed, $R$ is recomputed. $T_y^{\pi} \subset T_y$
  (prior-preserving) additionally preserves the class histogram of $y$.
- Feature-side mechanisms (sign flip, mean shift, scaling drift, dropout with
  imputation and, in the frozen experiment, the adaptive cluster-preserving
  variants): overwrite $\tilde X$ (or its upstream source $X$); $\hat y$ and
  $R$ are recomputed.
- Circuit-side interventions (class (a) of Section 6): overwrite $C$;
  $K_{\mathrm{sem}}$, $\hat K$, $K_{\mathrm{obs}}$, $\hat y$ and $R$ are
  recomputed.
- Estimation/execution variation (class (b)): overwrite $\xi$ or $E$; $C$ and
  $K_{\mathrm{sem}}$ are fixed, $\hat K$ and its descendants are recomputed.
- Post-processing / kernel substitution (class (c)): overwrite $g$ or
  $K_{\mathrm{obs}}$ directly; $C$, $K_{\mathrm{sem}}$ and $\hat K$ are fixed,
  $\hat y$ and $R$ are recomputed.

`src/integrity/workflow_state.py` implements these semantics
(`State.intervene`, `descendants`, `intervention_class`) and
`tests/test_workflow_state.py` checks them.

**Conclusion and materiality.** The conclusion functional is
$R : \mathcal S \to \mathbb R$, here balanced accuracy of $\hat y$ against $y$,
which is a function $R = g(M)$ of the confusion matrix
$M(s) = (\#\{i : \hat y_i = u, y_i = v\})_{u,v}$. The signed conclusion change
is $\Delta_R(a) = R(s_0) - R(s_a)$. An intervention is *material at level*
$\tau$ if $|\Delta_R(a)| \ge \tau$; $\tau \to 0^{+}$ is the
*structural-sensitivity endpoint* ("any change of the reported conclusion"),
not a claim that every epsilon has the same operational consequence. The
fixed $\tau=0.02$ and $0.05$ analyses are larger-effect sensitivities. The
positive part $\max(\Delta_R, 0)$ is the "harm"
endpoint of artifacts 1.0.0–1.1.1; the signed definition is used from 1.2.0
because an apparent improvement caused by an integrity failure is a
conclusion change (witness W7).

**Three integrity notions.** For a label-path intervention $a$,
*item-identity integrity* holds if $y_a = y_0$ item-wise; *aggregate (joint)
integrity* holds if $M(s_a) = M(s_0)$; *conclusion integrity* holds if
$R(s_a) = R(s_0)$. Item-identity integrity implies aggregate integrity, which
implies conclusion integrity; neither converse holds (C1 and C4 below).

## 2. Information sets, views and references

**Views.** An information set $\mathcal I$ is a view map
$V_{\mathcal I} : \mathcal S \to \mathcal O_{\mathcal I}$ onto an observation
space. The auditor in regime $\mathcal I$ observes $V_{\mathcal I}(s)$ and
nothing else. The regimes of the study are

| Regime | View $V(s)$ |
|---|---|
| $\mathcal I_X$ | $\tilde X$ as a multiset of rows |
| $\mathcal I_{XF}$ | $\{(\tilde x_i, \hat y_i)\}$ as a multiset (features with scores/predictions) |
| $\mathcal I_{Y_m}$ | $\mathrm{hist}(y)$, the class-count vector |
| $\mathcal I_{XFY}$ | $\{(\tilde x_i, \hat y_i, y_i)\}$ as a multiset of triples |
| $\mathcal I_Q$ | $(C, K, E)$: circuit, kernel and execution evidence |

**Refinement.** $\mathcal I \sqsubseteq \mathcal I'$ ("$\mathcal I'$ refines
$\mathcal I$") iff there is a map $\pi$ with
$V_{\mathcal I} = \pi \circ V_{\mathcal I'}$. Then
$\mathcal I_X \sqsubseteq \mathcal I_{XF} \sqsubseteq \mathcal I_{XFY}$ and
$\mathcal I_{Y_m} \sqsubseteq \mathcal I_{XFY}$; $\mathcal I_{Y_m}$ is not
comparable with $\mathcal I_X$ or $\mathcal I_{XF}$, and $\mathcal I_Q$ is a
separate branch. The join $\mathcal I \vee \mathcal W$ of two views is the
pair $(V_{\mathcal I}, V_{\mathcal W})$.

**References and their three axes.** A reference is stored information
about the baseline against which the audited batch is compared. It is
*trusted* under assumption $\mathsf T(\rho)$: no intervention in the class
under study can alter it (it is authenticated, or held by a party outside the
adversary's reach). We keep three dimensions explicit:

- **Provenance:** historical, benchmark-protected, or deployed authenticated.
- **Granularity:** aggregate or item-aligned.
- **Decision:** statistical (calibrated tolerance) or exact (zero invariant).

The A/B/C names are compact reference classes, not a one-dimensional scale
that conflates these dimensions:

- **Level A, statistically thresholded aggregate comparison.** Its reference
  may be historical or may be a clean version of the same item set. In the
  executed benchmark, the selected feature, prediction, label-marginal and
  confusion-profile sensors compare aggregate current values with
  benchmark-protected clean arrays for the same item set, without using item
  correspondence; thresholds come from 200 calibration draws per cell. The
  benchmark oracle is outside the executed attack API, but no deployed
  authentication or delivery mechanism is demonstrated. Only the three raw
  feature distribution variants also have a training-population reference;
  there is no complete, prespecified historical counterpart for
  $\mathcal I_{XF}$, $\mathcal I_{Y_m}$ and $\mathcal I_{XFY}$.
- **Level B, trusted aggregate same-batch reference.** A stored, uncontrolled
  value $\rho = V_{\mathcal J}(s_0)$ of a permutation-invariant aggregate of
  the *same batch*, such as $M(s_0)$, $\mathrm{hist}(y_0)$ or $R(s_0)$.
  Comparison against it has an exact-zero null.
- **Level C, trusted item-aligned same-batch reference.** A stored,
  uncontrolled item-indexed tuple of the same items, such as $(y_{0,i})_i$ or
  $(\hat y_{0,i})_i$; comparison is item-wise with an exact-zero null.

The distinction that carries the results is between statistical aggregate
comparison without demonstrated deployed authentication (Level A) and an
authenticated same-batch exact anchor (Levels B and C), then between
aggregate and item-aligned integrity. We write
$\mathcal I^{\star}$ for a regime augmented with same-batch references of its
own baseline view; $\mathcal I_{XFY}^{\star}$ in the evidence holds both the
aggregate confusion profile (Level B) and the item-aligned labels and
predictions (Level C) of the same batch. A label being *available* in
$\mathcal I_{XFY}$ says nothing about whether it is *trusted*: if the label
store is the asset under attack, the auditor sees $y_a$, not $y_0$.

The runtime policy API consumes only union/family firing flags and an exact
reference flag; it never consumes $X_{te}$, $y_{te}$ or the clean item set
directly. Those arrays are required upstream to produce the executed Level-A
scores. Thus “experimental oracle used to measure a statistic” and “trusted
evidence available to a deployed auditor” are different claims.

## 3. Observational equivalence, sensors and blind regions

**Definition 1 (observational equivalence).** $s \sim_{\mathcal I} s'$ iff
$V_{\mathcal I}(s) = V_{\mathcal I}(s')$.

**Definition 2 (sensor).** A sensor admissible in $\mathcal I$ is a measurable
map $S : \mathcal O_{\mathcal I} \to \mathbb R^k$; we write
$S(s) = S(V_{\mathcal I}(s))$. A sensor family $\mathcal S$ is a set of
admissible sensors.

**Lemma 1 (structural blindness).** If $s_a \sim_{\mathcal I} s_0$ then
$S(s_a) = S(s_0)$ for every deterministic sensor admissible in $\mathcal I$,
and for every randomized sensor whose seed is part of the view. For a
randomized sensor with a fresh seed drawn independently of the state,
$S(s_a)$ and $S(s_0)$ are equal in distribution.

*Proof.* $S(s_a) = S(V_{\mathcal I}(s_a)) = S(V_{\mathcal I}(s_0)) = S(s_0)$:
a function evaluated on identical arguments. With a fresh independent seed
$\xi$, $S(V_{\mathcal I}(s_a), \xi)$ and $S(V_{\mathcal I}(s_0), \xi)$ are the
same function of the same random variable. $\square$

**Definition 3 (blind regions and separation).** For a class $\mathcal A$ and
baseline $s_0$, the *structural blind region* of $\mathcal I$ is
$$B_{\mathcal I}(\mathcal A) = \{ a \in \mathcal A : a(s_0) \sim_{\mathcal I} s_0 \},$$
and the *sensor blind region* of a family $\mathcal S$ is
$$B_{\mathcal I, \mathcal S}(\mathcal A) = \{ a \in \mathcal A : S(a(s_0)) = S(s_0)\ \forall S \in \mathcal S \}.$$
A view or sensor family is *baseline-separating on the orbit of $\mathcal A$*
if it takes a different value at $a(s_0)$ than at $s_0$ for every
$a \in \mathcal A \setminus B_{\mathcal I}(\mathcal A)$ (respectively, for
every $a \in \mathcal A$ whose view differs); it is *pairwise-separating* if
it also takes different values at $a(s_0)$ and $a'(s_0)$ whenever those
states differ. Baseline separation is what detection needs; pairwise
separation (injectivity on the orbit) is what *identification* of which
intervention occurred needs. Only baseline separation is used below.

By Lemma 1, $B_{\mathcal I}(\mathcal A) \subseteq B_{\mathcal I,\mathcal S}(\mathcal A)$,
with equality iff $\mathcal S$ is baseline-separating on the orbit of
$\mathcal A$ in $\mathcal I$; such a family is *sufficient* for $\mathcal A$
in $\mathcal I$. Sensor blindness therefore decomposes into information-level
blindness (the view is identical) and sensor insufficiency (the view differs
but the statistic does not).

**Definition 4 (auditability gaps).** The *structural gap* at level $\tau$ is
$G_{\mathcal I}(\tau) = \{ a \in \mathcal A : |\Delta_R(a)| \ge \tau,\ a \in B_{\mathcal I}(\mathcal A) \}$
and the *sensor gap* is $G_{\mathcal I,\mathcal S}(\tau)$ defined with
$B_{\mathcal I,\mathcal S}$. The gap of artifact 1.1.x (equation (4) of that
version) is the sensor gap; $G_{\mathcal I}(\tau) \subseteq G_{\mathcal I,\mathcal S}(\tau)$
for every family $\mathcal S$.

**Proposition 1 (monotonicity under refinement).** If
$\mathcal I \sqsubseteq \mathcal I'$ then
$\sim_{\mathcal I'} \subseteq \sim_{\mathcal I}$,
$B_{\mathcal I'}(\mathcal A) \subseteq B_{\mathcal I}(\mathcal A)$ and
$G_{\mathcal I'}(\tau) \subseteq G_{\mathcal I}(\tau)$ for every $\tau$.
Adding evidence never enlarges a structural blind region.

*Proof.* If $V_{\mathcal I'}(s_a) = V_{\mathcal I'}(s_0)$ then
$V_{\mathcal I}(s_a) = \pi(V_{\mathcal I'}(s_a)) = \pi(V_{\mathcal I'}(s_0)) = V_{\mathcal I}(s_0)$.
The inclusions follow; membership in the gap adds only the materiality
condition, which does not depend on the view. $\square$

The monotonicity is structural only. At a fixed false-alarm budget the
calibrated power of a sensor family is not monotone in the information set
(Proposition 5): joining more sensors raises both power and the false-alarm
rate unless the family is recalibrated.

**Corollary 1 (the 1.1.x propositions as instances).** Let $f$ be fixed and
deterministic. (a) For every $a \in T_y$, $V_{\mathcal I_{XF}}(s_a) = V_{\mathcal I_{XF}}(s_0)$,
hence $T_y \subseteq B_{\mathcal I_{XF}} \subseteq B_{\mathcal I_X}$ and every
sensor admissible in $\mathcal I_X$ or $\mathcal I_{XF}$ is invariant
(Proposition 1 of 1.1.x). (b) For every $a \in T_y^{\pi}$,
$\mathrm{hist}(y_a) = \mathrm{hist}(y_0)$, hence
$T_y^{\pi} \subseteq B_{\mathcal I_{Y_m}}$ and every sensor admissible in
$\mathcal I_{Y_m}$ is invariant (Proposition 2 of 1.1.x).

*Proof.* (a) $T_y$ fixes the primitives $X$, $P$, $C$, $E$, $\xi$, $g$ and
$f$. Hence $\tilde X$, $K_{\mathrm{sem}}$, $\hat K$ and $K_{\mathrm{obs}}$
remain fixed by their declared dependencies, and therefore
$\hat y = f(\tilde X,K_{\mathrm{obs}})$ is unchanged; apply Lemma 1 and
Proposition 1. (b) By definition of
$T_y^{\pi}$. $\square$

**Proposition 2 (closing a blind region).** For views $\mathcal I$ and
$\mathcal W$, $B_{\mathcal I \vee \mathcal W}(\mathcal A) = B_{\mathcal I}(\mathcal A) \cap B_{\mathcal W}(\mathcal A)$.
Consequently a class $\mathcal A \subseteq B_{\mathcal I}(\mathcal A)$ becomes
completely separable from the baseline after adding $\mathcal W$ iff
$V_{\mathcal W}(a(s_0)) \ne V_{\mathcal W}(s_0)$ for every $a \in \mathcal A$,
i.e. iff $\mathcal W$ is baseline-separating on the orbit of $\mathcal A$.
Necessity: if some $a$ leaves $V_{\mathcal W}$ unchanged it stays in the joint
blind region. Sufficiency: the joint view changes whenever either component
changes. Baseline separation does not identify *which* $a$ occurred; that
would require pairwise separation, which is not claimed.

*Proof.* $(V_{\mathcal I}, V_{\mathcal W})(s_a) = (V_{\mathcal I}, V_{\mathcal W})(s_0)$
iff both components agree. $\square$

**Corollary 2 (what cannot close the label-path region).** With $f$ fixed and
deterministic, no view that factors through
$(\tilde X, \hat y, \mathrm{hist}(y))$ separates any $a \in T_y^{\pi}$
from $s_0$: $T_y^{\pi} \subseteq B_{\mathcal I_{XF} \vee \mathcal I_{Y_m}}$.
The multiset of triples $\mathcal I_{XFY}$ separates $a \in T_y^{\pi}$ from
$s_0$ unless $a$ permutes labels only among items with identical
$(\tilde x, \hat y)$; an item-aligned view separates every non-identity
relabeling.

*Proof.* Apply Proposition 2 with $\mathcal W$ the view in question: by
Corollary 1 each component is invariant, so their join is. Two states with
the same $(\tilde x_i, \hat y_i)_i$ have the same multiset of triples iff a
permutation of items maps one label vector to the other while fixing
$(\tilde x, \hat y)$, i.e. moves labels only among items with identical
$(\tilde x, \hat y)$. An item-indexed tuple has no such freedom. $\square$

**Proposition 3 (materiality forces aggregate separability).** If
$a \in T_y$ and $\Delta_R(a) \ne 0$, then $M(s_a) \ne M(s_0)$; hence
$a \notin B_{\mathcal I_M}(T_y)$ for the confusion view $\mathcal I_M$,
$a \notin B_{\mathcal I_{XFY}}(T_y)$, and
$G_{\mathcal I_M}(\tau) \cap T_y = G_{\mathcal I_{XFY}}(\tau) \cap T_y = \emptyset$
for every $\tau > 0$.

*Proof.* Contrapositive of $M(s_a) = M(s_0) \Rightarrow R(s_a) = g(M(s_a)) = R(s_0)$.
The confusion view is a coarsening of the multiset of triples, so a changed
$M$ implies a changed multiset. $\square$

Proposition 3 is realised without exception in the frozen expansion: all
2,617 label-path observations whose balanced accuracy changed have a non-zero
confusion-profile delta (witness W8). It is also why the batch-level
$\mathcal I_{XFY}$ result (Section 4) is a statement about *detectability*,
not *separability*.

*Remark (metrics other than balanced accuracy).* Proposition 3 uses only
$R = g(M)$; it holds verbatim for accuracy, precision, recall, $F_1$ and every
other function of the binarised confusion matrix, with the confusion matrix as
the sufficient aggregate (Level B). A ranking metric such as ROC-AUC is not a
function of $M$: it depends on the multiset of (score, label) pairs
$\{(f_{\mathrm{score}}(\tilde x_i), y_i)\}$. The same argument applies with
that multiset in the role of $M$: a label-only intervention that changes the
AUC changes the score-label multiset, which is a coarsening of the joint view
$\mathcal I_{XFY}$ augmented with scores, and a trusted stored copy of that
multiset (Level B for ranking metrics) detects every material change exactly,
while item identity again needs Level C. No AUC experiment is run; the remark
delimits the hypothesis.

## 4. Auditor classes and which reference certifies which integrity

**Definition 5.** Relative to a regime $\mathcal I$ and a class $\mathcal A$:

(a) A *reference-anchored auditor* holds a trusted reference
$\rho = V_{\mathcal J}(s_0)$ (Level B or C) and computes
$D(s) = d(V_{\mathcal J}(s), \rho)$ with a metric $d$ ($d = 0$ iff equal).
Then $D(s_0) = 0$ exactly, the rule "fire iff $D > 0$" has false-alarm
probability zero, and it detects every $a$ with $V_{\mathcal J}(s_a) \ne \rho$.

(b) A *batch-level auditor* performs a Level-A statistical aggregate
comparison. In the executed instance its current/reference statistic uses a
benchmark-protected clean same-item set without item pairing, and the null
model $P_0$ comes from the Gate-N calibration draws. The benchmark does not
demonstrate deployed authentication of that reference. It decides with a
calibrated test at budget $\alpha$. For a separable $a$ the detection probability is the
power of the test against the shift $V_{\mathcal I}(s_a)$ relative to the
null variability of fresh batches; it is generally below one, and it is *not*
implied by separability.

(c) A *post-hoc certifier* recomputes a view from inputs it trusts (e.g. the
evaluation/report contract recomputes $R$ from $(\hat y, y)$) and compares
with the reported value. It needs trusted inputs and re-execution capability
rather than a stored reference, and it certifies consistency of the report
with those inputs, not authenticity of the inputs.

**Proposition 4 (separability is necessary; anchoring makes it sufficient).**
(i) For any auditor whose decision is a function of $V_{\mathcal I}(s)$ (and a
seed included in the view), $a \in B_{\mathcal I}(\mathcal A)$ implies
$\mathrm{fire}(s_a) = \mathrm{fire}(s_0)$ pathwise under the same state and
reference construction. This pathwise equality does not in general imply
equality with a false-action rate estimated under a different clean-resampling
or reference construction. (ii) A
reference-anchored auditor of class (a) detects every
$a \notin B_{\mathcal J}(\mathcal A)$, deterministically.

*Proof.* (i) is Lemma 1 applied to the decision function. (ii) is Definition
5(a) with $d = 0$ iff equal. $\square$

**Corollary 3 (which reference certifies which integrity).** Let $a \in T_y$
with $f$ fixed and deterministic.
(a) *Conclusion and aggregate integrity require claim-relative Level-B
anchors.* A trusted exact same-batch claim reference $R_0=R(s_0)$ detects
exactly every $R(s_a)\ne R_0$ and is sufficient for conclusion integrity only.
A trusted aggregate reference $M_0 = M(s_0)$ of the same batch detects every
$a$ that violates aggregate integrity and, by Proposition 3, every material
conclusion change in the declared setting.
(b) *Item-identity integrity, Level C is necessary.* Any reference that
factors through $M$, $\mathrm{hist}(y)$ or $R$ is invariant under every
relabeling that permutes labels among items with equal predictions; such
relabelings (counterexample C1) violate item-identity integrity, so no
Level-B reference detects them. A Level-C reference (item-aligned $y_0$)
detects every non-identity relabeling.

*Proof.* (a) Proposition 4(ii) with the conclusion view gives the exact $R_0$
comparison; applying it with $\mathcal J = \mathcal I_M$ gives the exact
$M_0$ comparison, and Proposition 3 supplies the material-conclusion
consequence. (b) A swap of $y_i, y_j$ with $\hat y_i = \hat y_j$ moves one
item from cell $(\hat y_i, y_i)$ to $(\hat y_i, y_j)$ and another from
$(\hat y_j, y_j)$ to $(\hat y_j, y_i)$; the two moves cancel in $M$, hence in
every function of $M$, and the histogram is unchanged. The item-indexed tuple
differs in positions $i$ and $j$. $\square$

In the frozen evidence, (a) is the 2,617/2,617 detection of material label
rows by the confusion-profile delta against the reference batch (and 2,792 of
3,600 label rows in total, witness W9), and (b) is the 808 relabelings with
zero confusion-profile delta that only the item-level label mismatch exposes
(W1 = W10). The batch-level $\mathcal I_{XFY}$ rule detects 11 (conformal
family rule), 16 (asymmetric comparison) or 43 (union) of the 2,617 material
label rows: every one is separable (Proposition 3), so the remaining cases are
finite-batch statistical misses, not structural blind regions. In this design,
a 2–10% relabeling of a 128-row batch can shift the confusion profile by less
than its variability across fresh clean batches. Structural blind regions are
independent of row count, whereas the power of a statistic that does change can
increase with batch size. No batch-size scaling is estimated here. The
value of a trusted reference of the same batch is therefore informational:
it replaces a statistical null with an exact one. Which level is needed
depends on the integrity notion: $R_0$ suffices for conclusion-only integrity,
$M_0$ additionally certifies aggregate integrity, and item-identity integrity
needs Level C. Neither is an oracle: each requires an uncontrolled reference
to a view of the baseline, i.e. provenance.

Granularity denotes the information authenticated or bound, not serialized
byte length. A Merkle root or position-binding vector commitment may represent
Level-C evidence in constant visible bytes precisely because it binds item
identity. For an aggregate- or conclusion-only claim, a Level-B anchor can
instead reduce the item-level information that must be retained or exposed to
the auditor, supporting data minimization and separation of duties without
constituting a new cryptographic primitive or a legal-compliance guarantee.

**Proposition 5 (union of calibrated sensors versus family calibration).**

(a) *Union rule.* Let $E_1, \dots, E_m$ be the null firing events of $m$
sensors with $p_j = \Pr_0[E_j] \le \alpha$. Then
$$\max_j p_j \;\le\; \Pr_0\Big[\bigcup_j E_j\Big] \;\le\; \min\Big(1, \sum_j p_j\Big) \;\le\; \min(1, m\alpha).$$
Without assuming that some $p_j = \alpha$, the universal lower bound is
$\max_j p_j$, which can be $0$. If every $p_j = \alpha$, then
$\alpha \le \Pr_0[\bigcup_j E_j] \le \min(1, m\alpha)$; the lower bound $\alpha$
is attained by coincident (nested) events, the upper bound $m\alpha$ (when
$m\alpha \le 1$) by mutually disjoint events, and under independence
$\Pr_0[\bigcup_j E_j] = 1 - \prod_j (1 - p_j) = 1 - (1-\alpha)^m$, which lies
strictly between the two bounds for $m \ge 2$ and $0 < \alpha < 1$.

(b) *Family rule: full conformal max-rank p-value (adopted in 1.3.0).* Let
$v_1, \dots, v_n \in \mathbb R^m$ be the sensor vectors of the $n$ calibration
draws and $v_{n+1}$ that of the audited batch, and write
$\mathcal V = \{v_1, \dots, v_{n+1}\}$ for the augmented set. Give every member
$j \in \{1, \dots, n+1\}$ the leave-one-out family score
$$\tilde U_j \;=\; \max_{s \le m}\ \frac{\#\{i \ne j : v_{s,i} < v_{s,j}\}}{n},$$
computed against the other $n$ members of $\mathcal V$, and define the
conformal p-value and the rule
$$p \;=\; \frac{1 + \#\{i \le n : \tilde U_i \ge \tilde U_{n+1}\}}{n+1}, \qquad
\text{fire iff } p \le \alpha .$$
Ties count against firing ($\ge$). Then, for every $\alpha \in (0,1)$:

  (i) *Deterministic counting bound.* For every augmented set $\mathcal V$, at
  most $\lfloor \alpha (n+1) \rfloor$ of its $n+1$ members satisfy
  $N_j := \#\{i \le n+1 : \tilde U_i \ge \tilde U_j\} \le \lfloor \alpha (n+1) \rfloor$,
  i.e. would fire if they were the audited member.

  (ii) *Exact finite-sample level.* If $(v_1, \dots, v_{n+1})$ are
  exchangeable, then
  $$\Pr_0[\,p \le \alpha\,] \;\le\; \frac{\lfloor \alpha (n+1) \rfloor}{n+1} \;\le\; \alpha,$$
  with equality in the first inequality when the $\tilde U_j$ are almost
  surely distinct. No continuity or tie assumption is needed; ties only
  lower the firing probability. For $n = 200$ and $\alpha = 0.05$ the level is
  $10/201 = 0.0498$.

  (iii) *Single sensor.* For $m = 1$ and distinct values the rule coincides
  with "fire iff $v_{n+1}$ exceeds the $\lceil (n+1)(1-\alpha) \rceil$-th
  smallest calibration value", the per-sensor rule of artifact 1.1.0, whose
  level is the same $\lfloor \alpha(n+1) \rfloor / (n+1)$.

  (iv) *What the guarantee is and is not.* The level is marginal over the
  joint draw of the calibration set and the audited batch (unconditional).
  Conditional on a fixed calibration set the false-alarm probability
  fluctuates around the level; audited batches that share one calibration set
  are dependent, so an empirical rate pooled over them is descriptive. The
  premise is exchangeability of the $n+1$ draws; nothing is claimed when it
  fails (Section 4, Gate F: the design's overlapping draws and its two pool
  halves violate it, and the observed rates measure that deviation).

(c) *The superseded rule of artifact 1.2.0 has no such guarantee.* That rule
scored each calibration draw against the other $n-1$ calibration draws only,
the audited batch against all $n$, and fired when the audited score exceeded
the $\lceil (n+1)(1-\alpha) \rceil$-th smallest calibration score. It claimed
$\Pr_0[\text{fire}] \le \alpha + 1/(n+1)$. The claim is false: for $n = 4$,
$\alpha = 0.2$ and $m = 3$ sensors with the cyclic orderings
$s_1: j_1 > j_2 > j_3 > x > y$, $s_2: j_2 > j_3 > j_1 > x > y$,
$s_3: j_3 > j_1 > j_2 > x > y$, the members $j_1, j_2, j_3$ each fire when
audited, so the firing probability under exchangeability is $3/5 = 0.60$
against the claimed $0.40$ and against $\alpha$. The asymmetry lets a
calibration draw tied with the audited batch in family score fall one grid
step below it whenever its maximising sensors rank the audited batch below,
and with several sensors many draws can do so at once. On the frozen null
draws, exchangeable random re-splits show the rule at 0.052 / 0.058 / 0.040 /
0.059 for $\mathcal I_X$ / $\mathcal I_{XF}$ / $\mathcal I_{Y_m}$ /
$\mathcal I_{XFY}$ where the conformal rule stays at 0.044 / 0.042 / 0.040 /
0.036 (level $0.0498$). Its published 1.2.0 numbers are retained only as
comparison columns.

*Proof.* (a) The union contains each $E_j$, which gives the lower bound;
Boole's inequality gives the upper bound; the attainment statements are the
standard nested, disjoint and independent constructions, and the inclusion
–exclusion identity gives the product form under independence.

(b)(i) Let $k = \lfloor \alpha (n+1) \rfloor$ and suppose $k+1$ members
$j_0, \dots, j_k$ satisfy $N_j \le k$. Let $j^\ast$ be one with the smallest
score among them. Every one of the $k+1$ members has $\tilde U \ge \tilde U_{j^\ast}$,
so $N_{j^\ast} \ge k+1$, a contradiction. Hence at most $k$ members fire.

(b)(ii) The score of member $j$ depends on $v_j$ and on the multiset
$\{v_i : i \ne j\}$; the map $(v_1, \dots, v_{n+1}) \mapsto (\tilde U_1, \dots, \tilde U_{n+1})$
is therefore permutation-equivariant, and exchangeability of the $v$'s gives
exchangeability of the $\tilde U$'s, hence of the $N_j$'s. The audited member
is $j = n+1$ and $p \le \alpha$ iff $N_{n+1} \le k$ (because
$N_{n+1} = 1 + \#\{i \le n : \tilde U_i \ge \tilde U_{n+1}\}$ and
$N_{n+1}/(n+1) \le \alpha$ iff $N_{n+1} \le k$). By exchangeability
$\Pr[N_{n+1} \le k] = \mathbb E[\#\{j : N_j \le k\}]/(n+1) \le k/(n+1)$ by
(i). With almost surely distinct scores exactly $k$ members satisfy
$N_j \le k$, giving equality. Ties can only merge ranks, which reduces the set
$\{j : N_j \le k\}$.

(b)(iii) For $m = 1$ and distinct values, $\tilde U_i \ge \tilde U_{n+1}$ iff
$v_i > v_{n+1}$: if $v_i > v_{n+1}$ then every value below $v_{n+1}$ is below
$v_i$ and $v_{n+1}$ itself is below $v_i$, so $\tilde U_i > \tilde U_{n+1}$;
symmetrically if $v_i < v_{n+1}$. Hence $p = (1 + \#\{i : v_i > v_{n+1}\})/(n+1)$
and $p \le \alpha$ iff $\#\{i : v_i > v_{n+1}\} \le k - 1$ iff $v_{n+1}$
exceeds at least $n - k + 1 = \lceil (n+1)(1-\alpha) \rceil$ calibration
values (for non-integer $\alpha(n+1)$; the integer case differs by the tie
convention on the grid and is covered by (ii)).

(b)(iv) is a restatement of what (ii) proves and of what it does not.

(c) The configuration is checked by enumeration
(`tests/test_family_calibration_exhaustive.py`): with $j_1$ audited, the
calibration scores are $0.75, 0.75, 0.25, 0$ and the audited score is $1$;
the threshold is the fourth smallest calibration score $0.75$ and $1 > 0.75$
fires; the same holds for $j_2$ and $j_3$ by the cyclic symmetry, while $x$
and $y$ do not fire. The re-split rates are `family_resplit_pooled.csv`.
$\square$

**Proposition 6 (no local authentication without an uncontrolled root).** Let
a *local verifier* be any map $\mathrm{acc} : \mathcal O_{\mathcal I} \times \mathrm{Ref} \to \{\text{accept}, \text{reject}\}$
whose input is the observed view $V_{\mathcal I}(s)$ together with a bundle of
references $\rho$, and nothing else. Let $\mathcal S_H \subseteq \mathcal S$ be
the honest family of states and $\rho_H(s) = V_{\mathcal J}(s)$ the reference
that the honest process attaches to state $s$. Assume

- (honest completeness) $\mathrm{acc}(V_{\mathcal I}(s), \rho_H(s)) = \text{accept}$
  for every $s \in \mathcal S_H$;
- (joint control) the adversarial class can produce, for some
  $s' \in \mathcal S_H$ with $s' \not\sim_{\mathcal I} s_0$, the pair
  $(V_{\mathcal I}(s'), \rho_H(s'))$, i.e. it can replace the asset and rewrite
  every reference in $\rho$ to the value the honest process would attach to
  $s'$.

Then the verifier accepts the substituted pair, so it cannot establish
authenticity of the served state relative to the baseline $s_0$: the
substituted state is observationally an honest run of $s'$. In particular, if
$R(s') \ne R(s_0)$, a material change is served. Conversely, if some component
$\rho^{\star} = V_{\mathcal K}(s_0)$ of the bundle cannot be written by the
class, the rule "reject iff $V_{\mathcal K}(s) \ne \rho^{\star}$" rejects every
substitution with $V_{\mathcal K}(s') \ne V_{\mathcal K}(s_0)$ (Proposition
4(ii)). Hence an integrity guarantee relative to an external baseline
requires at least one protected reference or authenticated channel that the declared
adversarial class cannot modify, and such a root is sufficient exactly for the
classes it separates.

*Proof.* The substituted input equals the honest input of $s'$; by honest
completeness the verifier accepts it. Acceptance is the same event as for an
honest run of $s'$, so no function of that input distinguishes the two. The
converse is Proposition 4(ii) applied to $\mathcal K$. $\square$

The proposition is deliberately about *authenticity relative to a baseline*,
not about consistency: a verifier that checks only internal relations among
asset and references (hash chains recomputable by the record's owner,
recomputed metrics from unauthenticated inputs, self-consistent label joins)
can certify consistency but not provenance. It does not claim that the
substituted pair equals the baseline pair; Proposition 3 shows that a
material substitution changes the joint view. What it shows is that the
change is invisible to any verifier all of whose evidence the class can
rewrite. This is the formal content of the sentence "if an adversary can
replace both an asset and every trusted reference used to authenticate it,
the present local contract cannot identify the event", and it is why the
study reports $\mathcal I_{XFY}^{\star}$ as a regime with an explicit trust
assumption rather than as a stronger detector.

## 5. Counterexamples and their witnesses in the frozen evidence

Each counterexample is a minimal construction; the witness count is the number
of frozen expansion observations (eight environments, 10,800 intervened rows)
that realise it, from `counterexample_witnesses.csv`.

| ID | Construction | What is invariant | What changes | Witnesses |
|---|---|---|---|---|
| C1 | Swap the labels of two items $i, j$ with $\hat y_i = \hat y_j$, $y_i \ne y_j$ | features, predictions, histogram, confusion matrix, $R$ | item-level identity of labels | W1: 808 / 3,600 label rows (flips with zero confusion-profile delta and zero conclusion change) |
| C2 | Any relabeling that changes $M$ | features, predictions | confusion matrix, $R$ | W2: 2,617 / 3,600 (non-zero conclusion change, zero prediction disagreement) |
| C3 | Swap the labels of $i, j$ with $\hat y_i \ne \hat y_j$, $y_i \ne y_j$ | features, predictions, histogram | confusion matrix, $R$ | W3: 1,059 / 1,800 prior-preserving rows |
| C4 | Compensating flips that move counts between cells of $M$ while keeping $g(M)$ | features, predictions, $R$ | confusion matrix | W4: 175 / 3,600 |
| C5 | Feature change that flips predictions of items whose flips cancel in $M$ | $R$ | representation, predictions | W5: 296 / 7,200 feature-side rows |
| C6 | Feature change that crosses no decision boundary | predictions, $R$ | representation | W6: 2,513 / 7,200 |
| C7 | Intervention that raises the reported metric | — | $R$ increases | W7: 1,534 / 10,800 (433 of them label-path rows) |
| C8 | Material label change (Proposition 3) | — | confusion matrix | W8: 2,617 / 2,617 material label rows change the confusion profile |
| — | Label rows detectable by a trusted aggregate reference (Corollary 3a) | — | confusion matrix | W9: 2,792 / 3,600 |
| — | Label rows detectable only item-wise (Corollary 3b) | confusion matrix, histogram, $R$ | item identity | W10: 808 / 3,600 (= W1) |
| C9 | Cluster-preserving feature drift (class F5, Gate A): the executed drift applied only to entries outside the tight clusters that the batch-level fingerprint relies on | the clustered entries, hence the mass points that a fresh batch reproduces | the remaining entries; possibly predictions and $R$ | Gate A tables (`adversarial_*.csv`); a sensor-level blindness of Level-A auditors that no structural statement predicts and that the executed gate measures |

C1 shows that *item-identity violation* and *conclusion impact* are different
events: 808 relabelings leave every aggregate and the conclusion untouched,
and are visible only item-wise against a Level-C reference. C2–C4 separate
marginal invariance, confusion-matrix invariance and conclusion invariance.
C5–C6 separate representation, output and conclusion on the feature side.
C7 shows that the clipped "harm" endpoint of 1.1.x hid 433 label-path
conclusion changes; they are counted from 1.2.0 on. C8 is the empirical face
of Proposition 3, and W9/W10 the empirical face of Corollary 3. C9 is not a
structural blind region (the view $\tilde X$ does change) but the executed
instance of sensor insufficiency of Definition 3 against an adaptive
attacker: whether the calibrated family detects it is an empirical question,
answered by Gate A.

## 6. The quantum branch as an instance of the view lattice

**Objects.** Let $\mathcal C$ be the set of circuit representations (canonical
OpenQASM 3 text with bound parameters), $\Phi : \mathcal C \to \mathcal K$ the
semantic kernel map that sends a circuit to the ideal fidelity kernel it
induces on a fixed probe set, $K_{\mathrm{sem}} = \Phi(C)$ the semantic
kernel, $\hat K = \mathrm{est}(K_{\mathrm{sem}}, E, \xi)$ the finite-shot
estimate produced by execution under context $E$ (shots, backend) with
randomness $\xi$, $K_{\mathrm{obs}} = g(\hat K)$ the kernel object delivered
downstream after estimation, transmission and post-processing,
$h : \mathcal C \to \{0,1\}^{256}$ the provenance hash,
$A : \mathcal K \to \mathbb R^q$ the algebraic invariants (symmetry residual,
diagonal residual, minimum eigenvalue, PSD-repair norm) and
$f_K : \tilde X \mapsto \hat y$ the classical decision computed from a
kernel. The views of $\mathcal I_Q$ are $V_h = h(C)$,
$V_{K_{\mathrm{sem}}} = K_{\mathrm{sem}}$, $V_{\hat K} = \hat K$,
$V_{K_{\mathrm{obs}}} = K_{\mathrm{obs}}$, $V_A = A(K_{\mathrm{obs}})$ and
$V_f = f_{K_{\mathrm{obs}}}(\tilde X)$. Three intervention classes are kept
apart (Section 1):

- **(a) circuit-side:** overwrites $C$; may change $K_{\mathrm{sem}}$ and
  everything below it;
- **(b) estimation/execution variation:** $C$ and $K_{\mathrm{sem}}$ fixed;
  $\hat K$ (hence $K_{\mathrm{obs}}$) changes through $\xi$ or $E$;
- **(c) post-processing / kernel substitution:** $C$, $K_{\mathrm{sem}}$ and
  $\hat K$ fixed; $K_{\mathrm{obs}}$ changes through $g$ or directly.

Every inclusion below names the class on which it holds. **No single
inclusion of blind regions is claimed across classes**: an inclusion
$B_h \subseteq B_{K_{\mathrm{sem}}}$ concerns interventions that act on $C$,
and says nothing about a substitution of $K_{\mathrm{obs}}$, for which $h(C)$
and $\Phi(C)$ are unchanged by definition.

**Proposition 7 (the quantum lattice).** Assume $h$ is collision-free on the
circuits under study (SHA-256 collision resistance).

(i) *Semantic equivalence classes (class (a)).* $[C] := \Phi^{-1}(\Phi(C))$ is
the class of circuits with the same kernel semantics; approved transpilation
and common-unitary rewrites map $C$ into $[C]$ without fixing $h(C)$.
Consequently $V_h$ refines $V_{K_{\mathrm{sem}}}$ on $\mathcal C$ (identical
hashes imply identical semantic kernels but not conversely) and
$B_h(\mathcal A) \subseteq B_{K_{\mathrm{sem}}}(\mathcal A)$ for every class
$\mathcal A$ of circuit-side interventions; the inclusion is strict whenever
$\mathcal A$ contains an approved rewrite. Separability in the provenance view
is therefore *not* evidence of harm; a provenance-anchored auditor needs the
approved class $[C_0]$, implemented as semantic equality of probe kernels
against the trusted semantic probe $K_{\mathrm{sem},0} = \Phi(C_0)$ (a
Level-B reference: an aggregate of the reference circuit on the probe set).

(ii) *Algebraic and output coarsenings (class (c)).*
$V_A = A \circ V_{K_{\mathrm{obs}}}$ and
$V_f = f_{\cdot}(\tilde X) \circ V_{K_{\mathrm{obs}}}$ are coarsenings of the
observed-kernel view, so by Proposition 1
$B_{K_{\mathrm{obs}}}(\mathcal A) \subseteq B_A(\mathcal A)$ and
$B_{K_{\mathrm{obs}}}(\mathcal A) \subseteq B_f(\mathcal A)$. A PSD-preserving
substitution $K' \ne K_{\mathrm{obs},0}$ with $A(K') = A(K_{\mathrm{obs},0})$
lies in $B_A \setminus B_{K_{\mathrm{obs}}}$: the algebraic family is
insufficient (Definition 3). Because $C$, $K_{\mathrm{sem}}$ and $\hat K$ are
fixed on this class, the substitution also lies in
$B_h \cap B_{K_{\mathrm{sem}}}$: neither the circuit hash nor the semantic
probe of the unchanged circuit can see it, and the blind region is closed
only by a trusted reference on $K_{\mathrm{obs}}$ itself (Proposition 4(ii)).
The trusted semantic probe $K_{\mathrm{sem},0}$ and the trusted
observed-kernel reference $K_{\mathrm{obs},0}$ are therefore different
anchors; in the ideal-statevector gate they have the same value on the
honest path, which is why one anchored comparison against $\Phi(C_0)$ serves
both roles there. A kernel change that crosses no decision boundary lies in
$B_f \setminus B_{K_{\mathrm{obs}}}$.

(iii) *Finite-shot estimation (class (b)).* For an honest finite-shot
estimate, the acceptance rule "accept iff $\hat K = K_{\mathrm{sem},0}$" has
false-alarm probability
$$1 - \Pr[\hat K = K_{\mathrm{sem},0} \mid \text{honest}],$$
which depends on the discrete support of the estimator and may be large or
equal to one, but is **not universally one**. Consequently: exact equality is
not an appropriate acceptance criterion under finite-shot estimation; the
discrepancy $d(\hat K, K_{\mathrm{sem},0})$ must be treated as a Level-A
statistic whose null is obtained from repeated honest estimation
(Definition 5(b)); if those repeated estimates and the audited estimate are
exchangeable, Proposition 5(b) applies to them with $m = 1$ and gives the
finite-sample level $\lfloor \alpha(n+1) \rfloor/(n+1)$; and where no
calibrated null is available, no statistical integrity claim is made and the
only sound action is to abstain, which is the `hold` that the executable
contract returns for approved stochastic estimation.

*Proof.* (i) If $h(C_1) = h(C_2)$ then $C_1 = C_2$ by collision freedom, so
$\Phi(C_1) = \Phi(C_2)$: $V_h$ refines $V_{K_{\mathrm{sem}}}$ through
$\Phi \circ h^{-1}$ and Proposition 1 gives the inclusion. An approved rewrite
$C' \in [C_0]$ with a different canonical text has $h(C') \ne h(C_0)$ and
$\Phi(C') = \Phi(C_0)$, so it lies in $B_{K_{\mathrm{sem}}} \setminus B_h$.
(ii) is Proposition 1 applied to the two coarsenings of
$V_{K_{\mathrm{obs}}}$; the membership in $B_h \cap B_{K_{\mathrm{sem}}}$ is
the definition of an intervention of class (c) (Section 1: $C$ is not
overwritten and is not a descendant of $g$ or $K_{\mathrm{obs}}$, so it is
fixed, and $h(C)$, $\Phi(C)$ are functions of $C$). The two set differences
are witnessed in the gate (Table 8 of the supplement: 15/15 PSD-preserving
substitutions with algebraic sensors at zero, circuit hash unchanged and the
anchored comparison of the delivered kernel firing; RZ mutations at 0.02 with
zero output change and semantic firing). (iii) For a kernel entry with
fidelity $p$ estimated from $N$ shots, $N \hat p \sim \mathrm{Binomial}(N, p)$
and
$$\Pr[\hat p = p] = \binom{N}{Np} p^{Np} (1-p)^{N-Np} \text{ if } Np \in \mathbb N, \qquad 0 \text{ otherwise};$$
for independently estimated entries the probabilities multiply. For
$p = 1/2$ and $N = 2$, $\Pr[\hat p = p] = \Pr[X = 1] = 1/2$, so the exact rule
has false-alarm probability $1/2$; for $p = 1/3$ and $N = 2$ it is one; for a
degenerate entry ($p \in \{0, 1\}$) it is zero. The universal statement of
version 1.2 (that the honest estimate never equals the reference under
non-degenerate shot noise, so that the exact rule always fires) was therefore
false on the support of the estimator (it holds only for an estimator with a
continuous law, which a finite-shot estimator is not) and is withdrawn; the operational
conclusion (calibrated null or abstention) is unchanged and is Definition 5(b)
with Proposition 5(b) on the repeated estimates. The arithmetic is checked in
`tests/test_workflow_state.py` (`FiniteShotEqualityTests`). $\square$

The empirical realisation is the 165-design-cell simulator gate of Section VI-E of
the article, read class by class: benign transpilation and the common-unitary
rewrite (class (a)) change $h(C)$ in every cell while $\Phi(C)$, $A$ and
$f_K$ are unchanged (i); the PSD-preserving mixture (class (c)) passes the
algebraic checks and leaves the circuit hash unchanged in every cell and is
exposed by the anchored comparison of the delivered kernel (ii); the mild RZ
mutation (class (a)) changes the semantic kernel in every cell and no
prediction (ii); and both shot emulators (class (b)) produce a non-zero
repeated-estimation discrepancy in every one of the 30 cells, an empirical
property of these cells that motivates the calibrated treatment of (iii) but
is not a law, and the contract holds them for adjudication. The proposition
adds no quantum mechanics: it states that the quantum branch is one more
chain of coarsenings of the same lattice, with two features that the
classical branches do not have, namely an approved equivalence class coarser
than provenance and an estimation step that turns an exact anchor into a
statistical one.

## 7. What the formal core does and does not claim

It claims that auditability is a property of the triple (intervention class,
view, trusted references); that structural blind regions are monotone under
refinement and closed exactly by baseline-separating added views; that
material label-path interventions always change the confusion matrix and are
therefore separable in the joint view and detected exactly by a trusted
aggregate reference of the same batch, while item-identity integrity needs an
item-aligned reference; that a batch-level auditor with a statistical
(Level-A) reference only detects such changes only with statistical power;
that decision-level calibration requires calibrating the family rather than
the sensors, with a conformal rule whose finite-sample level
$\lfloor \alpha(n+1) \rfloor/(n+1)$ is exact under exchangeability with ties
and whose executed-design deviation is measured (observed rates
0.056 / 0.058 / 0.048 / 0.053 in a design that violates the premise); that the
asymmetric rule of artifact 1.2.0 had no such guarantee; that the quantum
branch is an instance of the same lattice in which, class by class,
provenance refines the semantic kernel on circuit-side interventions, algebra
and outputs coarsen the observed kernel on post-processing interventions,
and finite-shot estimation makes exact equality an inappropriate acceptance
criterion whose replacement is a calibrated null or abstention; and that no
verifier all of whose evidence the adversarial class can rewrite establishes
authenticity relative to a baseline. It does not claim a general
detectability theory beyond finite batches with a fixed deterministic
predictor, does not claim that the exchangeability premise holds in
deployment, does not claim a conditional guarantee given a calibration set,
does not claim identification of which intervention occurred, and does not
claim anything about interventions outside the declared classes.
