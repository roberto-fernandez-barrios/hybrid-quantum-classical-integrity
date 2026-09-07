"""Manuscript consistency gates (artifact 1.3.1).

These tests read the LaTeX sources, the generated macro file and the active
documentation and fail closed on the editorial defects that the 1.3.1
correction removed, so that they cannot reappear silently:

* the abstract of the main article has at most 250 words after macro expansion;
* no active document carries the superseded hand-typed range ``88--95`` of the
  adaptive attacker's material retention (the generated range is 83--91 %);
* no sentence states that the executed Gate F has an exact level without the
  exchangeability premise, and no text says the experiment is exactly calibrated;
* no text claims that policy P3 guarantees a minimum detection power;
* the finite-shot statement of Proposition 7(iii) is never the universal
  ``false-alarm probability one'' of the earlier version;
* the trusted-regime interruption decomposition printed through the macros sums
  correctly (statistical holds + exact-reference blocks = total interruptions).

The tests run on a fresh checkout without the derived evidence: they need
only the repository text files.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "publication/tdsc/main.tex"
SUPPLEMENT = ROOT / "publication/tdsc/supplement.tex"
MACROS = ROOT / "publication/tdsc/tables/policy_macros.tex"

ACTIVE_DOCUMENTS = [
    "publication/tdsc/main.tex",
    "publication/tdsc/supplement.tex",
    "README.md",
    "publication/RELEASE_NOTES.md",
    "publication/tdsc/RELEASE_NOTES.md",
    "publication/tdsc/README.md",
    "publication/tdsc/CLAIMS_TRACEABILITY.md",
    "publication/tdsc/SUPPLEMENT_README.md",
    "publication/submission/cover_letter.md",
    "publication/submission/highlights.txt",
    "publication/submission/title_page_REQUIRED.md",
    "manuscript/ADVERSARY_MODEL.md",
    "manuscript/THREAT_MODEL_CARD.md",
    "manuscript/FORMAL_CORE.md",
    "manuscript/HSaaS_DEMONSTRATOR.md",
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


class TestAbstract:
    def test_abstract_has_at_most_250_words(self) -> None:
        words = abstract_words()
        assert 150 <= len(words) <= 250, f"abstract has {len(words)} words"

    def test_abstract_carries_the_required_elements(self) -> None:
        text = " ".join(abstract_words()).lower()
        for needle in ("indistinguishability", "information set", "trusted references", "evaluation-label", "aggregate", "item-aligned", "conformal", "exchangeability", "allow/hold/block", "adaptive attacker", "simulator gate"):
            assert needle in text, needle


class TestActiveNumbers:
    @pytest.mark.parametrize("rel", ACTIVE_DOCUMENTS)
    def test_no_superseded_retention_range(self, rel: str) -> None:
        text = _read(rel)
        assert not re.search(r"88\s*(?:--|–|-|to)\s*95", text), f"{rel} still carries the superseded 88-95 range"

    def test_generated_retention_range_is_83_91(self) -> None:
        macros = _macros()
        assert (macros["AdvMatRetentionMinPct"], macros["AdvMatRetentionMaxPct"]) == ("83", "91")

    def test_trusted_interruption_decomposition_sums(self) -> None:
        macros = _macros()
        holds = int(macros["BenignHoldFamilyIXFYtrusted"].replace(",", ""))
        blocks = int(macros["BenignBlockFamilyIXFYtrusted"].replace(",", ""))
        total = int(macros["BenignInterruptFamilyIXFYtrusted"].replace(",", ""))
        assert (holds, blocks, total) == (544, 85, 629)
        assert holds + blocks == total
        assert macros["BenignHBFamilyIXFYtrusted"] == f"{total / 1200:.2f}"
        assert macros["BenignHBPctFamilyIXFYtrusted"] == str(round(100 * total / 1200))

    def test_main_text_uses_macros_for_the_headline_numbers(self) -> None:
        text = _read("publication/tdsc/main.tex")
        assert "\\AdvMatRetentionMinPct--\\AdvMatRetentionMaxPct" in text
        assert "\\BenignInterruptFamilyIXFYtrusted" in text
        for literal in ("about half of the near-null", "interrupts about half", "0.52 of benign"):
            assert literal not in text


class TestClaimWording:
    @pytest.mark.parametrize("rel", ACTIVE_DOCUMENTS)
    def test_no_exactly_calibrated_experiment(self, rel: str) -> None:
        text = _read(rel).lower()
        for phrase in ("experiment is exactly calibrated", "exactly calibrated", "is exactly at its level", "exact in the executed design"):
            assert phrase not in text, f"{rel}: {phrase!r}"

    @pytest.mark.parametrize("rel", FORMAL_DOCUMENTS + ["README.md", "publication/submission/cover_letter.md", "publication/submission/highlights.txt", "publication/tdsc/CLAIMS_TRACEABILITY.md"])
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
        assert "statistical or\nhistorical reference" in main or "statistical or historical reference" in re.sub(r"\s+", " ", main)
        assert "with no stored\nbaseline value" not in main
        assert "no stored baseline" not in re.sub(r"\s+", " ", main)
        assert "coverage-complete abstaining" in main
        for rel in ("manuscript/FORMAL_CORE.md", "publication/tdsc/supplement.tex"):
            assert "no authenticated value of the same batch" in re.sub(r"\s+", " ", _read(rel)), rel


class TestPolicyTaxonomyInCode:
    def test_p3_class_string(self) -> None:
        from src.hsaas.policy import POLICY_CLASS

        strict = POLICY_CLASS["family_calibrated_strict"]
        assert "coverage-complete abstaining" in strict and "missing coverage" in strict and "no minimum-power guarantee" in strict
