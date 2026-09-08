# Hostile-review audit — IEEE TDSC candidate

This file keeps the audits in reverse chronological order. Audit 7 is the
single final hostile pass for artifact 1.3.2; Audit 6 records the 1.3.1
formal/editorial correction and Audit 5 the frozen 1.3.0 scientific closure.
The earlier audits are retained as history. Audit 4's verdict
"SCIENTIFICALLY CLOSED" for
1.2.0 was withdrawn on the same day by amendment A2
(`manuscript/paper15_v13_prereg.md`): its Proposition 5(b) was false.

# Audit 7 — final evidence-alignment check, artifact 1.3.2 (2026-09-08)

Scope was fixed before this pass: taxonomy versus implementation; headlines
versus manifested evidence; reference trust assumptions; structural versus
statistical claims; aggregate versus item-aligned granularity; the adaptive
results; and TDSC formatting. New datasets, attacks, models, seeds, metrics,
QPU runs, hardware noise and conceptual extensions were excluded.

## Executive verdict

**ACCEPTABLE FOR TDSC SUBMISSION; NO OBJECTIVE BLOCKER REMAINS.** The 1.3.1
objection was correct: every selected Class-A result sensor uses the clean
version of the audited item set as a benchmark-protected oracle, although its
statistic is aggregate and does not use item pairing. The repository contains
historical training-reference feature sensors, but not a complete,
prespecified historical family for all four regimes. Repair B is therefore
the only defensible correction: Class A is a statistically thresholded
aggregate comparison with no demonstrated deployed authentication; B and C
are trusted exact invariants at aggregate and item-aligned granularity.
Version 1.3.2 changes no experimental result and reruns no experiment, job,
model, kernel, attack, seed or draw.

## Fixed-scope checks

| Check | Evidence and disposition |
|---|---|
| Taxonomy ↔ implementation | Fourteen selected sensors traced through runner, builders, selected lists, frozen CSVs and policy builders. The generated sensor-reference table records current/reference values, pairing, same-set use, harness protection, threat-model trust, historical/statistical semantics and compatible class. **Pass.** |
| Policy API and trust | Gate D / src/hsaas/policy.py consumes union, family and exact flags plus regime—not clean arrays. Upstream scoring needs the audited references. Benchmark protection is explicitly not deployed authentication. **Pass.** |
| Structural/statistical boundary | Corollaries 1–3 are contiguous; structural blind-region statements are separated from calibrated decision rates; τ→0+ is a structural-sensitivity endpoint. **Pass.** |
| Trusted-reference cost | Generated and verified: 85/1,200 gross exact blocks, 46 overlapping batch interruptions, and 39/1,200 net additional interruptions (3.25 percentage points); total trusted interruption 629. **Pass.** |
| Adaptive headline | Aggregate served rates are 38.85%, 28.06% and 29.43% in I_X/I_XF/I_XFY; the complete I_XFY matched-strength profile spans 22%–90%, with materiality and detection for every strength in the supplement. **Pass.** |
| Endpoint and I_Ym | “Unsafe allow” is retained only as a code/CSV variable and defined as a materially corrupted audit/report result served, not a malicious network event; I_Ym has zero containment and 5,450 residual-blind material cases. **Pass.** |
| Evidence granularity | The main constructive result is the minimum authenticated evidence granularity relative to the protected claim: a trusted aggregate can protect conclusion integrity; item-identity integrity requires item alignment. The external trust-root necessity is not presented as eliminated. **Pass.** |
| Units and denominators | The 24,000 observations are derived policy rows; inference resides at prespecified environment/split clusters. Batch clean decision FPR (12,000), trusted exact-zero checks (1,200) and near-null interruption (1,200) are separated. **Pass.** |
| Conformal and quantum claims | Finite-sample conformal level remains conditional on exchangeability; executed non-exchangeable FPR is descriptive. Quantum validation is ideal-statevector plus finite-shot emulation, with no hardware claim. **Pass.** |
| TDSC format | Authorful IEEEtran regular paper, 184-word abstract after macro expansion, 12-page main article, separate supplement, complete declarations and companion-paper disclosure. **Pass.** |

