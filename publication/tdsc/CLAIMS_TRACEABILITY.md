# Claim-to-evidence traceability (artifact 1.2.0)

This map is the reviewer-facing preflight for the TDSC manuscript. "Exact"
denotes a consequence of the declared view and construction; "empirical"
denotes a result within the frozen finite design. Every number printed in
the article about the 1.2.0 gates enters through
`publication/tdsc/tables/policy_macros.tex`, generated from the manifested
tables.

| Manuscript claim | Type | Primary evidence | Verification |
|---|---|---|---|
| Structural blind regions are monotone under refinement and closed exactly by added evidence that separates the class (Props. 1–2) | Formal | `manuscript/FORMAL_CORE.md`; supplement Sec. 2 | Proofs; Corollaries reproduce the 1.1.x propositions |
| Feature, score and prediction sensors are blind to label-only changes for a fixed predictor; label marginals are blind to prior-preserving relabeling | Exact + exhaustive in design | `evidence/expansion/expansion_sensor_regime_table.csv`; Gate-1 counterpart | Verifier checks all 3,600 expansion and 1,440 Gate-1 label rows and all 1,800 prior-preserving rows |
| Signed conclusion change on the label path: 2,184 lowered / 983 unchanged / 433 raised (Gate 1: 1,276 / 105 / 59); every changed conclusion (2,617; 1,335) has non-zero item-aligned confusion evidence (Prop. 3) | Exact + empirical | `expansion_unique_observations.csv`, `gate1_unique_observations.csv`; `evidence/policy/counterexample_witnesses.csv` (W8) | Verifier recomputes the signed counts and the joint response of every changed-conclusion row |
| Counterexample witnesses C1–C8 | Empirical realisations of minimal constructions | `evidence/policy/counterexample_witnesses.csv` | Manifest hash; W8 is an acceptance check |
| Boundaries recur over three datasets and eight fixed ID/OOD environments | Empirical replication | `expansion_external_consistency.csv`; `expansion_gate_completeness.csv` | 360/360 planned jobs and environment keys verified |
| Null-calibrated feature/prediction regimes never fire on label interventions; label-marginal regime never fires on prior-preserving ones (Prop. 4(i)) | Exact invariance survives calibration (1.1.0) | `evidence/reinforcement/calibrated_label_path_summary.csv`; `null_calibration_thresholds.csv` | Verifier recomputes zero firings; thresholds from calibration draws only |
| Per-sensor calibration at alpha = 0.05 gives decision false-alarm rates 0.125 / 0.203 / 0.048 / 0.259; family calibration gives 0.061 / 0.073 / 0.048 / 0.079 (Prop. 5); inference unit is the (environment, split) cluster | Empirical, fixed design, simulator | `evidence/policy/family_false_alarm_overall.csv`, `family_false_alarm_by_environment.csv`, `family_false_alarm_by_cluster.csv`, `inference_units.csv` | Verifier checks family rate ≤ union rate per regime; F0 reproduces the frozen per-sensor thresholds |
| Batch-level I_XFY detects 16 (family) / 43 (union) of 2,617 material label rows; item-aligned auditor detects all 2,617 (Prop. 4) | Empirical (statistical vs exact separation) | `evidence/policy/family_label_path_summary.csv` | Verifier checks F3 zero firings; D3 acceptance check |
| Unsafe allows under calibrated policies: 4,494 / 4,327 / 7,008 / 4,322 of 7,008 for I_X / I_XF / I_Ym / I_XFY; 0 for I_XFY* with 0 false holds; strict policy serves nothing where the label boundary is unverified | Empirical end-to-end evaluation | `evidence/policy/policy_metrics.csv`, `policy_metrics_by_family.csv`, `policy_metrics_by_environment.csv`, `policy_decision_counts.csv`, `policy_reason_counts.csv` | Verifier checks P0 unsafe = material, trusted regime 0 unsafe / 0 false holds; D1–D4 acceptance checks |
| Composition of the policy layer with the four frozen contracts reproduces the six envelope actions | Executable prototype | `evidence/policy/policy_contract_composition.csv`; `evidence/hsaas/hsaas_audit_envelopes.jsonl` | D5 acceptance check; unit tests of the lattice |
| Adversary and failure model per executed intervention | Declarative | `manuscript/ADVERSARY_MODEL.md`; main Table 3 | Every row cites the frozen rate it quotes |
| Quantum sensors are complementary over 165 simulator cells; algebraic checks miss a PSD-preserving substitution | Empirical, simulator-only | `evidence/quantum_integrity/*` | Manifest checks 165/165 cells and nine acceptance conditions |
| The secondary ZZ-minus-SVC profile is direction-stable but scaler- and headroom-dependent | Secondary sensitivity | `evidence/reinforcement/prep_ablation_paired_zz_minus_svc.csv`, `tuned_paired_zz_minus_svc.csv`; `expansion_paired_zz_minus_svc_clustered.csv` | Split-cluster intervals; label-path invariance re-verified in every configuration |
| Artifact files and counts have not changed silently | Integrity of released evidence | `publication/artifact/ARTIFACT_MANIFEST.sha256` plus six embedded manifests | `verify_publication_artifact` recomputes hashes, shapes and primary counts; `publication/RELEASE_STATUS.md` records the counts |

## Claims intentionally unsupported

No evidence row supports physical-QPU security, calibrated backend noise,
scheduling or placement attacks, provider authentication or attestation,
multi-tenancy, side-channel resistance, attack prevalence, population
incidence, production readiness, non-repudiation, incident operations,
context-conditioned runtime calibration under non-stationarity, abstention
with recovery, or an operational Fleet Management System. Those topics must
not be inferred from simulator coverage, from the local hash chain, or from
the fixed-design calibration.
