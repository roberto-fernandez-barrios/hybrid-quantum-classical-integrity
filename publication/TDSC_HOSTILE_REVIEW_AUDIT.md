# Hostile-review audit — IEEE TDSC candidate

This file keeps the audits in reverse chronological order. Audit 4 (release
build) supersedes the verdicts below it; the earlier audits are retained as
history.

# Audit 4 — final mathematical and release review, artifact 1.2.0 (2026-09-07, release build)

Scope of this pass: correctness of the formal core, overclaim about trusted
references, authentication versus self-consistency, family calibration, the
signed-impact counts, novelty, the end-to-end policy, and release engineering.
Standard: attempt to reject; fix what breaks a claim; publish only when no
BLOCKER or reasonable MAJOR objection remains within scope.

## Executive verdict

**SCIENTIFICALLY CLOSED.** Three mathematical defects found in the 1.2.0
draft (M1–M3) were corrected, one overclaim (M4) was replaced by a sharper
three-level statement that strengthens the paper, and one headline-number
imprecision (M5) was fixed. After the corrections every proposition was
re-derived from scratch with a counterexample search (Section 2) and none
required further weakening. Remaining objections are MINOR or belong to
Paper 2.5. Release 1.2.0 proceeds.

## 1. Defects found and their disposition

| ID | Objection | Class | Disposition |
|---|---|---|---|
| M1 | Proposition 5 stated that the union of $m$ events each of probability $\le\alpha$ has probability in $[\alpha,\min(1,m\alpha)]$ with the upper bound attained under independence. Both parts are false in general: without some $p_j=\alpha$ the lower bound is $\max_j p_j$, which can be $0$; the upper bound $m\alpha$ is attained by disjoint events, and independence gives $1-(1-\alpha)^m$, strictly inside the bounds. | **BLOCKER (false statement)** | **Fixed.** Prop. 5(a) now states $\max_j p_j\le P(\bigcup E_j)\le\min(1,\sum_j p_j)\le\min(1,m\alpha)$, the equal-probability case with its attaining constructions (nested / disjoint), and the independence formula; main text, supplement, `FORMAL_CORE.md`. |
| M2 | Proposition 5's family guarantee claimed $\Pr_0[U>q]\le\alpha$ under exchangeability, but the calibration rank scores are computed against the other $n-1$ draws while the audited batch is ranked against all $n$; the scores are not exactly exchangeable. | MAJOR (overstated guarantee) | **Fixed.** Prop. 5(b) now proves $\Pr_0[U(v_{n+1})>q]\le(n+2-k)/(n+1)\le\alpha+1/(n+1)$ via the augmented-set scores $\tilde U_i$ ($0.0547$ for $n=200$), notes the exact single-sensor level $10/201$, and Prop. 5(c) separates the theoretical premise from the executed design (overlapping draws, different halves) and the observed deviation (0.061–0.079). |
| M3 | Proposition 6 claimed that a consistent rewrite of asset and reference makes the augmented view equal to the baseline view; false in general and contradicted by Prop. 3. | **BLOCKER (false statement)** | **Fixed.** Prop. 6 is now an impossibility result for local verifiers: under honest completeness and joint control, the substituted pair is observationally an honest run of the substituted state, so acceptance cannot establish authenticity relative to the baseline; the converse (an uncontrolled root separates exactly the classes it separates) is Prop. 4(ii). It is explicitly about authenticity, not consistency. |
| M4 | "Material label corruption is detectable at will only against an item-aligned trusted reference" is too strong: a trusted confusion-matrix reference of the same batch detects every material change exactly (Prop. 3). | MAJOR (overclaim) | **Fixed and turned into a result.** Three levels (A batch-level statistical; B trusted aggregate; C trusted item-aligned) and three integrity notions (conclusion, aggregate, item-identity) are defined; Corollary 3 proves that level B suffices for conclusion and aggregate integrity and that level C is necessary for item identity (C1). Witnesses W9 (2,792 of 3,600 label rows, all 2,617 material ones, detected by the aggregate reference) and W10 (808 detected only item-wise) were added to the evidence and the table generator. Abstract, introduction, Sections III-B/III-D/V/VI, Discussion, Conclusion, README, cover letter, threat-model card, adversary model, result summaries and claims map were rewritten accordingly. |
| M5 | The abstract summarized Gate F as lowering the false-alarm rate of "batch-level regimes" from 0.125–0.259 to 0.061–0.079, but the label-marginal regime stays at 0.048. | MAJOR (headline number) | **Fixed.** Abstract: "For regimes with feature evidence … from 0.125–0.259 to 0.061–0.079; the label-marginal regime stays at 0.048." Same wording in README, cover letter; changelog and release notes already listed the four rates. |
| M6 | Proposition 2 called the closing condition "injective on the orbit", but only baseline separation ($V_W(a(s_0))\ne V_W(s_0)$) is required; injectivity would be an identification condition. | MINOR (terminology with mathematical content) | **Fixed.** "Baseline-separating on the intervention orbit" is defined and used; pairwise separation (identification) is defined and explicitly not claimed; all occurrences of "injective" and "separates the orbit" replaced. |
| M7 | Release engineering: the pipeline did not realign `main`, committed release ZIPs and the draft state, and would have shown the concept DOI twice. | MAJOR (release integrity) | **Fixed.** Fail-closed Git checks (clean tree, expected branch, tag absence, remote branch ancestor, `main` fast-forwardable, no force), explicit fast-forward of `main`, post-push SHA verification, `.gitignore` for release assets, old tracked ZIPs removed from the tree, source-ZIP content check (no nested ZIP, no draft state, no token marker), RELEASE_STATUS reports "not yet minted" until the version DOI differs from the concept DOI, and the insert step aborts if they coincide. |

