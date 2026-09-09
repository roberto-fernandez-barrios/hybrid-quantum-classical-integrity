# Paper 1.5 reproduction guide (release 1.3.4; experimental evidence frozen at 1.3.0)

Version 1.3.4 is a corrective bibliographic/editorial release. No experiment,
kernel, model, dataset, seed, attack, draw, intervention, policy decision,
scientific result or formal theorem was re-executed or changed. Derived
metadata/coverage artifacts were regenerated from the frozen code/evidence to
correct an inconsistency; scientific observations and decisions are unchanged.

Reviewer path: repository `README.md` → this guide → `publication/artifact/`
→ `python -m src.experiments.verify_publication_artifact --root
publication/artifact`.

This guide separates two activities that a third party may want to perform
from a clean clone:

- **Verify the compact artifact** — no benchmark dataset is needed. The compact
  artifact under `publication/artifact/` carries the claim-supporting derived
  tables, eight embedded evidence manifests, 86 manifested outputs, figures,
  and an independent verifier that recomputes the primary claims. It begins
  from manifested compact derived evidence; raw benchmark jobs and raw datasets
  are not included.
- **Recompute everything** — the public benchmark datasets must be obtained
  from their official sources, verified by hash, staged with the documented
  commands, and the experiment queues, builders and assembler must be run.
  The GitHub/source snapshot contains those runners and builders; it is broader
  than the compact Zenodo artifact and does not imply that raw jobs are bundled.

Authoritative counts (tests, manifests, outputs, files, pages, hashes) are
generated into `publication/RELEASE_STATUS.md` at release time; if a number in
this guide and that file disagree, the generated file wins.

The claim boundary is unchanged: QPU execution, calibrated device noise,
scheduling, provider security, multi-tenancy, side channels and operational
Fleet Management are outside this paper and are not reproduction gates for its
claim. The exact-statevector engine is an ideal-simulation acceleration and the
256/1,024-shot conditions are binomial fidelity-estimation emulators; neither is
evidence from a QPU or a calibrated backend.

Commands are given for PowerShell 7 (`pwsh`, available on Windows, Linux and
macOS) and for a POSIX shell (`bash`). Run them from the repository root. On
Windows the virtual-environment interpreter is `.venv\Scripts\python.exe`; on
Linux/macOS it is `.venv/bin/python`. Below, `$PY` / `PY` stands for that
interpreter.

## 1. Environment

Python 3.10 is the reference interpreter (the evidence was frozen with Python
3.10.16, NumPy 2.2.6, pandas 2.3.3, scikit-learn 1.7.2, Qiskit 2.3.0, Qiskit
Machine Learning 0.9.0). The exact resolved environment is
`requirements-lock.txt` (archived copy:
`publication/artifact/environment/requirements-lock.txt`).

```powershell
# PowerShell 7
python -m venv .venv
$PY = if (Test-Path .venv\Scripts\python.exe) { ".venv\Scripts\python.exe" } else { ".venv/bin/python" }
& $PY -m pip install -r requirements-lock.txt
& $PY -m pip install -e . --no-deps
```

```bash
# POSIX shell
python3.10 -m venv .venv
PY=.venv/bin/python
$PY -m pip install -r requirements-lock.txt
$PY -m pip install -e . --no-deps
```

Qiskit 2.3 emits deprecation warnings for BlueprintCircuit-based feature-map
classes scheduled for removal in Qiskit 3. The release intentionally pins
Qiskit below 3 because migrating constructors would change frozen circuit
serialization and require a new evidence version. The warnings do not alter
any test or manifest result.

## 2. Verify the frozen artifact (no datasets needed)

```powershell
& $PY -m pytest tests -q -p no:cacheprovider
& $PY -m src.experiments.verify_publication_artifact --root publication\artifact
```

```bash
$PY -m pytest tests -q -p no:cacheprovider
$PY -m src.experiments.verify_publication_artifact --root publication/artifact
```

The test suite must pass (its size is recorded in
`publication/RELEASE_STATUS.md`). The verifier is read-only: it checks the
artifact-wide SHA-256 manifest, the eight embedded evidence manifests and
their 86 outputs, CSV row counts, the primary label-boundary counts (3,600 /
2,184 expansion and 1,440 / 1,276 Gate 1, plus the signed decreased /
unchanged / increased counts), the calibrated label-path consistency checks of
the reinforcement gate, the policy-level claims of the conformal calibration
and decision gates (level 10/201 recomputed from the frozen family scores,
exchangeable re-split rates at or below the level, unsafe-allow counts) and
the adversarial gate (exact replay of the matched controls, zero unsafe allows
in the trusted regime). It exits non-zero on any missing file, changed byte,
incomplete acceptance check or changed primary count.

