# IEEE TDSC submission checklist (artifact 1.2.0)

## Scientifically closed

- [x] Central claim frozen as observational indistinguishability and integrity
      blind regions under explicit information sets and trusted references.
- [x] Formal core: Lemma 1, Propositions 1–6, Corollaries 1–2, eight
      counterexamples with witnesses; the earlier Propositions 1–2 are corollaries.
- [x] Adversary and failure model with four classes and uncontrolled roots.
- [x] Signed conclusion change reported (2,184 / 983 / 433; 1,276 / 105 / 59) and
      verified; the clipped "harm" endpoint is no longer presented as "no negative
      impact".
- [x] ZZ-versus-SVC retained only as a short secondary subsection with details
      in the supplement; label intervention distinguished from statistical label
      shift.
- [x] Statistical units: five split clusters for the model profile;
      (environment, split) clusters for false-alarm rates; pooled rates and
      binomial intervals declared descriptive; no population claim.
- [x] Decision-level calibration (Gate F) and end-to-end policy evaluation
      (Gate D) preregistered before analysis and reported as executed,
      including the residual excess over nominal.
- [x] Quantum gate explicitly limited to ideal simulation and shot emulation;
      hash chain described as tamper-evident, not identity/non-repudiation.
- [x] ATHENA contribution bounded; no claim of complete project or WP5 coverage.
- [x] QPU, scheduling, multi-tenancy, provider attestation, context-conditioned
      runtime calibration, recovery and Fleet Management excluded.
- [x] Abstract is one paragraph within 150–250 words; five IEEE Index Terms.
- [x] In-text citations and reference keys are bidirectionally complete;
      figures and tables cited, captioned and generated from manifested tables.
- [x] Six evidence manifests, 65 outputs, primary count claims, signed label
      counts and policy claims verify (artifact 1.2.0).
- [x] Related work rechecked on 2026-09-07 (classical stealth/detectability,
      runtime assurance, integrity monitoring, evaluation integrity, quantum
      provenance API).
- [x] Tests and CI include the publication-artifact verifier and the policy
      layer tests.
- [x] TDSC `IEEEtran` Computer Society source and separate supplement compile
      cleanly; main article below the 12-page ceiling (counts in
      `publication/RELEASE_STATUS.md`).

## Administrative actions requiring the authors

- [x] Author list/order, affiliations, corresponding author and ORCIDs (2026-09-06).
- [x] CRediT roles and competing-interest wording (2026-09-06).
- [x] Licenses (Apache-2.0 code, CC BY 4.0 evidence/documentation, manuscript excluded).
- [x] Funding statement per AEI publicity guide v09 (2026-09-06).
- [x] Repository public; `main` aligned with the science branch at release.
- [ ] Re-approval by all authors of the 1.2.0 manuscript (new title, formal
      core, adversary model, policy gates) and of the extended AI-use disclosure.
- [ ] Version DOI of 1.2.0 minted with a fresh Zenodo token and inserted by the
      release pipeline (`publication/DOI_STATUS.md`).
- [x] Originality/not-under-review statement in the cover letter.
- [x] Closely related papers disclosed with a difference statement (§II-D,
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