## 2. From-scratch review of the formal core (counterexample search)

| Statement | Attack tried | Outcome |
|---|---|---|
| Lemma 1 | randomized sensor with a fresh seed | pointwise identity fails; statement restricted to deterministic / seeded-in-view sensors, with equality in distribution for independent fresh seeds |
| Definition 3 / sufficiency | family that separates some but not all orbit points | equality $B_{\mathcal I}=B_{\mathcal I,\mathcal S}$ holds iff baseline-separating; pairwise separation not needed; corrected wording |
| Proposition 1 | $\mathcal I'$ that refines $\mathcal I$ but with a non-injective $\pi$ | inclusion direction is right: the refined view equal implies the coarse view equal; no counterexample |
| Corollary 1 | stochastic predictor | hypothesis "fixed deterministic $f$" is stated and necessary; with a stochastic $f$ the prediction multiset could change even without a label change |
| Proposition 2 | intervention that changes $\mathcal W$ but not $\mathcal I$ | separable in the join, consistent with the intersection formula; "iff" holds |
| Corollary 2 | duplicate rows | relabelings among identical $(\tilde x,\hat y)$ items are invisible to the multiset view; stated explicitly; such relabelings are immaterial by Prop. 3 |
| Proposition 3 | a metric that is not a function of $M$ (e.g. ROC-AUC) | hypothesis $R=g(M)$ stated; balanced accuracy satisfies it; claim not extended to score-based metrics |
| Proposition 4(i) | auditor that uses a stored seed | seed in the view; covered by Lemma 1 |
| Proposition 4(ii) | pseudo-metric $d$ | $d$ must satisfy $d=0$ iff equal; stated |
| Corollary 3(a) | trusted $R_0$ only | detects material changes and nothing else; stated |
| Corollary 3(b) | aggregate finer than $M$ (e.g. per-class score histograms) | still permutation-invariant within equal-prediction items; C1 remains invisible; stated for references that factor through $M$, hist or $R$ |
| Proposition 5(a) | dependent events | bounds are tight only in the stated constructions; no counterexample |
| Proposition 5(b) | ties; in-sample ranks | ties count against firing; in-sample asymmetry bounded by $1/n$ in score and $1/(n+1)$ in level; proof via augmented scores |
| Proposition 5(c) | "the bound holds in deployment" | not claimed; the executed design violates exchangeability and the observed rates are reported as the deviation |
| Proposition 6 | verifier with a fixed stored baseline value | that is an uncontrolled root, excluded by the joint-control assumption; covered by the converse |
| Proposition 6 | verifier that rejects some honest states | honest completeness is an explicit assumption; without it the claim is not made |

## 3. Signed-impact counts, family calibration and policy (re-verified)

