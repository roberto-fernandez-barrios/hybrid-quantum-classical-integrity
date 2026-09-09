"""Manuscript consistency gates (release 1.3.5).

These tests read the LaTeX sources, the generated macro file and the active
documentation and fail closed on the editorial defects that the 1.3.1
correction removed, so that they cannot reappear silently:

* the abstract of the main article has 170--200 words after macro expansion;
* no active document carries the superseded hand-typed range ``88--95`` of the
  adaptive attacker's material retention (the generated range is 83--91 %);
* no sentence states that the executed Gate F has an exact level without the
  exchangeability premise, and no text says the experiment is exactly calibrated;
* no text claims that policy P3 guarantees a minimum detection power;
* the finite-shot statement of Proposition 7(iii) is never the universal
  ``false-alarm probability one'' of the earlier version;
* the trusted-regime interruption decomposition printed through the macros sums
  correctly (statistical holds + exact-reference blocks = total interruptions).
* verified bibliographic metadata and conservative prior-art positioning cannot
  silently regress.

The tests run on a fresh checkout without the derived evidence: they need
only the repository text files.
"""

from __future__ import annotations

import csv
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "publication/tdsc/main.tex"
SUPPLEMENT = ROOT / "publication/tdsc/supplement.tex"
MACROS = ROOT / "publication/tdsc/tables/policy_macros.tex"
REFERENCE_AUDITS = (
    ROOT / "publication/tdsc/reference_audit_v1.3.4.csv",
    ROOT / "publication/tdsc/reference_audit_v1.3.5_addendum.csv",
)

ACTIVE_DOCUMENTS = [
    "publication/tdsc/main.tex",
    "publication/tdsc/supplement.tex",
    "README.md",
    "REPRODUCIBILITY.md",
    "CHANGELOG.md",
    "LICENSING.md",
    "publication/RELEASE_STATUS.md",
    "publication/tdsc/README.md",
    "publication/tdsc/CLAIMS_TRACEABILITY.md",
    "publication/tdsc/SUPPLEMENT_README.md",
    "manuscript/ADVERSARY_MODEL.md",
    "manuscript/THREAT_MODEL_CARD.md",
    "manuscript/FORMAL_CORE.md",
    "manuscript/HSaaS_DEMONSTRATOR.md",
    "manuscript/METHODOLOGICAL_AMENDMENT_1.3.2.md",
    "manuscript/paper15_exact_statevector_validation.md",
    "manuscript/paper15_q1_gate1_result_summary.md",
    "manuscript/paper15_quantum_integrity_gate_summary.md",
    "manuscript/paper15_z_pauli_xz_equivalence_note.md",
    "CITATION.cff",
    ".zenodo.json",
]
ACTIVE_DOCUMENTS += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "publication/tdsc/tables").glob("*.tex"))]

FORMAL_DOCUMENTS = [
    "publication/tdsc/main.tex",
    "publication/tdsc/supplement.tex",
    "manuscript/FORMAL_CORE.md",
    "manuscript/THREAT_MODEL_CARD.md",
    "manuscript/ADVERSARY_MODEL.md",
]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _macros() -> dict[str, str]:
    values: dict[str, str] = {}
    for name, value in re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}", _read(MACROS.relative_to(ROOT).as_posix())):
        values[name] = value
    return values


def _expand(text: str, macros: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        return macros.get(name, match.group(0))

    return re.sub(r"\\([A-Za-z]+)\{\}|\\([A-Za-z]+)(?![A-Za-z])", lambda m: repl(type("M", (), {"group": lambda self, i: (m.group(1) or m.group(2)) if i == 1 else m.group(0)})()), text)


def abstract_words() -> list[str]:
    text = _read("publication/tdsc/main.tex")
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S)
    assert match, "abstract environment not found"
    body = match.group(1)
    body = _expand(body, _macros())
    body = re.sub(r"\\texttt\{([^}]*)\}", r"\1", body)
    body = re.sub(r"\$[^$]*\$", "X", body)  # every inline formula counts as one word
    body = body.replace("~", " ").replace("--", "-").replace("\\%", "%").replace("{}", "")
    body = re.sub(r"\\[A-Za-z]+", "", body)
    body = re.sub(r"[{}]", "", body)
    return [w for w in re.split(r"\s+", body.strip()) if w]


