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
aggregate (item-identity integrity).

The novelty is the integrated package: the observation model with its
monotonicity, closure and materiality results and counterexamples; an explicit
adversary model; multi-dataset / fixed-OOD validation with null calibration;
a decision-level (family-wise) calibration; an end-to-end `allow/hold/block`
evaluation whose primary endpoint is the number of materially changed results
a policy would serve; a bounded quantum-kernel integrity layer; and an
executable fail-closed contract. No constituent is presented as standalone
novelty, and the ZZ-versus-SVC comparison is secondary evidence only.

## Authoritative sources

| Question | Where |
|---|---|
| Counts (manifests, outputs, files, tests, pages, hashes, DOIs) | `publication/RELEASE_STATUS.md` (generated; wins over any other document) |
| Article and supplement | `publication/tdsc/main.tex`, `publication/tdsc/supplement.tex`, PDFs in `output/pdf/` |
| Formal core with proofs | `manuscript/FORMAL_CORE.md` |
| Adversary and failure model; threat-model card | `manuscript/ADVERSARY_MODEL.md`, `manuscript/THREAT_MODEL_CARD.md` |
| Preregistrations and result summaries | `manuscript/paper15_v11_reinforcement_prereg.md`, `..._result_summary.md`, `manuscript/paper15_v12_policy_prereg.md`, `..._result_summary.md` |
| Literature and overlap audit | `manuscript/NOVELTY_REVIEW_2026-08-09.md` (with the 6 and 7 September 2026 rechecks) |
| ATHENA-AEGIS traceability and the Paper 1.5 / 2.5 boundary | `manuscript/ATHENA_DEUSTO_TRACEABILITY.md` |
| Reproduction (verify the frozen artifact; recompute everything) | `Q1_REPRODUCTION.md`, `scripts/verify_datasets.py` |
| Hostile review and claims map | `publication/TDSC_HOSTILE_REVIEW_AUDIT.md`, `publication/tdsc/CLAIMS_TRACEABILITY.md` |
| Historical drafts (non-authoritative) | `manuscript/archive/` |

## Frozen evidence

| Gate | Design | Evidence used in the manuscript |
|---|---|---|
| CICIDS Gate 1 | 7,980 raw rows; 4,560 unique observations; 5 split x 4 nested model seeds | exact label-path blind regions and the secondary within-split ZZ-SVC profile |
| Expansion | 360/360 jobs; 13,680 raw rows; 11,400 unique observations; 8 fixed environments | replication over CICIDS2017, UNSW-NB15, ToN-IoT, scale and temporal OOD |
| Quantum integrity | 165/165 cells; 9/9 acceptance checks | semantic, provenance, algebraic, repeated-estimation and output coverage |
| HSaaS contract | 6/6 scenarios; 8/8 acceptance checks | hash-chained four-contract `allow/hold/block` policy |
| Reinforcement (1.1.0) | 390/390 preregistered jobs; null calibration over 8 environments (alpha = 0.05 per sensor, 200 calibration and 200 disjoint evaluation draws per cell), 3 preprocessing configurations, 2 tuned environments | per-sensor calibrated false-alarm/detection rates; symmetric-preprocessing and tuned-baseline sensitivity of the secondary profile |
| Policy (1.2.0) | preregistered; computed from the frozen 1.1.1 outputs, no re-execution; 60 cells x 4 regimes family-calibrated; 4 policies x 5 regimes on 24,000 frozen observations | decision-level false-alarm rates, unsafe allows, containment, residual blind cases, counterexample witnesses, contract composition |

The expansion contains 3,600 evaluation-label observations. All 3,600 leave
feature/prediction evidence and predictions invariant; all 1,800
prior-preserving observations also leave label marginals invariant. Of the
3,600, 2,184 lower the reported balanced accuracy, 983 leave it unchanged and
433 raise it; all 2,617 with a changed conclusion have non-zero item-aligned
joint-outcome evidence. For the multi-sensor regimes with feature evidence, decision-level
calibration lowers the pooled false-alarm rate from 0.125--0.259 to
0.061--0.079 (the label-marginal regime stays at 0.048); batch-level regimes
with feature evidence serve 4,322--4,494 of the 7,008
materially changed results (the label-marginal regime serves all of them); the
trusted item-aligned regime serves none. A fail-closed verifier recomputes these
counts from the released derived tables.

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
the artifact-wide SHA-256 manifest, six embedded evidence manifests, 65
manifested outputs, CSV row counts, the primary label-boundary counts
including the signed decreased / unchanged / increased counts, the calibrated
label-path consistency checks and the policy-level claims; it exits non-zero
on any mismatch. Test and file counts are in `publication/RELEASE_STATUS.md`.

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
.\.venv\Scripts\python.exe -m src.experiments.make_q1_policy_tables
.\.venv\Scripts\python.exe -m src.experiments.make_q1_policy_figures
.\.venv\Scripts\python.exe -m src.experiments.assemble_publication_artifact
.\.venv\Scripts\python.exe -m src.experiments.make_release_status
```

The exact-statevector engine is an ideal-simulation acceleration. The 256/1,024
shot conditions are binomial fidelity-estimation emulators. Neither is evidence
from a QPU or calibrated backend.

## Scientific boundary

This release studies data-to-evaluation integrity and selected simulated
quantum-kernel boundaries with a local, calibrated, fail-closed policy. It
does not study or claim:

- physical QPU behaviour or device-calibrated noise;
- malicious scheduling, multi-tenancy, provider attestation or provider-side
  security;
- production authentication, non-repudiation or incident operations;
- context-conditioned runtime calibration under non-stationarity, abstention
  with recovery, or service-level evaluation of enforcement;
- operational Fleet Management.

Within ATHENA-AEGIS it supplies strong but bounded evidence for G3.2/G3.3
(including calibrated false-alarm budgets, executable contracts and hash
chaining), selected simulator evidence for G3.1, a local research prototype
towards Result 3.1, and a publication contribution to WP5 Task 5.2. It does
not cover WP5 Task 5.1 or Result 5.1; those and the operational assurance
layer belong to Paper 2.5 (`manuscript/ATHENA_DEUSTO_TRACEABILITY.md`).

## Version, funding and citation

Artifact version: `1.2.0` (frozen 1.0.0 evidence, tag `paper15-q1-v1.0.0`;
reinforcement gates of 1.1.0; editorial 1.1.1; policy gates of 1.2.0; release
tag `paper15-q1-v1.2.0`). Tags `paper15-q1-v1.1.0` and `paper15-q1-v1.1.1`
and their Zenodo versions are immutable.

This work is part of grant PID2024-155693NB-C43, ATHENA-AEGIS (Advanced Secure Technologies for Hybrid Quantum-Classical Environments and Applications), funded by MICIU/AEI/10.13039/501100011033 and by ERDF/EU.

Zenodo concept DOI `10.5281/zenodo.22550852` resolves to the latest archived
version; the version DOI of 1.2.0 is `10.5281/zenodo.22644529` (1.1.1: `10.5281/zenodo.22552643`; 1.1.0:
`10.5281/zenodo.22550853`). Author metadata, CRediT roles and licenses were
confirmed by all authors on 2026-09-06: code is Apache-2.0, derived evidence
and documentation CC BY 4.0, and the manuscript files are author preprints
(see `LICENSING.md`). Citation metadata is in `CITATION.cff` and
`.zenodo.json`.
