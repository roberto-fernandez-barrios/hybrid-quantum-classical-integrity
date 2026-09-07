# Observational indistinguishability and integrity blind regions in hybrid quantum-classical kernel workflows

Reproducibility artifact for Paper 1.5:
*Observational Indistinguishability and Integrity Blind Regions Across the
Evidence Boundaries of Hybrid Quantum-Classical Kernel Workflows*
(IEEE TDSC candidate; earlier title *Information-Set Conditional Integrity
Auditing for Hybrid Quantum-Classical Kernel Workflows*).

The central claim is deliberately bounded: **auditability is a property of
the pair (intervention class, information set) refined by explicit trusted
references**. A structural blind region is the set of interventions whose
observable view equals the baseline view; it is monotone under refinement of
the view and closed exactly by added evidence that separates the class. The
evaluation-label path is a protected boundary: for a fixed predictor,
label-only changes leave feature and prediction evidence invariant,
prior-preserving changes also leave label marginals invariant, and every
change of the reported balanced accuracy changes the confusion matrix, so a
material label corruption is always separable in the joint item-label view;
a trusted aggregate reference of the same batch detects it exactly, and an
item-aligned reference is needed only for relabelings that preserve every
aggregate (item-identity integrity). Three reference levels are
distinguished: Level A, a statistical or historical reference (null
distribution, training or reference population, calibration sample) with no
authenticated value of the same batch, which every batch-level sensor holds;
Level B, a trusted aggregate same-batch reference; Level C, a trusted
item-aligned same-batch reference. The results turn on the distinction
between a statistical baseline and an authenticated same-batch anchor, not on
"having" a reference.

The novelty is the integrated package: the observation model (primitive and
derived artifacts, explicit intervention semantics) with its monotonicity,
closure and materiality results and counterexamples, and the quantum branch as
an instance of the same view lattice with semantic, estimated and observed
kernels kept apart; an explicit adversary model including an executed adaptive
attacker; multi-dataset / fixed-OOD validation with null calibration; a
decision-level calibration by a conformal family rule whose finite-sample
level holds under exchangeability (observed rates 0.048–0.058 in the executed,
non-exchangeable design); an offline end-to-end `allow/hold/block` evaluation
whose primary endpoint is the number of materially changed results a policy
would serve and whose secondary endpoint is the cost on near-null synthetic
variation; a bounded quantum-kernel integrity layer; and an executable
contract. No constituent is presented as standalone novelty, and the
ZZ-versus-SVC comparison is secondary evidence only (supplement).

## Version 1.3.1 in one paragraph

Version 1.3.1 is a formal and editorial correction of version 1.3.0; the
experimental evidence is frozen at 1.3.0 and no kernel, job, seed, model or
draw was re-executed. It restates Proposition 7(iii) for finite-shot
estimation (exact equality has false-alarm probability
1 − Pr[K̂ = K₀ | honest], which is not universally one: p = 1/2 at two shots
gives 1/2; the discrepancy needs a calibrated null, otherwise no statistical
claim), splits the workflow state into primitive and derived artifacts with
explicit intervention semantics (`src/integrity/workflow_state.py`),
separates the semantic, estimated and observed kernels by intervention class,
names the reference levels as above, states the conformal claim as a property
under exchangeability with the executed rates reported separately, renames
P3 *coverage-complete abstaining* (fail-closed on missing coverage; no
minimum-power guarantee), prints the adaptive attacker's material retention
everywhere from the generated macros (83–91 %), decomposes the trusted-regime
interruption (544 statistical holds + 85 exact-reference blocks = 629 of
1,200 near-null synthetic controls), reframes the zero-response cells as
validation checks, shortens the abstract to at most 250 words, adds a concrete
threat scenario and VAMP to related work, and makes the figures legible. New
tests: `tests/test_workflow_state.py`, `tests/test_manuscript_consistency.py`.
Only the textual `policy_class` label of P3 in the policy and adversarial
tables differs from 1.3.0; every number is unchanged.

## Authoritative sources

| Question | Where |
|---|---|
| Counts (manifests, outputs, files, tests, pages, hashes, DOIs) | `publication/RELEASE_STATUS.md` (generated; wins over any other document) |
| Article and supplement | `publication/tdsc/main.tex`, `publication/tdsc/supplement.tex`, PDFs in `output/pdf/` |
| Formal core with proofs; statement-by-statement reviews; executable state semantics | `manuscript/FORMAL_CORE.md`, `manuscript/FORMAL_REVIEW_1.3.0.md`, `manuscript/FORMAL_REVIEW_1.3.1.md`, `src/integrity/workflow_state.py` |
| Adversary and failure model; threat-model card | `manuscript/ADVERSARY_MODEL.md`, `manuscript/THREAT_MODEL_CARD.md` |
| Preregistrations and result summaries | `manuscript/paper15_v11_reinforcement_prereg.md`, `..._result_summary.md`, `manuscript/paper15_v12_policy_prereg.md`, `..._result_summary.md`, `manuscript/paper15_v13_prereg.md` (amendments A2, A3; Gate A), `manuscript/paper15_v13_result_summary.md` |
| Literature and overlap audit | `manuscript/NOVELTY_REVIEW_2026-08-09.md` (with the 6 and 7 September 2026 rechecks) |
| ATHENA-AEGIS traceability and the Paper 1.5 / 2.5 boundary | `manuscript/ATHENA_DEUSTO_TRACEABILITY.md` |
| Reproduction (verify the frozen artifact; recompute everything) | `Q1_REPRODUCTION.md`, `scripts/verify_datasets.py` |
| Hostile review and claims map | `publication/TDSC_HOSTILE_REVIEW_AUDIT.md`, `publication/tdsc/CLAIMS_TRACEABILITY.md` |
| Historical drafts (non-authoritative) | `manuscript/archive/` |

