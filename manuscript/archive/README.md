# ARCHIVED / NON-AUTHORITATIVE

> **Everything in this directory is historical.** It preserves, with its Git
> history, the workshop-era and pre-TDSC Markdown drafts of Paper 1.5, the
> audit logs that accompanied them, superseded strategy and planning documents,
> throw-away tooling, and the frozen Markdown spine (`paper15_q1_manuscript_spine_v11.md`)
> from which the TDSC LaTeX article was first derived. **Numbers, counts,
> claims, page counts, test counts, manifest counts and scope statements in
> these files are NOT current** and must not be cited as the state of the
> artifact. Several of them describe a single-dataset workshop paper, a
> different journal target, or stealth/vulnerability claims that the current
> article deliberately does not make.

Archived on 2026-09-07 for artifact 1.2.0 so that a reviewer cannot confuse a
historical draft with current documentation.

## Authoritative sources (current)

| Topic | Authoritative file |
|---|---|
| Article | `publication/tdsc/main.tex` (rendered as `output/pdf/paper15_tdsc_submission.pdf`) |
| Supplement | `publication/tdsc/supplement.tex` (rendered as `output/pdf/paper15_tdsc_supplement.pdf`) |
| Repository overview and quick verification | `README.md` |
| Reproduction (compact verification and full replay) | `Q1_REPRODUCTION.md` |
| Release counts, hashes, pages, tests (generated) | `publication/RELEASE_STATUS.md` |
| ATHENA-AEGIS requirement-to-evidence map | `manuscript/ATHENA_DEUSTO_TRACEABILITY.md` |
| Threat-model card | `manuscript/THREAT_MODEL_CARD.md` |
| Adversary model per intervention class | `manuscript/ADVERSARY_MODEL.md` |
| Formal core (observation model, blind regions, propositions) | `manuscript/FORMAL_CORE.md` |
| Preregistrations and result summaries | `manuscript/paper15_v11_reinforcement_prereg.md`, `manuscript/paper15_v11_reinforcement_result_summary.md`, `manuscript/paper15_v12_policy_prereg.md`, `manuscript/paper15_v12_policy_result_summary.md` |
| Gate summaries still in force | `manuscript/paper15_q1_gate1_result_summary.md`, `manuscript/paper15_q1_expansion_result_summary.md`, `manuscript/paper15_quantum_integrity_gate_summary.md`, `manuscript/paper15_exact_statevector_validation.md`, `manuscript/paper15_z_pauli_xz_equivalence_note.md` |

## Contents

Original locations are relative to the repository root. Descriptions are the
first heading or purpose line of each file at the time of archiving.

### Master manuscript drafts (Markdown, workshop era)

| Archived file | Original location | Description |
|---|---|---|
| `paper15_master_manuscript_draft_v0.md` | `manuscript/` | Paper 1.5 master manuscript draft v0 |
| `paper15_master_manuscript_draft_v1.md` | `manuscript/` | Paper 1.5 master manuscript draft v1 |
| `paper15_master_manuscript_draft_v1_clean.md` | `manuscript/` | Auditability Gaps in Classical and Quantum Kernel Benchmarks under Structured Perturbations (v1 clean) |
| `paper15_master_manuscript_draft_v2.md` | `manuscript/` | Auditability Gaps … (v2) |
| `paper15_master_manuscript_draft_v3_refs_seeded.md` | `manuscript/` | Auditability Gaps … (v3, references seeded) |
| `paper15_master_manuscript_draft_v4_hardfixes.md` | `manuscript/` | Auditability Gaps … (v4, hard fixes) |
| `paper15_master_manuscript_draft_v5_citationfix.md` | `manuscript/` | Auditability Gaps … (v5, citation fix) |
| `paper15_master_manuscript_draft_v6_claude_fixes.md` | `manuscript/` | Auditability Gaps … (v6) |
| `paper15_master_manuscript_draft_v7_scaler_repro_fixes.md` | `manuscript/` | Auditability Gaps … (v7, scaler/reproducibility fixes) |
| `paper15_master_manuscript_draft_v8_submission_polish.md` | `manuscript/` | Auditability Gaps … (v8, submission polish) |
| `paper15_master_manuscript_draft_v8_submission_polish_tablefix.md` | `manuscript/` | Auditability Gaps … (v8, table fix) |
| `paper15_master_manuscript_draft_v9_workshop_ready.md` | `manuscript/` | Auditability Gaps … (v9, workshop ready) |
| `paper15_master_manuscript_draft_v10_workshop_submit.md` | `manuscript/` | Auditability Gaps … (v10, workshop submission; tag `paper15-v10-workshop-ready`) |
| `paper15_master_manuscript_draft_v10_workshop_submit_clean.md` | `manuscript/` | Auditability Gaps … (v10 clean) |
| `paper15_q1_manuscript_spine_v11.md` | `manuscript/` | Information-Set Conditional Integrity Auditing … — frozen Markdown spine (v11) superseded by `publication/tdsc/main.tex` |

