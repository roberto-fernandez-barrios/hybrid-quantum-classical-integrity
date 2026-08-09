# Paper 1.5 Q1 reproduction guide

This guide separates verification of the compact publication artifact from a
full replay of frozen Gate 1, the exact-statevector expansion, the
quantum-specific simulator gate and the local contract demonstrator. QPU,
scheduling, provider security, multi-tenancy and operational Fleet Management
are outside this paper and are not reproduction gates for its claim.

## Environment and tests

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

The reference evidence was produced with Python 3.10.16, NumPy 2.2.6,
pandas 2.3.3, scikit-learn 1.7.2, Qiskit 2.3.0 and Qiskit Machine Learning
0.9.0. The exact resolved environment is archived in
`publication/artifact/environment/requirements-lock.txt`. The cache provider is
disabled because restricted Windows sessions may deny creation of pytest's
temporary cache directories; this does not skip tests.

Qiskit 2.3 emits deprecation warnings for BlueprintCircuit-based feature-map
classes scheduled for removal in Qiskit 3. The release intentionally pins
Qiskit below 3 because migrating constructors would change frozen circuit
serialization and require a new evidence version. The warnings do not alter any
test or manifest result.

## Compact artifact verification (recommended first)

```powershell
.\.venv\Scripts\python.exe -m src.experiments.verify_publication_artifact `
  --root publication\artifact
```

This read-only command verifies the artifact-wide SHA-256 manifest, all four
embedded evidence manifests and 22 outputs, their row counts, and the exact
primary-claim counts. It fails on a missing file, changed byte, incomplete
acceptance check or changed blind-region result.

## Frozen Gate 1 evidence

```powershell
.\.venv\Scripts\python.exe -m src.experiments.build_q1_gate1_evidence
```

Primary intervals average nested model/perturbation seeds within each data
split and infer over the five split clusters. The 20 split-model combinations
are exported only as a sensitivity analysis. Repeated SVC rows are accepted as
duplicates only after the script verifies numerical identity.

## Exact-statevector expansion

The accelerated engine is selected explicitly:

```text
--q-backend-method exact_statevector
```

It evaluates the ideal fidelity kernel and is not a finite-shot, noisy, or QPU
backend. Its validation record is
`manuscript/paper15_exact_statevector_validation.md`.

Launch or resume all prespecified expansion gates:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\run_paper15_q1_exact_queue.ps1
```

Monitor progress:

```powershell
Get-Content results\logs\paper15_q1_exact_queue_console.log -Tail 30 -Wait
```

The queue uses two quantum workers. On restricted Windows sessions it may need
an elevated shell because Python multiprocessing creates named pipes.

Create a progress-only evidence snapshot:

```powershell
.\.venv\Scripts\python.exe -m src.experiments.build_q1_expansion_evidence --allow-partial
```

Create the reviewer-facing package after all gates finish:

```powershell
.\.venv\Scripts\python.exe -m src.experiments.build_q1_expansion_evidence
```

The strict command fails closed if any of the 360 expected CSV/JSON job pairs
is absent or a completed gate violates its declared model/dimension/seed/attack
design. Cross-environment summaries are descriptive fixed-case consistency;
they are not presented as random-effects population inference.

## Quantum-specific simulator gate

Rebuild the 165-cell circuit/kernel integrity experiment and its figure:

```powershell
.\.venv\Scripts\python.exe -m src.experiments.run_quantum_integrity_gate
.\.venv\Scripts\python.exe -m src.experiments.make_quantum_integrity_figure
```

The strict manifest records hashes for every evidence table. The gate includes
clean and semantic-equivalence controls, circuit/parameter mutations,
controlled algebraic and PSD-preserving kernel corruptions, and binomial
fidelity-estimation emulators at 256 and 1,024 shots. The latter sample exact
fidelities; they are not sampler-backend or QPU runs. Reviewer-facing copies
of the figure and small tables are under `manuscript/figures/` and
`manuscript/tables/`.

## Auditable HSaaS demonstrator

Run the six-scenario, four-contract fail-closed prototype:

```powershell
.\.venv\Scripts\python.exe -m src.hsaas.demo
```

Alternatively, install the local package and use its stable console entry point:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\athena-aegis-demo.exe
```

The strict manifest and hash-chained envelopes are written under
`results/paper_digest/paper15_hsaas_demo/`. This is a local research prototype,
not a deployed HTTP service, authenticated provider ledger, or QPU run.

## Claim boundary

The completed software supports information-set conditional integrity auditing
from data and preprocessing through simulated circuit construction/transpilation,
kernel estimation, prediction, labels and benchmark conclusion. Exact
blind-region claims use constructed raw invariance; non-zero sensor responses
are not presented as calibrated operational alarms. Split-cluster intervals
describe uncertainty within each of eight fixed environments and are not
population-level or multiplicity-adjusted inference.

Malicious scheduling/provider behaviour, device-calibrated noise, backend
operations, multi-tenant interference, QPU execution and Fleet Management are
explicitly excluded from this article. Reproducing them is neither necessary nor
sufficient to validate the frozen claim reported here.
