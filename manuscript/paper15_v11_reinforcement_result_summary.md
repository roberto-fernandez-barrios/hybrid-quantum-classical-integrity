# Paper 1.5 reinforcement gates — result summary (artifact 1.1.0)

Date: 2026-09-06  
Protocol: `manuscript/paper15_v11_reinforcement_prereg.md` (frozen before
execution; amendment A1 recorded).  
Evidence: `results/paper_digest/paper15_v11_reinforcement/` (22 tables,
`reinforcement_evidence_manifest.json`, 14/14 acceptance checks).  
Execution: 390/390 jobs, 0 failures, 2026-09-06 19:06–19:48, exact-statevector
engine, single-threaded BLAS per worker.

Nothing in the frozen 1.0.0 evidence changed. Every number below is reported as
executed.

## Gate N — null calibration with disjoint clean pools

**Design realized.** 240 runs (eight environments × 5 splits × 2 model seeds × 3
dimensions), 20 calibration and 20 disjoint evaluation clean draws per run,
identity and two near-null controls, 10,560 + 10,560 unique null-draw
observations (SVC, ZZ; plus Z and PauliXYZ in E2/E3). Pool halves: 1,436 rows
(CICIDS/UNSW OOD), 386 rows (UNSW/ToN-IoT ID), 322 rows (E1, n = 256).

**N1 — false-alarm rate (12,000 evaluation draws pooled, nominal 0.05).**

| Sensor | Rate [95% CI] | Sensor | Rate [95% CI] |
|---|---|---|---|
| Feature JSD | 0.050 [0.046, 0.054] | Prediction JSD | 0.049 [0.045, 0.053] |
| Feature MMD | 0.069 [0.064, 0.073] | Label prior shift | 0.048 [0.044, 0.052] |
| KS rejection | 0.029 [0.026, 0.032] | Label JSD | 0.048 [0.044, 0.052] |
| Score JSD | 0.056 [0.052, 0.060] | Confusion L1 | 0.043 [0.040, 0.047] |
| Prediction-rate shift | 0.043 [0.040, 0.047] | Confusion JSD | 0.053 [0.049, 0.057] |

Regime unions (uncorrected): I_X 0.125, I_XF 0.203, I_Ym 0.048, I_XFY 0.259.
Per-cell sensor rates (n = 200): median 0.04; excluding E1, 92.8% of cells lie
in [0.01, 0.10]. E1 (256-row draws from 322-row halves) and E3 ToN-IoT (25.7%
near-duplicate rows; MMD 0.172) show the highest regime rates and are flagged.

**N2 — exact blind regions survive calibration (acceptance checks).** On all
3,600 evaluation-label observations, calibrated I_X and I_XF fire 0 times; on
all 1,800 prior-preserving observations, calibrated I_Ym fires 0 times; the
item-aligned I_XF (prediction disagreement) fires 0 times.

**N3 — label path, joint evidence.** Item-aligned I_XFY detects 3,600/3,600
label interventions and 2,184/2,184 positive impacts (exact). Batch-level
I_XFY (distributional confusion statistics without item correspondence) detects
43/3,600 (1.2%) and 40/2,184 positive impacts (1.8%): a 2–10% label corruption
lies inside the natural variability of a fresh 128-row batch.

**N4 — feature-side interventions (pooled detection rate).**

| Intervention | I_X | I_XF | I_XFY | I_XFY item-aligned |
|---|---|---|---|---|
| Sign flip 0.02 / 0.05 / 0.10 | 0.12 / 0.53 / 0.76 | 0.19 / 0.64 / 0.88 | 0.20 / 0.64 / 0.88 | 0.79 / 0.87 / 0.91 |
| Mean shift 0.02 / 0.05 / 0.10 | 1.00 / 1.00 / 1.00 | 1.00 | 1.00 | 0.36 / 0.50 / 0.62 |
| Scaling drift 0.02 / 0.05 / 0.10 | 1.00 / 1.00 / 1.00 | 1.00 | 1.00 | 0.54 / 0.61 / 0.67 |
| Dropout 0.02 / 0.05 / 0.10 | 0.00 / 0.00 / 0.00 | 0.00 / 0.02 / 0.06 | 0.00 / 0.02 / 0.06 | 0.49 / 0.70 / 0.76 |

**N5 — near-null controls.** In-place Gaussian noise σ = 0.001 fires I_X in
71.2% of cells and scaling α = 0.001 in 87.9%, almost entirely through the KS
sensor; identity fires nowhere. Item-aligned prediction changes occur in 4.2%
and 9.9% of cells.

