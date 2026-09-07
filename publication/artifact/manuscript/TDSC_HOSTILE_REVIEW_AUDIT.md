# Hostile-review audit — IEEE TDSC candidate

This file keeps the audits in reverse chronological order. The 1.2.0 audit
supersedes the verdicts below it; the earlier audits are retained as history.

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
