# Formal core — observational indistinguishability and integrity blind regions (artifact 1.2.0)

Version 1.1 (2026-09-07; version 1.0 of the same day corrected in
Propositions 2, 5 and 6 and in the treatment of trusted references after the
final mathematical review). This document is the complete statement, with
proofs, of the formal section of the TDSC article. The article prints the
definitions and the propositions; the supplement reproduces the proofs. Every
witness count quoted here is generated from the manifested table
`counterexample_witnesses.csv` (Gate D) and printed in the article through
`publication/tdsc/tables/policy_macros.tex`.

The results are elementary by design. Their role is to make exact which
evidence separates which class of intervention, so that the empirical gates
test statements rather than intuitions. Every statement below is pointwise
(for a fixed baseline state and a fixed finite batch) unless it says
"in distribution" or names a probability.

## 1. Objects

**States.** A workflow state is the complete tuple of artifacts of one
evaluation run, $s = (X, P, C, K, E, f, y, R) \in \mathcal S$: acquired
features $X$, preprocessing $P$, circuit/feature map $C$, estimated kernel
$K$, execution metadata $E$, fitted predictor $f$, evaluation labels $y$ and
reported result $R$. We write $\tilde X = P(X)$ for the evaluation
representation and $\hat y = f(\tilde X)$ for the predictions. Items carry an
identity $i = 1, \dots, n$ (the row of the evaluation batch).

**Interventions.** An intervention is a map $a : \mathcal S \to \mathcal S$.
The baseline state is $s_0$, the intervened state $s_a = a(s_0)$. An
intervention class $\mathcal A$ is a set of such maps. Classes used in the
study: $T_y$ (label-only: changes $y$ item-wise, leaves every other component
fixed), $T_y^{\pi} \subset T_y$ (prior-preserving: additionally preserves the
class histogram of $y$), and the feature-side mechanisms (sign flip, mean
shift, scaling drift, dropout with imputation), which change $\tilde X$ and,
through $f$, may change $\hat y$ and $R$.

