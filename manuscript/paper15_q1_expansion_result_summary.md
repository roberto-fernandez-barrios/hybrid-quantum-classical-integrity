# Paper 1.5 Q1 expansion: completed result summary

Date: 2026-08-09  
Evidence status: complete and fail-closed validated.

## Completion and audit

- 360/360 prespecified exact-statevector jobs completed; 0 failures.
- Eight fixed expansion environments: CICIDS ID at 256/256, UNSW-NB15 ID,
  ToN-IoT ID, four temporal CICIDS OOD pairs, and one UNSW OOD pair.
- Five split clusters and two nested model seeds per environment/dimension/map.
- 13,680 raw rows; 11,400 unique observations after verifying and removing
  2,280 repeated SVC rows.
- Every CSV has matching JSON metadata and hashes in the evidence manifest.
- The ideal-statevector engine passed reference-matrix and end-to-end replay
  validation; it is not finite-shot or QPU evidence.

## Primary result: replicated information-set boundary

The expansion contains 3,600 observations from random or prior-preserving
label perturbations.

- 3,600/3,600 leave predictions, feature evidence, and
  feature-plus-prediction evidence exactly unchanged.
- 1,800/1,800 prior-preserving observations also leave both label-marginal
  signals exactly unchanged.
- 2,184/3,600 produce positive balanced-accuracy conclusion impact.
- 2,184/2,184 of those materially positive cases produce non-zero
  joint-outcome evidence.

This is the central empirical contribution. It reproduces the formal
information-set claim across every expansion environment and model profile:
feature or score monitoring cannot identify an evaluation-label change that
does not enter its observable sigma-field; joint trusted outcomes or provenance
can close that gap.

## Secondary result: ZZ-versus-SVC model profile

The inferential endpoint is the within-split ZZ-minus-SVC mean conclusion-impact
difference, after averaging the two nested model seeds. Intervals are two-sided
95% Student-t intervals over five split clusters.

| Environment | d=8 mean [95% CI] | d=10 mean [95% CI] | d=12 mean [95% CI] |
|---|---:|---:|---:|
| CICIDS ID 256 | 0.03143 [0.02050, 0.04236] | 0.05214 [0.03543, 0.06885] | 0.04510 [0.03674, 0.05347] |
| UNSW-NB15 ID | 0.02197 [0.01111, 0.03282] | 0.04062 [0.03136, 0.04988] | 0.04840 [0.03716, 0.05964] |
| ToN-IoT ID | 0.09382 [0.07740, 0.11024] | 0.09508 [0.07550, 0.11466] | 0.11585 [0.09166, 0.14004] |
| CICIDS Tue→Wed | -0.00009 [-0.00179, 0.00161] | 0.00107 [-0.00314, 0.00528] | 0.00835 [-0.01077, 0.02747] |
| CICIDS Tue→Fri-PortScan | 0.03790 [-0.00393, 0.07972] | 0.07959 [0.04797, 0.11121] | 0.10716 [0.07674, 0.13759] |
| CICIDS Wed→Thu-Web | 0.00483 [-0.00154, 0.01120] | 0.00939 [0.00040, 0.01838] | 0.01826 [-0.00065, 0.03717] |
| CICIDS Wed→Fri-AM | 0.00301 [-0.00068, 0.00671] | 0.00407 [0.00057, 0.00756] | 0.00403 [-0.00276, 0.01081] |
| UNSW temporal OOD | 0.02258 [0.01479, 0.03036] | 0.03791 [0.02603, 0.04978] | 0.04827 [0.04000, 0.05653] |

Direction counts:

| Dimension | Environments with positive mean | Environment CIs excluding zero | Range of means |
|---:|---:|---:|---:|
| 8 | 7/8 | 4/8 | [-0.00009, 0.09382] |
| 10 | 8/8 | 7/8 | [0.00107, 0.09508] |
| 12 | 8/8 | 5/8 | [0.00403, 0.11585] |

These are fixed-environment consistency summaries, not a pooled population
effect. The profile is heterogeneous and several OOD clean baselines approach
chance. Clean balanced accuracy correlates with suite-average conclusion impact
across expansion cells (`r=0.714`, exploratory), demonstrating performance
headroom confounding. The paper must not translate this profile into “quantum
kernels are generally more vulnerable.”

## Claim disposition

Safe as primary:

- auditability is conditional on the information set;
- label-only and prior-preserving perturbations have exact blind regions;
- model-output impact and evaluation-conclusion impact are different causal
  loci;
- the coverage boundary replicates across the eight fixed environments;
- integrity claims require boundary, observable evidence, coverage, residual
  blind region, and response policy.

Safe only as secondary and conditional:

- QSVC-ZZ usually has greater suite-average conclusion impact than SVC-RBF;
- the direction is broadly consistent, but magnitude and interval support vary;
- comparisons are between complete frozen pipelines and do not isolate quantum
  geometry from preprocessing or clean-performance headroom.

Not supported by current evidence:

- universal quantum vulnerability or robustness;
- calibrated finite-shot/noise, hardware, malicious compiler/scheduler,
  multi-tenant, or side-channel claims;
- population-level generalization from the eight fixed environments;
- full coverage of ATHENA-AEGIS G3.1.

## ATHENA-AEGIS status

The artifact provides strong software and empirical evidence for the
data-to-evaluation portion of G3.2 and the metrics/coverage mechanisms under
G3.3. The completed 165-cell Gate D simulator tier adds circuit/parameter
mutation, semantics-preserving transpilation controls, controlled kernel
corruption, finite-shot emulation, and layered countermeasures, materially
strengthening G3.1. Complete Deusto-side quantum-lifecycle justification still
requires the operational tier: calibrated backend noise, scheduling/provider
evidence, multi-tenant testing, and QPU execution.

## Generated artifacts

- strict manifest: `results/paper_digest/paper15_q1_expansion/expansion_evidence_manifest.json`
- clustered forest source: `expansion_paired_zz_minus_svc_clustered.csv`
- sensor coverage source: `expansion_sensor_regime_table.csv`
- forest plot: `results/figures/paper15_q1_expansion/fig_q1_external_forest.{png,pdf}`
- coverage matrix: `results/figures/paper15_q1_expansion/fig_q1_sensor_coverage.{png,pdf}`
- figure manifest: `results/figures/paper15_q1_expansion/figure_manifest.json`
