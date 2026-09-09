# Version 1.3.5 geometry-aligned sensitivity: result summary

Completed on **2026-09-09 at 16:10:41+02:00 (Europe/Madrid)** under the protocol frozen in `manuscript/v135_geometry_aligned_sensitivity_prereg.md`. The preregistration commit is `62cec146689e3ff8cdb95027c7a9c7371ef767fd` (2026-09-09T14:46:14+02:00), before any aligned intervention result existed.

## Executed design

- Eight preregistered environments; dimensions 8/10/12; split seeds 42--46; model seeds 42/43.
- 240 deterministic replay jobs, 600 model cells, 22 existing feature-side/identity interventions, and 13,200 unique intervention observations.
- Calibration: `s(E_c,C_{c,k})`; clean-resample evaluation: `s(E_c,B_{c,k})`; aligned intervention: `s(E_c,T_a(B_{c,1}))`; exact paired identity: `s(B_{c,1},B_{c,1})`.
- All replay comparisons to the frozen outputs were within `1e-9`; all feature interventions preserved labels; all 240 jobs and every expected strength/model/environment cell were present.
- Label-only attacks were not rerun.

The complete fail-closed output is in `publication/artifact/evidence/geometry_sensitivity/` after artifact assembly. Its source package is `results/paper_digest/paper15_v135_geometry_sensitivity/`.

## Controls

The exact paired identity response was zero for all eleven batch statistics and the four explicit paired outcome statistics over all 600 model cells (maximum absolute response 0). In contrast, evaluating the identity copy as `s(E,B)` reproduced the clean-resample draw, as required; it is not an exact-zero estimand.

The pooled adopted-family clean-resample false-action rates remain the frozen values: 0.056 for `I_X`, 0.057917 for `I_XF`, 0.0475 for `I_Ym`, and 0.053083 for batch `I_XFY`. These are clean-resample false-action rates, not identity false-positive rates.

## Q1--Q7

**Q1 -- Does high feature-side response persist? YES for mean shift and scaling drift; strength-dependent for dropout.** Under the adopted family rule, aligned mean-shift response is 1.000/0.993 at strength 0.02 and 1.000/1.000 at 0.05 and 0.10 in `I_X`/`I_XF`. Scaling response is 1.000/0.997 at 0.02 and 1.000/1.000 at 0.05 and 0.10. Thus the high response of these feature-side controls is not an artifact of the original same-item editing geometry. Dropout remains the low-response exception.

**Q2 -- Do tiny Gaussian and tiny scaling remain extremely sensitive? PARTIAL.** Tiny Gaussian gives aligned family response 0.637 (`I_X`) and 0.568 (`I_XF`), clearly above the corresponding clean-resample rates but not near-universal. Tiny scaling remains very high at 0.822 and 0.808. The manuscript must not generalize the original near-null wording to both mechanisms as uniformly near-universal.

**Q3 -- Is mean shift still highly detectable? YES.** Family response is 0.993--1.000 across both principal regimes and all three matched strengths.

**Q4 -- Is feature dropout still poorly detectable? PARTIAL/strength-dependent.** Family response is 0.057/0.068 at 0.02, essentially the clean-resample background; 0.085/0.137 at 0.05; and 0.212/0.320 at 0.10 for `I_X`/`I_XF`. It remains much less detectable than mean shift or scaling, especially at the two lower strengths, but “undetectable” without a strength qualifier would be too strong.

**Q5 -- Does Gate A still reduce response? YES.** At matched strengths 0.02/0.05/0.10, every one of the 12 mechanism/strength/regime family comparisons has lower adaptive than control response. The adaptive response is lower in 25--40 of 40 environment/split cells (0.625--1.000 of cells), equal in the rest, and higher in none. Pooled controls are 0.993--1.000; adaptive responses are 0.185--0.823. Across all five adaptive strengths, the response rises with strength, reaching 0.895--0.990 at 0.25/0.50 in the principal regimes; the sensitivity therefore supports the mechanism-specific reduction, not a strength-independent failure headline.

Materiality is retained. At the three matched strengths, 157--400 of 600 adaptive rows per mechanism/strength are materially changed (`|Delta_R|>0`). Depending on mechanism, strength and regime, 6.0%--83.4% of those material rows do not trigger the adopted family rule. This is the directly identified residual coverage gap; no claim is made that every non-response is caused by one component in isolation.

**Q6 -- Is “calibration controls false actions but does not guarantee coverage against a monitor-aware attacker” supported? YES.** Clean-resample family actions remain approximately 0.05--0.06 in the principal regimes, yet materially changed adaptive rows fail to trigger in every matched mechanism/strength/regime comparison. The statement remains conditional on the declared calibration construction and attacker, and is not a universal detector claim.

**Q7 -- What came from cluster structure, paired geometry, and monitor-aware evasion?**

- **Dataset cluster structure:** the aligned controls remain almost perfectly responsive and the aligned tiny-scaling response remains 0.808--0.822, so the duplicate/cluster structure continues to drive a very sharp fingerprint even without same-item attack scoring. This is a design-specific observation, not a population causal estimate.
- **Paired editing geometry:** changing `s(E,T(E))` to `s(E,T(B))` raises matched adaptive responses relative to the original results (original 0.007--0.662; aligned 0.185--0.823) while the controls remain near one. Exact identity remains zero only in the separately reported paired statistic; the aligned identity copy inherits clean-resample variability. The original geometry therefore amplified the visual contrast for some adaptive cells and mixed identity with a different estimand, but it does not explain away the control/adaptive ordering.
- **Monitor-aware component:** within the aligned geometry and on the same fresh `B`, the cluster-preserving variant is lower than its matched intervention in a majority of every environment/split comparison and never higher. That within-geometry contrast is the evidence that remains for monitor-aware evasion.

These components interact. The gate supports only the matched descriptive decomposition above; it does not identify a general causal fraction attributable to any component.

## Scientific verdict

- M1: **YES** for the batch-calibrated feature, prediction/score, label-marginal, and joint-outcome statistics in the original feature-intervention design. Exact item-aligned sensors were already paired and are not part of M1.
- Gate A qualitative survival: **YES** under the prespecified descriptive criterion.
- Original frozen evidence: retained unchanged and reported as a design-specific calibration geometry.
- Geometry-aligned sensitivity: additional evidence, never retrospectively substituted for the original design.
- Core theorem/proposition changes: **none**.
- Old scientific evidence modified: **0 files**.
- New sensitivity evidence: **8 files** (seven CSV files, including the manifested observation source, plus one JSON manifest).