**Conclusion and materiality.** The conclusion functional is
$R : \mathcal S \to \mathbb R$, here balanced accuracy of $\hat y$ against $y$,
which is a function $R = g(M)$ of the confusion matrix
$M(s) = (\#\{i : \hat y_i = u, y_i = v\})_{u,v}$. The signed conclusion change
is $\Delta_R(a) = R(s_0) - R(s_a)$. An intervention is *material at level*
$\tau$ if $|\Delta_R(a)| \ge \tau$; $\tau \to 0^{+}$ means "any change of the
reported conclusion". The positive part $\max(\Delta_R, 0)$ is the "harm"
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

**References and their three levels.** A reference is a stored value
$\rho = V_{\mathcal J}(s_0)$ of some view of the baseline. It is *trusted*
under assumption $\mathsf T(\rho)$: no intervention in the class under study
can alter it (it is authenticated, or held by a party outside the adversary's
reach). Three levels of evidence are distinguished throughout:

- **Level A, batch-level statistical evidence.** No stored value of the
  baseline view; the auditor holds a null model of $V_{\mathcal I}$ over
  fresh clean batches. Detection is a statistical test with power below one.
- **Level B, trusted aggregate reference.** A stored, uncontrolled value of a
  permutation-invariant aggregate of the *same batch*, such as $M(s_0)$,
  $\mathrm{hist}(y_0)$ or $R(s_0)$. Comparison against it has an exact-zero
  null.
- **Level C, trusted item-aligned reference.** A stored, uncontrolled
  item-indexed tuple of the same items, such as $(y_{0,i})_i$ or
  $(\hat y_{0,i})_i$; comparison is item-wise with an exact-zero null.

We write $\mathcal I^{\star}$ for a regime augmented with trusted references
of its own baseline view; $\mathcal I_{XFY}^{\star}$ in the evidence holds
both the aggregate confusion profile (Level B) and the item-aligned labels
and predictions (Level C) of the same batch. A label being *available* in
$\mathcal I_{XFY}$ says nothing about whether it is *trusted*: if the label
store is the asset under attack, the auditor sees $y_a$, not $y_0$.

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

*Proof.* (a) $T_y$ fixes $X$, $P$ and $f$, so $\tilde X$ and $\hat y = f(\tilde X)$
are unchanged; apply Lemma 1 and Proposition 1. (b) By definition of
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
$(\tilde X, f(\tilde X), \mathrm{hist}(y))$ separates any $a \in T_y^{\pi}$
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

## 4. Auditor classes and which reference certifies which integrity

**Definition 5.** Relative to a regime $\mathcal I$ and a class $\mathcal A$:

(a) A *reference-anchored auditor* holds a trusted reference
$\rho = V_{\mathcal J}(s_0)$ (Level B or C) and computes
$D(s) = d(V_{\mathcal J}(s), \rho)$ with a metric $d$ ($d = 0$ iff equal).
Then $D(s_0) = 0$ exactly, the rule "fire iff $D > 0$" has false-alarm
probability zero, and it detects every $a$ with $V_{\mathcal J}(s_a) \ne \rho$.

(b) An *anchor-free (batch-level) auditor* (Level A) holds no value of the
baseline view. It holds a null model $P_0$ of $V_{\mathcal I}$ over clean
batches (the calibration draws of Gate N) and decides with a calibrated test
at budget $\alpha$. For a separable $a$ the detection probability is the power
of the test against the shift $V_{\mathcal I}(s_a)$ relative to the null
variability of fresh batches; it is generally below one, and it is *not*
implied by separability.

(c) A *post-hoc certifier* recomputes a view from inputs it trusts (e.g. the
evaluation/report contract recomputes $R$ from $(\hat y, y)$) and compares
with the reported value. It needs trusted inputs and re-execution capability
rather than a stored reference, and it certifies consistency of the report
with those inputs, not authenticity of the inputs.

**Proposition 4 (separability is necessary; anchoring makes it sufficient).**
(i) For any auditor whose decision is a function of $V_{\mathcal I}(s)$ (and a
seed included in the view), $a \in B_{\mathcal I}(\mathcal A)$ implies
$\mathrm{fire}(s_a) = \mathrm{fire}(s_0)$: on every batch the decision on the
intervened state is the decision on the clean state, so over any design the
calibrated detection rate equals the false-alarm rate. (ii) A
reference-anchored auditor of class (a) detects every
$a \notin B_{\mathcal J}(\mathcal A)$, deterministically.

*Proof.* (i) is Lemma 1 applied to the decision function. (ii) is Definition
5(a) with $d = 0$ iff equal. $\square$

**Corollary 3 (which reference certifies which integrity).** Let $a \in T_y$
with $f$ fixed and deterministic.
(a) *Conclusion and aggregate integrity, Level B suffices.* With a trusted
aggregate reference $M_0 = M(s_0)$ of the same batch, the rule "fire iff
$M(s_a) \ne M_0$" detects every $a$ that violates aggregate integrity and, by
Proposition 3, every material $a$. A trusted $R_0$ detects every material
$a$ and nothing else.
(b) *Item-identity integrity, Level C is necessary.* Any reference that
factors through $M$, $\mathrm{hist}(y)$ or $R$ is invariant under every
relabeling that permutes labels among items with equal predictions; such
relabelings (counterexample C1) violate item-identity integrity, so no
Level-B reference detects them. A Level-C reference (item-aligned $y_0$)
detects every non-identity relabeling.

*Proof.* (a) Proposition 4(ii) with $\mathcal J = \mathcal I_M$, then
Proposition 3. (b) A swap of $y_i, y_j$ with $\hat y_i = \hat y_j$ moves one
item from cell $(\hat y_i, y_i)$ to $(\hat y_i, y_j)$ and another from
$(\hat y_j, y_j)$ to $(\hat y_j, y_i)$; the two moves cancel in $M$, hence in
every function of $M$, and the histogram is unchanged. The item-indexed tuple
differs in positions $i$ and $j$. $\square$

In the frozen evidence, (a) is the 2,617/2,617 detection of material label
rows by the confusion-profile delta against the reference batch (and 2,792 of
3,600 label rows in total, witness W9), and (b) is the 808 relabelings with
zero confusion-profile delta that only the item-level label mismatch exposes
(W1 = W10). The batch-level $\mathcal I_{XFY}$ rule detects 16
(family-calibrated) or 43 (union) of the 2,617 material label rows: every one
of them is separable (Proposition 3), but a 2–10% relabeling of a 128-row
batch shifts the confusion profile by less than the profile's natural
variability across fresh clean batches. The value of a trusted reference of
the same batch is therefore informational: it replaces a statistical null
with an exact one. Which level is needed depends on the integrity notion:
conclusion and aggregate integrity need Level B; item-identity integrity
needs Level C. Neither is an oracle: each costs an uncontrolled copy of a
view of the baseline, i.e. provenance.

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

(b) *Family rule, theoretical guarantee.* Let $v_1, \dots, v_n$ be the sensor
vectors of the calibration draws and $v_{n+1}$ that of the audited batch. For
a family $F$ of sensors define the score of any vector $v$ as
$U(v) = \max_{j \in F} \#\{i \le n : v_{j,i} < v_j\}/n$ (the largest
calibration rank score over the family; ties count against firing), and let
$q$ be the $k$-th smallest of $U(v_1), \dots, U(v_n)$ with
$k = \lceil (n+1)(1-\alpha) \rceil$. If the $n+1$ draws are exchangeable, then
$$\Pr_0[U(v_{n+1}) > q] \;\le\; \frac{n+2-k}{n+1} \;\le\; \alpha + \frac{1}{n+1}.$$
For $n = 200$, $\alpha = 0.05$: $k = 191$ and the bound is $11/201 = 0.0547$.
For a single sensor the rule "fire iff $U(v_{n+1}) > q$" coincides with
"fire iff $v_{n+1}$ exceeds the $k$-th smallest calibration value", whose
exact exchangeable level is $(n+1-k)/(n+1) = 10/201 = 0.0498$; the extra
$1/(n+1)$ in the family bound comes from the calibration draws being ranked
against the other $n-1$ draws while the audited batch is ranked against all
$n$.