- Signed label-path counts 2,184 / 983 / 433 (Gate 1: 1,276 / 105 / 59) are recomputed by the verifier; all 2,617 changed conclusions have non-zero confusion evidence (W8).
- Gate F rates 0.125 / 0.203 / 0.048 / 0.259 → 0.061 / 0.073 / 0.048 / 0.079; family ≤ union in every regime (verifier check); per-environment cluster means 0.025–0.146.
- Gate D unsafe allows 4,494 / 4,327 / 7,008 / 4,322 / 0; trusted regime 0 false holds; composition 6/6.
- W9 = 2,792 and W10 = 808 added; W1 = W10 by construction.

## 4. Residual objections (no action)

| Objection | Class |
|---|---|
| Formal results are elementary. | MINOR: stated as such in Section III; the contribution is the characterization and its measured consequences. |
| Family rule exceeds nominal (0.061–0.079). | MINOR: reported as executed with its cause; Prop. 5(c) separates premise, design and deviation. |
| Equal-weighted suite; τ = 0⁺ materiality. | MINOR: stress profile, sensitivity at 0.02 / 0.05 in the supplement. |
| Simulator only, 128/128, fixed environments, no QPU, no scheduler, no attestation, no Fleet Management, no runtime recalibration. | OUT OF SCOPE / PAPER 2.5. |
| Overlap with QCIVET / QML-PipeGuard / companion papers. | MINOR: positioned and disclosed. |

Verdict: no BLOCKER, no reasonable MAJOR within scope. **Paper 1.5 v1.2.0 is scientifically closed.**

---

# Audit 3 — artifact 1.2.0 (2026-09-07)

Manuscript: `publication/tdsc/main.tex` (retitled *Observational
Indistinguishability and Integrity Blind Regions Across the Evidence
Boundaries of Hybrid Quantum-Classical Kernel Workflows*)  
Supplement: `publication/tdsc/supplement.tex`  
Artifact: 1.2.0 (six evidence manifests; counts in `publication/RELEASE_STATUS.md`)  
Standard: attempt to reject; classify every objection as BLOCKER, MAJOR,
MINOR or OUT OF SCOPE / PAPER 2.5; fix what breaks a claim; repeat until no
BLOCKER or reasonable MAJOR remains within scope.

## Executive verdict

**No BLOCKER and no reasonable MAJOR objection remains within the declared
scope.** The audit found one correctness defect in the new text (H1, fixed),
one finite-sample subtlety in a proof (H2, fixed by an explicit remark), one
presentation risk (H3, fixed), and confirmed the prior audit finding that
drove amendment A1 (the clipped "harm" endpoint). Two objections are
classified MAJOR-if-unaddressed but are addressed by explicit statements in
the manuscript (H4, H5). Everything else is MINOR or belongs to Paper 2.5.

Residual editorial risk is discussed at the end. **Recommendation: proceed to
release 1.2.0 and submission.**

## 1. Objections found in this audit and their disposition