This is the final generative review of Paper 1.5. After publication, reopening
is limited to a portal/editor/reviewer requirement or an objective demonstrated
error; new science belongs to Paper 2.5.

# Audit 6 — final formal and editorial check, artifact 1.3.1 (2026-09-07)

Scope, fixed in advance and not widened: false statements, internal numerical
inconsistencies, figure readability, page and abstract limits, overclaims.
Formal review limited to definitions, state semantics, Proposition 7, the
reference taxonomy, the conformal wording and the P3 semantics
(`manuscript/FORMAL_REVIEW_1.3.1.md`). No experiment was re-audited from
scratch and none was executed; the science is frozen at 1.3.0. Requests for
more datasets, attacks, QPU, noise, FMS, alternative models, more seeds,
continuous datasets, optimized adversaries or new statistical methods are not
reasons to reopen and are recorded as limitations or Paper 2.5 items.

## Executive verdict

**EDITORIALLY CLOSED.** Twelve objective defects were found and fixed; none
changes a number of the frozen evidence. After the fixes the article is at 12
pages (the IEEE Computer Society limit for a Transactions regular paper,
references included; biographies are not required at submission), the
abstract is at most 250 words (CI-enforced), every headline number is printed
from a generated macro, no figure has overlapping titles or legends over data,
and every formal statement of the corrected core has a counterexample search
and a permanent test. No false statement, numerical inconsistency or
overclaim remains within the declared scope.

## 1. Defects found and their disposition

| ID | Objection | Class | Disposition |
|---|---|---|---|
| E1 | Proposition 7(iii) asserted `Pr[K̂ = K₀] = 0` under non-degenerate shot noise, hence "false-alarm probability one" for exact equality. False for a discrete estimator: fidelity 1/2 at two shots gives `Pr[K̂ = K₀] = 1/2`. | **False statement** | **Fixed** in article, supplement (with proof and the binomial arithmetic), formal core, threat card, adversary model, `tests/test_formal_core.py` comment; correct consequence stated (not an acceptance criterion; calibrated null or abstention; no claim otherwise); permanent test and regression guard. |
| E2 | Proposition 7 used one symbol `K` for the semantic kernel, the finite-shot estimate and the delivered matrix, so the inclusions were undefined across intervention classes; a PSD-preserving substitution of the delivered kernel cannot be seen by `h(C)` or by the semantic probe of the unchanged circuit, which the text glossed over. | **Formal inconsistency** | **Fixed**: `K_sem`, `K̂`, `K_obs`; classes (a)/(b)/(c); every inclusion names its class; the article explains why one anchored comparison against Φ(C₀) serves both roles in the ideal-statevector gate. |
| E3 | State `s = (X, P, C, K, E, f, y, R)` with `T_y` "fixing everything else" while `R` depends on `y`. | **Formal inconsistency** | **Fixed**: primitive/derived artifacts and overwrite/fix/recompute semantics; executable model `src/integrity/workflow_state.py`; tests. |
| E4 | Level A described as "no stored baseline value" although the batch-level sensors hold calibration draws, training-fitted preprocessing and null distributions. | **Overclaim (too strong)** | **Fixed**: Level A statistical/historical reference; Level B trusted aggregate same-batch; Level C trusted item-aligned same-batch; "no reference" never used for a batch-level auditor. |
| E5 | Abstract said the conformal rule "with an exact finite-sample level calibrates the regimes ... to 0.053–0.058", conflating the property under exchangeability with the executed, non-exchangeable result. | **Overclaim** | **Fixed** everywhere (abstract, contributions, related work, results, conclusion, claims matrix, README, cover letter, highlights, threat card); tests forbid "exactly calibrated" and an "exact level" sentence without its premise. |
| E6 | P3 named "strict fail-closed" although it abstains only on missing coverage and coincides with P2 (4,390 unsafe allows) in I_XFY; a reviewer could read "no unsafe allow whenever a sensor exists". | **Misleading name** | **Fixed**: coverage-complete abstaining; definition and the explicit absence of a minimum-power guarantee in code, `POLICY_CLASS`, evidence label (regenerated by the unchanged builders), tables, figures, article, supplement, documents; decisions unchanged. |
| E7 | Article Table 3, F5 row still typed "88--95\%" by hand (the generated range is 83–91 %); Audit 5 had marked H1 "fixed everywhere". | **Numerical inconsistency** | **Fixed** with the macros; `test_no_superseded_retention_range` scans every active document. |
| E8 | Discussion attributed "about half" of the benign interruption to exact provenance; the table gives 544 statistical holds (a cost P2 already pays: 590–654 in the batch regimes) and 85 exact-reference blocks, 629 of 1,200. | **Numerical misattribution** | **Fixed**: decomposition printed from new macros in abstract, results, discussion, figure caption and documents; verifier and tests check 544 + 85 = 629; "near-null synthetic controls", never operational benign traffic. |
| E9 | 3,600/3,600 exact invariants and "blind regions survive calibration" presented as findings; they are consequences of Corollary 1 and Proposition 4(i). | **Framing** | **Fixed**: validation checks; weight moved to material cases missed, unsafe-allow structure, aggregate vs item-aligned evidence, the adaptive attacker, the rule-bias/design-effect decomposition and the trusted-policy cost. |
| E10 | Abstract at 284 words (limit 250). | **Limit** | **Fixed**: 244 words after macro expansion; `test_abstract_has_at_most_250_words`. |
| E11 | Fig. 1: panel titles (b)/(c) overlapping, legend of (b) over the P0 points, legend of (c) over bars; Fig. 2: titles overlapping, legend over the dashed curves; quantum heatmap fonts scaled to about 3 pt. | **Figure readability** | **Fixed**: short titles, legends off the data (centre-right / below the axes), decomposition annotated, heatmap re-sized for a single column and moved to the supplement next to its table (main text keeps every number), supplement figures at full width. |
| E12 | Introduction lacked a concrete answer to "who corrupts evaluation labels and why does signing not solve it"; related work omitted VAMP; the positioning table used only axes favourable to this work. | **Positioning** | **Fixed**: one-paragraph scenario (reading aid, not incidence); VAMP positioned without artificial difference; nine-axis table showing where QCIVET, QML-PipeGuard and VAMP exceed this work. |

