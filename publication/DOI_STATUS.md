# Zenodo/DOI status

Status on 9 August 2026: **release package prepared; DOI not minted**.

The repository is private and no Zenodo access token is available in the
workspace. More importantly, public archival requires author/order metadata and
a license choice that cannot be inferred safely. The GitHub-Zenodo path also
requires the repository to be public. No repository visibility, license or
authorship decision has therefore been changed automatically.

Ready inputs:

- version `1.0.0` and intended tag `paper15-q1-v1.0.0`;
- `publication/paper15-q1-v1.0.0.zip` and its SHA-256 file;
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

Minting the DOI before these confirmations would create a public scholarly
record with potentially incorrect authorship or reuse rights.