| ID | Objection (as a hostile reviewer would write it) | Class | Disposition |
|---|---|---|---|
| H1 | "The abstract says batch-level regimes serve 4,322–4,494 of 7,008 material results, but your own Table 5 shows the label-marginal regime, which is batch-level, serves all 7,008." | **MAJOR (correctness of a headline number)** | **Fixed.** Abstract, supplement claims matrix, README, cover letter, changelog and release notes now say "batch-level regimes with feature evidence serve 4,322–4,494 … the label-marginal regime serves all of them, the trusted item-aligned regime serves none". |
| H2 | "Proposition 5 claims the conformal bound, but the rank scores of the calibration draws are computed in-sample (against the other n−1 draws) whereas the audited batch is compared against all n; the scores are not exactly exchangeable." | MINOR (formal precision) | **Fixed.** The supplement proof now states the asymmetry, bounds it by 1/n in the score and 1/(n+1) in the level (0.005 at n = 200), and notes that it is far below the observed excess. |
| H3 | "Lemma 1 and Propositions 1–3 are trivial; dressing them as a formal core inflates the contribution." | MINOR (presentation) if stated; MAJOR if hidden | **Fixed.** Section III now opens by stating that the results are elementary by design and that their role is to make exact which evidence separates which class so that the gates test statements rather than intuitions; the introduction already says no constituent is standalone novelty. |
| H4 | "The family-calibrated rule does not reach the nominal 0.05 (0.061–0.079 pooled; up to 0.146 per environment). Your calibration does not work." | MAJOR if presented as achieved; addressed | The manuscript reports the excess as executed, records that the preregistered expectation was met only approximately, attributes it to overlapping draws and to calibration/evaluation halves being different rows, and does not claim the bound holds in deployment. The rule still lowers the decision false-alarm rate by a factor 2–3.3 at a containment cost of 0.01–0.02. A design with disjoint draws would need larger pools; it is stated as a limitation, not hidden. |
| H5 | "The earlier version said 'no negative impact occurs'; now 433 label corruptions raise the metric. Was the earlier statement wrong?" | MAJOR if unexplained; addressed | Yes, and the manuscript says so: the earlier column was the positive part of the signed change (amendment A1 in the 1.2.0 preregistration, changelog, release notes, cover letter). The 2,184 count is unchanged and is a subset of the 2,617 material rows; all 2,617 carry item-aligned confusion evidence; the verifier recomputes the signed counts. The correction strengthens rather than weakens the claim (an apparent improvement caused by corruption is a conclusion change). |
| H6 | "Unsafe allow depends on the equal-weighted suite; three fifths served is not a deployment number." | MINOR | Stated: equal weighting is a stress profile, not a threat distribution; the Discussion says "in this suite"; materiality sensitivity at 0.02 and 0.05 is in the supplement. |
| H7 | "The strict policy P3 is a straw man: it holds everything in three regimes." | MINOR | It is presented as making information-set conditionality literal, not as a recommended operating point; the choice between P2 and P3 is described as a declared risk decision. |
| H8 | "The policy layer is evaluated offline on frozen outputs, not inside the running prototype." | MINOR | The composition with the six frozen contract envelopes reproduces every action (D5); a runtime integration would add engineering, not evidence. The policy function is pure and transport-agnostic. |
| H9 | "The trusted item-aligned regime is an oracle." | MINOR (already addressed) | Section III-D and Proposition 6 state that it is a trust assumption with a cost (an item-aligned copy of the baseline view) and no guarantee if the reference can be rewritten with the asset; the contrast with batch-level detection is presented as the informational value of provenance. |
| H10 | "Who corrupts evaluation labels? The threat is contrived." | MINOR | The adversary model maps the classes to corruption of the ground-truth store or of the label join, cites pervasive test-set label errors and evaluation blindness, and never estimates prevalence. |
| H11 | "Mean shift and scaling are detected at 100% only because of duplicate-row clusters; an adaptive attacker evades this." | MINOR (already disclosed) | Disclosed in Results, Table 3 (cluster-preserving perturbation, discussed but not executed) and Limitations. |
| H12 | "128/128 samples, balanced staging, simulators." | OUT OF SCOPE / disclosed | Limitations state them; the exact claims do not depend on them. |
| H13 | "No QPU, no scheduler, no provider attestation, no multi-tenancy, no Fleet Management." | OUT OF SCOPE / PAPER 2.5 | The claim is delimited and the boundary with Paper 2.5 is explicit in the manuscript, the traceability matrix and the roadmap. |
| H14 | "Another dataset / more seeds would strengthen the generalization claim." | OUT OF SCOPE | No generalization beyond the eight fixed environments is claimed; the exact results are structural. |
| H15 | "Overlap with QCIVET / QML-PipeGuard." | MINOR | Positioned in §II-C and Table 1 by unit of analysis (quantum stage / pipeline trace versus information set with the label path as a boundary); no priority claim on contracts, hashes or semantic probes. |
| H16 | "Overlap with the companion collider paper (information-conditional auditor)." | MINOR | Disclosed in §II-D with the difference (certification of a scientific claim under benign systematics versus integrity of the evidence chain under interventions, with trusted references, calibrated policy and executable response); no shared propositions, interventions, tables or experiments. |
| H17 | "The formal section uses multiset views; near-duplicate rows (ToN-IoT) make some relabelings structurally invisible even in the joint view." | MINOR | Corollary 2 states exactly this case (permutations among items with identical (x̃, ŷ)); such relabelings are immaterial (Proposition 3), and the near-duplicate fraction is reported in the supplement's cluster table. |
| H18 | "The dependence structure of the null draws is only partly addressed." | MINOR | The inference unit is now the (environment, split) cluster with five-cluster t intervals per environment; pooled rates and the 1.1.0 binomial intervals are declared descriptive; the number of mutually disjoint batches per pool half is tabulated. |