## 2. Consistency checks performed

- `tests/test_manuscript_consistency.py`: abstract ≤ 250 words; no `88–95`
  in any active document; `83`/`91` macros; 544 + 85 = 629 and 0.52 = 629/1,200
  in the macros; no "exactly calibrated"; every "exact level" sentence carries
  "exchangeab" or "premise"; no P3 sentence with "guarantee" without its
  negation; no "false-alarm probability one" / `Pr[K̂ = K₀] = 0` / "never
  reproducing the exact kernel" in the formal documents; reference taxonomy
  wording present; `POLICY_CLASS` string.
- `tests/test_workflow_state.py`: intervention recomputation semantics
  (label-only, feature, circuit, estimation, post-processing, mixed); the
  finite-shot counterexample and the binomial arithmetic.
- Verifier: `policy_trusted_benign_holds/blocks/interruptions` = 544 / 85 /
  629 recorded in `publication/RELEASE_STATUS.md`.
- Evidence: the policy and adversarial builders re-run into a scratch
  directory reproduced the frozen 1.3.0 tables byte for byte before the P3
  label change; after it, only `policy_class` strings differ in
  `policy_metrics.csv`, `policy_metrics_rule_comparison.csv`,
  `policy_taxonomy.csv` and `adversarial_policy_metrics.csv`.
- Layout: 12 main pages (12-page ceiling, references included, no
  biographies required at submission per the IEEE Computer Society author
  page checked on 2026-09-07); supplement reflowed for legibility; every page
  rendered and inspected.

## 3. Residual objections (recorded, not actionable in this paper)

- Novelty and significance remain the main reviewer risk (elementary formal
  core, standard conformal rule, NIDS datasets with duplicate clusters, thin
  quantum branch); the article states each of these limits itself.
- Anything that needs new evidence (more datasets or attacks, real QPU,
  calibrated noise, FMS slice, alternative models, more seeds, continuous
  datasets, an optimized adversary, a different statistical method) is a
  Paper 2.5 item or a reviewer-response item, not a reason to reopen 1.5.

# Audit 5 — final hostile review, artifact 1.3.0 (2026-09-07, scientific closure)

