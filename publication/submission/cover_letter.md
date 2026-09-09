Dear Editor-in-Chief,

Please consider our manuscript, “Observational Indistinguishability and
Integrity Blind Regions in Hybrid Quantum-Classical Workflows,” as a Regular
Paper for *IEEE Transactions on Dependable and Secure Computing*.

Hybrid workflows distribute one reported result across data acquisition,
preprocessing, quantum and classical computation, prediction, evaluation
labels, and reporting. A conclusion can change while every sensor available at
the audited boundary remains invariant, or a statistically visible change can
become difficult to detect once an attacker knows the monitored fingerprint.
The paper asks a precise dependability question: which evidence, under which
trusted reference, is sufficient for the integrity claim being protected?

We formalize auditability through observational indistinguishability under an
explicit information set and reference profile. The main constructive result
is claim-relative minimum evidence granularity: a trusted same-batch aggregate
anchor can certify the integrity of a reported conclusion, whereas
item-identity integrity requires item alignment; every such assurance claim
also needs a root outside the adversary’s rewrite class. The information-set
lattice covers the evaluation-label path as well as semantic, estimated, and
observed quantum kernels. An explicit adversary/failure model and an offline
`allow/hold/block` policy connect the formal statements to auditable decisions.

The evidence uses eight fixed ID/OOD environments from CICIDS2017, UNSW-NB15,
and ToN-IoT, with 11,400 deduplicated observations. Across 3,600 label
interventions, the implementation reproduces the exact structural boundaries.
A conformal family rule has finite-sample validity under exchangeability; the
executed design is not exchangeable, so its observed false-action rates are
reported descriptively. On the prespecified equal-weight intervention grid,
feature-bearing batch regimes serve 4,365–4,496 of 7,008 materially altered
audit results; the label-marginal regime serves 7,008/7,008 and is not included
in that range. Under the declared trusted reference, containment follows
constructively from the theory; the empirical result measures its cost: 85
gross exact-reference blocks overlap 46 batch interruptions, producing 39/1,200
net additional near-null interruptions (3.25 percentage points).

Gate A is a stress test of a fragile, cluster-dependent fingerprint. It does
not present a generally powerful detector that an attacker defeats. Rather,
high matched-control response, near-null sensitivity, and adaptive evasion are
three manifestations of the same duplicate/cluster structure. The adaptive
intervention retains 83–91% of the conclusion changes while sharply reducing
detection in the feature and feature-plus-prediction regimes. A separate
165-cell quantum gate is limited to ideal statevector simulation and
finite-shot emulation. The local four-contract prototype is an ATHENA-AEGIS
HSaaS research instance, not a deployed service.

The work fits TDSC through its focus on integrity assurance, observation-bound
failure modes, calibrated audit decisions, software validation, and dependable
hybrid computing. We do not claim quantum advantage, hardware or QPU coverage,
provider attestation, calibrated device-noise coverage, multi-tenant or
scheduling protection, confidentiality, operational prevalence, or deployed
deployed runtime assurance. Raw benchmark jobs and datasets are not included in the
compact artifact; the release starts from manifested derived evidence and
documents official data sources, staging, hashes, and the full recomputation
path.

Three related manuscripts are disclosed in Section II-E and on the title page.
“Conditional Validity of Quantum Event Classifiers under Collider Systematics
and Quantum Estimation Uncertainty” is available as arXiv:2609.02781.
“Candidate Comparability Before Promotion: Conditional Validation in Adaptive
Network Intrusion Detection” is available as arXiv:2609.04388. “Sharp
Target-Domain Certificates for Quantum-Kernel Advantage under Distribution
Shift” was submitted to *EPJ Quantum Technology* on 6 September 2026; its
Zenodo DOI 10.5281/zenodo.21776862 identifies the related software artifact,
not the manuscript. Copies of the related manuscripts are included in the
submission-support directory. Shared datasets, kernels, or monitors are
disclosed; the present propositions, interventions, tables, and integrity
claim are not reused from them.

Code, tests, compact derived evidence, vector figures, eight SHA-256 evidence
manifests, and a fail-closed verifier accompany the manuscript under the
at Zenodo (version DOI 10.5281/zenodo.22672505, version 1.3.4; concept DOI 10.5281/zenodo.22550852). Experimental evidence is frozen at artifact 1.3.0.
This work is supported by PID2024-155693NB-C43, ATHENA-AEGIS, funded by
MICIU/AEI/10.13039/501100011033 and ERDF/EU. The authors declare no competing
interests. OpenAI Codex and Anthropic Claude Code assisted with documented
drafting, implementation, audit, and editorial tasks; the human authors
verified the sources, proofs, code, numbers, and text, approved the manuscript,
and retain full responsibility. Neither system is an author.

The manuscript is original and is not under consideration elsewhere.

Sincerely,

Roberto Fernández-Barrios, corresponding author<br>
Faculty of Engineering, University of Deusto, Bilbao, Spain<br>
roberto.fernandez.b@deusto.es
