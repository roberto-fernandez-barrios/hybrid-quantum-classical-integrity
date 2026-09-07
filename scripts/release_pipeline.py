"""Release pipeline for Paper 1.5 artifact versions (1.2.0 and later).

The pipeline makes the version DOI, the manuscript, the citation metadata, the
Git tag, the GitHub release and the Zenodo record point at the same object.
It never stores a token: pass a fresh Zenodo personal access token through
the ``ZENODO_TOKEN`` environment variable for the steps that need it. Earlier
tokens must not be reused.

Steps (run from the repository root, in this order):

    python scripts/release_pipeline.py preflight
        tests, verifier, build, artifact assembly, release status; fails closed.
    python scripts/release_pipeline.py reserve-doi
        creates a new Zenodo version of the concept record and prints the
        reserved version DOI (requires ZENODO_TOKEN).
    python scripts/release_pipeline.py insert-doi --doi 10.5281/zenodo.NNNNNN
        inserts the version DOI into the manuscript data statement, the
        supplement, CITATION.cff, README.md, the title page, the cover letter
        and publication/DOI_STATUS.md, then rebuilds, reassembles and verifies.
    python scripts/release_pipeline.py finalize --doi 10.5281/zenodo.NNNNNN
        commits, creates the annotated tag, the GitHub release with the artifact
        ZIP and its SHA-256, uploads the artifact and source ZIPs to the reserved
        Zenodo deposition and publishes it (requires ZENODO_TOKEN and gh).

Every step prints what it did; nothing is silently skipped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DOI = "10.5281/zenodo.22550852"
ZENODO_API = "https://zenodo.org/api"


def _run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT, check=check, capture_output=capture, text=True)


def _python() -> str:
    for candidate in (ROOT / ".venv/Scripts/python.exe", ROOT / ".venv/bin/python"):
        if candidate.exists():
            return str(candidate)
    return sys.executable


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def _tag() -> str:
    return f"paper15-q1-v{_version()}"


def _token() -> str:
    token = os.environ.get("ZENODO_TOKEN", "").strip()
    if not token:
        raise SystemExit("ZENODO_TOKEN is not set; generate a fresh personal access token (deposit:write, deposit:actions) and export it for this shell only")
    return token


def _requests():
    try:
        import requests  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("the 'requests' package is required for the Zenodo steps: pip install requests") from exc
    return requests


# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------


def preflight() -> None:
    py = _python()
    # Build first, then assemble the compact artifact (the PDFs are part of it),
    # then verify it and run the tests, which check the assembled artifact.
    _run(["pwsh", "-NoProfile", "-File", "publication/tdsc/build.ps1"])
    _run([py, "-m", "src.experiments.assemble_publication_artifact"])
    _run([py, "-m", "src.experiments.verify_publication_artifact", "--root", "publication/artifact"])
    _run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider"])
    _run([py, "-m", "src.experiments.make_release_status"])
    checksums = ROOT / "publication/tdsc/CHECKSUMS.sha256"
    lines = [f"{_sha256(ROOT / 'output/pdf' / name)}  output/pdf/{name}" for name in ("paper15_tdsc_submission.pdf", "paper15_tdsc_supplement.pdf")]
    checksums.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("preflight passed; checksums written to", checksums)


# ---------------------------------------------------------------------------
# reserve-doi
# ---------------------------------------------------------------------------


def reserve_doi() -> str:
    requests = _requests()
    headers = {"Authorization": f"Bearer {_token()}"}
    concept_id = CONCEPT_DOI.rsplit(".", 1)[-1]
    # Latest published record of the concept.
    latest = requests.get(f"{ZENODO_API}/records/{concept_id}", headers=headers, timeout=60)
    latest.raise_for_status()
    latest_id = latest.json()["id"]
    created = requests.post(f"{ZENODO_API}/deposit/depositions/{latest_id}/actions/newversion", headers=headers, timeout=60)
    created.raise_for_status()
    draft_url = created.json()["links"]["latest_draft"]
    draft = requests.get(draft_url, headers=headers, timeout=60)
    draft.raise_for_status()
    payload = draft.json()
    doi = payload.get("metadata", {}).get("prereserve_doi", {}).get("doi") or payload.get("doi")
    if not doi:
        raise SystemExit("Zenodo did not return a reserved DOI; inspect the draft in the web UI")
    metadata = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    metadata["prereserve_doi"] = payload["metadata"].get("prereserve_doi", {"doi": doi})
    updated = requests.put(draft_url, headers={**headers, "Content-Type": "application/json"}, data=json.dumps({"metadata": metadata}), timeout=60)
    updated.raise_for_status()
    state = {"deposition_id": payload["id"], "draft_url": draft_url, "doi": doi, "version": _version()}
    (ROOT / "publication" / "zenodo_draft_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print("reserved version DOI:", doi)
    print("draft state written to publication/zenodo_draft_state.json (no token inside)")
    return doi


# ---------------------------------------------------------------------------
# insert-doi
# ---------------------------------------------------------------------------


def insert_doi(doi: str) -> None:
    if not re.fullmatch(r"10\.5281/zenodo\.\d+", doi):
        raise SystemExit(f"unexpected DOI format: {doi}")
    version = _version()
    tag = _tag()
    edits: list[tuple[Path, str, str]] = [
        (ROOT / "publication/tdsc/main.tex",
         "Version\n1.2.0 is archived at Zenodo under the concept DOI 10.5281/zenodo.22550852\n(version DOI in the artifact metadata)",
         f"Version\n{version} is archived at Zenodo, DOI {doi} (concept DOI\n{CONCEPT_DOI})"),
        (ROOT / "publication/tdsc/supplement.tex",
         "Version 1.2.0 is archived at Zenodo under the concept\nDOI 10.5281/zenodo.22550852 with repository tag \\texttt{paper15-q1-v1.2.0};",
         f"Version {version} is archived at Zenodo, DOI {doi} (concept\nDOI {CONCEPT_DOI}), with repository tag \\texttt{{{tag}}};"),
        (ROOT / "CITATION.cff", f'doi: "{CONCEPT_DOI}"', f'doi: "{doi}"'),
        (ROOT / "README.md",
         "the version DOI of 1.2.0 is recorded in `CITATION.cff` and\n`publication/DOI_STATUS.md`",
         f"the version DOI of {version} is `{doi}`"),
        (ROOT / "publication/DOI_STATUS.md", "| 1.2.0 | recorded here by the release pipeline |", f"| {version} | `{doi}` |"),
        (ROOT / "publication/submission/title_page_REQUIRED.md",
         "the version DOI\nof 1.2.0 is recorded in `publication/DOI_STATUS.md` and `CITATION.cff`",
         f"version DOI of {version}: **{doi}**"),
        (ROOT / "publication/submission/cover_letter.md",
         "under the concept DOI 10.5281/zenodo.22550852 (version 1.2.0; the version DOI\nis recorded in the artifact metadata)",
         f"at Zenodo (DOI {doi}, version {version}; concept DOI {CONCEPT_DOI})"),
    ]
    for path, old, new in edits:
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise SystemExit(f"insertion anchor not found in {path.relative_to(ROOT)}: {old[:60]!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
        print("inserted DOI in", path.relative_to(ROOT))
    status = ROOT / "publication/DOI_STATUS.md"
    text = status.read_text(encoding="utf-8")
    text = text.replace("Status on 7 September 2026: **version 1.2.0 prepared**", f"Status: **version {version} DOI reserved ({doi})**", 1)
    status.write_text(text, encoding="utf-8", newline="\n")
    preflight()


# ---------------------------------------------------------------------------
# finalize
# ---------------------------------------------------------------------------


def _zip_dir(source: Path, target: Path, prefix: str) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            archive.write(path, f"{prefix}/{path.relative_to(source).as_posix()}")


def finalize(doi: str) -> None:
    requests = _requests()
    version, tag = _version(), _tag()
    state_path = ROOT / "publication" / "zenodo_draft_state.json"
    if not state_path.exists():
        raise SystemExit("run reserve-doi first (publication/zenodo_draft_state.json missing)")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state["doi"] != doi:
        raise SystemExit(f"DOI mismatch: reserved {state['doi']} vs requested {doi}")

    artifact_zip = ROOT / "publication" / f"{tag}.zip"
    _zip_dir(ROOT / "publication/artifact", artifact_zip, tag)
    (ROOT / "publication" / f"{tag}.zip.sha256").write_text(f"{_sha256(artifact_zip)}  {tag}.zip\n", encoding="utf-8", newline="\n")

    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", f"Release {tag}: scientific closure of Paper 1.5 for IEEE TDSC (version DOI {doi})\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"])
    _run(["git", "tag", "-a", tag, "-m", f"Paper 1.5 artifact {version} - observational indistinguishability and integrity blind regions; policy-level calibration and end-to-end decisions. Zenodo DOI {doi}."])
    _run(["git", "push", "origin", "HEAD"])
    _run(["git", "push", "origin", tag])
    _run(["gh", "release", "create", tag, str(artifact_zip), str(ROOT / "publication" / f"{tag}.zip.sha256"), "--title", f"Paper 1.5 artifact {version} (scientific closure for IEEE TDSC)", "--notes-file", str(ROOT / "publication/tdsc/RELEASE_NOTES.md")])

    source_zip = ROOT / "publication" / f"{tag}-source.zip"
    _run(["git", "archive", "--format=zip", f"--prefix={tag}-source/", "-o", str(source_zip), tag])
    sums = ROOT / "publication" / "SHA256SUMS.txt"
    sums.write_text("".join(f"{_sha256(p)}  {p.name}\n" for p in (artifact_zip, source_zip)), encoding="utf-8", newline="\n")

    headers = {"Authorization": f"Bearer {_token()}"}
    draft = requests.get(state["draft_url"], headers=headers, timeout=60)
    draft.raise_for_status()
    bucket = draft.json()["links"]["bucket"]
    for path in (artifact_zip, source_zip, sums):
        with path.open("rb") as handle:
            up = requests.put(f"{bucket}/{path.name}", data=handle, headers=headers, timeout=1800)
            up.raise_for_status()
            print("uploaded", path.name)
    published = requests.post(state["draft_url"].replace("/api/deposit/depositions/", "/api/deposit/depositions/") + "/actions/publish", headers=headers, timeout=120)
    published.raise_for_status()
    print("published Zenodo record:", published.json().get("links", {}).get("record_html"))
    print("record the deposited file sizes and hashes in publication/DOI_STATUS.md and commit (post-release documentary commit)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="step", required=True)
    sub.add_parser("preflight")
    sub.add_parser("reserve-doi")
    p_insert = sub.add_parser("insert-doi")
    p_insert.add_argument("--doi", required=True)
    p_final = sub.add_parser("finalize")
    p_final.add_argument("--doi", required=True)
    args = parser.parse_args()
    if args.step == "preflight":
        preflight()
    elif args.step == "reserve-doi":
        reserve_doi()
    elif args.step == "insert-doi":
        insert_doi(args.doi)
    elif args.step == "finalize":
        finalize(args.doi)


if __name__ == "__main__":
    main()