Scope of this pass: the replacement of Proposition 5(b) and its exhaustive
tests, amendment A2 and the regenerated Gates F and D, the executed adversarial
Gate A, the policy taxonomy and wording, the quantum branch as an instance of
the view lattice, every headline number of the abstract against the generated
macros and CSV tables, layout, and release hygiene. Standard: attempt to
reject; only a BLOCKER or a reasonable MAJOR objection within the declared
scope can stop the release; MINOR objections are fixed or recorded.

## Executive verdict

**SCIENTIFICALLY CLOSED.** The one false statement of 1.2.0 (Proposition 5(b),
asymmetric family rule; five-vector counterexample 0.60 against the claimed
0.40) is replaced by the full conformal max-rank p-value, whose level
⌊α(n+1)⌋/(n+1) = 10/201 is exact under exchangeability including ties
(proof in the supplement, weak-ordering enumeration and the counterexample as
permanent tests). The regenerated results are reported as executed, including
the parts that got worse for the earlier narrative (most of the 1.2.0 excess
was rule bias, not the design; E1 stays at 0.12 in every regime with feature
evidence). This pass found one MAJOR headline-number error and four MINOR
issues, all fixed before the release build; no BLOCKER or MAJOR objection
remains within scope. Release 1.3.0 proceeds; the paper is reopened only for
an objective error that invalidates a claim, an editorial requirement or a
reviewer request.

## 1. Defects found in this pass and their disposition

| ID | Objection | Class | Disposition |
|---|---|---|---|
| H1 | The abstract, supplement, README, changelog, release notes, cover letter, claims table, result summary, adversary model and status note said the adaptive attacker keeps "88–95 %" of the conclusion changes. The generated table `adversarial_evasion_ratios.csv` gives material-fraction ratios adaptive/control of 0.883 / 0.862 / 0.907 (mean shift 0.02 / 0.05 / 0.10) and 0.831 / 0.907 / 0.907 (scaling drift): the range is **83–91 %**. | **MAJOR (headline number)** | **Fixed everywhere.** The range is now generated as macros (`\AdvMatRetentionMinPct`, `\AdvMatRetentionMaxPct`) from the CSV and used in the article and supplement; the Markdown documents were corrected by hand and the slip is recorded in the result summary. |
| H2 | The abstract said the conformal rule calibrates "the multi-sensor regimes to 0.056–0.058", but the four regimes are 0.056 / 0.058 / 0.048 / 0.053; the label-marginal regime is already at the level and I_XFY is below 0.056. | MINOR (imprecise range) | **Fixed.** "Calibrates the regimes with feature evidence to 0.053–0.058" (macros `\FprFamilyIXFY`–`\FprFamilyIXF`); cover letter aligned. |
| H3 | The adaptive scaling-drift detection at strength 0.10 in I_X is exactly 339/600 = 0.565; the generated tables print 0.56 while the adversary table of the article, the adversary model, the threat-model card and the result summary said 0.57. | MINOR (rounding inconsistency) | **Fixed.** Prose aligned to the generated value; the article's adversary table now uses the macro. |
| H4 | The main article reached 13 pages after §II-C, Proposition 7, the Gate A methodology and the three-panel policy figure were added; a table* and the coverage heatmap sat in the main text while the supplement duplicated neither. | MINOR (layout, 12-page ceiling) | **Fixed.** Heatmap figure and adversarial table moved to the supplement (a coverage-only heatmap remains referenced from the supplement), text compressed without removing any number or boundary statement, premature column trigger removed; build passes with 12 + 16 pages and no overfull box above 1 pt. |
| H5 | The artifact README template still described the Gate D evaluation as "end-to-end" without "offline"; the supplement's environment tables overflowed the column. | MINOR (wording, layout) | **Fixed.** "Offline end-to-end" in the template; environment codes and compact intervals in the supplement tables. |

## 2. Re-verification of the formal core and of the executed numbers

