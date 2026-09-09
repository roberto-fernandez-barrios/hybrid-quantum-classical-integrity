# Generative-AI disclosure (release 1.3.4; authors retain full responsibility)

Text used in the manuscript Acknowledgment and in the submission portal:

> During manuscript and artifact preparation the authors used two generative-AI
> coding assistants. OpenAI Codex (May–August 2026) assisted with literature
> discovery, drafting and language editing of the Markdown manuscript and its
> TDSC conversion, code inspection, and the evidence builders, verifier and
> tests of artifact 1.0.0. Anthropic Claude Code (September 2026) assisted with
> the related-work additions, the formal section and its counterexamples, the
> adversary model, the abstract, results, limitations and conclusion edits, the
> supplement sections on the calibration, policy and adversarial gates and
> their generated tables, the artifact 1.1.0 and 1.2.0 code (null-control
> sampler, cross-validated tuning, execution queue, evidence builders, policy
> layer, figure and table generators, artifact assembler and their tests),
> and, for artifact 1.3.0, the mathematical audit that found the defect in the
> earlier calibration rule, the implementation and exhaustive tests of the
> conformal rule, the design and implementation of the cluster-preserving
> adversarial gate, the statistical decomposition of the earlier excess, the
> manuscript revision and the release automation, and, for version 1.3.1, the
> formal review that corrected the finite-shot statement of Proposition 7,
> the workflow-state semantics and the reference taxonomy, the executable
> state model and its tests, the manuscript consistency tests, the figure
> layout and the editorial corrections. OpenAI Codex (September 2026) also
> assisted with the controlled 1.3.2 implementation/reference audit,
> frozen-output-derived tables and macros, manuscript alignment, permanent
> regression tests, PDF verification and release preparation. For version
> 1.3.3, Codex assisted only with primary-source bibliographic verification,
> bibliographic metadata and prior-art positioning, a final readability pass,
> regression guards, PDF verification and release preparation. For version
> 1.3.4, Codex assisted with the reference-by-reference primary-source audit,
> corrective bibliographic and frozen-derived metadata edits, editorial
> consistency checks, regression guards, PDF verification and release
> preparation; no experiment was designed or rerun. The authors specified the protocols,
> verified the primary sources, proofs, numerical results, code and generated
> text, and retain full responsibility for the article.

Level of use by system and section, as the IEEE editorial policy on
AI-generated content requires:

| System | Period | Sections / components | Level of use |
|---|---|---|---|
| OpenAI Codex | May–August 2026 | Markdown manuscript drafting and editing, TDSC conversion, code inspection, 1.0.0 evidence builders, verifier, tests | Drafting and implementation under author specification; authors verified sources, code and numbers |
| OpenAI Codex | September 2026 | 1.3.2 sensor/reference audit; frozen-derived trusted-cost and adaptive-strength tables; taxonomy, manuscript and submission-package alignment; guards and release verification | Implementation audit and controlled editorial correction under author specification; no new experiment; authors verified the interpretation, code, numbers and text |
| OpenAI Codex | September 2026 | 1.3.3 primary-source bibliographic verification; bibliography/metadata and prior-art positioning; readability edit; bibliographic guards; PDF and release verification | Bibliographic/editorial correction under author specification; no science or evidence changed; authors retain responsibility for every source and statement |
| OpenAI Codex | September 2026 | 1.3.4 reference-by-reference primary-source audit; frozen-derived coverage-metadata correction; bibliography, manuscript and submission-package alignment; guards, PDF and release verification | Corrective bibliographic/editorial work under author specification; no experiment, model, dataset, seed, attack, intervention, policy decision, result or theorem rerun or changed; authors verified every source and edit |
| Anthropic Claude Code | September 2026 | Related work (§II), formal section (§III) and counterexamples, adversary model (§IV), abstract, results, limitations, conclusion; supplement sections on Gates N/P/T, F/D and A; artifact 1.1.0–1.3.1 code; release automation; 1.3.1 formal and editorial corrections | Drafting, implementation, mathematical audit (found the false Proposition 5(b) of 1.2.0; corrected the finite-shot statement of Proposition 7(iii), the state semantics and the reference taxonomy in 1.3.1), statistical correction (conformal rule, exhaustive tests, rule-bias decomposition), experimental design of Gate A (preregistered by the authors), manuscript revision, consistency tests and figure layout; authors specified protocols, re-derived proofs, verified numbers, code and text |

Neither system is an author. The preregistrations of the three gate sets,
their amendment records (A1, A2, A3) and the numerical results were reviewed
by the authors before inclusion. The extensions through 1.3.2 were approved by
all authors (communicated by the corresponding author). The 1.3.3 and 1.3.4
bibliographic/editorial closures were performed under author instruction; the
authors retain responsibility for final approval and submission.
