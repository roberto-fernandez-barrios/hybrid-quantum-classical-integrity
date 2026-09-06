# Zenodo/DOI status

Status on 6 September 2026: **artifact 1.1.0 (frozen 1.0.0 evidence plus
preregistered reinforcement gates) and TDSC release candidate rc2 prepared;
DOI not minted**. The GitHub repository became public on 6 September 2026 and
`main` now points at the science branch; a LICENSE file is still missing and
must be added before archival.

No Zenodo access token is available in the workspace. Author order,
affiliations and ORCIDs were confirmed on 6 September 2026; CRediT roles are
proposed on the title page and await all-author confirmation; the license
choice is still open. No license or archival decision has been made
automatically.

Ready inputs:

- frozen evidence version `1.0.0` (tag `paper15-q1-v1.0.0`) and artifact
  version `1.1.0` (submission tag to be created after all-author approval);
- `publication/paper15-q1-v1.0.0.zip` and its SHA-256 file;
- TDSC submission build `1.1.0-tdsc-rc2`, with checked main and supplement
  sources in `publication/tdsc/` and rendered PDFs in `output/pdf/`;
- `publication/tdsc/CHECKSUMS.sha256`, binding the inspected PDFs;
- `.zenodo.json.in` and `CITATION.cff.in` metadata templates;
- verified AEI grant `PID2024-155693NB-C43`;
- artifact-wide and evidence-level SHA-256 manifests.

To mint the DOI after author confirmation:

1. choose and add the approved license;
2. replace author placeholders in both metadata templates and rename them to
   `.zenodo.json` and `CITATION.cff`;
3. publish the exact tagged release or upload the prepared ZIP directly;
4. reserve then publish the Zenodo record;
5. replace `DOI PENDING` in the metadata, manuscript availability statement and
   submission files with the version DOI.

After inserting the DOI and confirmed author metadata, rerun
`publication/tdsc/build.ps1`, regenerate `CHECKSUMS.sha256`, and visually inspect
every page. The root artifact tag must not be silently moved; create a new,
author-approved submission/release tag if the public package differs.

Minting the DOI before these confirmations would create a public scholarly
record with potentially incorrect authorship or reuse rights.