- Proposition 5(b) (adopted rule): re-derived from scratch; the deterministic counting bound #{j : N_j ≤ k} ≤ k with k = ⌊α(n+1)⌋ holds for every weak ordering of the n+1 augmented scores, hence the level is exact under exchangeability of the calibration draws and the audited batch, with ties, marginally over the calibration set. No conditional guarantee is claimed. `tests/test_family_calibration_exhaustive.py` enumerates all weak orderings for small n and re-runs the five-vector counterexample against both rules; `tests/test_formal_core.py` brute-forces Lemma 1, Propositions 1–4, 6 and Corollaries 1–3 on finite state spaces (`manuscript/FORMAL_REVIEW_1.3.0.md`).
- Proposition 7 (quantum branch): the refinement chain provenance ⊐ semantic ⊐ algebraic ⊐ output is checked against the 165 simulator cells; the shot-noise statement (exact anchor has false-alarm rate 1 under any non-degenerate shot noise) is checked by the 256/1,024-shot rows of the gate.
- Gate F: 0.056 / 0.058 / 0.048 / 0.053 (conformal) against 0.061 / 0.073 / 0.048 / 0.079 (1.2.0) and 0.125 / 0.203 / 0.048 / 0.259 (union); rule bias +0.005 / +0.015 / 0 / +0.025, design effect +0.006 / +0.008 / −0.003 / +0.003; exchangeable re-splits 0.044 / 0.042 / 0.040 / 0.036 (conformal) and 0.052 / 0.058 / 0.040 / 0.059 (1.2.0); the verifier recomputes the level 10/201 from the frozen family scores and requires the re-split rates to lie within 0.005 of the level.
- Gate D: unsafe allows 4,496 / 4,365 / 7,008 / 4,390 / 0 of 7,008 under P2; trusted regime 544 held + 85 blocked of 1,200 benign controls (52 %); P3 holds everything in I_X, I_XF, I_Ym and coincides with P2 in I_XFY and I_XFY*; the six frozen envelopes reproduce their contract actions under the lattice maximum.
- Gate A: 240/240 jobs; the matched controls replay the frozen 1.1.1 observations exactly (max |Δ| = 0 on 4,200 rows); detection at matched strengths 0.01–0.34 (I_X) and 0.06–0.66 (I_XF) against 0.96–1.00; material retention 83–91 %; P2 serves 1,328 / 959 / 1,006 of 3,418 material adaptive rows, the trusted regime 0; classical branch more evasive than the quantum branch (0.30 / 0.34 against 0.37 / 0.58 at strength 0.10); perturbed-entry fraction 0.32 (0.12–0.55).
- Every number of the abstract is a macro generated from a manifested CSV or a count recomputed by the verifier; the seven manifests and 83 outputs are hashed in the compact artifact.

## 3. Residual objections (no action within this paper)

- **"E1 is at 0.12 in three regimes."** Reported as executed in the primary aggregate, separately and without E1 (0.045–0.052); the exchangeable re-splits show the excess is the overlap of 256-row draws from 322-row halves, i.e. a design property of one environment, not a property of the rule. Removing E1 would be post-hoc; it stays.
- **"The adversarial gate fixes one cluster rule and two mechanisms."** Declared in the limitations and in the adversary model; an attacker with a different model of the sensors is not evaluated. The gate is an existence proof of adaptive evasion against a calibrated audit, not a coverage bound.
- **"The conformal rule is not new."** Correct and stated: the article claims the placement of a known conformal p-value in the view lattice, the exact level for the multi-sensor decision, and the measured decomposition of the earlier excess, not a new statistical rule.
- **"Simulator-only, fixed design."** Declared throughout; QPU execution, calibrated noise, scheduling, provider security, multi-tenancy, confidentiality and operational Fleet Management belong to Paper 2.5 or other project deliverables.

## 4. Reject-risk assessment

- **Mathematical-validity risk: low.** The only false statement of 1.2.0 was found by the authors' own audit, replaced, proved and tested exhaustively; the remaining propositions survived a brute-force counterexample search.
- **Statistical-validity risk: low.** The level is exact under a stated, testable premise; the premise's violation in the executed design is measured (design effect) and separated from the rule.
- **Headline-number risk: low after H1–H3.** All ranges in the abstract are macros.
- **Realism risk: moderate, out of scope by declaration.**
- **Overall: a defensible TDSC regular-paper submission; the main risk is editorial taste about formal characterization versus mechanism novelty, not a correctable omission within the declared paper.**

---

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
