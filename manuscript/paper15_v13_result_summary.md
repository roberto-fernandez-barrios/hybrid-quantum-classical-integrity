# Paper 1.5 artifact 1.3.0 — result summary (amendment A2, regenerated Gates F and D, adversarial Gate A)

Date: 2026-09-07  
Note (artifact 1.3.1, same day): this summary records the frozen 1.3.0
evidence and is unchanged in every number. Version 1.3.1 renamed policy P3
*sensor-coverage-complete relative to the declared evidence dimensions* (fail-closed on missing coverage; no
minimum-power guarantee; the identifier `family_calibrated_strict` and every
decision are unchanged, only the `policy_class` label of the evidence tables
was regenerated), decomposed the trusted-regime interruption as 544
statistical holds + 85 exact-reference blocks = 629 of 1,200 near-null
synthetic controls (not operational benign traffic), and stated the conformal
result as "finite-sample level under exchangeability; observed 0.056 / 0.058 /
0.048 / 0.053 in the executed, non-exchangeable design". Where the tables
below say "P3 strict", read "P3 sensor-coverage-complete".
Protocol: `manuscript/paper15_v13_prereg.md` (frozen at commit `cad9136`
before any regenerated table or Gate A job existed; amendment A3 recorded at
`678c5d7` before the first builder run).  
Evidence: `results/paper_digest/paper15_v12_policy/` (27 tables, 12/12
consistency checks; regenerated) and
`results/paper_digest/paper15_v13_adversarial/` (12 tables, 5/5 acceptance
checks; new). Every number below is reported as executed and enters the
article through `publication/tdsc/tables/policy_macros.tex`.

## A2 — what changed and why

The family rule of artifact 1.2.0 scored calibration draws against the
calibration set only and the audited batch against all calibration draws. Its
stated guarantee (`alpha + 1/(n+1)`) was false: with several sensors and tied
max-rank scores the scores are not exchangeable, and a five-vector
configuration fires with probability 0.60 against a claimed 0.40. Artifact
1.3.0 adopts the full conformal max-rank p-value, whose level under
exchangeability is exactly `floor(alpha (n+1))/(n+1) = 10/201 = 0.0498`
with ties counted against firing (Proposition 5(b), version 1.2; exhaustive
tests). No kernel, model or draw was re-executed for Gates F and D.

## Gate F — decision-level false-alarm rate (12,000 disjoint evaluation draws, nominal 0.05)

| Regime | Union (1.1.0) | 1.2.0 rule (superseded) | Conformal (adopted) | Conformal, env. cluster means | Excluding E1 | E1 only |
|---|---|---|---|---|---|---|
| I_X (3 sensors) | 0.125 | 0.061 | 0.056 | 0.023–0.125 | 0.048 | 0.125 |
| I_XF (6) | 0.203 | 0.073 | 0.058 | 0.023–0.115 | 0.052 | 0.115 |
| I_Ym (2, perfectly dependent) | 0.048 | 0.048 | 0.048 | 0.025–0.070 | 0.048 | 0.045 |
| I_XFY (10) | 0.259 | 0.079 | 0.053 | 0.034–0.123 | 0.045 | 0.123 |

The conformal rule reproduces the pre-amendment diagnostic exactly
(0.056 / 0.058 / 0.048 / 0.053), as the preregistration said it would.

**Decomposition of the 1.2.0 excess.** Rule bias (1.2.0 minus conformal on
the same draws): +0.005 / +0.015 / 0.000 / +0.025. Design effect (conformal
minus nominal): +0.006 / +0.008 / −0.003 / +0.003. Under 30 exchangeable
random re-splits of the 400 pooled draws of every cell (seed 20260907), the
1.2.0 rule fires at 0.052 / 0.058 / 0.040 / 0.059 and the conformal rule at
0.044 / 0.042 / 0.040 / 0.036 (level 0.0498; per-cell means at most 0.054;
check F4 passed). In `I_XF` and `I_XFY` most of the published 1.2.0 excess
was the rule's own bias; what remains with the conformal rule is the design
effect, which is concentrated in E1 (256-row draws from 322-row pool halves:
0.125 / 0.115 / 0.045 / 0.123) and, to a smaller extent, in E3 ToN-IoT and E4
Tue→Wed. Without E1 the conformal rule sits at 0.045–0.052 in every regime.
E1 is retained in the primary aggregate as preregistered.

**Split construction S1** (reference draws 01–10, calibration 11–20, p-value
resolution 1/101): 0.049 / 0.039 / 0.067 / 0.034. Reported once as a
sensitivity; not adopted.

