# Formal core — observational indistinguishability and integrity blind regions (artifact 1.2.0)

Version 1.0 (2026-09-07). This document is the complete statement, with proofs,
of the formal section of the TDSC article. The article prints the definitions
and the propositions; the supplement reproduces this file. Every witness count
quoted here is generated from the manifested table
`counterexample_witnesses.csv` (Gate D) and printed in the article through
`publication/tdsc/tables/policy_macros.tex`.

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
$R : \mathcal S \to \mathbb R$, here balanced accuracy of $\hat y$ against $y$.
The signed conclusion change is $\Delta_R(a) = R(s_0) - R(s_a)$. An
intervention is *material at level* $\tau$ if $|\Delta_R(a)| \ge \tau$;
$\tau \to 0^{+}$ means "any change of the reported conclusion". The positive
part $\max(\Delta_R, 0)$ is the "harm" endpoint of artifacts 1.0.0–1.1.1; the
signed definition is used from 1.2.0 because an apparent improvement caused
by an integrity failure is a conclusion change (witness W7 below).

## 2. Information sets, views and trusted references

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

**Trusted references.** A reference is a stored value $\rho = V_{\mathcal J}(s_0)$
of some view of the baseline. It is *trusted* under assumption
$\mathsf T(\rho)$: no intervention in the class under study can alter $\rho$
(it is authenticated, or held by a party outside the adversary's reach). It is
*item-aligned* when $V_{\mathcal J}$ is item-indexed (a tuple indexed by item
identity) rather than a multiset, so that $\rho$ supports item-wise
comparison. An auditor with regime $\mathcal I$ and reference $\rho$ observes
$(V_{\mathcal I}(s), \rho)$. We write $\mathcal I^{\star}$ for a regime
augmented with a trusted item-aligned reference of its own view of $s_0$
(e.g. $\mathcal I_{XFY}^{\star}$ holds the reference triples of the same
items).

The distinction matters because a label being *available* to the auditor
says nothing about whether it is *trusted*: in $\mathcal I_{XFY}$ the auditor
sees labels, but if the label store is the asset under attack the labels it
sees are $y_a$, not $y_0$.

## 3. Observational equivalence, sensors and blind regions

**Definition 1 (observational equivalence).** $s \sim_{\mathcal I} s'$ iff
$V_{\mathcal I}(s) = V_{\mathcal I}(s')$.

**Definition 2 (sensor).** A sensor admissible in $\mathcal I$ is a measurable
map $S : \mathcal O_{\mathcal I} \to \mathbb R^k$; we write
$S(s) = S(V_{\mathcal I}(s))$. A sensor family $\mathcal S$ is a set of
admissible sensors.

**Lemma 1 (structural blindness).** If $s_a \sim_{\mathcal I} s_0$ then
$S(s_a) = S(s_0)$ for every sensor admissible in $\mathcal I$, deterministic
or randomized with a seed that is part of the view.

*Proof.* $S(s_a) = S(V_{\mathcal I}(s_a)) = S(V_{\mathcal I}(s_0)) = S(s_0)$:
a function evaluated on identical arguments. For a randomized sensor whose
seed is fixed and observable, the same holds path-wise; if the seed is fresh,
the *distribution* of $S(s_a)$ equals that of $S(s_0)$. $\square$

**Definition 3 (blind regions).** For a class $\mathcal A$ and baseline $s_0$,
the *structural blind region* of $\mathcal I$ is
$$B_{\mathcal I}(\mathcal A) = \{ a \in \mathcal A : a(s_0) \sim_{\mathcal I} s_0 \},$$
and the *sensor blind region* of a family $\mathcal S$ is
$$B_{\mathcal I, \mathcal S}(\mathcal A) = \{ a \in \mathcal A : S(a(s_0)) = S(s_0)\ \forall S \in \mathcal S \}.$$
By Lemma 1, $B_{\mathcal I}(\mathcal A) \subseteq B_{\mathcal I,\mathcal S}(\mathcal A)$,
with equality iff $\mathcal S$ separates the orbit
$\{V_{\mathcal I}(a(s_0)) : a \in \mathcal A\} \cup \{V_{\mathcal I}(s_0)\}$;
such a family is *sufficient* for $\mathcal A$ in $\mathcal I$. Sensor
blindness therefore decomposes into information-level blindness (the view is
identical) and sensor insufficiency (the view differs but the statistic does
not).

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
The inclusions follow. $\square$

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
Consequently a class $\mathcal A \subseteq B_{\mathcal I}(\mathcal A)$ is
completely separable after adding $\mathcal W$ iff
$V_{\mathcal W}(a(s_0)) \ne V_{\mathcal W}(s_0)$ for every $a \in \mathcal A$:
the added view must be injective on the orbit of $\mathcal A$ relative to
$s_0$. Necessity: if some $a$ leaves $V_{\mathcal W}$ unchanged it stays in
the joint blind region. Sufficiency: the joint view changes whenever either
component changes.

*Proof.* $(V_{\mathcal I}, V_{\mathcal W})(s_a) = (V_{\mathcal I}, V_{\mathcal W})(s_0)$
iff both components agree. $\square$

**Corollary 2 (what cannot close the label-path region).** With $f$ fixed and
deterministic, no view that factors through
$(\tilde X, f(\tilde X), \mathrm{hist}(y))$ can separate any $a \in T_y^{\pi}$
from $s_0$: $T_y^{\pi} \subseteq B_{\mathcal I_{XF} \vee \mathcal I_{Y_m}}$.
Closing the region requires a view that depends on the item-level assignment
of labels: the multiset of triples $\mathcal I_{XFY}$ separates
$a \in T_y^{\pi}$ unless $a$ permutes labels only among items with identical
$(\tilde x, \hat y)$, and the item-aligned reference $\mathcal I_{XFY}^{\star}$
separates every non-identity relabeling.

**Proposition 3 (materiality forces separability in the joint view).** Let
$R = g(M)$ be a function of the confusion matrix
$M(s) = (\#\{i : \hat y_i = u, y_i = v\})_{u,v}$, as balanced accuracy is. If
$a \in T_y$ and $\Delta_R(a) \ne 0$, then $M(s_a) \ne M(s_0)$, so
$a \notin B_{\mathcal I_{XFY}}(T_y)$ and $a \notin B_{\mathcal I_M}(T_y)$ where
$\mathcal I_M$ is the confusion view. Hence
$G_{\mathcal I_{XFY}}(\tau) \cap T_y = \emptyset$ for every $\tau > 0$: the
material label-path gap is empty in the joint view.

*Proof.* Contrapositive of $M(s_a) = M(s_0) \Rightarrow R(s_a) = R(s_0)$. The
confusion view is a coarsening of the multiset of triples. $\square$

Proposition 3 is realised without exception in the frozen expansion: all
2,617 label-path observations whose balanced accuracy changed have a non-zero
confusion-profile delta (witness W8). It is also the reason why the
batch-level $\mathcal I_{XFY}$ result (Section 4) is a statement about
*detectability*, not *separability*.

## 4. Three auditor classes

**Definition 5.** Relative to a regime $\mathcal I$ and a class $\mathcal A$:

(a) A *reference-anchored (item-aligned) auditor* holds a trusted item-aligned
reference $\rho = V_{\mathcal J}(s_0)$ and computes $D(s) = d(V_{\mathcal J}(s), \rho)$
with a metric $d$. Then $D(s_0) = 0$ exactly and the rule "fire iff $D > 0$"
has false-alarm probability zero and detects every $a$ with
$V_{\mathcal J}(s_a) \ne \rho$: separability is sufficient for detection.

(b) An *anchor-free (batch-level) auditor* holds no value of the baseline
view. It holds a null model $P_0$ of $V_{\mathcal I}$ over clean batches (the
calibration draws of Gate N) and decides with a calibrated test at budget
$\alpha$. For a separable $a$ the detection probability is the power of the
test against the shift $V_{\mathcal I}(s_a)$ relative to the null variability
of fresh batches; it is generally below one, and it is *not* implied by
separability.

(c) A *post-hoc certifier* recomputes a view from inputs it trusts (e.g. the
evaluation/report contract recomputes $R$ from $(\hat y, y)$) and compares
with the reported value. It needs trusted inputs and re-execution capability
rather than a stored reference.

**Proposition 4 (separability is necessary; anchoring makes it sufficient).**
(i) For any auditor whose decision is a function of $V_{\mathcal I}(s)$ (and a
seed included in the view), $a \in B_{\mathcal I}(\mathcal A)$ implies
$\mathrm{fire}(s_a) = \mathrm{fire}(s_0)$: the decision on the intervened
state is the decision on the clean state, so the calibrated detection rate
equals the false-alarm rate. (ii) For a reference-anchored auditor of class
(a), $a \notin B_{\mathcal J}(\mathcal A)$ implies detection with probability
one.

*Proof.* (i) is Lemma 1 applied to the decision function. (ii) is Definition
5(a). $\square$

In the frozen evidence, (i) is the calibrated label-path result (zero fires
of the calibrated $\mathcal I_X$, $\mathcal I_{XF}$ and, for $T_y^{\pi}$,
$\mathcal I_{Y_m}$ rules on 3,600 / 1,800 observations), and (ii) is the
2,617/2,617 item-aligned detection. The batch-level $\mathcal I_{XFY}$ rule
detects 16 (family-calibrated) or 43 (union) of the 2,617 material label
rows: every one of them is separable (Proposition 3), but a 2–10% relabeling
of a 128-row batch shifts the confusion profile by less than the profile's
natural variability across fresh clean batches. The value of the item-aligned
reference is therefore informational: it replaces a statistical null with an
exact one, and this is what the 2,617/2,617 versus 0.6–1.6% contrast
measures. It is not an oracle: it costs a trusted, item-aligned copy of the
baseline view, i.e. provenance.

**Proposition 5 (union versus family calibration).** Let $S_1, \dots, S_m$ be
sensors each calibrated so that $\Pr_0[S_j > t_j] \le \alpha$ under the null.
The union rule "fire iff some $S_j > t_j$" has null firing probability in
$[\alpha, \min(1, m\alpha)]$, with the upper bound attained under
independence and the lower bound under perfect dependence. Let
$U = \max_j F_j(S_j)$ where $F_j$ is the calibration distribution of $S_j$,
and let $q$ be the $\lceil (n+1)(1-\alpha) \rceil$-th smallest value of $U$
over $n$ calibration draws. If the calibration draws and the new batch are
exchangeable, $\Pr_0[U > q] \le \alpha$.

*Proof.* The union bounds are Boole's inequality and monotonicity. The family
statement is the standard exchangeability argument for an order-statistic
threshold of a scalar score (Vovk et al. 2005; Westfall and Young 1993 for the
max-statistic construction): among $n+1$ exchangeable scores, the new one
exceeds the $\lceil (n+1)(1-\alpha) \rceil$-th smallest of the others with
probability at most $\alpha$; ties count against firing, which only lowers the
probability. $\square$

The exchangeability premise is the part that the study can only check
empirically. The 20 draws of one run are overlapping subsets of one pool half,
and the calibration and evaluation halves are different rows of the same
staged table, so the 1.2.0 evaluation-half rates (0.061–0.079 pooled;
0.025–0.146 per environment) measure the size of the violation rather than
confirm the bound. The uncalibrated union rule stays at 0.125–0.259 on the
same draws.

**Proposition 6 (no local guarantee without an uncontrolled root).** Suppose
the intervention class acts jointly on the state and on the reference,
$a : (s, \rho) \mapsto (a(s), V_{\mathcal J}(a(s)))$, i.e. the adversary can
rewrite the reference consistently with the asset. Then the augmented auditor
$(V_{\mathcal I}, \rho)$ is a function of the state alone,
$V_{\mathcal I \vee \mathcal J}$, and Lemma 1 and Propositions 1–4 apply to
$\mathcal I \vee \mathcal J$: every $a \in T_y^{\pi}$ with $\mathcal J$
factoring through $(\tilde X, f(\tilde X), y)$ satisfies
$a \in B_{\mathcal I_{XFY} \vee \mathcal J}$ for the joint attack, because the
rewritten reference equals the rewritten view. No sensor admissible to that
auditor separates the attack from the baseline. Local identification of a
label-path intervention therefore requires at least one item-aligned root
that the intervention class cannot write.

*Proof.* Substitute $\rho_a = V_{\mathcal J}(s_a)$ into Definition 1 for the
joint view. $\square$

This is the formal content of the sentence "if an adversary can replace both
an asset and every trusted reference used to authenticate it, the present
local contract cannot identify the event", and it is why the study reports
$\mathcal I_{XFY}^{\star}$ as a regime with an explicit trust assumption
rather than as a stronger detector.

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

C1 shows that *integrity violation* (the labels are not the labels) and
*conclusion impact* are different events: 808 relabelings leave every
batch-level statistic and the conclusion untouched, and are visible only
item-wise against a trusted reference. C2–C4 separate marginal invariance,
confusion-matrix invariance and conclusion invariance. C5–C6 separate
representation, output and conclusion on the feature side. C7 shows that the
clipped "harm" endpoint of 1.1.x hid 433 label-path conclusion changes; they
are counted from 1.2.0 on. C8 is the empirical face of Proposition 3.

## 6. The quantum branch in the same lattice

The quantum-workflow gate of Section IV-C uses the same objects. Views of
$\mathcal I_Q$: the provenance view $h(C)$ (canonical circuit hash), the
kernel view $K$, the algebraic view $\mathrm{alg}(K)$ (symmetry, diagonal,
minimum eigenvalue; a coarsening of $K$), the repeated-estimation view, and
the output view $f_K(\tilde X)$ (a coarsening of $K$ through the decision).

- Approved transpilation: $a \in B_{K}$ (kernel unchanged) but
  $a \notin B_{h}$. Separability in the provenance view is not harm; the
  policy needs an approved equivalence class, implemented as semantic
  equality of probe kernels against a trusted reference.
- PSD-preserving substitution: $a \in B_{\mathrm{alg}}$ (the coarsened view
  is invariant) but $a \notin B_{K}$. This is sensor-level blindness
  (insufficiency of the algebraic family), closed by a reference-anchored
  comparison with the trusted $K_0$ (Definition 5(a)).
- Output monitoring: $a \in B_{f}$ for every $a$ that does not cross a
  decision boundary, although $a \notin B_K$: the output view is a coarsening.
- Hash chaining of the audit envelope: a reference-anchored comparison over
  the envelope itself; tamper-evident but not authenticated, i.e. the root is
  not assumed uncontrolled (Proposition 6 applies).

## 7. What the formal core does and does not claim

It claims that auditability is a property of the pair (intervention class,
view) refined by trusted references, that structural blind regions are
monotone under refinement and closed exactly by injective added views, that
material label-path interventions are always separable in the joint view
but detectable at will only with an item-aligned trusted root, and that
decision-level calibration requires calibrating the family rather than the
sensors. It does not claim a general detectability theory beyond finite
batches with a fixed deterministic predictor, does not claim that the
exchangeability premise holds in deployment, and does not claim anything
about interventions outside the declared classes.
