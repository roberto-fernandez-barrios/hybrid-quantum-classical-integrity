# Master manuscript audit report

File audited: `manuscript\paper15_master_manuscript_draft_v0.md`

Characters: 42330
Approx words: 5507

## 1. Headings found

- L21: # Auditability Gaps in Classical and Quantum Kernel Benchmarks under Structured Perturbations
- L24: # Abstract and Introduction
- L29: # 2. Related Work
- L35: ## 2.1 Classical kernel methods and SVC baselines
- L57: ## 2.2 Quantum kernel methods and QSVC
- L83: ## 2.3 Quantum feature maps and benchmark sensitivity
- L108: ## 2.4 Robustness, perturbations, and label noise
- L134: ## 2.5 Drift detection and integrity monitoring
- L163: ## 2.6 Benchmark reliability, reproducibility, and auditability
- L189: ## 2.7 Positioning of this paper
- L206: ## 2.8 Related Work gap statement
- L221: # 3. Problem Formulation
- L246: # 4. Methodology
- L250: ## 4.1 Threat model and auditability setting
- L258: ## 4.2 Data and protocols
- L264: ### ID protocol
- L268: ### OOD protocol
- L272: ## 4.3 Models and feature maps
- L291: ## 4.4 Perturbation families
- L295: ### Target shift
- L299: ### Corruption
- L303: ### Covariate shift
- L307: ### Pipeline perturbations
- L311: ## 4.5 Impact metrics
- L321: ## 4.6 Detectability signals
- L325: ### Standard feature/score-based signals
- L336: ### Label-aware and prediction-aware signals
- L350: ## 4.7 Shared normalization of detectability
- L358: ## 4.8 Stealth score
- L370: ## 4.9 Auditability quadrant analysis
- L383: ## 4.10 Statistical analysis
- L391: ## 4.11 Reproducibility controls
- L402: ## 4.12 Methodological limitations
- L419: # 5. Results
- L427: ## 5.1 Clean performance is necessary but not sufficient
- L433: ## 5.2 QSVC-ZZ shows the strongest ID impact profile
- L455: ## 5.3 Shared-normalized stealth remains highest for QSVC-ZZ
- L479: ## 5.4 Quantum kernel behaviour is feature-map dependent
- L505: ## 5.5 True auditability-gap cases differ from high-impact detectable perturbations
- L524: ## 5.6 Signal-family analysis explains the auditability gap
- L543: ## 5.7 OOD acts as a boundary condition
- L564: ## 5.8 Summary of findings
- L583: # 6. Proposed Auditability-Aware Benchmark Protocol
- L589: ## 6.1 Principle 1: Report clean performance as a baseline, not as reliability evidence
- L595: ## 6.2 Principle 2: Disaggregate models and feature maps
- L601: ## 6.3 Principle 3: Evaluate perturbation families, not only isolated perturbations
- L614: ## 6.4 Principle 4: Measure impact explicitly
- L626: ## 6.5 Principle 5: Measure detectability by signal family
- L632: ### Standard feature/score-based signals
- L643: ### Label-aware and prediction-aware signals
- L658: ## 6.6 Principle 6: Use shared normalization for cross-model detectability
- L666: ## 6.7 Principle 7: Compute stealth, but do not rely on stealth alone
- L678: ## 6.8 Principle 8: Separate true auditability gaps from damaging but detectable perturbations
- L682: ### True auditability gap
- L691: ### High-impact but detectable perturbation
- L702: ## 6.9 Principle 9: Treat OOD as a boundary condition unless multiple OOD settings are tested
- L708: ## 6.10 Principle 10: Report uncertainty
- L714: ## 6.11 Recommended reporting checklist
- L729: ## 6.12 Summary
- L742: # 7. Discussion, Limitations, and Conclusion

## 2. Expected top-level sections

- OK: # Abstract
- MISSING: # 1. Introduction
- OK: # 2. Related Work
- OK: # 3. Problem Formulation
- OK: # 4. Methodology
- OK: # 5. Results
- OK: # 6. Proposed Auditability-Aware Benchmark Protocol
- OK: # 7. Discussion
- MISSING: # 8. Limitations
- MISSING: # 9. Conclusion

