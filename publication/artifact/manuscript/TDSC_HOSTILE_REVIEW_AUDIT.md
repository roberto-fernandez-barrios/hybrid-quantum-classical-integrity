# Hostile-review audit — IEEE TDSC candidate

Audit date: **2026-08-10**  
Manuscript: `publication/tdsc/main.tex`  
Supplement: `publication/tdsc/supplement.tex`  
Scientific artifact: frozen version `1.0.0`, tag `paper15-q1-v1.0.0`

## Executive verdict

**Scientifically submission-ready for a regular-paper attempt at IEEE TDSC.**
The manuscript now makes one coherent claim: integrity auditability is
conditional on the evidence available to the auditor. Exact blind regions,
sensor coverage, multi-dataset/fixed-OOD validation, the bounded
quantum-specific layer, and fail-closed enforcement form one contribution.
There is no scientific blocker that justifies adding an opportunistic
experiment.

The package is **not yet upload-ready** because author identities, ORCIDs,
CRediT roles, official funding wording, competing interests, artifact license,
related-work disclosure, and DOI require author decisions. These are explicit
gates, not hidden manuscript defects.

## 1. Desk-review test

### Why it is in scope

The first page identifies the protected asset, the threat/failure locus, the
information boundary, the assurance property, and the enforcement behavior.
The paper contributes a foundation and evaluation methodology for dependable
and secure hybrid workflows, using monitoring, measurement, controlled
interventions, validation, and quantum computing. This maps directly to the
TDSC general scope without presenting quantum machine learning performance as
the headline.

### Most plausible desk-rejection reading

> “This is a logging/checklist paper around an ordinary robustness benchmark.”

The current manuscript counters that reading in four ways: it proves exact
invariance boundaries; separates model-output from evaluation-conclusion
effects; validates the resulting coverage contract over fixed environments;
and makes absent mandatory evidence cause executable abstention or blocking.
The quantum boundary is not decorative: semantic equivalence, provenance,
positive-semidefinite substitution, finite-shot estimation, and output
monitoring have different coverage.

### Residual desk risk

**Medium, appropriate for an ambitious Q1 submission.** TDSC may still prefer a
more mature deployed mechanism or a stronger adversarial security model. That
is a venue-selectivity risk, not a correctable omission within the declared
paper. Adding QPU/provider/Fleet evidence would create a different study and
weaken the present claim discipline.

## 2. Novelty and overlap

The novelty claim is not attached to contracts, hash chaining, elementary
label-invariance propositions, or quantum-versus-classical accuracy. The
contribution is the integrated assurance construction:

1. information-set conditional formalization;
2. exact and empirical blind-region classification;
3. explicit attack/failure-to-sensor coverage;
4. replication over three datasets and eight fixed ID/OOD environments;
5. a bounded quantum-specific coverage layer; and
6. executable fail-closed composition.

The literature recheck through 10 August 2026 includes the closest concurrent
work on quantum lifecycle integrity, evidence sufficiency, and multi-level
integrity architecture. Those works strengthen the motivation but do not
replace the paper's boundary-relative claim, evaluation-label counterexample,
multi-environment coverage evidence, or executable contract. The manuscript
states this difference without claiming that adjacent frameworks are absent.

Residual novelty risk is **moderate but defensible**: a reviewer may regard
“guarantees depend on observables” as intuitive. The paper therefore does not
sell the intuition alone; it sells the formalization-to-coverage-to-validation-
to-enforcement chain and the exact blind regions that prevent overclaiming.

## 3. Formal and methodological audit

### Passes

- The workflow separates input, representation/kernel, prediction, labels,
  reported evaluation, and execution evidence.
- Auditability is defined relative to information set, sensor family, and
  consequential endpoint.
- Structural blindness is distinguished from zero empirical response and low
  detector power.
- The threat boundary includes benign faults and controlled adversarial
  interventions but does not infer prevalence or malicious intent.
- Evaluation-label intervention is not mislabeled as population label shift.
- The exact propositions are supporting lemmas, not novelty theater.
- The ideal-statevector engine and binomial shot emulator are not called QPU
  execution or calibrated noise.
- The hash chain is called tamper-evident, not authenticated or non-repudiable.

### Statistical judgment

The primary coverage results are finite-design counts and exact invariances;
null-hypothesis testing would add no inferential value. For the secondary
ZZ-minus-SVC profile, nested model seeds are averaged within each split and the
five split clusters are the uncertainty units. The intervals are explicitly
sensitivity summaries, not population-generalization claims. Fixed OOD routes
are environments, not random draws. No multiplicity-adjusted discovery claim
is made. This is statistically coherent for the questions asked.

### Known validity limits, correctly disclosed