The same verification works on an unpacked compact release ZIP
(`paper15-q1-v1.3.4.zip`): from inside the unpacked directory run
`python software/src/experiments/verify_publication_artifact.py --root .`
(pandas is the only third-party dependency of the verifier).

The cache provider is disabled because restricted Windows sessions may deny
creation of pytest's temporary cache directories; this does not skip tests.

## 3. Obtain the public datasets (only for recomputation)

The raw datasets are **not redistributed** with this repository or the Zenodo
artifact; they retain the terms of their publishers. Download them from the
official sources and place them under `data/raw/` exactly as follows.

| Dataset | Official source | Files used | Place under |
|---|---|---|---|
| CICIDS2017 (`MachineLearningCVE` CSVs) | Canadian Institute for Cybersecurity, <https://www.unb.ca/cic/datasets/ids-2017.html> | `Monday-WorkingHours.pcap_ISCX.csv`, `Tuesday-WorkingHours.pcap_ISCX.csv`, `Wednesday-workingHours.pcap_ISCX.csv`, `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv`, `Friday-WorkingHours-Morning.pcap_ISCX.csv`, `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | `data/raw/cicids2017/MachineLearningCVE/` |
| UNSW-NB15 (official training/testing sets) | UNSW Canberra Cyber, <https://research.unsw.edu.au/projects/unsw-nb15-dataset> | `UNSW_NB15_training-set.csv`, `UNSW_NB15_testing-set.csv` | `data/raw/unsw_nb15/Training and Testing Sets/` |
| ToN-IoT (network dataset) | UNSW Canberra Cyber, <https://research.unsw.edu.au/projects/toniot-datasets> | `train_test_network.csv` | `data/raw/ton_iot/` |

Expected SHA-256 of the raw source files, as recorded by the staging scripts
when the frozen evidence was produced (`data/*.prep_report.json`,
`data/processed/*.prep_report.json`, `data/raw/staging/stage_report.json`):