**Mechanism (`null_mass_point_profile.csv`).** Standardized projected features
contain tight clusters: in every environment some feature holds 69–87% of the
rows within 0.01 standard deviations (mean over features 0.43–0.75; 48–82%
within 0.001 SD). A fresh clean batch reproduces the cluster, so the KS null
is narrow; any in-place perturbation of order 1e-3 SD or larger smears it. This
is a legitimate fingerprint of unmodified data but a fragile one: perturbations
that preserve the cluster would evade it. It also explains why mean shift and
scaling drift are detected at 100% even at strength 0.02.

## Gate P — symmetric preprocessing ablation (CICIDS ID, 128/128)

ZZ − SVC within-split difference, mean [95% t CI], positive clusters:

| Configuration | d = 8 | d = 10 | d = 12 |
|---|---|---|---|
| P0 reference (standard / minmax2π) | 0.0245 [0.0069, 0.0422] 5/5 | 0.0348 [0.0176, 0.0520] 5/5 | 0.0407 [0.0305, 0.0509] 5/5 |
| PA standard / standard | 0.0070 [0.0014, 0.0125] 5/5 | 0.0130 [0.0041, 0.0219] 5/5 | 0.0111 [0.0052, 0.0170] 5/5 |
| PB minmax2π / minmax2π | 0.0239 [0.0054, 0.0423] 5/5 | 0.0323 [0.0156, 0.0491] 5/5 | 0.0396 [0.0261, 0.0531] 5/5 |

Direction is stable (5/5 clusters, all intervals above zero); magnitude is
scaler-dependent: standardizing the quantum branch cuts the difference by
about two thirds (ZZ suite impact 0.042–0.060 → 0.025–0.030) while SVC is
unchanged; matched min–max leaves it at the reference level. Clean balanced
accuracy: ZZ 0.720–0.747, SVC 0.747–0.778 across configurations. Exact
label-path invariance holds in every configuration (360/360, 180/180, all
positive impacts with joint response, no negative impact).

## Gate T — cross-validated tuning of both learners

| Environment | Condition | d = 8 | d = 10 | d = 12 |
|---|---|---|---|---|
| CICIDS ID | frozen defaults (P0) | 0.0245 [0.0069, 0.0422] | 0.0348 [0.0176, 0.0520] | 0.0407 [0.0305, 0.0509] |
| CICIDS ID | both tuned (CV5) | 0.0426 [0.0094, 0.0757] | 0.0713 [0.0494, 0.0932] | 0.0776 [0.0610, 0.0943] |
| UNSW temporal OOD | frozen defaults (E8) | 0.0226 [0.0148, 0.0304] | 0.0379 [0.0260, 0.0498] | 0.0483 [0.0400, 0.0565] |
| UNSW temporal OOD | both tuned (CV5) | 0.0230 [0.0103, 0.0356] | 0.0348 [0.0205, 0.0492] | 0.0459 [0.0371, 0.0546] |

All cells 5/5 positive clusters. Tuning widens the profile in CICIDS ID and
leaves UNSW OOD unchanged. Clean balanced accuracy: CICIDS ID tuned ZZ
0.750–0.802 (from 0.728–0.747) versus SVC 0.741–0.780 (≈ unchanged); UNSW OOD
tuned ZZ 0.757–0.770 versus SVC 0.723–0.739 (below the untuned 0.748–0.756,
as expected for training-only tuning under shift). Selected constants: QSVC
C = 100 in 17/30 CICIDS cells, C ∈ {1, 10} in all UNSW cells; SVC selections
spread over the grid. Exact label-path invariance holds in both environments.

## Interpretation and boundary

- The exact blind regions are not threshold artifacts: they are zero under
  calibration and are closed only by item-aligned evidence, exactly as the
  article's contract requires.
- Non-invariant sensors reach nominal false-alarm rates on disjoint clean
  pools; regime unions are honestly larger. Detection is mechanism-dependent
  and, for KS, rests on cluster structure that an adversary could preserve.
- The secondary ZZ-minus-SVC profile is direction-stable but magnitude-
  conditional on the quantum-branch scaler and on clean headroom; it must not
  be read as a universal ordering.
- These are fixed-design, simulator-only sensitivities. Context-conditioned
  runtime calibration, false-alarm budgets in operation, QPU, scheduling,
  provider security, multi-tenancy and Fleet Management remain outside this
  article.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -m src.experiments.run_v11_reinforcement_queue --gates N,P,T --n-jobs 6
.\.venv\Scripts\python.exe -m src.experiments.build_q1_reinforcement_evidence
.\.venv\Scripts\python.exe -m src.experiments.make_q1_reinforcement_figures
.\.venv\Scripts\python.exe -m src.experiments.make_q1_reinforcement_tables
```