def _sentences(text: str) -> list[str]:
    # Sentence ends, bullet starts, table rows and blank lines all delimit a unit, so that a
    # Markdown list item never inherits the words of its neighbour.
    pieces = re.split(r"(?<=[.!?])\s+|\n(?=\s*[-*|])|\n\s*\n", text)
    return [re.sub(r"\s+", " ", piece) for piece in pieces if piece.strip()]


def _bib_entry(key: str) -> str:
    bib = _read("publication/tdsc/references.bib")
    match = re.search(rf"@[A-Za-z]+\{{{re.escape(key)},(.*?)(?=\n@|\Z)", bib, re.S)
    assert match, f"missing BibTeX entry {key}"
    return match.group(0)


def _citation_keys(text: str) -> set[str]:
    return {
        key.strip()
        for group in re.findall(r"\\cite\{([^}]*)\}", text)
        for key in group.split(",")
        if key.strip()
    }


def _bib_entries() -> dict[str, str]:
    bib = _read("publication/tdsc/references.bib")
    return {
        match.group(1): match.group(0)
        for match in re.finditer(r"@[A-Za-z]+\{([^,]+),(.*?)(?=\n@|\Z)", bib, re.S)
    }


def _bib_field(entry: str, field: str) -> str | None:
    match = re.search(rf"(?mi)^\s*{re.escape(field)}\s*=\s*\{{(.*?)\}}\s*,?\s*$", entry)
    return match.group(1).strip() if match else None


def _normalized_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = re.sub(r"\\[A-Za-z]+|[{}$\\]", "", value)
    return re.sub(r"[^a-z0-9]+", "", value.lower())


class TestAbstract:
    def test_abstract_has_170_to_200_words(self) -> None:
        words = abstract_words()
        assert 170 <= len(words) <= 200, f"abstract has {len(words)} words"

    def test_abstract_carries_the_required_elements(self) -> None:
        text = " ".join(abstract_words()).lower()
        for needle in ("indistinguishability", "minimum evidence granularity", "trusted aggregate", "item-aligned", "conformal", "exchangeability", "materially altered audit results", "adaptive", "ideal-statevector", "hardware claim"):
            assert needle in text, needle