| Raw file | SHA-256 |
|---|---|
| `Monday-WorkingHours.pcap_ISCX.csv` | `852c4beb34eda186f32561fa79df7a0747e92e1a6535b01270820dd9ffe17f34` |
| `Tuesday-WorkingHours.pcap_ISCX.csv` | `52b8692ae8c7d2ed04671fe2b98335693c0a92c7ab157d8c8b534d6523080851` |
| `Wednesday-workingHours.pcap_ISCX.csv` | `893c27dc968bf7a8adef1689f90be55ca4a4dc3088fb63d6ff247ac56856df2a` |
| `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv` | `d67066211fb1689c78406f1506f4c44704ecb92088353d5c96d96d6474eb819d` |
| `Friday-WorkingHours-Morning.pcap_ISCX.csv` | `53a41c24d570ea83b7ac55b2e94df94e7a8216aeb80a2af0246b6bc8bb543000` |
| `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | `ca1824c51bfbb7b3c72290a11be04366ba8815878c6a1cc5c44cb1cee269e99b` |
| `UNSW_NB15_training-set.csv` | `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` |
| `UNSW_NB15_testing-set.csv` | `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` |
| `train_test_network.csv` (ToN-IoT) | `26ddc513552de36de6428b2e578efaed2b57504c716dfba847cc0109a64e1974` |

A raw file with a different hash is a different release of the dataset; the
staged tables below would then differ and the full replay would not reproduce
the frozen counts bit for bit.

## 4. Verify hashes and stage the tables

`scripts/verify_datasets.py` (standard library only) recomputes the SHA-256 of
every staged table and, when present, of every raw source, against the
expected values in the staging reports:

```powershell
& $PY scripts\verify_datasets.py                 # staged tables; raw sources if present
& $PY scripts\verify_datasets.py --require-raw --require-staged   # precondition for a full replay
```

```bash
$PY scripts/verify_datasets.py
$PY scripts/verify_datasets.py --require-raw --require-staged
```

Expected SHA-256 of the staged tables (all tracked in this repository, so a
clean clone already passes the staged checks):

| Staged table | Rows | SHA-256 |
|---|---:|---|
| `data/cicids_subset.csv` | 3,000 | `8c8771f4e348bcbd6a58c8e215ba143d6f98a4a7a341d0e991bb8f3c211a9588` |
| `data/unsw_subset.csv` | 3,000 | `6292a46b03eef422acd660f68b5c76c3e04118a63d617a8e5f5b755450078780` |
| `data/ton_iot_subset.csv` | 3,000 | `cc6a61e9a3c294b5520cb59e8874c12929d1a91acca92f06c1ca868a5768c01b` |
| `data/raw/staging/unsw_nb15/unsw_train.csv` | 175,341 | `ff8f800823506ffba408c7edbe6f1d57c1707b098e7ed6e3785a8d9d2dc10c75` |
| `data/raw/staging/unsw_nb15/unsw_test.csv` | 82,332 | `0aa749da7abc0dc38ff2c1ea1c6636095e4795dcd09f1975e70511957c4608e4` |
| `data/raw/staging/ton_iot/ton_network.csv` | 211,043 | `443619d118439d8e9e1f7593f8e929c1d45cf0014739b861484c85a07ae7614f` |
| `data/processed/cicids_ood_tuesday_train.csv` (and the byte-identical `..._tuesday_train_portscan.csv`) | 3,000 | `649b5ffb6a09a89cb28f021ef8878ed990d0c5c2f2283fe1394f9b5e88a500e9` |
| `data/processed/cicids_ood_wednesday_test.csv` (and the byte-identical `..._wednesday_train.csv`) | 3,000 | `c82af0bab09f10ac46dd078c5dbab4f46e8a67fb5602dbedf4cdc3faf5a73c6d` |
| `data/processed/cicids_ood_friday_portscan_test.csv` | 3,000 | `0e535a9942a24bb09d7b04b1d3e3e2714a182ed3f4b7d62711ef329d2d392b11` |
| `data/processed/cicids_ood_thursday_webattacks_test.csv` | 3,000 | `3ec6a4d7c4b363d436088f064c43b1a0cffd72efd5825ab2a12ea1096c233674` |
| `data/processed/cicids_ood_friday_morning_test.csv` | 3,000 | `5c44b321468f72c3a4ef0f51135629092d253b02b7746cae64b5905a2fe89dd5` |
| `data/processed/unsw_ood_train.csv` | 3,000 | `993984caf61b9e60a68d9722fae9564edbd3ea91f8e2204b3ce13c26f612c350` |
| `data/processed/unsw_ood_test.csv` | 3,000 | `b9107599e6510ae5116d26ac952283814d80f8fdba775977893c2879a3c6cee0` |

The staged tables are tracked, so staging is only needed to demonstrate that
they derive from the raw sources. The staging pipeline is deterministic (prep
seed 42, balanced 1,500 + 1,500 rows, no imputation and no scaling at staging;
imputation, projection and scaling are fitted on training rows inside
`run_benchmark`). The commands below are reconstructed from the staging code
and the `dataset_id_payload` / `source` fields of the reports; **regenerate into
a scratch location and compare hashes rather than overwriting the tracked
tables.** Two caveats are stated explicitly:

- `data/cicids_subset.prep_report.json` was written by an earlier revision of
  `prepare_cicids_subset.py` (February 2026) whose report layout has no
  `dataset_id_payload`. The parameters it records (Monday + Tuesday +
  Wednesday files, `--label-col Label`, benign token `benign`, 3,000 rows,
  1,500 per class, seed 42, `max_nan_frac` 0.2, 77 numeric features, no
  `_source_file` column) are consistent with the current script under the
  command below, but bit-identical regeneration of that one table with the
  current code has not been re-verified; the SHA-256 check is the arbiter.
- `_source_file` is kept in the CICIDS OOD tables (`keep_source_file: true` in
  their reports) and not in the ID tables.

### 4.1 UNSW-NB15 and ToN-IoT staging (leakage-column removal)

```bash
$PY -m src.datasets.stage_unsw_ton
```

(`pwsh`: `& $PY -m src.datasets.stage_unsw_ton`.) This reads
`data/raw/unsw_nb15/Training and Testing Sets/UNSW_NB15_{training,testing}-set.csv`
and `data/raw/ton_iot/train_test_network.csv`, drops `id` and `label` (UNSW; the
label source becomes `attack_cat`) and `label`, `src_port`, `dst_port` (ToN-IoT;
label source `type`), drops feature columns that are mostly missing after
numeric coercion (ToN-IoT: `http_trans_depth`, `http_version`, `weird_addl`),
writes `data/raw/staging/{unsw_nb15,ton_iot}/*.csv` and
`data/raw/staging/stage_report.json`. The script has no arguments.

### 4.2 Balanced ID subsets

```bash
# CICIDS2017 ID subset (Monday + Tuesday + Wednesday pool)
$PY -m src.datasets.prepare_cicids_subset \
  --indir data/raw/cicids2017/MachineLearningCVE \
  --use-only-files "Monday-WorkingHours.pcap_ISCX.csv" "Tuesday-WorkingHours.pcap_ISCX.csv" "Wednesday-workingHours.pcap_ISCX.csv" \
  --label-col Label --benign-token benign --drop-non-numeric --max-nan-frac 0.2 \
  --n-total 3000 --seed 42 \
  --out data/cicids_subset.csv --report data/cicids_subset.prep_report.json

# UNSW-NB15 ID subset (pool = staged train + test)
$PY -m src.datasets.prepare_cicids_subset \
  --indir data/raw/staging/unsw_nb15 \
  --label-col attack_cat --benign-token normal --drop-non-numeric --max-nan-frac 0.2 \
  --n-total 3000 --seed 42 \
  --out data/unsw_subset.csv --report data/unsw_subset.prep_report.json

# ToN-IoT ID subset
$PY -m src.datasets.prepare_cicids_subset \
  --indir data/raw/staging/ton_iot \
  --label-col type --benign-token normal --drop-non-numeric --max-nan-frac 0.2 \
  --n-total 3000 --seed 42 \
  --out data/ton_iot_subset.csv --report data/ton_iot_subset.prep_report.json
```

In `pwsh` replace the line continuations `\` by backticks (`` ` ``) or write
each command on one line.

### 4.3 Temporal OOD pairs (train and test from disjoint files)

```bash
CIC=data/raw/cicids2017/MachineLearningCVE
COMMON="--label-col Label --benign-token benign --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --schema-from train --keep-source-file"

$PY -m src.datasets.prepare_cicids_subset --indir $CIC --ood $COMMON \
  --train-files "Tuesday-WorkingHours.pcap_ISCX.csv" --test-files "Wednesday-workingHours.pcap_ISCX.csv" \
  --out-train data/processed/cicids_ood_tuesday_train.csv --out-test data/processed/cicids_ood_wednesday_test.csv \
  --report data/processed/cicids_ood_tuesday_vs_wednesday.prep_report.json

$PY -m src.datasets.prepare_cicids_subset --indir $CIC --ood $COMMON \
  --train-files "Tuesday-WorkingHours.pcap_ISCX.csv" --test-files "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv" \
  --out-train data/processed/cicids_ood_tuesday_train_portscan.csv --out-test data/processed/cicids_ood_friday_portscan_test.csv \
  --report data/processed/cicids_ood_tuesday_vs_friday_portscan.prep_report.json

$PY -m src.datasets.prepare_cicids_subset --indir $CIC --ood $COMMON \
  --train-files "Wednesday-workingHours.pcap_ISCX.csv" --test-files "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv" \
  --out-train data/processed/cicids_ood_wednesday_train.csv --out-test data/processed/cicids_ood_thursday_webattacks_test.csv \
  --report data/processed/cicids_ood_wednesday_vs_thursday_webattacks.prep_report.json

$PY -m src.datasets.prepare_cicids_subset --indir $CIC --ood $COMMON \
  --train-files "Wednesday-workingHours.pcap_ISCX.csv" --test-files "Friday-WorkingHours-Morning.pcap_ISCX.csv" \
  --out-train data/processed/cicids_ood_wednesday_train.csv --out-test data/processed/cicids_ood_friday_morning_test.csv \
  --report data/processed/cicids_ood_wednesday_vs_friday_morning.prep_report.json

# UNSW-NB15 temporal pair (official train -> official test), schema = intersection, no _source_file
$PY -m src.datasets.prepare_cicids_subset --indir data/raw/staging/unsw_nb15 --ood \
  --label-col attack_cat --benign-token normal --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 \
  --schema-from intersection \
  --train-files "unsw_train.csv" --test-files "unsw_test.csv" \
  --out-train data/processed/unsw_ood_train.csv --out-test data/processed/unsw_ood_test.csv \
  --report data/processed/unsw_ood_train_vs_test.prep_report.json
```

Every parameter above is read from the corresponding report
(`dataset_id_payload`: `mode`, `train_files_used`/`test_files_used`,
`label_col_clean`, `benign_token`, `drop_non_numeric`, `max_nan_frac`,
`keep_source_file`, `schema_from`, `n_total`, `prep_seed`). The CICIDS pairs that
share a training day produce byte-identical training tables (the two Tuesday
and the two Wednesday files above), which is why the hash table in Section 4
lists them together.

## 5. Compact reproduction (needs only `data/cicids_subset.csv`)

These runs exercise the executable parts of the study that are cheap on a
laptop and need no raw dataset because the CICIDS subset is tracked:

```bash
$PY -m src.experiments.run_quantum_integrity_gate      # 165-cell simulator gate
$PY -m src.experiments.make_quantum_integrity_figure
$PY -m src.hsaas.demo                                  # six-scenario, four-contract prototype
```

(`pwsh`: prefix each with `& $PY`.) The strict manifests and hash-chained
envelopes are written under `results/paper_digest/`. The installed console
entry point `athena-aegis-demo` (`pip install -e ".[dev]"`) runs the same
prototype. Both are local research prototypes, not a deployed service,
authenticated provider ledger or QPU run.

The policy gates (Gate F calibration, Gate D offline end-to-end decisions)
need only the frozen 1.1.1 derived tables that are part of the compact
artifact and of `results/paper_digest/` in a full checkout:

```bash
$PY -m src.experiments.build_q1_policy_evidence        # Gate F + Gate D from frozen outputs
$PY -m src.experiments.make_q1_policy_tables
$PY -m src.experiments.make_q1_policy_figures
```

They re-execute no kernel and no draw; their protocol was frozen in
`manuscript/paper15_v12_policy_prereg.md` before analysis (amendment A1
recorded) and amended in `manuscript/paper15_v13_prereg.md` (amendment A2:
the 1.2.0 family rule was replaced by the conformal max-rank rule after its
stated guarantee was found false; the superseded rule is recomputed as a
comparison column, never as the adopted rule; amendment A3 fixes the
evaluation of check F4). The builder prints every acceptance check
(F0, F1, F3, F4, D1--D5, W8) and fails closed on any failure.

The adversarial gate (Gate A, artifact 1.3.0) needs the staged datasets of
the eight environments because it executes 240 new exact-statevector jobs;
see Section 6.6. Its evidence builder, tables and figure run from the frozen
raw outputs:

```bash
$PY -m src.experiments.build_q1_adversarial_evidence   # Gate A tables + manifest, checks A0, AC1--AC4
$PY -m src.experiments.make_q1_policy_tables           # includes the adversarial tables and macros
$PY -m src.experiments.make_q1_adversarial_figures
```

## 6. Full replay (needs the staged datasets)

Run in this order. Every queue supports `--resume`, so re-running after an
interruption is safe. Compute cost on the reference machine: about 30 minutes
for the 360-job exact-statevector expansion and about 45 minutes for the
390-job reinforcement queue with six workers; Gate 1 uses the slower Qiskit
reference evaluator.

### 6.1 Frozen Gate 1 (CICIDS ID, Qiskit reference evaluator)

The raw Gate 1 jobs were produced with `run_grid` using the Qiskit reference
evaluator (`--q-backend-method statevector`); the per-job `run_cfg` metadata in
`results/raw/paper15_q1_gate1_id_seeds_20/*.json` and the design recorded in
`gate1_evidence_manifest.json` (five split seeds 42–46, four model seeds 42–45,
dimensions 8/10/12, maps `zz`, `z`, `pauli_xyz`, 128/128, `paper_core`)
correspond to:

```bash
$PY -m src.experiments.run_grid --protocol id --id-data data/cicids_subset.csv \
  --dims 8,10,12 --split-seeds 42,43,44,45,46 --model-seeds 42,43,44,45 \
  --q-feature-maps zz,z,pauli_xyz --attack-suite paper_core --max-train 128 --max-test 128 \
  --q-reps 1 --q-backend-method statevector --q-shots 1024 --q-max-iter 1000 --run-both \
  --outdir results/raw/paper15_q1_gate1_id_seeds_20 --resume
$PY -m src.experiments.build_q1_gate1_evidence
```

This command is reconstructed from the metadata (the original launch line was
not archived); the frozen Gate 1 tables are authoritative through their
manifested hashes, and the builder fails closed if the regenerated design
differs.

### 6.2 Exact-statevector expansion (360 jobs, eight environments)

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./run_paper15_q1_exact_queue.ps1
```

The queue script resolves the repository from its own location and uses
`.venv/Scripts/python.exe` or `.venv/bin/python`, so it runs unchanged on
Linux/macOS under `pwsh`. It uses two quantum workers; on restricted Windows
sessions it may need an elevated shell because Python multiprocessing creates
named pipes. Monitor with `Get-Content results/logs/paper15_q1_exact_queue_console.log -Tail 30 -Wait`
(or `tail -f`). The two older queues `run_paper15_q1_queue.ps1` and
`run_paper15_q1_queue2.ps1` are the historical pairwise-evaluator versions
that the exact queue superseded; they are kept for provenance. Then:

```bash
$PY -m src.experiments.build_q1_expansion_evidence --allow-partial   # progress snapshot (optional)
$PY -m src.experiments.build_q1_expansion_evidence                   # strict: fails unless 360/360 jobs exist
```

### 6.3 Quantum-specific simulator gate and contract prototype

See Section 5 (`run_quantum_integrity_gate`, `make_quantum_integrity_figure`,
`src.hsaas.demo`).

### 6.4 Reinforcement gates (artifact 1.1.0)

```bash
$PY -m src.experiments.run_v11_reinforcement_queue --gates N,P,T --n-jobs 6
$PY -m src.experiments.build_q1_reinforcement_evidence
$PY -m src.experiments.make_q1_reinforcement_figures
$PY -m src.experiments.make_q1_reinforcement_tables
```

The queue is a cross-platform Python runner (390 jobs: 240 null-calibration,
90 preprocessing-ablation, 60 tuned-baseline; single-threaded BLAS per
worker). Protocol: `manuscript/paper15_v11_reinforcement_prereg.md`.

### 6.5 Policy gates (artifacts 1.2.0 and 1.3.0)

```bash
$PY -m src.experiments.build_q1_policy_evidence
$PY -m src.experiments.make_q1_policy_tables
$PY -m src.experiments.make_q1_policy_figures
```

### 6.6 Adversarial gate (artifact 1.3.0), artifact assembly and verification

The preregistered cluster-preserving attacker
(`manuscript/paper15_v13_prereg.md`, Gate A; `src/attacks/cluster_preserving.py`)
is executed by a dedicated queue over the eight environments, five split
seeds and three feature dimensions (240 jobs, suite `paper_f5`: clean control,
six matched unconstrained controls and ten cluster-preserving conditions per
job). The queue is resumable; its status file records the log path of every
job.

```bash
$PY -m src.experiments.run_v13_f5_queue                 # 240 exact-statevector jobs, resumable
$PY -m src.experiments.build_q1_adversarial_evidence    # Gate A evidence + manifest
$PY -m src.experiments.make_q1_policy_tables
$PY -m src.experiments.make_q1_adversarial_figures
$PY -m src.experiments.assemble_publication_artifact
$PY -m src.experiments.verify_publication_artifact --root publication/artifact
$PY -m src.experiments.verify_publication_artifact --root results/paper_digest   # same checks on the full digest
```

The matched controls of the adversarial suite must replay the frozen 1.1.1
observations exactly (check AC1, maximum absolute difference within 1e-9 on
4,200 rows); the builder fails closed otherwise.

A successful full replay reproduces the manifested output hashes of the
compact artifact, except that the two gate-completeness tables record the
repository-relative raw-result directories of the replaying checkout.

## 7. Claim boundary

The completed software supports information-set conditional integrity
auditing from data and preprocessing through simulated circuit
construction/transpilation, kernel estimation, prediction, labels and
benchmark conclusion, plus the conformally calibrated, information-aware
`allow/hold/block` policy layer evaluated offline on the frozen outputs and
the adaptive cluster-preserving attacker executed against it. Exact
blind-region claims use constructed raw invariance; non-zero sensor responses
are calibrated against clean draws within the frozen design and are not
presented as deployment-level detector power. Split-cluster intervals describe
uncertainty within each of eight fixed environments and are not
population-level or multiplicity-adjusted inference.

Malicious scheduling/provider behaviour, device-calibrated noise, backend
operations, multi-tenant interference, side channels, QPU execution and Fleet
Management are explicitly excluded from this article. Reproducing them is
neither necessary nor sufficient to validate the frozen claim reported here.