- balanced, staged binary samples rather than operational prevalence;
- numerical preprocessing and excluded categorical fields;
- small projected dimensions and potentially limited clean headroom;
- five split clusters per environment;
- fixed source-to-target OOD routes;
- three public intrusion-detection datasets;
- ideal simulation and controlled shot emulation;
- non-calibrated nonzero sensor response;
- local prototype rather than a production service.

None invalidates the exact information-set claims. Together they limit the
transport of empirical response magnitudes, which the manuscript states.

## 4. Results and claim consistency

The manuscript, supplement, manifests, and verifier agree on:

- Gate 1: 7,980 raw rows, 3,420 verified repeats, 4,560 unique observations,
  1,440 label rows, and 1,276 positive label impacts;
- expansion: 360/360 jobs, 13,680 raw rows, 2,280 verified repeats, 11,400
  unique observations, 3,600 label rows, and 2,184 positive label impacts;
- quantum integrity: 165/165 cells across 5 splits, 3 dimensions, and 11
  conditions, with nine frozen acceptance checks;
- executable contract: six scenarios and eight acceptance checks.

The main article reports the counts needed to assess the claim. Detailed
environment, intervention, sensor, and validation tables are retained in the
supplement. Figure-source tables reproduce the plotted values. ZZ-versus-SVC is
visually and narratively secondary.

## 5. Figures, tables, and layout

- Main article: 9 pages in `IEEEtran` 10-point journal/compsoc, US Letter.
- Supplement: 3 pages in the same visual system.
- Three figures are vector PDFs; their plotted value tables are frozen.
- Figure fonts were regenerated as embedded CID TrueType rather than Type 3,
  with no change to the underlying CSV values.
- Tables are editable LaTeX, cited in order, and captions identify their role.
- The clean build rejects unresolved references and overfull boxes.
- Every rendered page is subject to visual QA after the final author block.

Page 9 is intentionally sparse in the anonymous build because the reference
list ends in the first column. This is not a reading defect; the final author
block and any required biographies may change the last-page balance. Artificial
padding was not added.

## 6. Reproducibility and integrity

The clean test suite passes 17 tests. The publication verifier checks 96
artifact files, four evidence manifests, 22 manifested outputs, hashes, row
counts, and primary claims. CI installs the locked environment, compiles the
auditable modules, runs the tests, and verifies the release artifact.

The artifact contains code, dependencies, compact derived evidence, figures,
figure sources, tests, and expected outputs. Raw public benchmark datasets are
not redistributed; acquisition and deterministic staging are documented. The
exact-statevector replacement was checked against Qiskit reference matrices,
unit properties, an end-to-end replay, and a larger pilot.

## 7. Project and scope discipline

ATHENA-AEGIS is a funding and traceability context, not evidence of complete
project coverage. The paper supplies a strong but bounded security-assurance
slice. It does not claim WP5/Fleet Management operation. The new Paper 2.5 plan
owns real-QPU context, calibration/drift, scheduling/layout, provider boundary,
multi-tenancy, runtime response, and operational AEGIS/Fleet integration. No
claim or experiment has been duplicated prospectively.

## 8. Final action gate

No new scientific experiment is recommended before first submission. Complete
only these author-controlled actions:

1. insert confirmed author metadata and CRediT roles;
2. confirm conflicts and the AI-use disclosure;
3. reproduce the official funding formula verbatim;
4. choose the artifact license and public repository state;
5. disclose related thesis papers/preprints and state non-overlap;
6. mint and insert the version DOI;
7. rebuild, rerun all checks, and visually inspect every page; and
8. recheck the TDSC portal and open calls on the actual submission date.

**Final scientific verdict:** strong Q1 candidate and ready to submit to TDSC
once the administrative gate is closed. **Acceptance is not assured**; the main
residual scholarly risk is editorial judgment about the generality and maturity
of the assurance mechanism, already maximized without changing the study.

## Addendum — rc2, 6 September 2026

Two of the residual risks listed above ("non-zero response is not calibrated
detection power" and "the ZZ-versus-SVC profile is confounded by
preprocessing and untuned baselines") were addressed after freezing by three
preregistered sensitivity gates (`manuscript/paper15_v11_reinforcement_prereg.md`),
executed on the frozen seeds with the exact-statevector engine and reported as
executed in the supplement and in `manuscript/paper15_v11_reinforcement_result_summary.md`.
The central claim, the abstract counts and every 1.0.0 table are unchanged.

Additional desk-review defences added in rc2: QML-PipeGuard and the
evaluation-blindness preprint are positioned in Section II and Table 1; the
three companion manuscripts are disclosed in Section II-C with an explicit
non-overlap statement; the author block, affiliation and funding footnote are
in place; the generative-AI disclosure names both systems used.

Still open before upload: all-author approval of CRediT roles, competing
interests and the AI disclosure; artifact license; Zenodo DOI; final rebuild,
checksums and page-by-page inspection; the portal recheck on submission day.