(c) *Design actually used and empirical deviation.* Gate F uses exactly the
rule of (b) with $n = 200$ calibration draws per (environment, dimension,
model) cell and evaluates it on 200 disjoint evaluation draws of the same
cell. The 20 draws of one run are overlapping simple random subsets of one
pool half, and the calibration and evaluation halves are different rows of
the same staged table, so the exchangeability premise of (b) does not hold
exactly. The observed pooled false-alarm rates are 0.061 ($\mathcal I_X$),
0.073 ($\mathcal I_{XF}$), 0.048 ($\mathcal I_{Y_m}$, whose two sensors are
monotone transforms of each other, so union and family coincide) and 0.079
($\mathcal I_{XFY}$), against 0.125, 0.203, 0.048 and 0.259 for the union
rule on the same draws; per-environment cluster means range from 0.025 to
0.146. These numbers measure the violation of the premise; they are not
evidence that the bound holds in deployment.

*Proof.* (a) The union contains each $E_j$, which gives the lower bound;
Boole's inequality gives the upper bound; the attainment statements are the
standard nested, disjoint and independent constructions, and the inclusion
–exclusion identity gives the product form under independence. (b) Let
$\tilde U_i$ be the score of draw $i$ computed against the *other* $n$ draws
of the augmented set $\{1, \dots, n+1\}$. Under exchangeability the
$\tilde U_i$ are exchangeable, so the rank of $\tilde U_{n+1}$ among the
$n+1$ scores is uniform up to ties, and
$\Pr[\tilde U_{n+1} \ge \tilde U_{(k)}] \le (n+2-k)/(n+1)$, where
$\tilde U_{(k)}$ is the $k$-th smallest of $\tilde U_1, \dots, \tilde U_n$
(ties count against firing and can only lower the probability). Now
$U(v_{n+1}) = \tilde U_{n+1}$ and, for $i \le n$, $U(v_i) \le \tilde U_i \le U(v_i) + 1/n$,
because the augmented comparison set adds one element. Hence
$q \ge \tilde U_{(k)} - 1/n$ and, on the grid $\{0, 1/n, \dots, 1\}$,
$\{U(v_{n+1}) > q\} \subseteq \{\tilde U_{n+1} \ge \tilde U_{(k)}\}$. The
single-sensor statement is the same argument with $U(v_i) = \tilde U_i$
exactly, since the audited batch's value is either above or below $v_i$ and
the rank of $v_i$ among the other $n$ is what the threshold uses. $\square$

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
requires at least one reference, commitment or channel that the declared
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