class TestActiveNumbers:
    @pytest.mark.parametrize("rel", ACTIVE_DOCUMENTS)
    def test_no_superseded_retention_range(self, rel: str) -> None:
        text = _read(rel)
        assert not re.search(r"88\s*(?:--|–|-|to)\s*95", text), f"{rel} still carries the superseded 88-95 range"

    def test_generated_retention_range_is_83_91(self) -> None:
        macros = _macros()
        assert (macros["AdvMatRetentionMinPct"], macros["AdvMatRetentionMaxPct"]) == ("83", "91")

    def test_generated_gate_a_detection_ranges_are_regime_correct(self) -> None:
        macros = _macros()
        assert (macros["AdvDetCtrlIXMin"], macros["AdvDetCtrlIXMax"]) == ("0.99", "1.00")
        assert (macros["AdvDetCtrlIXFMin"], macros["AdvDetCtrlIXFMax"]) == ("0.96", "1.00")
        assert (macros["AdvDetCtrlIXFYMin"], macros["AdvDetCtrlIXFYMax"]) == ("0.95", "1.00")
        assert (macros["AdvDetCtrlHeadlineMin"], macros["AdvDetCtrlHeadlineMax"]) == ("0.96", "1.00")
        assert (macros["AdvDetAdaptHeadlineMin"], macros["AdvDetAdaptHeadlineMax"]) == ("0.01", "0.66")

    @pytest.mark.parametrize("rel", ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex"))
    def test_gate_a_headline_ranges_are_macro_driven(self, rel: str) -> None:
        text = _read(rel)
        assert "0.96--1.00" not in text and "0.01--0.66" not in text
        assert r"\AdvDetCtrlHeadlineMin--\AdvDetCtrlHeadlineMax" in text
        assert r"\AdvDetAdaptHeadlineMin--\AdvDetAdaptHeadlineMax" in text

    def test_trusted_interruption_decomposition_sums(self) -> None:
        macros = _macros()
        holds = int(macros["BenignHoldFamilyIXFYtrusted"].replace(",", ""))
        blocks = int(macros["BenignBlockFamilyIXFYtrusted"].replace(",", ""))
        total = int(macros["BenignInterruptFamilyIXFYtrusted"].replace(",", ""))
        assert (holds, blocks, total) == (544, 85, 629)
        assert holds + blocks == total
        assert macros["BenignHBFamilyIXFYtrusted"] == f"{total / 1200:.2f}"
        assert macros["BenignHBPctFamilyIXFYtrusted"] == str(round(100 * total / 1200))
        assert macros["TrustedGrossExactBlocks"] == "85"
        assert macros["TrustedExactOverlap"] == "46"
        assert macros["TrustedNetAdditional"] == "39"
        assert macros["TrustedNetAdditionalPct"] == "3.25"

    def test_main_text_uses_macros_for_the_headline_numbers(self) -> None:
        text = _read("publication/tdsc/main.tex")
        assert "\\AdvMatRetentionMinPct--\\AdvMatRetentionMaxPct" in text
        assert "\\BenignInterruptFamilyIXFYtrusted" in text
        for literal in ("about half of the near-null", "interrupts about half", "0.52 of benign"):
            assert literal not in text


class TestClaimWording:
    def test_minimum_evidence_is_declared_reference_relative(self) -> None:
        text = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        relevant = [
            sentence
            for sentence in _sentences(text)
            if re.search(r"minimum (?:evidence|external root|granularity)|root's minimum|the minimum is relative", sentence, re.I)
        ]
        assert relevant
        for sentence in relevant:
            assert re.search(r"declared reference (?:lattice|model)|relative to the declared reference", sentence, re.I), sentence

    def test_internal_paper_numbering_is_absent_from_submission_manuscript(self) -> None:
        corpus = "\n".join(_read(rel) for rel in ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex"))
        assert not re.search(r"(?:planned[ ~]+)?Paper[ ~]+(?:1\.5|2\.5)", corpus, re.I)

    def test_traceability_uses_current_adversary_table_number(self) -> None:
        trace = _read("publication/tdsc/CLAIMS_TRACEABILITY.md")
        assert "main Table 3" not in trace
        assert "main Table 1" in trace

    def test_table_one_heading_does_not_promise_perfect_identification(self) -> None:
        text = _read("publication/tdsc/main.tex")
        assert "Identifying regime" not in text
        assert "Least separating evidence in frozen design" in text

    def test_max_rank_attribution_is_explicit_and_non_novel(self) -> None:
        text = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "use the Max-Rank statistic of Timans et al. within a full-conformal family construction" in text
        assert "claim no novelty for the statistic or rule" in text

    def test_abstract_uses_aligned_sensitivity_not_original_gate_a_headline(self) -> None:
        text = _read("publication/tdsc/main.tex")
        abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S)
        assert abstract
        body = abstract.group(1)
        assert "geometry-aligned sensitivity" in body
        assert "AdvDetCtrl" not in body and "AdvDetAdapt" not in body

    def test_identity_and_clean_resample_estimands_are_separate(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        supplement = re.sub(r"\s+", " ", _read("publication/tdsc/supplement.tex"))
        for text in (main, supplement):
            assert "clean-resample false-action rate" in text
            assert "identity" in text and "exact" in text
        assert "not an identity false-positive rate" in supplement

    def test_no_unsupported_operational_calibration_language(self) -> None:
        corpus = re.sub(r"\s+", " ", "\n".join(_read(rel).lower() for rel in ACTIVE_DOCUMENTS))
        for forbidden in (
            "operationally calibrated",
            "calibration guarantees coverage",
            "guaranteed attack coverage",
            "deployment-calibrated false-positive rate",
        ):
            assert forbidden not in corpus
        assert "calibration controls clean-resample false actions but does not guarantee coverage" in corpus

    @pytest.mark.parametrize("rel", ACTIVE_DOCUMENTS)
    def test_no_exactly_calibrated_experiment(self, rel: str) -> None:
        text = _read(rel).lower()
        for phrase in ("experiment is exactly calibrated", "exactly calibrated", "is exactly at its level", "exact in the executed design"):
            assert phrase not in text, f"{rel}: {phrase!r}"

    @pytest.mark.parametrize("rel", FORMAL_DOCUMENTS + ["README.md", "REPRODUCIBILITY.md", "manuscript/METHODOLOGICAL_AMENDMENT_1.3.2.md", "publication/tdsc/CLAIMS_TRACEABILITY.md"])
    def test_exact_level_is_always_tied_to_exchangeability(self, rel: str) -> None:
        for sentence in _sentences(_read(rel)):
            low = sentence.lower()
            if re.search(r"exact(?:ly)?\s+(?:finite-sample\s+)?level", low) or "level is exact" in low or "exact level" in low:
                assert re.search(r"exchangeab|premise|stated assumption", low), f"{rel}: exact level stated without its premise: {sentence.strip()[:160]!r}"

    @pytest.mark.parametrize("rel", ACTIVE_DOCUMENTS)
    def test_no_minimum_power_claim_for_p3(self, rel: str) -> None:
        for sentence in _sentences(_read(rel)):
            low = sentence.lower()
            if "p3" in low and re.search(r"guarantee", low):
                assert re.search(r"no minimum|does not guarantee|guarantees no|no guarantee|not a guarantee|no promise", low), f"{rel}: P3 guarantee wording: {sentence.strip()[:160]!r}"
            assert "strict fail-closed" not in low, f"{rel}: superseded P3 name"

    @pytest.mark.parametrize("rel", FORMAL_DOCUMENTS)
    def test_prop7_never_claims_universal_false_alarm_one(self, rel: str) -> None:
        text = re.sub(r"\s+", " ", _read(rel))
        assert not re.search(r"false-alarm\s+probability\s+one", text), f"{rel}: universal FPR = 1 claim"
        assert not re.search(r"\\Pr\[\\hat K\s*=\s*K_0\]\s*=\s*0", text), f"{rel}: Pr[K_hat = K_0] = 0 claim"
        assert not re.search(r"Pr\[\\hat K = K_0\] = 0", text), f"{rel}: Pr[K_hat = K_0] = 0 claim"
        assert not re.search(r"never reproduc(?:e|ing) the exact kernel", text), f"{rel}: universal never-reproduces claim"

    def test_reference_taxonomy_is_named_consistently(self) -> None:
        main = _read("publication/tdsc/main.tex")
        flat = re.sub(r"\s+", " ", main)
        assert "statistically thresholded aggregate" in flat
        assert "protected clean same-item-set oracle" in flat
        assert "no deployed authentication mechanism is demonstrated" in flat
        assert "with no stored\nbaseline value" not in main
        assert "no stored baseline" not in flat
        assert "coverage-complete abstaining" in main
        for rel in ("manuscript/FORMAL_CORE.md", "publication/tdsc/supplement.tex"):
            text = re.sub(r"\s+", " ", _read(rel))
            assert "benchmark-protected" in text and "deployed authentication" in text, rel


class TestBibliographicIntegrity:
    def test_required_prior_art_is_present_and_cited(self) -> None:
        cited = _citation_keys(_read("publication/tdsc/main.tex"))
        for key in ("Hinder2025", "Timans2025", "Weder2021"):
            assert key in cited, key
            assert _bib_entry(key)

    def test_selective_prior_art_is_present_and_cited(self) -> None:
        cited = _citation_keys(_read("publication/tdsc/main.tex"))
        for key in ("Seto1998", "Pendlebury2019", "Birkholz2023"):
            assert key in cited, key
            assert _bib_entry(key)

    def test_bibliography_and_citations_are_bidirectionally_complete(self) -> None:
        bib = _read("publication/tdsc/references.bib")
        bib_keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
        cited = _citation_keys(_read("publication/tdsc/main.tex"))
        assert cited == bib_keys, {
            "uncited_bibliography_entries": sorted(bib_keys - cited),
            "missing_bibliography_entries": sorted(cited - bib_keys),
        }

    def test_published_versions_and_corrected_metadata(self) -> None:
        primer = _bib_entry("Ghosh2025")
        assert "Proceedings of the IEEE" in primer
        assert "10.1109/JPROC.2025.3630989" in primer
        assert "arXiv preprint" not in primer

        quantum_leak = _bib_entry("Lu2025")
        assert "Great Lakes Symposium" in quantum_leak
        assert "Chao Lu" in quantum_leak and "Esha Telang" in quantum_leak
        assert "SIGSAC" not in quantum_leak and "CCS" not in quantum_leak

        qemi = _bib_entry("Luo2026")
        assert "Lecture Notes in Computer Science" in qemi and "16504" in qemi
        assert "10.1007/978-3-032-22774-4_8" in qemi
        assert "arXiv preprint" not in qemi

        dbc = _bib_entry("Yamaguchi2023")
        assert "Masaomi Yamaguchi" in dbc and "Q-SE" in dbc
        assert "10.1109/Q-SE59154.2023.00010" in dbc
        assert "arXiv preprint" not in dbc

        qiskit = _bib_entry("JavadiAbhari2024")
        assert "Jay M. Gambetta" in qiskit

    def test_no_generic_priority_claim_for_adaptive_drift_evasion(self) -> None:
        corpus = re.sub(
            r"\s+",
            " ",
            "\n".join(
                _read(rel).lower()
                for rel in ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex")
            ),
        )
        for forbidden in (
            "first adaptive attacker",
            "first adaptive drift",
            "first monitor-aware",
            "novel monitor-aware attack",
            "novel adaptive drift",
            "new idea that an attacker models the detector",
        ):
            assert forbidden not in corpus, forbidden
        assert "without claiming priority for adaptive drift evasion" in corpus

    def test_vamp_positioning_recognizes_attacked_evaluation_artifacts(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "explicitly treats evaluation artifacts as authenticated assets" in main
        assert "may be poisoned or substituted" in main
        assert "not that evaluation data can be attacked" in main
        assert "claim-relative" in main and "trusted-reference granularity" in main

    def test_quantum_prior_art_positioning_is_fair(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "QProv records provider-independent provenance" in main
        assert "stronger here on QPU/hardware and runtime/provider evidence" in main
        assert "Our orthogonal contribution" in main

    def test_release_identity_is_v135_with_immutable_v134_predecessor(self) -> None:
        assert _read("VERSION").strip() == "1.3.5"
        citation = _read("CITATION.cff")
        status = _read("publication/RELEASE_STATUS.md")
        for value in ("1.3.5", "10.5281/zenodo.22678092", "10.5281/zenodo.22550852"):
            assert value in citation
            assert value in status
        assert "10.5281/zenodo.22672505" in citation

    def test_bibtex_has_no_duplicate_keys_or_dois(self) -> None:
        bib = _read("publication/tdsc/references.bib")
        keys = re.findall(r"@[A-Za-z]+\{([^,]+),", bib)
        assert len(keys) == len(set(keys)), "duplicate BibTeX key"
        dois = [doi.lower() for doi in re.findall(r"\bdoi\s*=\s*\{([^}]+)\}", bib, re.I)]
        assert len(dois) == len(set(dois)), "duplicate DOI"

    def test_tracked_main_pdf_is_within_page_budget(self) -> None:
        pdf = ROOT / "output/pdf/paper15_tdsc_submission.pdf"
        pdfinfo = shutil.which("pdfinfo")
        if not pdf.exists() or not pdfinfo:
            pytest.skip("tracked PDF or pdfinfo unavailable")
        out = subprocess.run(
            [pdfinfo, str(pdf)], capture_output=True, text=True, check=True
        ).stdout
        match = re.search(r"^Pages:\s+(\d+)$", out, re.M)
        assert match and int(match.group(1)) <= 12


class TestReferenceAudit:
    def test_audit_is_complete_verified_and_frozen_at_cutoff(self) -> None:
        rows = []
        for path in REFERENCE_AUDITS:
            with path.open(encoding="utf-8", newline="") as handle:
                rows.extend(csv.DictReader(handle))
        assert len(rows) == 62  # immutable v1.3.4 audit plus two bounded v1.3.5 clarifications
        assert sum(row["original_v1_3_3"] == "yes" for row in rows) == 58
        assert all(row["verified"] == "VERIFIED" for row in rows)
        assert all(row["cutoff_ok"] == "yes" for row in rows)
        assert all(row["primary_url"] for row in rows)

    def test_audited_bib_and_citations_have_the_same_keys(self) -> None:
        entries = _bib_entries()
        audited = set()
        for path in REFERENCE_AUDITS:
            with path.open(encoding="utf-8", newline="") as handle:
                audited.update(row["key"] for row in csv.DictReader(handle))
        cited = _citation_keys(_read("publication/tdsc/main.tex"))
        assert set(entries) == audited == cited

    def test_every_entry_has_author_title_and_year(self) -> None:
        for key, entry in _bib_entries().items():
            for field in ("author", "title", "year"):
                value = _bib_field(entry, field)
                assert value and value.strip(), f"{key}: missing {field}"

    def test_no_duplicate_doi_arxiv_or_normalized_title(self) -> None:
        entries = _bib_entries()
        dois = [value.lower() for entry in entries.values() if (value := _bib_field(entry, "doi"))]
        arxiv = [value.lower() for entry in entries.values() if (value := _bib_field(entry, "eprint"))]
        titles = [_normalized_title(_bib_field(entry, "title") or "") for entry in entries.values()]
        assert len(dois) == len(set(dois)), "duplicate DOI"
        assert len(arxiv) == len(set(arxiv)), "duplicate arXiv identifier"
        assert len(titles) == len(set(titles)), "duplicate normalized title"

    def test_known_bibliographic_corrections_cannot_regress(self) -> None:
        bib = _read("publication/tdsc/references.bib")
        for forbidden in (
            "David Koebler",
            "Lauren Zhang",
            "Aviral Garg",
            "Satrajit Kundu",
            "Yuan Shi",
            "Dmitri Volya",
            "Tianshu Zhang",
            "Nasser Alam",
            "Abdun Naser Mahmood",
        ):
            assert forbidden not in bib
        expected = {
            "Koebler2025": ("Alexander Koebler", "Thomas Decker", "Incremental Uncertainty-aware", "2188--2196"),
            "Ginart2022": ("Antonio A. Ginart", "Martin Jinye Zhang", "James Zou"),
            "Saki2022": ("Satwik Kundu",),
            "Shi2019": ("Yunong Shi", "1908.08963"),
            "SLSA2025": ("Version 1.2", "year         = {2025}", "24 November 2025"),
        }
        for key, snippets in expected.items():
            entry = _bib_entry(key)
            assert all(snippet in entry for snippet in snippets), key

    def test_companion_identifiers_have_the_right_resource_type(self) -> None:
        conditional = _bib_entry("FernandezBarrios2026Conditional")
        vbc = _bib_entry("FernandezBarrios2026VBC")
        certificates = _bib_entry("FernandezBarrios2026Certificates")
        assert "2609.02781" in conditional
        assert "2609.04388" in vbc and "22239106" not in vbc
        assert _bib_field(certificates, "doi") is None
        assert "related reproducibility artifact (software)" in certificates
        assert "21776862" in certificates

    def test_required_new_boundary_references_are_cited(self) -> None:
        cited = _citation_keys(_read("publication/tdsc/main.tex"))
        assert {"Barber2023", "Engelen2021"} <= cited


class TestPolicyTaxonomyInCode:
    def test_p3_class_string(self) -> None:
        from src.hsaas.policy import POLICY_CLASS

        strict = POLICY_CLASS["family_calibrated_strict"]
        assert "coverage-complete abstaining" in strict and "missing coverage" in strict and "no minimum-power guarantee" in strict


class TestV132ClosingGuards:
    def test_all_selected_sensor_references_have_compatible_semantics(self) -> None:
        from src.experiments.build_v132_amendment_evidence import sensor_reference_audit

        audit = sensor_reference_audit()
        assert len(audit) == 14
        class_a = audit[audit["compatible_reference_class"] == "A"]
        assert len(class_a) == 10
        assert (class_a["item_correspondence_used"] == "no").all()
        assert (class_a["same_batch_item_set"] == "yes").all()
        assert (class_a["protected_in_executed_harness"] == "yes").all()
        assert (class_a["deployed_authentication_demonstrated"] == "no").all()
        assert class_a["historical_or_statistical"].str.contains("statistical=yes").all()
        assert set(audit[audit["compatible_reference_class"] == "B"]["item_correspondence_used"]) == {"no"}
        assert set(audit[audit["compatible_reference_class"] == "C"]["item_correspondence_used"]) == {"yes"}

    @pytest.mark.parametrize("rel", ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex"))
    def test_corollary_numbering_is_contiguous(self, rel: str) -> None:
        numbers = [int(x) for x in re.findall(r"\\textbf\{Corollary\s+(\d+)", _read(rel))]
        assert numbers == [1, 2, 3], (rel, numbers)

    def test_adaptive_aggregate_and_strength_profile_macros(self) -> None:
        macros = _macros()
        assert (
            macros["AdvServedOverallAdaptFamilyIX"],
            macros["AdvServedOverallAdaptFamilyIXF"],
            macros["AdvServedOverallAdaptFamilyIXFY"],
        ) == ("0.39", "0.28", "0.29")
        assert (
            macros["AdvServedRateMSTwoPctIXFY"],
            macros["AdvServedRateMSFivePctIXFY"],
            macros["AdvServedRateMSTenPctIXFY"],
            macros["AdvServedRateSDTwoPctIXFY"],
            macros["AdvServedRateSDFivePctIXFY"],
            macros["AdvServedRateSDTenPctIXFY"],
        ) == ("0.90", "0.67", "0.46", "0.55", "0.36", "0.22")

    @pytest.mark.parametrize("rel", ACTIVE_DOCUMENTS)
    def test_iym_contains_nothing_phrase_is_retired(self, rel: str) -> None:
        assert "contains nothing" not in _read(rel).lower(), rel

    def test_iym_containment_and_residual_blind_count_are_explicit(self) -> None:
        macros = _macros()
        assert macros["ResidualBlindFamilyIYm"] == "5,450"
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "provides zero containment" in main
        assert r"\ResidualBlindFamilyIYm{}" in main

    def test_structural_materiality_endpoint_is_not_operational_threshold(self) -> None:
        for rel in ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex", "manuscript/FORMAL_CORE.md"):
            text = re.sub(r"\s+", " ", _read(rel)).lower()
            assert "structural-sensitivity endpoint" in text, rel
            assert "not an operational risk threshold" in text or "not a claim that every epsilon" in text or "not imply equal operational consequence" in text, rel

    def test_24000_are_policy_rows_not_independent_episodes(self) -> None:
        corpus = "\n".join(_read(rel) for rel in ACTIVE_DOCUMENTS)
        assert not re.search(r"24,?000\s+(?:independent\s+)?episodes", corpus, re.I)
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        supplement = re.sub(r"\s+", " ", _read("publication/tdsc/supplement.tex"))
        for text in (main, supplement):
            assert "24,000 policy rows derived from the frozen intervention grid" in text
            assert "environment/split clusters rather than at row level" in text

    def test_batch_and_trusted_denominators_are_different_estimands(self) -> None:
        for rel in ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex"):
            text = re.sub(r"\s+", " ", _read(rel))
            assert "12,000" in text and "1,200" in text
            assert "different" in text and "estimand" in text

    def test_unsafe_allow_is_never_a_network_event_claim(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex")).lower()
        assert "not necessarily changing the classifier's live prediction" in main
        assert "not malicious network events" in _read("publication/tdsc/tables/m_policy.tex").lower()
        corpus = "\n".join(_read(rel).lower() for rel in ACTIVE_DOCUMENTS)
        assert "unsafe network event" not in corpus

    def test_gate_d_policy_api_accepts_flags_not_clean_arrays(self) -> None:
        policy = _read("src/hsaas/policy.py")
        assert "union_fire" in policy and "family_fire" in policy and "exact_fire" in policy
        assert "X_te_f" not in policy and "y_te_f" not in policy
