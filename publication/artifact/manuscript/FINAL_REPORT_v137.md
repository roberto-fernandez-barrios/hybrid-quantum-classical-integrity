# Final report — v1.3.7

## A. JSD defect

- **Reproduced:** YES.
- **Cause:** independent per-sample quantile clipping plus finite reference-only
  histogram edges allowed every current observation to fall outside the
  histogram. `numpy.histogram(..., density=True)` then divided by zero mass and
  produced NaN before the pseudocount. Legacy calibration mapped the NaN to
  `-inf`, suppressing that sensor.
- **Affected code paths:** feature JSD and score JSD shared the helper. The only
  applicable historical NaNs observed are feature JSD under mean shift and
  scaling drift.
- **Historical count:** 3,374 physical NaNs = 744 direct defects + 230 derived
  deltas + 2,400 non-applicable placeholders; 527 lineage-deduplicated
  scientific evaluations.
- **Fix:** one reference-derived shared edge vector with explicit underflow and
  overflow bins, count-PMF normalization, finite validation, and fail-closed
  current calibration. Legacy conversion is isolated for reproduction only.

## B. JSD impact

- Changed observation rows: 58,074 scope-qualified row identifiers.
- Changed per-sensor fires: 4,432 coordinates / 4,282 rows.
- Changed family fires: 2,265 coordinates / 1,588 rows.
- Changed union fires: 2,808 coordinates / 1,254 rows.
- Primary P2 served counts: I_X 4,496 (no change), I_XF 4,368 (+3), I_Ym
  7,008 (no change), I_XFY 4,394 (+4), trusted 0 (no change).
- Near-null range: 0.41--0.64 -> 0.41--0.62.
- Gate-A adaptive P2 served range: 28--39% -> 27--39%.
- Trusted net near-null increment: 3.25 pp -> 3.42 pp.
- Every other changed or invariant headline is listed in `headline_delta.csv`.

## C. Label geometry

- Original: calibration `s(E,C)`, statistical label response `s(E,T_y(E))`.
- Aligned: calibration `s(E,C)`, clean `s(E,B)`, label response
  `s(E,T_y(B))`.
- Original conformal: 11/2,617; corrected-original: 11/2,617; aligned:
  343/2,700.
- Original union: 43/2,617; corrected-original: 43/2,617; aligned:
  1,183/2,700.
- Aggregate-separable aligned detection: conformal 352/2,836 (12.41%); union
  1,204/2,836 (42.45%).
- Aggregate-blind aligned rows: 764; attack-only family/union increments: 0/0.
- Aligned I_XFY/P2 material results served: 2,357/2,700; trusted exact: 0.

## D. Structural claims

- Blind regions: unchanged.
- Propositions 1--7: unchanged.
- R0/M0/C hierarchy: unchanged.
- Exact C1 and trusted-reference results: unchanged.

## E. Sensor decomposition

The release publishes per-mechanism, per-strength response for feature JSD,
MMD, KS statistic/rejection, score JSD, prediction marginal, label marginal,
confusion L1 and confusion JSD. KS dominates near-null response and contributes
strongly on shifts that disturb frozen point masses/tight clusters. It remains
in the primary family. The frozen-only recalibrated ablation shows that much of
the core and Gate-A family response survives without KS, while almost all
near-null response does not. No replacement KS or post-hoc primary is used.

## F. Items not done

No new dataset, environment, model, map, kernel, attack, strength,
hyperparameter, model selection, QPU/hardware/noise study, PSD repair, batch
sweep, calibration campaign, detector, theorem, policy redesign, bootstrap,
deployment experiment or literature campaign was added. Historical manifests
and evidence were not rewritten. The portal submission was not performed.

Final release/CI/DOI fields are populated only after the corresponding public
operations and post-release verification succeed.