## 3. TODO markers

- L10: Known TODOs:
- L26: TODO: Missing source file `paper15_abstract_introduction_draft.md`.
- L744: TODO: Missing source file `paper15_discussion_limitations_conclusion_draft.md`.

## 4. Risky phrase scan

- OK: `quantum advantage` not found.
- OK: `quantum models are worse` not found.
- OK: `quantum models are less robust` not found.
- OK: `four distinct quantum feature maps` not found.
- OK: `four independent quantum` not found.
- OK: `stealth ratio of 2.20` not found.
- OK: `2.20x` not found.
- OK: `2.51x` not found.
- OK: `2.33x` not found.
- OK: `above 2x` not found.
- OK: `more than 2x stealth` not found.
- OK: `generalizes under OOD` not found.
- OK: `OOD generalization` not found.
- OK: `falsify` not found.
- OK: `manipulate` not found.
- OK: `bank` not found.

### FOUND: `attack recipe`
Reason: Avoid operational framing.
- L256: This work does not frame the perturbations as operational attack recipes. Instead, they are used as controlled probes to study methodological reliability. The purpose is defensive: to identify which perturbation families are visible to standard benchmark diagnostics and which require additional audit signals.

## 5. Required concept scan

- OK: `shared-normalized stealth` count=17 — Cross-model stealth should use shared normalization.
- OK: `Z/PauliXZ-equivalent` count=6 — Equivalence must be explicit.
- OK: `boundary condition` count=8 — OOD should be framed conservatively.
- OK: `paired seed-unit` count=3 — Statistical support should be described.
- MISSING: `Student t` count=0 — CI method should be disclosed.
- MISSING: `five degrees of freedom` count=0 — CI df=5 should be disclosed.
- OK: `signal family` count=7 — Detectability must be signal-family specific.
- OK: `quadrant` count=8 — True auditability gap should use impact-detectability quadrant.

## 6. Figure references found

- fig10_top12_standard_signal_blindspots.png
- fig11_id_auditability_map_sharednorm.png
- fig12_id_impact_ci_unique_kernel_profiles.png
- fig13_id_sharednorm_stealth_ci_unique_kernel_profiles.png
- fig2_v2_id_attack_impact_unique_kernel_profiles.png
- fig3_v2_id_sharednorm_stealth_unique_kernel_profiles.png
- fig4_v2_id_sharednorm_stealth_ratio_unique_kernel_profiles.png
- fig7_v2_id_vs_ood_sharednorm_stealth_dim12_unique_profiles_ci.png
- fig8_standard_vs_full_detectability_id.png
- fig9_detectability_old_vs_full_by_family_id.png

## 7. Old figure reference check

- OK: fig5_id_stealth_ratio_vs_svc.png
- OK: fig7_id_vs_ood_stealth_dim12.png
- OK: fig4_id_impact_ratio_vs_svc.png

## 8. Numeric claim checks

- OK: `1.59x` — Updated shared-normalized stealth ratio dim=8.
- OK: `1.81x` — Updated shared-normalized stealth ratio dim=10.
- OK: `1.67x` — Updated shared-normalized stealth ratio dim=12.
- OK: `2.97x` — Impact ratio dim=8.
- OK: `3.66x` — Impact ratio dim=10.
- OK: `3.39x` — Impact ratio dim=12.
- OK: `0.0347` — Paired impact diff dim=8.
- OK: `0.0437` — Paired impact diff dim=10.
- OK: `0.0462` — Paired impact diff dim=12.
- OK: `0.0098` — Paired stealth diff dim=8.
- OK: `0.0133` — Paired stealth diff dim=10.
- OK: `0.0143` — Paired stealth diff dim=12.

## 9. Repetition counts

- `auditability gap`: 12
- `shared-normalized stealth`: 17
- `boundary condition`: 8
- `Z/PauliXZ`: 7
- `QSVC-ZZ`: 20
- `SVC-RBF`: 9