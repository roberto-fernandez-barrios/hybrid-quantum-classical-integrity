# IEEE TDSC submission checklist (artifact 1.3.0)

## Scientifically closed

- [x] Central claim frozen as observational indistinguishability and integrity
      blind regions under explicit information sets and trusted references.
- [x] Formal core: Lemma 1, Propositions 1–7, Corollaries 1–3, counterexamples
      C1–C9 with witnesses; Proposition 5(b) of 1.2.0 replaced by the conformal
      rule with an exact level (amendment A2); statement-by-statement review
      with brute-force and exhaustive tests (`manuscript/FORMAL_REVIEW_1.3.0.md`).
- [x] Adversary and failure model with four classes and uncontrolled roots;
      the adaptive cluster-preserving attacker executed (Gate A), L3 decision
      recorded.
- [x] Signed conclusion change reported (2,184 / 983 / 433; 1,276 / 105 / 59) and
      verified.
- [x] ZZ-versus-SVC in the supplement; one sentence in the main text; label
      intervention distinguished from statistical label shift.
- [x] Statistical units: five split clusters for the model profile;
      (environment, split) clusters for false-alarm rates; pooled rates and
      binomial intervals declared descriptive; conformal level declared marginal;
      no population claim.
- [x] Gates F and D regenerated with the conformal rule; 1.2.0 rule kept as
      comparison; excess decomposed into rule bias and design effect; E1 in the
      primary aggregate and reported separately; benign interruption cost of
      every policy and regime explicit; "offline end-to-end" wording throughout.
- [x] Policy taxonomy: P0 baseline, P1 uncalibrated risk-tolerant, P2
      calibrated risk-tolerant, P3 strict fail-closed; contracts fail closed on
      their invariants.
- [x] Quantum gate explicitly limited to ideal simulation and shot emulation and
      placed on the view lattice (Proposition 7); hash chain described as
      tamper-evident, not identity/non-repudiation.
- [x] Dataset weights explicit (five CICIDS2017, two UNSW-NB15, one ToN-IoT
      environments; six of nine with Gate 1).
- [x] ATHENA contribution bounded; no claim of complete project or WP5 coverage.
- [x] QPU, scheduling, multi-tenancy, provider attestation, deployed services,
      context-conditioned runtime calibration, recovery and Fleet Management
      excluded.
- [x] Abstract is one paragraph within 150–250 words; five IEEE Index Terms.
- [x] In-text citations and reference keys are bidirectionally complete;
      figures and tables cited, captioned and generated from manifested tables.
- [x] Seven evidence manifests, primary count claims, signed label counts,
      conformal-level and adversarial claims verify (artifact 1.3.0).
- [x] Related work rechecked on 2026-09-07 (classical stealth/detectability,
      runtime assurance, integrity monitoring, evaluation integrity, quantum
      provenance API, conformal p-values and multiple testing).
- [x] Tests and CI include the publication-artifact verifier, the exhaustive
      calibration tests and the formal-core tests.
- [x] TDSC `IEEEtran` Computer Society source and separate supplement compile
      cleanly; main article at or below the 12-page ceiling (counts in
      `publication/RELEASE_STATUS.md`).

## Administrative actions

- [x] Author list/order, affiliations, corresponding author and ORCIDs (2026-09-06).
- [x] CRediT roles and competing-interest wording (2026-09-06; reconfirmed 2026-09-07).
- [x] Licenses (Apache-2.0 code, CC BY 4.0 evidence/documentation, manuscript excluded).
- [x] Funding statement per AEI publicity guide v09 (2026-09-06).
- [x] Repository public; `main` aligned with the science branch at release.
- [x] Approval by all authors of the 1.3.0 manuscript (new Proposition 5,
      amendment A2, Gate A, framing changes) and of the extended AI-use
      disclosure (2026-09-07, communicated by the corresponding author).
- [ ] Version DOI of 1.3.0 minted with a fresh Zenodo token and inserted by the
      release pipeline (`publication/DOI_STATUS.md`).
- [x] Originality/not-under-review statement in the cover letter.
- [x] Closely related papers disclosed with a difference statement (§II-E,
      title page, cover letter); attach copies if the portal asks.
- [ ] Recheck the TDSC portal on submission day for article type, page limit,
      biographies, template, supplement designation and current special issues.

## Automated preflight immediately before upload

- [ ] Run `pwsh -File publication/tdsc/build.ps1` from the repository root.
- [ ] Run the complete test suite and the artifact verifier.
- [ ] Regenerate `publication/RELEASE_STATUS.md` and confirm PDF hashes match
      `publication/tdsc/CHECKSUMS.sha256`.
- [ ] Search the active package for `INSERT`, `DOI PENDING`, `Anonymous Author`
      and any obsolete journal name; none may remain.
- [ ] Inspect every final PDF page at submission size.

## Reopening rule after 1.3.0

The article is reopened only for an objective error that invalidates a claim,
an editorial requirement of the journal, or a reviewer request. New scientific
ideas go to Paper 2.5 or other work.
