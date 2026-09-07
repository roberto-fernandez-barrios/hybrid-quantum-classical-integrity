# Generative-AI disclosure (1.1.0 wording approved by all authors on 2026-09-06; extended for 1.2.0 and 1.3.0 on 2026-09-07, approval communicated by the corresponding author)

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
> manuscript revision and the release automation. The authors specified the
> protocols, verified the primary sources, proofs, numerical results, code and
> generated text, and retain full responsibility for the article.

Level of use by system and section, as the IEEE editorial policy on
AI-generated content requires:

| System | Period | Sections / components | Level of use |
|---|---|---|---|
| OpenAI Codex | May–August 2026 | Markdown manuscript drafting and editing, TDSC conversion, code inspection, 1.0.0 evidence builders, verifier, tests | Drafting and implementation under author specification; authors verified sources, code and numbers |
| Anthropic Claude Code | September 2026 | Related work (§II), formal section (§III) and counterexamples, adversary model (§IV), abstract, results, limitations, conclusion; supplement sections on Gates N/P/T, F/D and A; artifact 1.1.0–1.3.0 code; release automation | Drafting, implementation, mathematical audit (found the false Proposition 5(b) of 1.2.0), statistical correction (conformal rule, exhaustive tests, rule-bias decomposition), experimental design of Gate A (preregistered by the authors), manuscript revision; authors specified protocols, re-derived proofs, verified numbers, code and text |

Neither system is an author. The preregistrations of the three gate sets,
their amendment records (A1, A2, A3) and the numerical results were reviewed
by the authors before inclusion. The 1.3.0 extension of this statement was
approved by all authors on 2026-09-07 (communicated by the corresponding
author).
