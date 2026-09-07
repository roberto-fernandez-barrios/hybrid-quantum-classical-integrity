"""Release pipeline for Paper 1.5 artifact versions (1.2.0 and later; anchors and messages are version-parametrised).

The pipeline makes the version DOI, the manuscript, the citation metadata, the
Git tag, the GitHub release and the Zenodo record point at the same object,
and leaves the science branch, ``main`` and the annotated tag on that object.
It never stores a token: pass a fresh Zenodo personal access token through
the ``ZENODO_TOKEN`` environment variable for the steps that need it, for the
duration of that shell only. The token is never printed and never written.

Steps (run from the repository root, in this order):

    python scripts/release_pipeline.py preflight
        build, artifact assembly, verifier, tests, release status, checksums;
        fails closed.
    python scripts/release_pipeline.py reserve-doi
        creates a new Zenodo version of the concept record and prints the
        reserved version DOI (requires ZENODO_TOKEN).
    python scripts/release_pipeline.py insert-doi --doi 10.5281/zenodo.NNNNNN
        inserts the version DOI into the manuscript data statement, the
        supplement, CITATION.cff, README.md, the title page, the cover letter
        and publication/DOI_STATUS.md, then runs preflight again and checks
        that the version DOI and the concept DOI differ everywhere.
    python scripts/release_pipeline.py finalize --doi 10.5281/zenodo.NNNNNN
        fail-closed Git checks (clean tree, expected branch, main fast-forwardable,
        no force), release commit, annotated tag, fast-forward of main, pushes,
        GitHub release with the artifact ZIP and its SHA-256, clean source ZIP
        from the tag (verified to contain no release asset, draft state or
        token), upload of both ZIPs and SHA256SUMS to the reserved Zenodo
        deposition, publication, and post-publication checks (DOI resolution,
        concept relation, files, sizes, hashes).

Release assets (ZIPs, SHA256SUMS, draft state) are ignored by Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DOI = "10.5281/zenodo.22550852"
# Human-readable summary of the version being released (commit, tag and GitHub release titles).
RELEASE_SUMMARY = {
    "1.3.0": "scientific closure of Paper 1.5 for IEEE TDSC",
    "1.3.1": "formal and editorial correction of Paper 1.5 for IEEE TDSC (experimental evidence frozen at 1.3.0)",
}
ZENODO_API = "https://zenodo.org/api"
SCIENCE_BRANCH = "paper15-q1-expansion"
MAIN_BRANCH = "main"
REMOTE = "origin"
TOKEN_MARKERS = ("ZENODO_TOKEN=", "Bearer ")


def _run(cmd: list[str], *, check: bool = True, capture: bool = False, quiet: bool = False) -> subprocess.CompletedProcess:
    if not quiet:
        print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT, check=check, capture_output=capture, text=True)


def _out(cmd: list[str]) -> str:
    return _run(cmd, capture=True, quiet=True).stdout.strip()


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


def _summary() -> str:
    version = _version()
    if version not in RELEASE_SUMMARY:
        _fail(f"no release summary registered for version {version}; add it to RELEASE_SUMMARY")
    return RELEASE_SUMMARY[version]


def _token() -> str:
    token = os.environ.get("ZENODO_TOKEN", "").strip()
    if not token:
        raise SystemExit("ZENODO_TOKEN is not set; export a fresh personal access token (deposit:write, deposit:actions) for this shell only")
    return token


def _requests():
    try:
        import requests  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("the 'requests' package is required for the Zenodo steps: pip install requests") from exc
    return requests


def _fail(message: str) -> None:
    raise SystemExit(f"ABORT: {message}")


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
    _run([py, "scripts/verify_datasets.py"])
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
        _fail("Zenodo did not return a reserved DOI; inspect the draft in the web UI")
    metadata = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    metadata["prereserve_doi"] = payload["metadata"].get("prereserve_doi", {"doi": doi})
    updated = requests.put(draft_url, headers={**headers, "Content-Type": "application/json"}, data=json.dumps({"metadata": metadata}), timeout=60)
    updated.raise_for_status()
    # Remove files inherited from the previous version so that only the assets of this version are deposited.
    for f in updated.json().get("files", []):
        requests.delete(f["links"]["self"], headers=headers, timeout=60).raise_for_status()
        print("removed inherited file", f.get("filename"))
    state = {"deposition_id": payload["id"], "draft_url": draft_url, "doi": doi, "version": _version()}
    (ROOT / "publication" / "zenodo_draft_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print("reserved version DOI:", doi)
    print("draft state written to publication/zenodo_draft_state.json (ignored by Git; contains no token)")
    return doi


# ---------------------------------------------------------------------------
# insert-doi
# ---------------------------------------------------------------------------


def insert_doi(doi: str) -> None:
    if not re.fullmatch(r"10\.5281/zenodo\.\d+", doi):
        _fail(f"unexpected DOI format: {doi}")
    if doi == CONCEPT_DOI:
        _fail("the version DOI must differ from the concept DOI")
    version = _version()
    tag = _tag()
    edits: list[tuple[Path, str, str]] = [
        (ROOT / "publication/tdsc/main.tex",
         f"Version\n{version} is archived at Zenodo under the concept DOI {CONCEPT_DOI}\n(version DOI in the artifact metadata)",
         f"Version\n{version} is archived at Zenodo, version DOI {doi} (concept DOI\n{CONCEPT_DOI})"),
        (ROOT / "publication/tdsc/supplement.tex",
         f"Version {version} is archived at Zenodo under the concept\nDOI {CONCEPT_DOI} with repository tag \\texttt{{{tag}}};",
         f"Version {version} is archived at Zenodo, version DOI {doi} (concept\nDOI {CONCEPT_DOI}), with repository tag \\texttt{{{tag}}};"),
        (ROOT / "CITATION.cff", f'doi: "{CONCEPT_DOI}"', f'doi: "{doi}"'),
        (ROOT / "CITATION.cff",
         f"concept DOI below resolves to the latest version; the version DOI of {version} is recorded in publication/DOI_STATUS.md once minted",
         f"version DOI {doi}; concept DOI {CONCEPT_DOI} resolves to the latest version"),
        (ROOT / "README.md",
         f"the version DOI of {version} is recorded in `CITATION.cff` and\n`publication/DOI_STATUS.md`",
         f"the version DOI of {version} is `{doi}`"),
        (ROOT / "publication/DOI_STATUS.md", f"| {version} | recorded here by the release pipeline |", f"| {version} | `{doi}` |"),
        (ROOT / "publication/submission/title_page_REQUIRED.md",
         f"the version DOI\nof {version} is recorded in `publication/DOI_STATUS.md` and `CITATION.cff`",
         f"version DOI of {version}: **{doi}**"),
        (ROOT / "publication/submission/cover_letter.md",
         f"under the concept DOI {CONCEPT_DOI} (version {version}; the version DOI\nis recorded in the artifact metadata)",
         f"at Zenodo (version DOI {doi}, version {version}; concept DOI {CONCEPT_DOI})"),
    ]
    for path, old, new in edits:
        text = path.read_text(encoding="utf-8")
        if old not in text:
            _fail(f"insertion anchor not found in {path.relative_to(ROOT)}: {old[:60]!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
        print("inserted DOI in", path.relative_to(ROOT))
    status = ROOT / "publication/DOI_STATUS.md"
    text = status.read_text(encoding="utf-8")
    text = text.replace(f"Status: **version {version} prepared**", f"Status: **version {version} DOI reserved ({doi}); publication in progress**", 1)
    status.write_text(text, encoding="utf-8", newline="\n")
    preflight()
    release_status = json.loads((ROOT / "publication/RELEASE_STATUS.json").read_text(encoding="utf-8"))
    if release_status.get("version_doi") != doi or release_status.get("concept_doi") != CONCEPT_DOI:
        _fail(f"RELEASE_STATUS does not show version DOI {doi} and concept DOI {CONCEPT_DOI}: {release_status.get('version_doi')!r} / {release_status.get('concept_doi')!r}")
    print("RELEASE_STATUS: version DOI", doi, "concept DOI", CONCEPT_DOI)


# ---------------------------------------------------------------------------
# finalize
# ---------------------------------------------------------------------------


def _zip_dir(source: Path, target: Path, prefix: str) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            archive.write(path, f"{prefix}/{path.relative_to(source).as_posix()}")


def _git_checks(tag: str) -> None:
    if _out(["git", "status", "--porcelain"]):
        _fail("working tree is not clean; commit or stash before finalize")
    branch = _out(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch != SCIENCE_BRANCH:
        _fail(f"expected branch {SCIENCE_BRANCH}, on {branch}")
    if _out(["git", "tag", "-l", tag]):
        _fail(f"tag {tag} already exists; tags are immutable")
    _run(["git", "fetch", REMOTE, "--tags", "--quiet"])
    if _out(["git", "ls-remote", "--tags", REMOTE, tag]):
        _fail(f"tag {tag} already exists on {REMOTE}")
    head = _out(["git", "rev-parse", "HEAD"])
    remote_branch = _out(["git", "rev-parse", f"{REMOTE}/{SCIENCE_BRANCH}"])
    if _run(["git", "merge-base", "--is-ancestor", remote_branch, head], check=False, quiet=True).returncode != 0:
        _fail(f"{REMOTE}/{SCIENCE_BRANCH} is not an ancestor of HEAD; pull first (no force push)")
    remote_main = _out(["git", "rev-parse", f"{REMOTE}/{MAIN_BRANCH}"])
    if _run(["git", "merge-base", "--is-ancestor", remote_main, head], check=False, quiet=True).returncode != 0:
        _fail(f"{REMOTE}/{MAIN_BRANCH} has diverged from the release commit; main cannot be fast-forwarded (no force push)")


def _verify_source_zip(path: Path, tag: str) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        bad = [n for n in names if n.lower().endswith(".zip") or n.endswith("SHA256SUMS.txt") or n.endswith("zenodo_draft_state.json")]
        if bad:
            _fail(f"source ZIP contains release assets or draft state: {bad}")
        if not all(n.startswith(f"{tag}-source/") for n in names):
            _fail("source ZIP entries are not under the expected prefix")
        for n in names:
            if n.endswith((".py", ".md", ".txt", ".cff", ".json", ".toml", ".ps1", ".yml", ".tex", ".bib")):
                data = archive.read(n)
                for marker in TOKEN_MARKERS:
                    if marker.encode() in data and "release_pipeline.py" not in n:
                        _fail(f"token-like marker {marker!r} found in {n}")
    print("source ZIP verified:", path.name, f"({len(names)} entries)")


def finalize(doi: str) -> None:
    requests = _requests()
    version, tag = _version(), _tag()
    state_path = ROOT / "publication" / "zenodo_draft_state.json"
    if not state_path.exists():
        _fail("run reserve-doi first (publication/zenodo_draft_state.json missing)")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state["doi"] != doi:
        _fail(f"DOI mismatch: reserved {state['doi']} vs requested {doi}")
    release_status = json.loads((ROOT / "publication/RELEASE_STATUS.json").read_text(encoding="utf-8"))
    if release_status.get("version_doi") != doi:
        _fail("RELEASE_STATUS does not carry the version DOI; run insert-doi first")

    # Release commit (if there is anything to commit), then the fail-closed Git checks.
    if _out(["git", "status", "--porcelain"]):
        _run(["git", "add", "-A"])
        staged = _out(["git", "diff", "--cached", "--name-only"]).splitlines()
        forbidden = [f for f in staged if f.endswith(".zip") or f.endswith("SHA256SUMS.txt") or f.endswith("zenodo_draft_state.json")]
        if forbidden:
            _fail(f"release assets staged for commit: {forbidden}")
        _run(["git", "commit", "-q", "-m", f"Release {tag}: {_summary()} (version DOI {doi})\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01KWdy8kq2aH9hjFa8cMvd5D"])
    _git_checks(tag)
    head = _out(["git", "rev-parse", "HEAD"])

    # Assets are built outside the tree that the tag records.
    artifact_zip = ROOT / "publication" / f"{tag}.zip"
    _zip_dir(ROOT / "publication/artifact", artifact_zip, tag)
    (ROOT / "publication" / f"{tag}.zip.sha256").write_text(f"{_sha256(artifact_zip)}  {tag}.zip\n", encoding="utf-8", newline="\n")
    if _out(["git", "status", "--porcelain"]):
        _fail("building the assets dirtied the working tree; check .gitignore")

    _run(["git", "tag", "-a", tag, "-m", f"Paper 1.5 artifact {version} - observational indistinguishability and integrity blind regions; {_summary()}. Zenodo DOI {doi}."])
    tagged = _out(["git", "rev-list", "-n", "1", tag])
    if tagged != head:
        _fail("tag does not point at HEAD")
    with zipfile.ZipFile(artifact_zip) as archive:
        if any(n.lower().endswith(".zip") for n in archive.namelist()):
            _fail("artifact ZIP contains a nested ZIP")
    if _out(["git", "ls-tree", "-r", "--name-only", tag, "publication/"]).lower().count(".zip"):
        _fail("the tagged tree contains a ZIP under publication/")

    # Fast-forward main explicitly; never force.
    _run(["git", "branch", "-f", MAIN_BRANCH, head]) if _run(["git", "merge-base", "--is-ancestor", MAIN_BRANCH, head], check=False, quiet=True).returncode == 0 else _fail("local main is not an ancestor of HEAD")
    _run(["git", "push", REMOTE, f"{SCIENCE_BRANCH}:{SCIENCE_BRANCH}"])
    _run(["git", "push", REMOTE, f"{head}:refs/heads/{MAIN_BRANCH}"])  # fast-forward only: the remote rejects non-ff pushes
    _run(["git", "push", REMOTE, tag])
    _run(["git", "fetch", REMOTE, "--quiet"])
    for ref in (f"{REMOTE}/{SCIENCE_BRANCH}", f"{REMOTE}/{MAIN_BRANCH}"):
        if _out(["git", "rev-parse", ref]) != head:
            _fail(f"{ref} does not point at the release commit after push")
    if _out(["git", "ls-remote", "--tags", REMOTE, f"{tag}^{{}}"]).split()[0] != head:
        _fail("remote tag does not point at the release commit")
    print("branch, main and tag all point at", head)

    _run(["gh", "release", "create", tag, str(artifact_zip), str(ROOT / "publication" / f"{tag}.zip.sha256"), "--title", f"Paper 1.5 artifact {version} ({_summary()})", "--notes-file", str(ROOT / "publication/tdsc/RELEASE_NOTES.md")])

    source_zip = ROOT / "publication" / f"{tag}-source.zip"
    _run(["git", "archive", "--format=zip", f"--prefix={tag}-source/", "-o", str(source_zip), tag])
    _verify_source_zip(source_zip, tag)
    sums = ROOT / "publication" / "SHA256SUMS.txt"
    sums.write_text("".join(f"{_sha256(p)}  {p.name}\n" for p in (artifact_zip, source_zip)), encoding="utf-8", newline="\n")

    headers = {"Authorization": f"Bearer {_token()}"}
    draft = requests.get(state["draft_url"], headers=headers, timeout=60)
    draft.raise_for_status()
    bucket = draft.json()["links"]["bucket"]
    uploaded: dict[str, tuple[int, str]] = {}
    for path in (artifact_zip, source_zip, sums):
        with path.open("rb") as handle:
            up = requests.put(f"{bucket}/{path.name}", data=handle, headers=headers, timeout=3600)
            up.raise_for_status()
        uploaded[path.name] = (path.stat().st_size, _sha256(path))
        print("uploaded", path.name, uploaded[path.name])
    published = requests.post(f"{ZENODO_API}/deposit/depositions/{state['deposition_id']}/actions/publish", headers=headers, timeout=300)
    published.raise_for_status()
    record = published.json()
    print("published Zenodo record:", record.get("links", {}).get("record_html"), "DOI", record.get("doi"))

    # Post-publication checks: DOI, concept relation, files, sizes, hashes.
    time.sleep(10)
    rec = requests.get(f"{ZENODO_API}/records/{record['id']}", timeout=60)
    rec.raise_for_status()
    rec = rec.json()
    if rec.get("doi") != doi:
        _fail(f"published DOI {rec.get('doi')} != {doi}")
    if rec.get("conceptdoi") != CONCEPT_DOI:
        _fail(f"concept DOI {rec.get('conceptdoi')} != {CONCEPT_DOI}")
    files = {f["key"]: f for f in rec.get("files", [])}
    for name, (size, digest) in uploaded.items():
        if name not in files:
            _fail(f"published record lacks {name}")
        if int(files[name]["size"]) != size:
            _fail(f"published size mismatch for {name}: {files[name]['size']} != {size}")
        remote_md5 = files[name].get("checksum", "").replace("md5:", "")
        local_md5 = hashlib.md5((ROOT / "publication" / name).read_bytes()).hexdigest()
        if remote_md5 and remote_md5 != local_md5:
            _fail(f"published checksum mismatch for {name}")
    resolved = requests.get(f"https://doi.org/{doi}", allow_redirects=True, timeout=60)
    if resolved.status_code != 200:
        _fail(f"DOI {doi} does not resolve yet (HTTP {resolved.status_code})")
    summary = {"tag": tag, "commit": head, "doi": doi, "concept_doi": CONCEPT_DOI, "record": rec.get("links", {}).get("self_html"), "files": {k: {"bytes": v[0], "sha256": v[1]} for k, v in uploaded.items()}}
    (ROOT / "publication" / "zenodo_published_state.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
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
