# v1.3.7 sensor-correction and label-geometry result summary

This document reports the preregistered corrective replay fixed at commit
`711a46c5c9af567d6777dd3811f44ef3a7987224` (2026-09-10T20:24:42+02:00).
It does not modify or reinterpret the v1.3.5/v1.3.6 evidence trees.

## Corrected JSD

The defect was reproduced. The historical helper clipped reference and current
against their own quantiles, built finite edges only from the reference and
called a density histogram. A wholly out-of-range current sample therefore had
zero in-range mass, producing NaN before the pseudocount was applied. The
historical calibration adapter mapped that NaN to `-inf`.

The corrected helper derives one edge vector from the reference, extends its
first and last edges to `-inf` and `+inf`, forms ordinary counts for both
samples and normalizes positive count totals to PMFs. Identical samples give
zero; partially or wholly disjoint finite samples remain finite; wholly
disjoint support gives a high JSD. Current calibration rejects every non-finite
input. The NaN-to-`-inf` conversion is restricted to the named v1.3.6 legacy
reproduction path.

The historical audit found 3,374 physical NaNs: 744 direct defective
coordinates, 230 derived delta coordinates and 2,400 non-applicable clean
placeholders. Lineage deduplication leaves 527 scientific evaluations. The only
applicable broken observed sensor is feature JSD, under mean shift and scaling
drift; score JSD shared the vulnerable helper but had no applicable historical
NaN. Every canonical family-scored NaN row already had another sensor firing,
so both union and conformal-family decisions were already positive in those
specific rows.

## Exact replay impact

- Jobs: 300/300; raw corrected rows: 67,920; accepted observation rows: 64,560.
- Scope-qualified rows with at least one changed JSD coordinate: 58,074.
- Changed JSD sensor-fire coordinates: 4,432 across 4,282 rows.
  - Feature JSD: 3,129 (1,140 `0->1`, 1,989 `1->0`).
  - Score JSD: 1,303 (540 `0->1`, 763 `1->0`).
- Changed conformal-family coordinates: 2,265 across 1,588 rows
  (963 `0->1`, 1,302 `1->0`).
- Changed union coordinates: 2,808 across 1,254 rows
  (1,196 `0->1`, 1,612 `1->0`).
- The delta ledger has 192,487 coordinate records and retains the old/new
  value, sensor fire, four union decisions and four family decisions.

The feature response ranges change only where reported in
`headline_delta.csv`: scaling drift is `0.95--1.00 -> 0.94--1.00`; mean shift
remains `0.97--1.00`, sign flip `0.09--0.84`, dropout `0.00--0.03`, and exact
dropout prediction change `0.49--0.76`. The near-null conformal range changes
from `0.41--0.64` to `0.41--0.62`. The original Gate-A control/adaptive ranges
change from `0.95--1.00 / 0.01--0.66` to
`0.94--1.00 / 0.01--0.65`; the aligned ranges become
`0.96--1.00 / 0.18--0.81`.

Primary P2 material results served are `4496/7008` (unchanged) in I_X,
`4368/7008` (`+3`) in I_XF, `7008/7008` (unchanged) in I_Ym and
`4394/7008` (`+4`) in I_XFY; the trusted exact regime remains zero. The Gate-A
adaptive P2 served range becomes `27--39%` (previously `28--39%`). The exact
near-null blocks remain 85; their overlap with batch I_XFY/P2 becomes 44
(previously 46), so the net increment becomes `41/1200 = 3.42 pp`
(previously `39/1200 = 3.25 pp`).

## Label geometry answers

The original statistical geometry is `s(E,T_y(E))`. The aligned geometry uses
frozen calibration `s(E,C)`, clean response `s(E,B)` and label intervention
`s(E,T_y(B))`.

1. Correcting JSD alone leaves the original conformal result at `11/2617`.
   Under aligned geometry it is `343/2700` material rows.
2. Correcting JSD alone leaves the original union result at `43/2617`.
   Under aligned geometry it is `1183/2700`.
3. Both aligned responses increase. The material denominator changes because
   balanced-accuracy materiality is recomputed on the frozen fresh batch B,
   not through outcome-selected filtering.
4. Yes. All 764 aggregate-blind aligned rows have the same declared sensor
   vector as their paired clean row; attack-only family and union increments
   are both zero.
5. Of 2,836 aggregate-separable aligned interventions, the conformal family
   detects 352 (12.41%) and the union detects 1,204 (42.45%).
6. Yes, sensitivity policy counts change. On aligned material label rows P2
   serves 2,506, 2,509, 2,391 and 2,357 of 2,700 in I_X, I_XF, I_Ym and I_XFY;
   the trusted exact regime serves zero. Union serves 2,201, 1,983, 2,391 and
   1,517, respectively.
7. For the aligned label sensitivity, I_XFY/P2 material altered results served
   changes from `2606/2617` to `2357/2700`. This does not retroactively replace
   the corrected-original all-mechanism primary headline `4394/7008`.
8. Structural blind regions, Propositions 1--7, the R0/M0/C hierarchy, exact
   aggregate/item-aligned checks, model predictions, attacks, strengths and
   the bounded quantum results remain invariant.

## Sensor decomposition and frozen-only KS ablation

Over the unchanged 10,800 core interventions, individual sensor-fire totals
are: feature JSD 2,663; MMD 2,139; KS rejection 3,600; score JSD 3,352;
prediction-rate shift 1,364; prediction JSD 1,425; label-prior shift 0; label
JSD 0; confusion L1 1,207; and confusion JSD 1,421. These pooled counts are not
substitutes for the mechanism/strength table. The manifested decomposition
reports every sensor, mechanism, strength, regime, mean response, fire count,
sensor-only fire and family response.

KS rejection is retained because it was prespecified. Its strong response is
associated with large point masses and tight near-duplicate clusters in the
frozen staged data. In the core grid, 3,521/4,361 primary I_X family fires,
4,008/4,462 I_XF fires and 3,959/4,419 I_XFY fires survive the recalibrated
without-KS family. Gate A retains 5,545/6,401, 6,380/6,835 and 6,251/6,712.
Near-null response largely disappears: 10/650, 62/603 and 62/576 primary fires
survive. Since removing KS changes the family and its calibration, the
without-KS total is reported separately from surviving primary fires. This is
descriptive, frozen-only and does not replace the primary family.

## Invariants and immutability

- Structural blind regions: unchanged.
- Propositions 1--7: unchanged.
- R0/M0/C hierarchy: unchanged.
- Exact C1/item-aligned results: unchanged (all 3,600 label interventions and
  all 2,617 original material label rows exposed by the declared exact check;
  808 aggregate-preserving relabelings remain item-aligned-only witnesses).
- Quantum cells/checks: 165 dependent design cells and 9/9 checks, unchanged.
- v1.3.6 evidence modified: 0 files.
- v1.3.5 geometry evidence modified: 0 files.
- New v1.3.7 evidence: 24 files across two separate manifested directories.

The exhaustive headline comparison is
`publication/artifact/evidence/jsd_correction/headline_delta.csv` after final
artifact assembly.