## Frozen evidence

| Gate | Design | Evidence used in the manuscript |
|---|---|---|
| CICIDS Gate 1 | 7,980 raw rows; 4,560 unique observations; 5 split x 4 nested model seeds | exact label-path blind regions and the secondary within-split ZZ-SVC profile |
| Expansion | 360/360 jobs; 13,680 raw rows; 11,400 unique observations; 8 fixed environments (five CICIDS2017, two UNSW-NB15, one ToN-IoT) | replication over the three datasets, scale and temporal OOD |
| Quantum integrity | 165/165 cells; 9/9 acceptance checks | semantic, provenance, algebraic, repeated-estimation and output coverage (Proposition 7) |
| HSaaS contract | 6/6 scenarios; 8/8 acceptance checks | hash-chained four-contract `allow/hold/block` prototype |
| Reinforcement (1.1.0) | 390/390 preregistered jobs; null calibration over 8 environments (alpha = 0.05 per sensor, 200 calibration and 200 disjoint evaluation draws per cell), 3 preprocessing configurations, 2 tuned environments | per-sensor calibrated false-alarm/detection rates; symmetric-preprocessing and tuned-baseline sensitivity of the secondary profile |
| Policy (1.2.0, regenerated in 1.3.0) | preregistered; computed from the frozen 1.1.1 outputs, no re-execution; 60 cells x 4 regimes calibrated with the conformal family rule; 4 policies x 5 regimes on 24,000 frozen observations | decision-level false-alarm rates with the 1.2.0 rule as comparison, rule-bias / design-effect decomposition, unsafe allows, containment, benign interruption, residual blind cases, counterexample witnesses, contract composition |
| Adversarial (1.3.0) | preregistered; 240/240 exact-statevector jobs; 8 environments; cluster-preserving mean shift and scaling at 5 strengths with matched controls | detection, materiality and unsafe allows of an adaptive attacker who preserves the batch-level fingerprint |

The expansion contains 3,600 evaluation-label observations. All 3,600 leave
feature/prediction evidence and predictions invariant; all 1,800
prior-preserving observations also leave label marginals invariant. Of the
3,600, 2,184 lower the reported balanced accuracy, 983 leave it unchanged and
433 raise it; all 2,617 with a changed conclusion have non-zero item-aligned
joint-outcome evidence. The conformal family rule has finite-sample level
10/201 under exchangeability, a premise the executed design violates; its
observed decision false-alarm rates are 0.056 / 0.058 / 0.053 (`I_X` /
`I_XF` / `I_XFY`; the label-marginal regime stays at 0.048) against 0.125 /
0.203 / 0.259 for the union of per-sensor rules; the asymmetric rule of 1.2.0
(0.061 / 0.073 / 0.079) had a false guarantee (amendment A2), and most of its
excess was rule bias, not the design. Batch-level regimes with feature
evidence serve 4,365--4,496 of the 7,008 materially changed results under the
calibrated risk-tolerant policy (the label-marginal regime serves all of
them); the trusted item-aligned regime serves none, with zero clean false
actions on its 1,200 exact-zero rows, but interrupts 629 of the 1,200
near-null synthetic controls (544 statistical holds that the calibrated
batch-level policy also pays, 85 exact-reference blocks). The adaptive
cluster-preserving attacker cuts the detection of feature drift from
0.96--1.00 to 0.01--0.66 at matched strengths while keeping 83--91 % of the
conclusion changes, and is served by the calibrated policy in 28--39 % of its
material rows. A fail-closed verifier recomputes these counts from the
released derived tables.

## Quick verification

Python 3.10 is the reference interpreter.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

Linux/macOS: use `.venv/bin/python` and `/` separators. The verifier checks
the artifact-wide SHA-256 manifest, seven embedded evidence manifests, the
manifested outputs, CSV row counts, the primary label-boundary counts
including the signed decreased / unchanged / increased counts, the calibrated
label-path consistency checks, the policy-level claims (including the exact
level of the conformal rule under exchangeable re-splits) and the replay and
trust checks of the adversarial gate; it exits non-zero on any mismatch. Test
and file counts are in `publication/RELEASE_STATUS.md`. The test suite
includes the exhaustive counting-bound tests of the conformal rule and the
brute-force checks of the formal core.

Build the article and supplement with:

