# Reproducing and verifying the published artifact

This guide covers release `1.3.7`, the sensor-correction and label-geometry
closure release, under concept DOI
[10.5281/zenodo.22550852](https://doi.org/10.5281/zenodo.22550852). Its
version DOI is
[10.5281/zenodo.22698329](https://doi.org/10.5281/zenodo.22698329). Its
immutable predecessor is version `1.3.6`, DOI
[10.5281/zenodo.22694063](https://doi.org/10.5281/zenodo.22694063). Version
1.3.7 adds separate corrective evidence; no previous evidence file is changed. The compact
artifact can be verified without benchmark datasets. A full replay additionally
requires the public CICIDS2017, UNSW-NB15, and ToN-IoT source files.

Run commands from the repository root. PowerShell examples use `$PY`; POSIX
examples use `PY`. The authoritative release counts, page totals, PDF hashes,
and DOI are recorded in `publication/RELEASE_STATUS.md`.

## 1. Quick verification

Create the reference environment:

```powershell
python -m venv .venv
$PY = if (Test-Path .venv\Scripts\python.exe) { ".venv\Scripts\python.exe" } else { ".venv/bin/python" }
& $PY -m pip install -r requirements-lock.txt
& $PY -m pip install -e . --no-deps
```

Then run the tests and the fail-closed artifact verifier:

```powershell
& $PY -m pytest -q -p no:cacheprovider
& $PY -m src.experiments.verify_publication_artifact --root publication\artifact
```

No raw dataset is needed for these checks. The verifier validates the
artifact-wide SHA-256 manifest, eleven embedded evidence manifests and their
manifested outputs, CSV row counts, acceptance checks, and the primary counts
recomputed from the frozen derived evidence.

An unpacked `paper15-q1-v1.3.7.zip` can be verified independently from its own
root with:

```powershell
python -m pip install pandas==2.3.3
python software/src/experiments/verify_publication_artifact.py --root .
```

## 2. Full reproduction

Full replay begins only after the dataset checks in Section 3 pass with
`--require-raw --require-staged`. Every long-running queue is resumable.

Gate 1 uses the Qiskit reference evaluator. Its launch command was reconstructed
from the frozen per-job configuration and evidence manifest:

```bash
$PY -m src.experiments.run_grid --protocol id --id-data data/cicids_subset.csv \
  --dims 8,10,12 --split-seeds 42,43,44,45,46 --model-seeds 42,43,44,45 \
  --q-feature-maps zz,z,pauli_xyz --attack-suite paper_core \
  --max-train 128 --max-test 128 --q-reps 1 \
  --q-backend-method statevector --q-shots 1024 --q-max-iter 1000 --run-both \
  --outdir results/raw/paper15_q1_gate1_id_seeds_20 --resume
$PY -m src.experiments.build_q1_gate1_evidence
```

Run the eight-environment exact-statevector expansion and rebuild its evidence:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ./run_paper15_q1_exact_queue.ps1
& $PY -m src.experiments.build_q1_expansion_evidence
```

Run the quantum-integrity and contract components:

```powershell
& $PY -m src.experiments.run_quantum_integrity_gate
& $PY -m src.experiments.make_quantum_integrity_figure
& $PY -m src.hsaas.demo
```

Run the reinforcement, policy, and adversarial stages in order:

```powershell
& $PY -m src.experiments.run_v11_reinforcement_queue --gates N,P,T --n-jobs 6
& $PY -m src.experiments.build_q1_reinforcement_evidence
& $PY -m src.experiments.make_q1_reinforcement_figures
& $PY -m src.experiments.make_q1_reinforcement_tables
& $PY -m src.experiments.build_q1_policy_evidence
& $PY -m src.experiments.make_q1_policy_tables
& $PY -m src.experiments.make_q1_policy_figures
& $PY -m src.experiments.run_v13_f5_queue
& $PY -m src.experiments.build_q1_adversarial_evidence
& $PY -m src.experiments.make_q1_adversarial_figures
```

Run the preregistered geometry-aligned sensitivity. This deterministically
replays the frozen model configurations; it performs no model selection or
hyperparameter search:

```powershell
& $PY -m src.experiments.run_v135_geometry_queue --n-jobs 6 --retries 1
& $PY -m src.experiments.build_v135_geometry_sensitivity --out-dir results/paper_digest/paper15_v135_geometry_sensitivity
& $PY -m src.experiments.verify_geometry_sensitivity --evidence-dir results/paper_digest/paper15_v135_geometry_sensitivity
```

Run the preregistered v1.3.7 dependency-limited correction. The queue rebuilds
the same frozen models and verifies their clean predictions before accepting a
job; it introduces no model selection, attack or calibration campaign:

```powershell
& $PY -m src.experiments.run_v137_correction_queue --n-jobs 6 --retries 1
& $PY -m src.experiments.build_v137_correction_evidence
& $PY -m src.experiments.verify_v137_correction
& $PY -m src.experiments.make_v137_tables
& $PY -m src.experiments.make_v137_figures
```

Verify the full digest and assemble a separate compact copy without overwriting
the checked-in artifact:

```powershell
& $PY -m src.experiments.verify_publication_artifact --root results/paper_digest
& $PY -m src.experiments.assemble_publication_artifact --out tmp/reproduced-artifact
& $PY -m src.experiments.verify_publication_artifact --root tmp/reproduced-artifact
pwsh -NoProfile -File publication/tdsc/build.ps1
```

## 3. Datasets

The raw datasets are not redistributed. Obtain them from their official
publishers and retain their original terms:

| Dataset | Official source | Required files |
|---|---|---|
| CICIDS2017 | [Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/ids-2017.html) | Six `MachineLearningCVE` day/attack CSVs |
| UNSW-NB15 | [UNSW Canberra Cyber](https://research.unsw.edu.au/projects/unsw-nb15-dataset) | Official training and testing CSVs |
| ToN-IoT | [UNSW Canberra Cyber](https://research.unsw.edu.au/projects/toniot-datasets) | `train_test_network.csv` |

Place them under:

```text
data/raw/cicids2017/MachineLearningCVE/
data/raw/unsw_nb15/Training and Testing Sets/
data/raw/ton_iot/
```

The expected raw SHA-256 values are:

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
| `train_test_network.csv` | `26ddc513552de36de6428b2e578efaed2b57504c716dfba847cc0109a64e1974` |

All raw and staged identities are also machine-readable in
`publication/DATASET_HASHES_v1.3.6.json`. In a clean clone,
`scripts/verify_datasets.py` validates that public manifest and reports the
optional data files as absent; with local data, `--require-raw
--require-staged` verifies all 24 files byte-for-byte.

Stage UNSW-NB15 and ToN-IoT, then create the balanced subsets and temporal
pairs using the recorded seed (`42`) and sample size (`3,000`):

```powershell
& $PY -m src.datasets.stage_unsw_ton
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/cicids2017/MachineLearningCVE --use-only-files "Monday-WorkingHours.pcap_ISCX.csv" "Tuesday-WorkingHours.pcap_ISCX.csv" "Wednesday-workingHours.pcap_ISCX.csv" --label-col Label --benign-token benign --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --out data/cicids_subset.csv --report data/cicids_subset.prep_report.json
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/staging/unsw_nb15 --label-col attack_cat --benign-token normal --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --out data/unsw_subset.csv --report data/unsw_subset.prep_report.json
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/staging/ton_iot --label-col type --benign-token normal --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --out data/ton_iot_subset.csv --report data/ton_iot_subset.prep_report.json
```

Create the four CICIDS2017 temporal pairs and the UNSW-NB15 official
train-to-test pair:

```powershell
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/cicids2017/MachineLearningCVE --ood --label-col Label --benign-token benign --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --schema-from train --keep-source-file --train-files "Tuesday-WorkingHours.pcap_ISCX.csv" --test-files "Wednesday-workingHours.pcap_ISCX.csv" --out-train data/processed/cicids_ood_tuesday_train.csv --out-test data/processed/cicids_ood_wednesday_test.csv --report data/processed/cicids_ood_tuesday_vs_wednesday.prep_report.json
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/cicids2017/MachineLearningCVE --ood --label-col Label --benign-token benign --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --schema-from train --keep-source-file --train-files "Tuesday-WorkingHours.pcap_ISCX.csv" --test-files "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv" --out-train data/processed/cicids_ood_tuesday_train_portscan.csv --out-test data/processed/cicids_ood_friday_portscan_test.csv --report data/processed/cicids_ood_tuesday_vs_friday_portscan.prep_report.json
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/cicids2017/MachineLearningCVE --ood --label-col Label --benign-token benign --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --schema-from train --keep-source-file --train-files "Wednesday-workingHours.pcap_ISCX.csv" --test-files "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv" --out-train data/processed/cicids_ood_wednesday_train.csv --out-test data/processed/cicids_ood_thursday_webattacks_test.csv --report data/processed/cicids_ood_wednesday_vs_thursday_webattacks.prep_report.json
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/cicids2017/MachineLearningCVE --ood --label-col Label --benign-token benign --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --schema-from train --keep-source-file --train-files "Wednesday-workingHours.pcap_ISCX.csv" --test-files "Friday-WorkingHours-Morning.pcap_ISCX.csv" --out-train data/processed/cicids_ood_wednesday_train.csv --out-test data/processed/cicids_ood_friday_morning_test.csv --report data/processed/cicids_ood_wednesday_vs_friday_morning.prep_report.json
& $PY -m src.datasets.prepare_cicids_subset --indir data/raw/staging/unsw_nb15 --ood --label-col attack_cat --benign-token normal --drop-non-numeric --max-nan-frac 0.2 --n-total 3000 --seed 42 --schema-from intersection --train-files "unsw_train.csv" --test-files "unsw_test.csv" --out-train data/processed/unsw_ood_train.csv --out-test data/processed/unsw_ood_test.csv --report data/processed/unsw_ood_train_vs_test.prep_report.json
```

The staged identities expected by the frozen design are:

| Staged table | Rows | SHA-256 |
|---|---:|---|
| `data/cicids_subset.csv` | 3,000 | `8c8771f4e348bcbd6a58c8e215ba143d6f98a4a7a341d0e991bb8f3c211a9588` |
| `data/unsw_subset.csv` | 3,000 | `6292a46b03eef422acd660f68b5c76c3e04118a63d617a8e5f5b755450078780` |
| `data/ton_iot_subset.csv` | 3,000 | `cc6a61e9a3c294b5520cb59e8874c12929d1a91acca92f06c1ca868a5768c01b` |
| `data/raw/staging/unsw_nb15/unsw_train.csv` | 175,341 | `ff8f800823506ffba408c7edbe6f1d57c1707b098e7ed6e3785a8d9d2dc10c75` |
| `data/raw/staging/unsw_nb15/unsw_test.csv` | 82,332 | `0aa749da7abc0dc38ff2c1ea1c6636095e4795dcd09f1975e70511957c4608e4` |
| `data/raw/staging/ton_iot/ton_network.csv` | 211,043 | `443619d118439d8e9e1f7593f8e929c1d45cf0014739b861484c85a07ae7614f` |
| `data/processed/cicids_ood_tuesday_train.csv` | 3,000 | `649b5ffb6a09a89cb28f021ef8878ed990d0c5c2f2283fe1394f9b5e88a500e9` |
| `data/processed/cicids_ood_wednesday_test.csv` | 3,000 | `c82af0bab09f10ac46dd078c5dbab4f46e8a67fb5602dbedf4cdc3faf5a73c6d` |
| `data/processed/cicids_ood_friday_portscan_test.csv` | 3,000 | `0e535a9942a24bb09d7b04b1d3e3e2714a182ed3f4b7d62711ef329d2d392b11` |
| `data/processed/cicids_ood_thursday_webattacks_test.csv` | 3,000 | `3ec6a4d7c4b363d436088f064c43b1a0cffd72efd5825ab2a12ea1096c233674` |
| `data/processed/cicids_ood_friday_morning_test.csv` | 3,000 | `5c44b321468f72c3a4ef0f51135629092d253b02b7746cae64b5905a2fe89dd5` |
| `data/processed/unsw_ood_train.csv` | 3,000 | `993984caf61b9e60a68d9722fae9564edbd3ea91f8e2204b3ce13c26f612c350` |
| `data/processed/unsw_ood_test.csv` | 3,000 | `b9107599e6510ae5116d26ac952283814d80f8fdba775977893c2879a3c6cee0` |

The staging commands write the corresponding `*.prep_report.json` files used
by `scripts/verify_datasets.py`. Run:

```powershell
& $PY scripts/verify_datasets.py
& $PY scripts/verify_datasets.py --require-raw --require-staged
```

On the reference data layout the verifier reports `24 OK`, `0 MISMATCH`, and
no missing staged or raw file. A different source hash denotes a different
dataset release and cannot reproduce the frozen results bit for bit.

## 4. Environment

- Reference interpreter: Python 3.10.16.
- Locked packages: `requirements-lock.txt`.
- Core frozen versions: NumPy 2.2.6, pandas 2.3.3, scikit-learn 1.7.2,
  Qiskit 2.3.0, and Qiskit Machine Learning 0.9.0.
- LaTeX build: PowerShell 7, `pdflatex`, `bibtex`, IEEEtran 1.8b, and
  Poppler `pdfinfo`.

Qiskit 2.3 may emit deprecation warnings for BlueprintCircuit feature maps.
The environment intentionally remains below Qiskit 3 because changing circuit
constructors would alter frozen serialization and require a new scientific
version.

## 5. Expected outputs

A successful verification has the following invariants:

- the complete test suite passes; its collected count is recorded in
  `publication/RELEASE_STATUS.md`;
- eleven evidence manifests and all manifested outputs verify;
- Gate 1 contains 1,440 label-path rows; the expansion contains 3,600;
- the policy evidence contains 7,008 material observations over five regimes
  and four policies;
- the adversarial evidence contains 16 conditions and 6,000 adaptive rows;
- the geometry sensitivity contains 13,200 observations across eight
  environments and 22 frozen interventions, with exact identity, declared
  geometry, matched-control/adaptive pairing, and derived-summary checks;
- the v1.3.7 correction contains 64,560 accepted JSD-dependent observation
  rows, 3,600 aligned label rows, finite JSD throughout, and reproduces the
  original 11/2,617 and 43/2,617 label endpoints before alignment;
- the dataset verifier reports `24 OK / 0 mismatch / 0 missing` when all local
  raw and staged resources are present;
- the article builds to no more than 12 pages and the article abstract contains
  no more than 200 words. Final page totals are recorded in
  `publication/RELEASE_STATUS.md`.

Exact values and released PDF SHA-256 hashes are centralized in
`publication/RELEASE_STATUS.md`. A manifest, row-count, acceptance-check, or
primary-count mismatch is a verification failure.

## 6. Computational requirements

Quick verification requires Python 3.10, pandas, and the checked-in compact
artifact; it completes on a conventional laptop. The LaTeX build additionally
requires the tools listed in Section 4.

On the reference machine, the 360-job exact-statevector expansion took about
30 minutes and the 390-job reinforcement queue about 45 minutes with six
workers. Gate 1 uses the slower Qiskit reference evaluator. The adversarial
queue executes 240 exact-statevector jobs. The geometry sensitivity replays the
same 240 frozen configurations and writes a separate evidence tree. Runtime and
memory depend on CPU, process count, and BLAS configuration; the resumable
queues write under `results/`.

## 7. External and raw-resource limitations

- Raw CICIDS2017, UNSW-NB15, and ToN-IoT files must be downloaded separately;
  their licenses prohibit treating this repository as their distribution.
- The original Gate 1 launch command was not archived verbatim; the command in
  Section 2 is reconstructed from frozen job metadata, and manifested hashes
  remain authoritative.
- The historical CICIDS2017 ID preparation report predates the current report
  schema. Its recorded parameters are compatible with the current staging
  command, but the SHA-256 value is the final identity check.
- Exact-statevector execution and binomial shot emulation do not reproduce
  physical-QPU behavior, calibrated backend noise, scheduling, provider
  security, multi-tenancy, side channels, or operational services.
- Split-cluster intervals describe uncertainty within the eight fixed
  environments; they are not population-level or multiplicity-adjusted
  inference.
- The geometry-aligned sensitivity uses one fresh clean batch per frozen model
  cell and applies every intervention to that batch. It distinguishes the
  clean-resample geometry effect from within-geometry monitor-aware response,
  but it does not causally apportion the observed response among dataset
  cluster structure, editing geometry, and evasion mechanism.
- The label-side aligned sensitivity changes statistical response and its
  material denominator on the fixed fresh batch; structural aggregate-blind
  rows remain exactly equal to their paired clean response.
