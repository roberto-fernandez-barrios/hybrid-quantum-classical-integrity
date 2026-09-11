"""Manuscript consistency gates (release 1.3.8).

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
import inspect
import json
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
V137_MACROS = ROOT / "publication/tdsc/tables/v137_correction_macros.tex"
REFERENCE_AUDITS = (
    ROOT / "publication/tdsc/reference_audit_v1.3.4.csv",
    ROOT / "publication/tdsc/reference_audit_v1.3.5_addendum.csv",
    ROOT / "publication/tdsc/reference_audit_v1.3.6.csv",
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
    for path in (MACROS, V137_MACROS):
        for name, value in re.findall(
            r"\\(?:newcommand|renewcommand)\{\\([A-Za-z]+)\}\{([^}]*)\}",
            _read(path.relative_to(ROOT).as_posix()),
        ):
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
        for needle in ("claim-relative evidence/reference", "indistinguishability", "trusted same-batch scalar", "item-aligned", "343/2,700", "1,183/2,700", "conformal", "exchangeability", "adaptive", "ideal-statevector", "qpu"):
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
        assert (macros["AdvDetCtrlIXFYMin"], macros["AdvDetCtrlIXFYMax"]) == ("0.94", "1.00")
        assert (macros["AdvDetCtrlHeadlineMin"], macros["AdvDetCtrlHeadlineMax"]) == ("0.94", "1.00")
        assert (macros["AdvDetAdaptHeadlineMin"], macros["AdvDetAdaptHeadlineMax"]) == ("0.01", "0.65")

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
        assert (holds, blocks, total) == (532, 85, 617)
        assert holds + blocks == total
        assert macros["BenignHBFamilyIXFYtrusted"] == f"{total / 1200:.2f}"
        assert macros["BenignHBPctFamilyIXFYtrusted"] == str(round(100 * total / 1200))
        assert macros["TrustedGrossExactBlocks"] == "85"
        assert macros["TrustedExactOverlap"] == "44"
        assert macros["TrustedNetAdditional"] == "41"
        assert macros["TrustedNetAdditionalPct"] == "3.42"

    def test_main_text_uses_macros_for_the_headline_numbers(self) -> None:
        text = _read("publication/tdsc/main.tex")
        assert "\\AdvMatRetentionMinPct--\\AdvMatRetentionMaxPct" in text
        assert "\\BenignInterruptFamilyIXFYtrusted" in text
        for literal in ("about half of the near-null", "interrupts about half", "0.52 of benign"):
            assert literal not in text


class TestV138EditorialClosure:
    def test_aligned_label_geometry_is_primary_and_original_is_retained(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        aligned = "primary empirical interpretation of finite-batch label response uses the geometry-aligned construction"
        original = "original frozen benchmark geometry"
        assert aligned in main and original in main
        assert main.index(aligned) < main.index(original)
        assert r"\AlignedLabelFamilyFires{}/\AlignedLabelMaterialDen{} material interventions with the conformal family rule" in main
        assert r"\AlignedLabelUnionFires{}/\AlignedLabelMaterialDen{} with the uncorrected union" in main
        assert r"\BatchFamilyLabelFires{}/\NMaterialLabel{} conformal" in main
        assert r"\BatchUnionLabelFires{}/\NMaterialLabel{} union" in main
        assert "retained for release reproduction and comparison" in main
        assert "not the preferred estimate of statistical response under the clean-resample geometry" in main

    def test_structural_and_statistical_label_results_are_separate(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "aggregate-blind aligned rows exactly equal their paired-clean sensor and rule responses" in main
        assert "attack-only increment is zero; this is the structural result" in main
        assert "finite-batch miss, not structural blindness" in main

    def test_without_ks_ablation_is_in_main(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        for value in (
            "3,521/4,361", "4,008/4,462", "3,959/4,419",
            "10/650", "62/603", "62/576",
            "Sensor dependence is substantial and explicitly quantified",
            "KS stays because it was prespecified",
            "does not replace the primary family",
        ):
            assert value in main, value

    def test_disjoint_draw_wording_is_exact(self) -> None:
        files = [
            "publication/tdsc/main.tex",
            "publication/tdsc/supplement.tex",
            "src/experiments/build_q1_policy_evidence.py",
            "src/experiments/build_v137_correction_evidence.py",
            "src/experiments/make_q1_policy_tables.py",
            "src/experiments/make_q1_reinforcement_tables.py",
            "manuscript/paper15_v13_prereg.md",
            "manuscript/paper15_v13_result_summary.md",
            *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "publication/tdsc/tables").glob("*.tex"))],
        ]
        corpus = "\n".join(_read(rel).lower() for rel in files)
        for forbidden in ("12,000 disjoint clean draws", "12,000 disjoint evaluation draws", "disjoint clean evaluation draws"):
            assert forbidden not in corpus, forbidden
        assert "evaluation pools disjoint from the calibration pools" in corpus
        assert "draws within a pool may overlap" in corpus or "draws within each pool may overlap" in corpus

    def test_trusted_headlines_are_recomputed_from_manifested_policy(self) -> None:
        import pandas as pd
        from src.experiments.make_v137_tables import _correction_macros, _trusted_current_counts

        policy = pd.read_csv(
            ROOT / "publication/artifact/evidence/jsd_correction/jsd_primary_policy_effect.csv"
        )
        counts = _trusted_current_counts(policy)
        assert (
            counts["gross_exact_blocks"], counts["exact_overlap"],
            counts["net_additional"], round(float(counts["net_additional_pct"]), 2),
        ) == (85, 44, 41, 3.42)
        source = inspect.getsource(_correction_macros)
        for name, literal in (
            ("TrustedGrossExactBlocks", "85"),
            ("TrustedExactOverlap", "44"),
            ("TrustedNetAdditional", "41"),
            ("TrustedNetAdditionalPct", "3.42"),
        ):
            assert not re.search(rf'_renew\("{name}",\s*"{re.escape(literal)}"\)', source)

    def test_release_status_separates_historical_and_current_counts(self) -> None:
        text = _read("publication/RELEASE_STATUS.md")
        status = json.loads(_read("publication/RELEASE_STATUS.json"))
        assert "## Historical v1.3.2/v1.3.6 quantities" in text
        assert "## Current v1.3.7/v1.3.8 corrected quantities" in text
        counts = status["primary_counts"]
        assert (
            counts["current_v137_v138_gross_exact_blocks"],
            counts["current_v137_v138_corrected_batch_interruptions"],
            counts["current_v137_v138_trusted_total_interruptions"],
            counts["current_v137_v138_exact_overlap"],
            counts["current_v137_v138_net_additional"],
            counts["current_v137_v138_net_additional_basis_points"],
        ) == (85, 576, 617, 44, 41, 342)

    def test_label_headline_formatting_is_unambiguous(self) -> None:
        macros = _macros()
        assert macros["AlignedLabelMaterialDen"] == "2,700"
        assert macros["AlignedLabelUnionFires"] == "1,183"
        assert macros["AlignedLabelSeparableDen"] == "2,836"
        assert macros["AlignedLabelSeparableUnionFires"] == "1,204"
        corpus = "\n".join(_read(rel) for rel in ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex"))
        for pattern in (r"11\s*(?:--|–)\s*43", r"343\s*(?:--|–)\s*1,?183", r"AlignedLabelFamilyFires\{\}\s*--"):
            assert not re.search(pattern, corpus)

    def test_executed_design_does_not_validate_exchangeability_guarantee(self) -> None:
        corpus = re.sub(
            r"\s+", " ",
            "\n".join(_read(rel).lower() for rel in ("publication/tdsc/main.tex", "publication/tdsc/supplement.tex")),
        )
        for forbidden in ("validated 5% guarantee", "validates the exchangeability guarantee", "validation of the theorem"):
            assert forbidden not in corpus
        assert "executed rates are descriptive" in corpus or "executed false-action rates are descriptive" in corpus

    def test_no_stale_public_release_identity(self) -> None:
        assert _read("VERSION").strip() == "1.3.8"
        assert _read("publication/tdsc/VERSION").strip() == "1.3.8-tdsc"
        readme = _read("README.md")
        assert "Current release | [Version 1.3.8]" in readme
        assert "Immutable predecessor | [Zenodo version 1.3.7]" in readme


class TestClaimWording:
    def test_minimum_evidence_is_declared_reference_relative(self) -> None:
        text = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "claim-relative minimum evidence granularity" not in text
        assert "minimum number of bytes" not in text
        assert "minimum commitment size" not in text
        assert "minimum over every possible audit architecture" in text

    def test_claim_headline_uses_sufficiency_and_necessity(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "Evidence sufficiency and necessity are claim-relative within the declared reference lattice" in main
        assert "claim-relative minimum evidence granularity" not in main

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
        assert "geometry-aligned construction" in body
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
        assert "sensor-coverage-complete" in main
        for rel in ("manuscript/FORMAL_CORE.md", "publication/tdsc/supplement.tex"):
            text = re.sub(r"\s+", " ", _read(rel))
            assert "benchmark-protected" in text and "deployed authentication" in text, rel


class TestV136FormalEditorialGuards:
    def test_proposition4_is_pathwise_and_does_not_equate_distinct_rates(self) -> None:
        for rel in (
            "publication/tdsc/main.tex",
            "publication/tdsc/supplement.tex",
            "manuscript/FORMAL_CORE.md",
        ):
            text = re.sub(r"\s+", " ", _read(rel))
            low = text.lower()
            assert "pathwise" in low, rel
            assert "does not in general imply equality with a false-action rate" in low, rel
            for forbidden in (
                "detection rate equals the false-alarm rate",
                "detection rate equals the false-action rate",
                "blind attack fires at the false-alarm rate",
                "over any design the calibrated detection rate",
                "same as fpr",
            ):
                assert forbidden not in low, (rel, forbidden)

    def test_corollary1_keeps_the_declared_kernel_dependency(self) -> None:
        for rel in ("publication/tdsc/supplement.tex", "manuscript/FORMAL_CORE.md"):
            text = re.sub(r"\s+", " ", _read(rel))
            assert r"\hat y=f(\tilde X,K_{\mathrm{obs}})" in text or r"\hat y = f(\tilde X,K_{\mathrm{obs}})" in text, rel
            for primitive in ("$X$", "$P$", "$C$", "$E$", "$\\xi$", "$g$", "$f$"):
                assert primitive in text, (rel, primitive)
            assert r"\hat y=f(\tilde X)$" not in text
            assert r"\hat y = f(\tilde X)$" not in text

    def test_claim_relative_r0_m0_and_level_c_distinction_is_explicit(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "trusted exact same-batch claim reference" in main
        assert "$R_0=R(s_0)$ detects exactly every $R(s_a)\\ne R_0$" in main
        assert "$M_0=M(s_0)$ detects every violation of aggregate integrity" in main
        assert "item identity needs level C" in main
        assert "aligned $y_0$ detects every non-identity relabeling" in main

    def test_minimum_claims_remain_bounded_to_the_declared_lattice(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "counterexample necessity are claim-relative within the declared reference lattice" in main
        assert "minimality statement is not over every encoding or audit architecture" in main
        assert "minimum over every possible audit architecture" in main
        assert "neither a deployed protocol nor" in main

    def test_main_has_no_unnecessary_artifact_version_archaeology(self) -> None:
        main = _read("publication/tdsc/main.tex").lower()
        for forbidden in (
            "frozen evidence of artifact 1.3.0",
            "preregistered in artifact 1.1.0",
            "amendment a2",
            "the 1.2.0 rule was wrong",
            "superseded 1.2.0",
        ):
            assert forbidden not in main, forbidden

    def test_batch_size_and_structural_statistical_scope_is_explicit(self) -> None:
        main = re.sub(r"\s+", " ", _read("publication/tdsc/main.tex"))
        assert "Structural blind regions are independent of the number of rows" in main
        assert r"\BatchFamilyLabelFires{}/\NMaterialLabel{} conformal" in main
        assert r"\BatchUnionLabelFires{}/\NMaterialLabel{} union" in main
        assert "finite-design results, not power bounds" in main
        assert "batch size is confounded with environment and null behavior" in main

    def test_quantum_heading_and_scope_are_unambiguous(self) -> None:
        supplement = re.sub(r"\s+", " ", _read("publication/tdsc/supplement.tex"))
        assert "Anchored kernel comparison" in supplement
        assert "165 design cells" in supplement
        assert "raw estimated/observed kernel before any downstream PSD-repair" in supplement

    def test_clean_ba_table_is_derived_from_frozen_evidence(self) -> None:
        evidence = ROOT / "publication/artifact/evidence/expansion/expansion_unique_observations.csv"
        rows = [row for row in csv.DictReader(evidence.open(encoding="utf-8", newline="")) if row["attack_is_clean"] == "1"]
        by_split: dict[tuple[str, str], list[float]] = {}
        for row in rows:
            by_split.setdefault((row["gate"], row["split_seed"]), []).append(float(row["bal_acc_clean"]))
        cluster_means = {(gate, seed): sum(values) / len(values) for (gate, seed), values in by_split.items()}
        expected = {
            "gate2_id_256": "0.762 [0.756, 0.766]",
            "gate5a_id_unsw": "0.766 [0.738, 0.800]",
            "gate5b_id_ton_iot": "0.752 [0.716, 0.807]",
            "gate3a_ood_tue_wed": "0.492 [0.480, 0.520]",
            "gate3b_ood_tue_fri_portscan": "0.590 [0.565, 0.615]",
            "gate3c_ood_wed_thu_webattacks": "0.483 [0.454, 0.518]",
            "gate3d_ood_wed_fri_morning": "0.459 [0.431, 0.493]",
            "gate6_ood_unsw": "0.759 [0.743, 0.775]",
        }
        table = _read("publication/tdsc/tables/s_clean_by_environment.tex")
        for gate, rendered in expected.items():
            values = [value for (row_gate, _), value in cluster_means.items() if row_gate == gate]
            actual = f"{sum(values) / len(values):.3f} [{min(values):.3f}, {max(values):.3f}]"
            assert actual == rendered
            assert rendered in table

    def test_release_status_count_matches_pytest_collection(self) -> None:
        status = __import__("json").loads(_read("publication/RELEASE_STATUS.json"))
        proc = subprocess.run(
            [__import__("sys").executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "tests"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        match = re.search(r"(\d+) tests? collected", proc.stdout + proc.stderr)
        assert match and status["tests_collected"] == int(match.group(1))

    def test_no_stale_paper_hais_path_is_tracked(self) -> None:
        stale_checkout_name = "paper_" + "HAIS"
        proc = subprocess.run(
            ["git", "grep", "-I", "-n", stale_checkout_name],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 1, proc.stdout


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

    def test_release_identity_is_v138_with_immutable_v137_predecessor(self) -> None:
        assert _read("VERSION").strip() == "1.3.8"
        citation = _read("CITATION.cff")
        for value in ("1.3.8", "10.5281/zenodo.22550852"):
            assert value in citation
        assert "10.5281/zenodo.22698329" in citation

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
        assert len(rows) == 65  # 64 included references plus one verified-not-added decision
        assert sum(row["original_v1_3_3"] == "yes" for row in rows) == 58
        assert all(row["verified"] == "VERIFIED" for row in rows)
        assert all(row["cutoff_ok"] == "yes" for row in rows)
        assert all(row["primary_url"] for row in rows)
        assert sum(row["action"] == "verified-not-added" for row in rows) == 1

    def test_audited_bib_and_citations_have_the_same_keys(self) -> None:
        entries = _bib_entries()
        audited = set()
        for path in REFERENCE_AUDITS:
            with path.open(encoding="utf-8", newline="") as handle:
                audited.update(
                    row["key"]
                    for row in csv.DictReader(handle)
                    if row["action"] != "verified-not-added"
                )
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
        assert "software artifact, not the article" in certificates
        assert "21776862" in certificates

    def test_required_new_boundary_references_are_cited(self) -> None:
        cited = _citation_keys(_read("publication/tdsc/main.tex"))
        assert {
            "Barber2023",
            "Engelen2021",
            "Bensoussan2026Taxonomy",
            "Bensoussan2026Squeeziness",
        } <= cited
        assert "NoiseFingerprints2026" not in cited


class TestPolicyTaxonomyInCode:
    def test_p3_class_string(self) -> None:
        from src.hsaas.policy import POLICY_CLASS

        strict = POLICY_CLASS["family_calibrated_strict"]
        assert "sensor-coverage-complete" in strict and "missing coverage" in strict and "no minimum-power guarantee" in strict


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
        ) == ("0.39", "0.27", "0.29")
        assert (
            macros["AdvServedRateMSTwoPctIXFY"],
            macros["AdvServedRateMSFivePctIXFY"],
            macros["AdvServedRateMSTenPctIXFY"],
            macros["AdvServedRateSDTwoPctIXFY"],
            macros["AdvServedRateSDFivePctIXFY"],
            macros["AdvServedRateSDTenPctIXFY"],
        ) == ("0.91", "0.67", "0.43", "0.55", "0.36", "0.24")

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