**Detection cost.** Conformal versus 1.2.0 rule on the frozen interventions:
mean shift and scaling stay at 0.95–1.00 in the batch regimes (0.97 in
`I_XF`/`I_XFY` at 0.02); sign flip 0.09 / 0.47 / 0.72 (`I_X`) and
0.13 / 0.52 / 0.84 (`I_XF`) against 0.09 / 0.47 / 0.72 and 0.15 / 0.56 / 0.85;
dropout 0.00–0.03; label path 0 in `I_X`, `I_XF`, `I_Ym`. Near-null shams fire
the conformal rule in 40–64 % of cells (1.2.0 rule 43–68 %; union 65–86 %).

**Label path (F3).** Conformal `I_X`, `I_XF`: 0/3,600; `I_Ym`: 0/1,800
prior-preserving. Batch-level `I_XFY` detects 11 (conformal), 16 (1.2.0
rule) or 43 (union) of the 2,617 material label rows; the item-aligned
auditor detects 2,617/2,617.

## Gate D — offline end-to-end decisions (24,000 frozen observations; primary |ΔR| > 0, 7,008 material)

| Regime | Policy | Clean false action | Benign interruption (1,200 shams) | Unsafe allow | Containment | Non-material interruption |
|---|---|---|---|---|---|---|
| I_X | P1 union | 0.125 | 0.76 | 4,429 | 0.37 | 0.25 |
| I_X | P2 conformal | 0.056 | 0.55 | 4,496 | 0.36 | 0.19 |
| I_X | P3 strict | 1.000 | 1.00 | 0 | 1.00 | 1.00 |
| I_XF | P1 union | 0.203 | 0.76 | 4,231 | 0.40 | 0.31 |
| I_XF | P2 conformal | 0.058 | 0.52 | 4,365 | 0.38 | 0.19 |
| I_XF | P3 strict | 1.000 | 1.00 | 0 | 1.00 | 1.00 |
| I_Ym | P1 = P2 | 0.048 | 0.00 | 7,008 | 0.00 | 0.03 |
| I_XFY | P1 union | 0.259 | 0.76 | 4,180 | 0.40 | 0.35 |
| I_XFY | P2 = P3 conformal | 0.053 | 0.49 | 4,390 | 0.37 | 0.18 |
| I_XFY* (trusted) | P1 union | 0.000 (1,200 exact-zero rows) | 0.77 | 0 | 1.00 | 0.64 |
| I_XFY* (trusted) | P2 = P3 conformal | 0.000 (1,200 exact-zero rows) | 0.52 (544 held + 85 blocked) | 0 | 1.00 | 0.58 |

Under the 1.2.0 rule P2 served 4,494 / 4,327 / 7,008 / 4,322 / 0; the
conformal rule serves 4,496 / 4,365 / 7,008 / 4,390 / 0 (within 1 % of the
material rows, as expected before execution). At τ = 0.02 / 0.05 the
conformal P2 serves 2,174 / 680 (`I_X`), 2,074 / 629 (`I_XF`), 2,088 / 629
(`I_XFY`) of 3,802 / 1,870 material rows. Unsafe allows by mechanism under P2
(conformal): label path 2,617 / 2,617 / 2,617 / 2,601 / 0 in
`I_X` / `I_XF` / `I_Ym` / `I_XFY` / `I_XFY*`; dropout 1,079 / 1,057 / 1,079 /
1,057 / 0; sign flip 800 / 685 / 1,464 / 717 / 0; mean shift and scaling
0 / 6 / 1,848 / 10 / 0.

**The trusted regime is not free.** Its zero unsafe allows and zero clean
false actions (on 1,200 exact-zero rows, a different denominator from the
12,000 clean draws of the batch regimes) come with 52 % benign interruption:
of 1,200 near-null in-place shams, 544 are held by the batch-level component
and 85 are blocked because a prediction changed under a 0.001 perturbation.
Stronger provenance closes blind regions and incurs a specificity cost when
exact invariance is enforced against benign variation.

**Policy taxonomy.** P0 baseline; P1 uncalibrated, risk-tolerant; P2
calibrated, risk-tolerant (serves under a declared residual blind region); P3
strict fail-closed / abstaining (unverified mandatory boundary ⇒ hold). The
contracts of the prototype fail closed on their invariants; P2 does not, and
is not called fail-closed anywhere in 1.3.0.

## Gate A — adaptive cluster-preserving perturbation (class F5)

Design executed as preregistered: 240/240 jobs, 16 interventions plus clean
per cell, the frozen maps and caps; clean rows and the six matched controls
reproduce the frozen expansion exactly (maximum absolute difference 0.0 on
4,200 rows over 13 columns; AC1); labels untouched (AC2); frozen-entry
fraction recorded on every adaptive row (AC3); every material adaptive row
carries a prediction change (AC4). The attacker perturbs 32 % of the entries
on average (16–47 % by environment, branch and dimension); 30 % of the rows
are fully frozen.