C1 shows that *item-identity violation* and *conclusion impact* are different
events: 808 relabelings leave every aggregate and the conclusion untouched,
and are visible only item-wise against a Level-C reference. C2–C4 separate
marginal invariance, confusion-matrix invariance and conclusion invariance.
C5–C6 separate representation, output and conclusion on the feature side.
C7 shows that the clipped "harm" endpoint of 1.1.x hid 433 label-path
conclusion changes; they are counted from 1.2.0 on. C8 is the empirical face
of Proposition 3, and W9/W10 the empirical face of Corollary 3.

## 6. The quantum branch in the same lattice

The quantum-workflow gate uses the same objects. Views of $\mathcal I_Q$: the
provenance view $h(C)$ (canonical circuit hash), the kernel view $K$, the
algebraic view $\mathrm{alg}(K)$ (symmetry, diagonal, minimum eigenvalue; a
coarsening of $K$), the repeated-estimation view, and the output view
$f_K(\tilde X)$ (a coarsening of $K$ through the decision).

- Approved transpilation: in $B_{K}$ (kernel unchanged) but not in $B_{h}$.
  Separability in the provenance view is not harm; the policy needs an
  approved equivalence class, implemented as semantic equality of probe
  kernels against a trusted reference (Level B: the reference kernel is an
  aggregate of the same inputs).
- PSD-preserving substitution: in $B_{\mathrm{alg}}$ (the coarsened view is
  invariant) but not in $B_{K}$. This is sensor-level blindness
  (insufficiency of the algebraic family), closed by a reference-anchored
  comparison with the trusted $K_0$ (Definition 5(a)).
- Output monitoring: in $B_{f}$ for every change that does not cross a
  decision boundary, although not in $B_K$: the output view is a coarsening.
- Hash chaining of the audit envelope: a local verifier of internal
  consistency; tamper-evident, but its root is writable by whoever controls
  the record and the verifier, so Proposition 6 applies and no authenticity
  relative to an external baseline is claimed.

## 7. What the formal core does and does not claim

It claims that auditability is a property of the triple (intervention class,
view, trusted references); that structural blind regions are monotone under
refinement and closed exactly by baseline-separating added views; that
material label-path interventions always change the confusion matrix and are
therefore separable in the joint view and detected exactly by a trusted
aggregate reference of the same batch, while item-identity integrity needs an
item-aligned reference; that a batch-level auditor without a reference
detects such changes only with statistical power; that decision-level
calibration requires calibrating the family rather than the sensors, with an
exchangeability bound of $\alpha + 1/(n+1)$ that the executed design violates
measurably; and that no verifier all of whose evidence the adversarial class
can rewrite establishes authenticity relative to a baseline. It does not
claim a general detectability theory beyond finite batches with a fixed
deterministic predictor, does not claim that the exchangeability premise
holds in deployment, does not claim identification of which intervention
occurred, and does not claim anything about interventions outside the
declared classes.