### Draft audits and review logs

| Archived file | Original location | Description |
|---|---|---|
| `paper15_master_audit_report.md` | `manuscript/` | Master manuscript audit report (v0) |
| `paper15_master_v1_audit_report.md` | `manuscript/` | Master v1 audit report |
| `paper15_master_v2_quick_audit.md` | `manuscript/` | Master v2 quick audit |
| `paper15_master_v4_hardfixes_audit.md` | `manuscript/` | Master v4 hardfixes audit |
| `paper15_master_v5_citationfix_audit.md` | `manuscript/` | Master v5 citation-fix audit |
| `paper15_master_v6_claude_fixes_audit.md` | `manuscript/` | Master v6 Claude-fixes audit |
| `paper15_master_v7_scaler_repro_fixes_audit.md` | `manuscript/` | Master v7 scaler/repro fixes audit |
| `paper15_master_v8_submission_polish_audit.md` | `manuscript/` | Master v8 submission-polish audit |
| `paper15_master_v9_workshop_ready_audit.md` | `manuscript/` | Master v9 workshop-ready audit |
| `paper15_master_v10_workshop_submit_audit.md` | `manuscript/` | Master v10 workshop-submit audit |
| `paper15_master_v10_workshop_submit_clean_audit.md` | `manuscript/` | Master v10 clean audit |
| `paper15_aggregate_results_static_audit.md` | `manuscript/` | `aggregate_results.py` static audit |
| `paper15_figure_existence_audit.md` | `manuscript/` | Figure existence audit |
| `review_tasks/CLAUDE_REVIEW_TASK.md` | repository root | Claude Code Review Task — Paper 1.5 Auditability Gap |
| `review_tasks/CLAUDE_REVIEW_TASK_V4.md` | repository root | Claude Code Review Task V4 — Full Repository Hard Review |
| `review_tasks/CLAUDE_REVIEW_TASK_V5.md` | repository root | Claude Code Review Task V5 — Post Citation Fix Hard Review |
| `review_tasks/CLAUDE_REVIEW_TASK_V6.md` | repository root | Claude Code Review Task V6 — Pre-Submission Hard Review |
| `review_tasks/CLAUDE_REVIEW_TASK_V7.md` | repository root | Claude Code Review Task V7 — Final Pre-Submission Review |
| `review_tasks/CLAUDE_REVIEW_TASK_V8.md` | repository root | Claude Code Review Task V8 — Final Submission-Readiness Review |
| `review_tasks/CLAUDE_REVIEW_TASK_V9.md` | repository root | Claude Code Review Task V9 — Workshop-Ready Final Check |

### Section drafts, tables and notes superseded by the TDSC sources