```powershell
pwsh -NoProfile -File publication/tdsc/build.ps1
```

## Rebuilding the evidence

The compact artifact supports result verification without recomputing quantum
kernels. Full replay starts from the public benchmark datasets (official
sources, expected hashes and staging commands in `Q1_REPRODUCTION.md`):

```powershell
.\.venv\Scripts\python.exe scripts\verify_datasets.py --require-raw --require-staged
.\.venv\Scripts\python.exe -m src.experiments.build_q1_gate1_evidence
pwsh -NoProfile -ExecutionPolicy Bypass -File .\run_paper15_q1_exact_queue.ps1
.\.venv\Scripts\python.exe -m src.experiments.build_q1_expansion_evidence
.\.venv\Scripts\python.exe -m src.experiments.run_quantum_integrity_gate
.\.venv\Scripts\python.exe -m src.hsaas.demo
.\.venv\Scripts\python.exe -m src.experiments.run_v11_reinforcement_queue --gates N,P,T
.\.venv\Scripts\python.exe -m src.experiments.build_q1_reinforcement_evidence
.\.venv\Scripts\python.exe -m src.experiments.make_q1_reinforcement_figures
.\.venv\Scripts\python.exe -m src.experiments.build_q1_policy_evidence
.\.venv\Scripts\python.exe -m src.experiments.run_v13_f5_queue --n-jobs 6
.\.venv\Scripts\python.exe -m src.experiments.build_q1_adversarial_evidence
.\.venv\Scripts\python.exe -m src.experiments.make_q1_policy_tables
.\.venv\Scripts\python.exe -m src.experiments.make_q1_policy_figures
.\.venv\Scripts\python.exe -m src.experiments.make_q1_adversarial_figures
.\.venv\Scripts\python.exe -m src.experiments.assemble_publication_artifact
.\.venv\Scripts\python.exe -m src.experiments.make_release_status
```

The exact-statevector engine is an ideal-simulation acceleration. The 256/1,024
shot conditions are binomial fidelity-estimation emulators. Neither is evidence
from a QPU or calibrated backend.

## Scientific boundary

This release studies data-to-evaluation integrity and selected simulated
quantum-kernel boundaries with a local, calibrated policy evaluated offline on
frozen outputs. It does not study or claim:

- physical QPU behaviour or device-calibrated noise;
- malicious scheduling, multi-tenancy, provider attestation or provider-side
  security;
- production authentication, non-repudiation, deployed runtime services or
  incident operations;
- context-conditioned runtime calibration under non-stationarity, abstention
  with recovery, or service-level evaluation of enforcement;
- operational Fleet Management.

Within ATHENA-AEGIS it supplies strong but bounded evidence for G3.2/G3.3
(including a decision-level false-alarm level with an exact premise, the
measured cost of enforcement on benign variation, an executed adaptive
attacker, executable contracts and hash chaining), selected simulator evidence
for G3.1, a local research prototype towards Result 3.1, and a publication
contribution to WP5 Task 5.2. It does not cover WP5 Task 5.1 or Result 5.1;
those and the operational assurance layer belong to Paper 2.5
(`manuscript/ATHENA_DEUSTO_TRACEABILITY.md`).

## Version, funding and citation

Artifact version: `1.3.1` (frozen 1.0.0 evidence, tag `paper15-q1-v1.0.0`;
reinforcement gates of 1.1.0; editorial 1.1.1; policy gates of 1.2.0,
regenerated in 1.3.0 with the conformal rule; adversarial gate of 1.3.0;
formal and editorial correction 1.3.1 with the evidence frozen at 1.3.0;
release tag `paper15-q1-v1.3.1`). Tags `paper15-q1-v1.1.0`,
`paper15-q1-v1.1.1`, `paper15-q1-v1.2.0` and `paper15-q1-v1.3.0` and their
Zenodo versions are immutable. After 1.3.1 the article is reopened only for
an objective error that invalidates a claim, an editorial requirement of the
journal, or a reviewer request; everything else belongs to Paper 2.5.

This work is part of grant PID2024-155693NB-C43, ATHENA-AEGIS (Advanced Secure Technologies for Hybrid Quantum-Classical Environments and Applications), funded by MICIU/AEI/10.13039/501100011033 and by ERDF/EU.

Zenodo concept DOI `10.5281/zenodo.22550852` resolves to the latest archived
version; the version DOI of 1.3.1 is recorded in `CITATION.cff` and
`publication/DOI_STATUS.md` (1.3.0: `10.5281/zenodo.22648573`; 1.2.0:
`10.5281/zenodo.22644529`; 1.1.1: `10.5281/zenodo.22552643`; 1.1.0:
`10.5281/zenodo.22550853`). Author metadata, CRediT roles and licenses were
confirmed by all authors on 2026-09-06 and the 1.3.0 and 1.3.1 changes on
2026-09-07: code is Apache-2.0, derived evidence and
documentation CC BY 4.0, and the manuscript files are author preprints (see
`LICENSING.md`). Citation metadata is in `CITATION.cff` and `.zenodo.json`.