## 2. Consistency checks performed

- Every number of the 1.2.0 gates printed in the article enters through
  generated macros; the manuscript source contains no hand-typed policy
  number. Spot checks: family FPR 0.061/0.073/0.048/0.079; union
  0.125/0.203/0.048/0.259; unsafe allows 4,494/4,327/7,008/4,322/0; witnesses
  808/2,617/1,059/175/296/2,513/1,534/2,617; signed counts 2,184/983/433 and
  1,276/105/59; 24,000 = 12,000 + 1,200 + 10,800.
- Table 3 rates cross-checked against `family_detection_pooled.csv` and
  `family_benign_control_response.csv`.
- Abstract within 150–250 words; five index terms; all citations resolve; no
  overfull box above 1 pt; main article below the 12-page ceiling.
- Verifier: six manifests, 65 outputs, signed label counts, policy claims,
  artifact-wide manifest; tests green; dataset hashes verified (24/24).
- No placeholder (`INSERT`, `DOI PENDING`, `Anonymous Author`), no
  machine-specific path in any active document, script or evidence table;
  historical drafts archived and marked non-authoritative.

## 3. Reject-risk assessment

- **Desk-reject risk: low.** The paper opens as an assurance-under-partial-observability
  paper for TDSC, with an explicit security model and an end-to-end decision
  endpoint.
- **Novelty risk: moderate.** A reviewer who values only new mechanisms may
  find the formal results elementary and the calibration method standard. The
  manuscript concedes both and rests the contribution on the characterization
  and its executable, measured consequences; the positive delimitation against
  CPS stealth theory, runtime assurance, integrity monitoring, evaluation
  integrity and quantum pipeline integrity is explicit.
- **Statistical-validity risk: low-moderate.** The residual excess of the
  family rule over nominal is the most likely point of attack; it is reported,
  explained and bounded by the design rather than hidden.
- **Realism risk: moderate, out of scope.** Simulator-only, small batches,
  fixed environments; declared and consistent with the claim.
- **Overall: a defensible Q1 submission whose main risk is editorial taste
  about the balance between formal characterization and mechanism novelty,
  not a correctable omission within the declared paper.**

---

# Audit 2 — rc2 addendum (2026-09-06)

Two of the residual risks listed in Audit 1 ("non-zero response is not
calibrated detection power" and "the ZZ-versus-SVC profile is confounded by
preprocessing and untuned baselines") were addressed after freezing by three
preregistered sensitivity gates (`manuscript/paper15_v11_reinforcement_prereg.md`),
executed on the frozen seeds with the exact-statevector engine and reported as
executed. The central claim, the abstract counts and every 1.0.0 table were
unchanged. Additional desk-review defences added in rc2: QML-PipeGuard and
the evaluation-blindness preprint positioned; the three companion manuscripts
disclosed; author block, affiliation and funding footnote in place;
generative-AI disclosure naming both systems.

---

# Audit 1 — artifact 1.0.0 / rc1 (2026-08-10)

**Scientifically submission-ready for a regular-paper attempt at IEEE TDSC**
under the 1.0.0 claim (information-set conditional integrity auditing): exact
blind regions, sensor coverage, multi-dataset/fixed-OOD validation, bounded
quantum layer and fail-closed enforcement as one contribution; administrative
gates (authors, ORCIDs, CRediT, funding, license, DOI) open at the time.
Residual risks recorded then: "guarantees depend on observables" may be
called intuitive; non-zero sensor response was not calibrated power; the
ZZ-versus-SVC profile was confounded by preprocessing. All three were
addressed in 1.1.0 and 1.2.0. The numerical checks of that audit (7,980 →
4,560; 13,680 → 11,400; 360/360; 165/165; 6/6; 3,600/1,800/2,184; 1,440/720/1,276)
remain valid, with the 1.2.0 qualification that 2,184 is the count of
lowered conclusions and 2,617 the count of changed conclusions.
