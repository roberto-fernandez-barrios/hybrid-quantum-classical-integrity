# Zenodo/DOI status

Status: **version 1.3.0 prepared** (final scientific closure of Paper 1.5);
the version DOI of 1.3.0 is minted by the release pipeline
(`scripts/release_pipeline.py`, steps `reserve-doi` → `insert-doi` →
`finalize`) with a fresh Zenodo personal access token supplied at run time
through the environment only; no token is stored in the repository and no
earlier token is reused. The concept DOI `10.5281/zenodo.22550852` resolves to
the latest archived version. The table below records every version.

| Version | Version DOI | Tag / release commit | Deposited files |
|---|---|---|---|
| 1.3.0 | recorded here by the release pipeline | `paper15-q1-v1.3.0` | `paper15-q1-v1.3.0.zip` (compact review artifact), `paper15-q1-v1.3.0-source.zip` (tagged source snapshot), `SHA256SUMS.txt`; sizes and hashes recorded after publication |
| 1.2.0 | `10.5281/zenodo.22644529` (<https://zenodo.org/records/22644529>, published 2026-09-07) | `paper15-q1-v1.2.0` / `7cbeb37` | `paper15-q1-v1.2.0.zip` (compact review artifact, 6,931,094 bytes, SHA-256 `b2c8a9d0d30061ca1e043142a3ddca155395ffee2a003ecae3dd4b26cb63d78b`); `paper15-q1-v1.2.0-source.zip` (tagged source snapshot, 10,894,679 bytes, SHA-256 `f8076702467985ab11bbf54e5b6810b50d129cb002dba5058b944b50fb601c70`); `SHA256SUMS.txt` (183 bytes). Superseded in one point by 1.3.0 (amendment A2: the family-calibration rule had a false guarantee) |
| 1.1.1 | `10.5281/zenodo.22552643` (<https://zenodo.org/records/22552643>, published 2026-09-06) | `paper15-q1-v1.1.1` / `d765a67` | `paper15-q1-v1.1.1.zip` 6,383,247 bytes, SHA-256 `8dcd71af6809078e3f38c4d4250898c93e19b818f523c69aadd1000dd0d776e0`; `paper15-q1-v1.1.1-source.zip` 20,723,313 bytes, SHA-256 `18c52141fb02a9d1d609689c65abd4c590f5f58332e1350681524a63608f818a` |
| 1.1.0 | `10.5281/zenodo.22550853` (<https://zenodo.org/records/22550853>) | `paper15-q1-v1.1.0` / `10a2a52` | `paper15-q1-v1.1.0.zip` 6,383,060 bytes, SHA-256 `1424ba3d0e5cf79ea1c47a370423d454c1d52e9cbf5c6682d98059345ea9aed7`; `paper15-q1-v1.1.0-source.zip` 20,721,105 bytes, SHA-256 `c83c4f5704f8bdc49ce47763f94d2a9aecd6425671b73fb67ee52cf207528338` |
| 1.0.0 | never archived | `paper15-q1-v1.0.0` | frozen evidence tag only |

Versions 1.1.0, 1.1.1 and 1.2.0 and their records are immutable: 1.3.0 is a
new Zenodo version under the same concept DOI, never an in-place edit. The
evidence manifests of 1.3.0 differ from 1.2.0 by the regenerated policy
manifest (27 tables; conformal rule, comparison columns, new cost metrics)
and by the seventh (adversarial) manifest; the gate1, expansion, quantum
integrity, hsaas and reinforcement evidence tables are byte-identical to
1.2.0.

Release order for 1.3.0 (so that PDF, `CITATION.cff`, `.zenodo.json`, tag,
GitHub release and Zenodo record point at the same object):

1. hostile review passes with no blocker or major objection within scope;
2. scientific commit; tests; verifier; clean rebuild; page-by-page
   inspection; checksums; artifact assembled and verified;
   `publication/RELEASE_STATUS.md` regenerated;
3. Zenodo draft created and version DOI reserved (`reserve-doi`);
4. DOI inserted in the manuscript data statement, the supplement, the title
   page, the cover letter, `CITATION.cff`, `README.md` and this file
   (`insert-doi`); rebuild; checksums; artifact reassembled and verified;
5. release commit, annotated tag `paper15-q1-v1.3.0`, GitHub release with the
   artifact ZIP and its SHA-256;
6. artifact and source ZIPs uploaded to the reserved deposition and published;
7. post-release documentary commit recording the file hashes and the record
   state.

Record metadata: authors Fernández-Barrios, Pastor-López, Pikatza-Huerga,
García Bringas (University of Deusto) with ORCIDs; license field Apache-2.0
(code) with the CC BY 4.0 evidence/documentation scope and the manuscript
exclusion stated in the record description and in `LICENSING.md`; funding
grant PID2024-155693NB-C43 (ATHENA-AEGIS) funded by
MICIU/AEI/10.13039/501100011033 and by ERDF/EU.