| Archived file | Original location | Description |
|---|---|---|
| `paper15_abstract_introduction_draft.md` | `manuscript/` | Abstract and Introduction draft |
| `paper15_related_work_skeleton.md` | `manuscript/` | Related Work — skeleton |
| `paper15_related_work_draft_with_refs.md` | `manuscript/` | Related Work draft with references |
| `paper15_related_work_draft_with_refs_v2.md` | `manuscript/` | Related Work draft with references (v2) |
| `paper15_reference_seed_list.md` | `manuscript/` | Reference seed list |
| `paper15_reference_list_v2.md` | `manuscript/` | References (v2) |
| `paper15_methodology_audit_protocol.md` | `manuscript/` | Methodology (audit protocol) draft |
| `paper15_results_section_draft.md` | `manuscript/` | Results section draft |
| `paper15_results_section_v3_sharednorm_ci.md` | `manuscript/` | Results section v3 (shared normalization, confidence intervals) |
| `paper15_signal_comparison_subsection.md` | `manuscript/` | Signal comparison subsection for Results |
| `paper15_discussion_limitations_conclusion_draft.md` | `manuscript/` | Discussion, Limitations, and Conclusion draft |
| `paper15_proposed_auditability_protocol.md` | `manuscript/` | Proposed Auditability-Aware Benchmark Protocol |
| `paper15_main_result_table.md` | `manuscript/` | Main result table (workshop era) |
| `paper15_clean_performance_table.md` / `.csv` | `manuscript/` | Clean operating point table (workshop era) |
| `paper15_attack_suite_table.md` / `.csv` | `manuscript/` | Appendix A perturbation suite table (workshop era) |
| `paper15_dataset_characteristics.md` | `manuscript/` | Dataset characteristics (single-dataset era) |
| `paper15_reproducibility_details.md` | `manuscript/` | Reproducibility details (superseded by `Q1_REPRODUCTION.md`) |
| `paper15_final_selected_figures.md` | `manuscript/` | Final selected figures for Paper 1.5 (workshop era) |
| `paper15_final_selected_figures_v2_clean.md` | `manuscript/` | Final selected figures — clean v2 |
| `paper15_available_figures.txt` | `manuscript/` | Listing of available figure files (workshop era) |
| `paper15_ci_statistical_support.md` | `manuscript/` | Statistical support after seed-unit CI analysis |
| `paper15_ci_and_ood_disclosure_patch.md` | `manuscript/` | CI and OOD disclosure patch |
| `paper15_claim_revision_after_sharednorm.md` | `manuscript/` | Claim revision after shared-normalization and quadrant analysis |
| `paper15_sharednorm_reproducibility_note.md` | `manuscript/` | Shared-normalization reproducibility note |
| `paper15_sharednorm_reverse_engineering_candidates.csv` | `manuscript/` | Shared-normalization reverse-engineering candidates |
| `paper15_results_checkpoint.md` | `manuscript/` | Paper 1.5 results checkpoint |
| `feature_map_z_vs_pauli_xz_sanity.txt` | `manuscript/` | Raw sanity-check output for the Z vs PauliXZ equivalence (the note `manuscript/paper15_z_pauli_xz_equivalence_note.md` remains current) |

### Superseded planning and strategy

| Archived file | Original location | Description |
|---|---|---|
| `paper15_assembly_plan.md` | `manuscript/` | Paper 1.5 assembly plan — Auditability gap paper |
| `paper15_q1_expansion_gate1_plan.md` | `manuscript/` | Paper 1.5 Q1 Expansion — Gate 1 plan |
| `PAPER15_Q1_MAXIMUM_STRATEGY.md` | `manuscript/` | Q1 ceiling strategy (cut-off 2026-08-09; pre-1.1.0 state) |
| `thesis_paper_map.md` | `manuscript/` | Thesis paper map (pre-Q1 framing of Paper 1.5 as robustness/stealth) |

### Throw-away tooling

| Archived file | Original location | Description |
|---|---|---|
| `tooling/export_scripts.py` | repository root | Ad-hoc script that exported source files for review |
| `tooling/scripts_tmp_build_table_qsvc_vs_rbf.py` | repository root | Temporary QSVC-vs-RBF table builder (workshop era) |

### Rendered PDF of the Markdown era

| Archived file | Original location | Description |
|---|---|---|
| `paper15_q1_submission.pdf` | `output/pdf/` | 16-page anonymous PDF of the 1.0.0 Markdown manuscript (pre-TDSC target); superseded by `output/pdf/paper15_tdsc_submission.pdf` |

Files referencing the archived paths from outside this directory are listed in
`REFERENCES_TO_UPDATE.md`.
