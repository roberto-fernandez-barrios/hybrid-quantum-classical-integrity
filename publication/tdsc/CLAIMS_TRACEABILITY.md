# Claim-to-evidence traceability

This map is the reviewer-facing preflight for the TDSC manuscript. “Exact”
denotes a consequence of the declared information set and construction;
“empirical” denotes a result within the frozen finite design.

| Manuscript claim | Type | Primary evidence | Verification |
|---|---|---|---|
| Feature, score, and prediction sensors are blind to evaluation-label-only changes for a fixed predictor | Exact + exhaustive in design | `publication/artifact/evidence/expansion/expansion_sensor_regime_table.csv`; Gate-1 counterpart | Artifact verifier checks all 3,600 expansion and 1,440 Gate-1 label rows |
| Label marginals are blind to prior-preserving relabeling | Exact + exhaustive in design | Expansion and Gate-1 sensor-regime tables | Verifier checks all 1,800 prior-preserving expansion cases; supplement states the boundary |
| Every positive expansion conclusion impact is exposed by item-aligned joint evidence | Empirical within fixed design | `expansion_structurally_blind_positive_impact_cases.csv`; `expansion_evidence_manifest.json` | 2,184/2,184 verified positive impacts |
| Boundaries recur over three datasets and eight fixed ID/OOD environments | Empirical transport/replication | `expansion_external_consistency.csv`; `expansion_gate_completeness.csv` | 360/360 planned jobs and environment keys verified |
| ZZ-versus-SVC differences vary by environment and mechanism | Secondary sensitivity | `expansion_paired_zz_minus_svc_clustered.csv`; `fig_q1_external_forest.pdf` | Split-cluster summaries; no population or universal-ordering claim |
| Quantum sensors are complementary over 165 simulator cells | Empirical, simulator-only | `quantum_integrity_gate_sensor_coverage.csv`; `quantum_integrity_gate_clustered_summary.csv` | Manifest checks 165/165 cells and nine frozen acceptance conditions |
| Algebraic kernel checks can miss a positive-semidefinite substitution | Constructed blind-region witness | Quantum integrity observations and sensor-coverage table | Provenance/semantic sensors react while the algebraic sensor passes |
| Four ordered contracts execute fail-closed `allow/hold/block` decisions | Executable prototype | `hsaas_audit_envelopes.jsonl`; `hsaas_contract_summary.csv` | Six scenarios and eight acceptance checks; unit tests cover policy and chain integrity |
| Artifact files and counts have not changed silently | Integrity of released evidence | `publication/artifact/ARTIFACT_MANIFEST.sha256` plus four embedded manifests | `verify_publication_artifact` recomputes hashes, shapes, and primary counts |

## Claims intentionally unsupported

No evidence row supports physical-QPU security, calibrated backend noise,
scheduling or placement attacks, provider authentication, multi-tenancy,
side-channel resistance, attack prevalence, population incidence, production
readiness, non-repudiation, incident operations, or an operational Fleet
Management System. Those topics must not be inferred from simulator coverage or
the local hash chain.