**Detection under the conformal rule (600 rows per condition, eight environments pooled).**

| Mechanism | Strength | Executed: I_X / I_XF | Cluster-preserving: I_X / I_XF | Material: executed / F5 | Prediction change: executed / F5 |
|---|---|---|---|---|---|
| Mean shift | 0.02 | 1.00 / 0.97 | 0.01 / 0.06 | 0.33 / 0.29 | 0.36 / 0.32 |
| Mean shift | 0.05 | 1.00 / 1.00 | 0.08 / 0.24 | 0.46 / 0.40 | 0.50 / 0.45 |
| Mean shift | 0.10 | 1.00 / 1.00 | 0.34 / 0.48 | 0.59 / 0.54 | 0.62 / 0.60 |
| Mean shift | 0.25 | — | 0.79 / 0.80 | — / 0.69 | — / 0.74 |
| Mean shift | 0.50 | — | 0.89 / 0.90 | — / 0.76 | — / 0.79 |
| Scaling drift | 0.02 | 1.00 / 0.96 | 0.05 / 0.23 | 0.48 / 0.40 | 0.54 / 0.47 |
| Scaling drift | 0.05 | 1.00 / 1.00 | 0.35 / 0.47 | 0.58 / 0.52 | 0.61 / 0.57 |
| Scaling drift | 0.10 | 1.00 / 1.00 | 0.56 / 0.66 | 0.64 / 0.58 | 0.67 / 0.64 |
| Scaling drift | 0.25 | — | 0.76 / 0.79 | — / 0.72 | — / 0.77 |
| Scaling drift | 0.50 | — | 0.88 / 0.88 | — / 0.81 | — / 0.87 |

At the matched strengths the attacker reduces detection from 0.96–1.00 to
0.01–0.34 (`I_X`) and 0.06–0.66 (`I_XF`) while keeping 83–91 % of the
material fraction (exact ratios 0.831–0.907 at the matched strengths).
Detection recovers at 0.25–0.50 because the unclustered
entries then move far enough to shift the feature distribution against the
between-batch null. The classical branch (standardized features) is more
evasive than the quantum branch (features scaled to [0, 2π]): at 0.10 the
mean shift is detected in 0.30 / 0.34 of classical cells and 0.37 / 0.58 of
quantum cells (`I_X` / `I_XF`); per environment, E4 (Tue→Wed) detects
nothing up to 0.10 for mean shift.

**Primary security endpoint (P2 conformal, |ΔR| > 0).** Of the 3,418 material
adaptive rows, P2 serves 1,328 in `I_X`, 959 in `I_XF` and 1,006 in `I_XFY`
(P1 union: 1,207 / 719 / 716; P3 strict: 0 / 0 / 1,006); the executed
mechanisms in the same runs are served 0 / 6 / 10 times out of 1,848 material
rows. Under `I_XFY*` every material adaptive row is blocked (a changed
conclusion requires a changed prediction when labels are fixed). The
"detected in every cell" result for feature drift in 1.2.0 was therefore a
property of the fingerprint, not of the mechanism: the same drift, restricted
to the unclustered entries, is served by the calibrated risk-tolerant policy
in 28–39 % of its material instances.

## L3

Not executed (decision recorded in the preregistration): the class is
realised by 808 executed rows (W1 = W10) and a controlled gate could change no
conclusion.

## Interpretation and boundary

- The published 1.2.0 attribution of the family rule's excess to the design
  alone was wrong; most of it in `I_XF` and `I_XFY` was rule bias. The
  conformal rule is within 0.006 of nominal in every regime and within 0.002
  without E1.
- Calibration does not buy coverage against an adaptive attacker who knows
  the fingerprint; only a reference (item-aligned predictions, or trusted
  features) does, and the reference has a measured benign cost.
- Everything is fixed-design and simulator-only, evaluated offline on frozen
  outputs. Context-conditioned runtime calibration under non-stationarity,
  abstention with recovery, real-QPU execution and service-level evaluation
  remain outside this article.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -m src.experiments.build_q1_policy_evidence
.\.venv\Scripts\python.exe -m src.experiments.run_v13_f5_queue --n-jobs 6
.\.venv\Scripts\python.exe -m src.experiments.build_q1_adversarial_evidence
.\.venv\Scripts\python.exe -m src.experiments.make_q1_policy_tables
.\.venv\Scripts\python.exe -m src.experiments.make_q1_policy_figures
.\.venv\Scripts\python.exe -m src.experiments.make_q1_adversarial_figures
```
