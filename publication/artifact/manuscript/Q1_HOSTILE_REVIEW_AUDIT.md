# Hostile Q1 review audit — Paper 1.5

Audit date: 9 August 2026  
Target: *Computers & Security* candidate submission  
Decision standard: reject any claim not directly supported by the frozen design.

## Major-reviewer objections and disposition

| Likely objection | Evidence checked | Disposition in final manuscript |
|---|---|---|
| “The propositions are trivial and cannot carry novelty.” | Formal section and nearest-work audit | Conceded explicitly; novelty is the integrated conditional-coverage package. |
| “QCIVET already has contracts and hash chains.” | QCIVET arXiv:2605.13109 | Contracts/hash chain demoted to executable instantiation; differentiation is information-set/evaluation-boundary coverage. |
| “This is ordinary label shift.” | Intervention code, rows, Lipton et al. | Renamed evaluation-label intervention; historical `target_shift` identifier disclosed only for artifact mapping. |
| “Information regimes are not nested.” | Formal definitions | Replaced the linear list with a partial order; label marginal and quantum evidence are separate branches. |
| “Every label attack is claimed harmful.” | Gate 1 and expansion unique rows | Corrected: Gate 1 1,276 positive/164 zero; expansion 2,184 positive/1,416 zero; no negatives. |
| “Twenty seeds are pseudo-replication.” | Grid keys and deduplication | Primary unit is five split clusters after averaging nested model seeds; 20-unit result is sensitivity only. |
| “Confidence intervals imply population transport.” | Expansion summaries | Intervals are descriptive within each fixed environment; no random-effects pooling or population inference. |
| “Many comparisons are uncorrected.” | Results tables and code | No family-wise significance claim; counts of intervals excluding zero are descriptive. |
| “Quantum is confounded with preprocessing and headroom.” | Pipeline code and clean performance | Complete-pipeline comparison stated; `r=0.714` headroom association disclosed; ZZ-SVC is secondary. |
| “OOD performance near chance makes impact uninterpretable.” | Clean expansion summaries | Explicit headroom limitation; primary invariance result does not depend on model ranking. |
| “Balanced 3,000-row subsets are unrealistic.” | Staged data metadata | Balance, caps, numeric-only fields and lack of prevalence realism disclosed. |
| “Non-zero statistics are not detectors.” | Signal code and captions | Exact zero is used only for constructed invariance; non-zero response is not operational power; thresholds require calibration. |
| “Equal attack weighting invents a threat distribution.” | Suite builder | Equal weighting described as an engineering profile, not attack prevalence. |
| “PSD repair can conceal tampering.” | Quantum gate conditions | Repair is containment only; PSD-preserving substitution is the explicit algebraic blind region. |
| “Hashes prove authentication.” | Contract implementation | Claim limited to tamper evidence; no identity, signature or non-repudiation. |
| “Finite shots imply hardware validation.” | Gate implementation and manifest | Conditions identified as binomial emulators of exact fidelities; no sampler, calibrated noise or QPU claim. |
| “ATHENA/WP5 is overclaimed.” | Project proposal WP3/WP5 pages | Strong bounded G3.2/G3.3 plus selected G3.1; WP5 only Task 5.2 dissemination, not Fleet Task 5.1/Result 5.1. |
| “Reproducibility depends on untracked local outputs.” | Four manifests and compact artifact | Derived evidence copied into release; independent verifier checks 22 outputs, hashes, row counts and primary claims. |

## Statistical and numerical checks

- Gate 1: 7,980 raw rows = 4,560 unique observations + 3,420 verified SVC
  repetitions.
- Expansion: 13,680 raw rows = 11,400 unique observations + 2,280 verified
  SVC repetitions.
- Expansion jobs: 360 observed / 360 expected; all eight designs valid.
- Label boundary: 3,600/3,600 feature/prediction invariant;
  1,800/1,800 prior-preserving label-marginal invariant.
- Positive-impact joint coverage: 2,184/2,184 non-zero; zero-impact cells are
  not silently relabeled positive.
- Quantum gate: 165 rows; 9/9 frozen acceptance checks pass.
- HSaaS: six envelopes; 8/8 checks pass; hash chains verify.
- Gate-1 paired intervals use `df=4`; expansion intervals do not pool fixed
  environments.
- Numerical non-zero threshold in Gate D is disclosed as `1e-8`; structural
  label invariance uses raw values with verifier tolerance `1e-12`.

## Figures and tables

- Figure 1 reports response fractions by information regime and states that
  zero is raw invariance, not detector power.
- Figure 2 separates ID/OOD fixed environments and rejects population pooling.
- Figure 3 includes clean and semantics-preserving controls, preventing a
  one-sided “all changes are detected” display.
- Table 1 presents the closest-work positioning without exceeding the text
  width. The fixed environments and compact secondary profile are reported in
  prose to prevent small tables from splitting across pages.
- Figure source tables and both PNG/PDF renderings are included and hashed.

## Residual risks that cannot be solved by more in-scope experiments

1. The novelty claim is a combination claim; reviewers may value its parts
   differently despite the explicit QCIVET comparison.
2. Eight environments improve transport evidence but do not establish a sampled
   deployment population.
3. The secondary model comparison remains headroom/preprocessing confounded.
4. Author list, license and public DOI require joint author/legal decisions.
5. The three closest 2026 items are recent preprints; reviewers may question
   priority or peer-review status, so their dates and the narrower combination
   claim must remain explicit.

## Audit verdict

No unresolved scientific blocker requiring an additional experiment was found
inside the frozen scope. The manuscript is defensible as a Q1 candidate because
the central exact result, its multi-environment replay and the bounded quantum
coverage lead to a coherent security-audit contribution. The remaining blockers
are administrative/publication metadata, not scientific validity.
