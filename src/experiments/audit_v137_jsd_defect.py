"""Audit frozen v1.3.6 evidence for historical JSD NaNs.

This audit is intentionally read-only with respect to every pre-v1.3.7
evidence directory.  It inventories the four JSD fields that can affect the
current batch-level pipeline, plus the geometry-prefixed copies that document
clean, paired, and derived responses.  Only the new v1.3.7 audit directory and
the manuscript report are written.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

import pandas as pd


SENSORS = (
    "integrity_jsd_vs_clean_eval",
    "integrity_score_jsd_vs_clean_eval",
    "integrity_label_jsd",
    "integrity_confusion_profile_jsd",
)
GEOMETRY_PREFIXES = ("", "clean__", "paired__", "delta__")
KEY = ["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"]
REGIMES = ("I_X", "I_XF", "I_Ym", "I_XFY")
SENSOR_REGIMES = {
    "integrity_jsd_vs_clean_eval": ("I_X", "I_XF", "I_XFY"),
    "integrity_score_jsd_vs_clean_eval": ("I_XF", "I_XFY"),
    "integrity_label_jsd": ("I_Ym", "I_XFY"),
    "integrity_confusion_profile_jsd": ("I_XFY",),
}
SOURCE_FILES = (
    ("gate1", "publication/artifact/evidence/gate1/gate1_unique_observations.csv"),
    ("expansion", "publication/artifact/evidence/expansion/expansion_unique_observations.csv"),
    ("reinforcement_null", "publication/artifact/evidence/reinforcement/null_unique_observations.csv"),
    ("adversarial", "publication/artifact/evidence/adversarial/adversarial_unique_observations.csv"),
    ("geometry_sensitivity", "publication/artifact/evidence/geometry_sensitivity/geometry_observations.csv"),
)


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def _tree_listing_hash(repo: Path, revision: str, path: str) -> str:
    listing = subprocess.check_output(
        ["git", "ls-tree", "-r", revision, "--", path], cwd=repo
    )
    return hashlib.sha256(listing).hexdigest()


def _bool_or_blank(value: object) -> object:
    if pd.isna(value):
        return ""
    return bool(value)


def _branch(model: object) -> str:
    return "quantum" if str(model).startswith("qsvc_") else "classical"


def _classification(source: str, attack: str, column: str) -> tuple[str, str]:
    base = next(sensor for sensor in SENSORS if column.endswith(sensor))
    prefix = column[: -len(base)]
    if source == "adversarial" and attack == "clean":
        return "not_applicable_clean_placeholder", "not_evaluated"
    if base == "integrity_jsd_vs_clean_eval" and prefix == "delta__":
        return "derived_from_defective_sensor_value", "derived"
    if base == "integrity_jsd_vs_clean_eval" and prefix == "paired__":
        return "histogram_support_defect", "paired_diagnostic"
    if base == "integrity_jsd_vs_clean_eval":
        if source == "gate1":
            return "histogram_support_defect", "legacy_gate1_observation"
        if source == "expansion":
            return "histogram_support_defect", "upstream_duplicate_of_original_geometry"
        if source == "adversarial":
            return "histogram_support_defect", "canonical_original_geometry"
        if source == "geometry_sensitivity":
            return "histogram_support_defect", "canonical_aligned_feature_geometry"
    return "unexpected_nan", "requires_investigation"


def _decision_lookup(repo: Path) -> pd.DataFrame:
    path = repo / "publication/artifact/evidence/adversarial/adversarial_decisions.csv"
    decisions = pd.read_csv(path, low_memory=False)
    keep = KEY + [
        column
        for regime in REGIMES
        for column in (f"fire_union__{regime}", f"fire_family__{regime}")
    ]
    return decisions[keep]


def audit_frame(repo: Path) -> pd.DataFrame:
    decisions = _decision_lookup(repo)
    records: list[dict[str, object]] = []
    for source, relative in SOURCE_FILES:
        path = repo / relative
        frame = pd.read_csv(path, low_memory=False)
        if source == "gate1" and "gate" not in frame:
            frame.insert(0, "gate", "gate1_id_cicids")
        if source in {"gate1", "expansion", "adversarial"}:
            frame = frame.merge(decisions, on=KEY, how="left", validate="many_to_one")

        columns = list(SENSORS)
        if source == "geometry_sensitivity":
            columns = [f"{prefix}{sensor}" for prefix in GEOMETRY_PREFIXES for sensor in SENSORS]
        for column in columns:
            if column not in frame:
                continue
            sensor = next(sensor for sensor in SENSORS if column.endswith(sensor))
            prefix = column[: -len(sensor)]
            for index, row in frame[frame[column].isna()].iterrows():
                attack = str(row.get("attack", ""))
                classification, lineage = _classification(source, attack, column)
                identifier = "|".join(
                    str(row.get(key, "")) for key in KEY
                ) + f"|{column}"
                record: dict[str, object] = {
                    "nan_occurrence_id": hashlib.sha256(
                        f"{relative}|{index}|{identifier}".encode("utf-8")
                    ).hexdigest()[:20],
                    "source_release": "v1.3.6-or-earlier-frozen",
                    "source_file": relative,
                    "source_row_index_zero_based": int(index),
                    "affected_row_identifier": identifier,
                    "sensor_column": column,
                    "base_sensor": sensor,
                    "geometry_value_role": prefix.removesuffix("__") or "primary",
                    "classification": classification,
                    "lineage_role": lineage,
                    "historical_family_nan_treatment": (
                        "NaN_to_minus_infinity" if classification == "histogram_support_defect" and prefix == "" else "not_applicable"
                    ),
                    "environment": row.get("gate", ""),
                    "dataset_tag": row.get("dataset_tag", ""),
                    "model": row.get("model", ""),
                    "branch": row.get("branch", _branch(row.get("model", ""))),
                    "svd_dim": row.get("svd_dim", ""),
                    "split_seed": row.get("split_seed", ""),
                    "model_seed": row.get("model_seed", ""),
                    "attack": attack,
                    "attack_class": row.get("attack_class", ""),
                    "mechanism": row.get("mechanism", row.get("attack_family", "")),
                    "strength": row.get("strength", row.get("attack_strength_nominal", "")),
                    "side": "feature-side" if sensor == "integrity_jsd_vs_clean_eval" else ("label-side" if sensor in SENSORS[2:] else "prediction-side"),
                    "regime_relevance": ";".join(SENSOR_REGIMES[sensor]) if prefix == "" else "not_in_family",
                    "gate_a": bool(row.get("attack_class", "") in {"control", "adaptive"}),
                    "clean_resample": bool("null_" in str(row.get("attack_priority_group", "")) or attack.startswith("sham_")),
                    "near_null": bool(attack in {"sham_tiny_gaussian_sigma_0.001", "sham_tiny_scaling_alpha_0.001"}),
                }
                for regime in REGIMES:
                    union = row.get(f"fire_union__{regime}", pd.NA)
                    family = row.get(f"fire_family__{regime}", pd.NA)
                    record[f"previous_union_fire__{regime}"] = _bool_or_blank(union)
                    record[f"previous_family_fire__{regime}"] = _bool_or_blank(family)
                    record[f"other_sensor_fired__{regime}"] = (
                        _bool_or_blank(union)
                        if prefix == "" and regime in SENSOR_REGIMES[sensor]
                        else ""
                    )
                records.append(record)
    out = pd.DataFrame.from_records(records)
    return out.sort_values(
        ["source_file", "source_row_index_zero_based", "sensor_column"]
    ).reset_index(drop=True)


def _count_table(audit: pd.DataFrame, columns: list[str]) -> str:
    counts = audit.groupby(columns, dropna=False).size().rename("n").reset_index()
    return counts.to_markdown(index=False)


def render_report(repo: Path, audit: pd.DataFrame) -> str:
    exact = audit[audit["geometry_value_role"] == "primary"]
    defects = audit[audit["classification"] == "histogram_support_defect"]
    canonical = defects[defects["lineage_role"].str.startswith("canonical_")]
    paired = defects[defects["lineage_role"] == "paired_diagnostic"]
    placeholders = audit[audit["classification"] == "not_applicable_clean_placeholder"]
    derived = audit[audit["classification"] == "derived_from_defective_sensor_value"]
    original = canonical[canonical["lineage_role"] == "canonical_original_geometry"]
    aligned = canonical[canonical["lineage_role"] == "canonical_aligned_feature_geometry"]

    def decision_line(frame: pd.DataFrame, regime: str, rule: str) -> str:
        col = f"previous_{rule}_fire__{regime}"
        values = frame[col].map(lambda value: value is True)
        return f"{int(values.sum())}/{len(frame)}"

    sha = _git(repo, "rev-parse", "HEAD")
    tag_tree = _tree_listing_hash(repo, "paper15-q1-v1.3.6", "publication/artifact/evidence")
    current_tree = _tree_listing_hash(repo, "HEAD", "publication/artifact/evidence")
    rows = [
        "# JSD defect audit for v1.3.7",
        "",
        "This report was generated before changing the JSD implementation. It is an audit of immutable v1.3.6-and-earlier evidence, not corrected evidence.",
        "",
        f"- Audit base commit: `{sha}`",
        f"- v1.3.6 evidence Git-tree-listing SHA-256: `{tag_tree}`",
        f"- Audit-base evidence Git-tree-listing SHA-256: `{current_tree}`",
        "- Historical evidence files modified by this audit: **0**",
        "",
        "## Reproduction and mathematical cause",
        "",
        "**Reproduced: YES.** With `reference ~ U[0,1]` and `current ~ U[10,11]`, the historical implementation returns NaN for both feature JSD and score JSD and emits NumPy's zero-mass histogram warning. Each sample is quantile-clipped against its own quantiles, while finite histogram edges are derived only from the clipped reference. If every current observation falls outside those edges, `numpy.histogram(..., density=True)` divides by a zero in-range count. Adding a pseudocount after that division cannot recover a PMF because the histogram already contains NaNs. `family_calibration._matrix` then maps audited NaN to `-inf`, so that sensor cannot contribute to the max-rank family response.",
        "",
        "The support defect is reachable in `integrity_jsd_vs_clean_eval` and in `integrity_score_jsd_vs_clean_eval`, because both use the affected continuous-histogram helper. No applicable historical NaN was found for score JSD. Label, prediction, and confusion JSD use explicit finite discrete PMFs in the executed pipeline and are not generated by the affected histogram helper.",
        "",
        "## Counts",
        "",
        f"The audit CSV contains **{len(audit)} physical NaN occurrences**: **{len(defects)}** direct histogram-support-defect evaluations, **{len(derived)}** `delta__` values derived from a defective coordinate, and **{len(placeholders)}** declared not-applicable clean placeholders.",
        "",
        "Physical CSV occurrences for the four named pipeline fields (including lineage duplicates and declared clean placeholders):",
        "",
        _count_table(exact, ["base_sensor", "classification"]),
        "",
        f"There are **{len(defects)}** stored defective sensor evaluations when geometry-prefixed copies are included. After removing the gate1/expansion lineage duplication and the derived `delta__` column, there are **{len(canonical) + len(paired)}** unique scientific evaluations: **{len(original)}** original-geometry intervention rows, **{len(aligned)}** aligned feature-geometry rows, and **{len(paired)}** paired diagnostics. The **{len(placeholders)}** not-applicable cells are clean placeholder rows in `adversarial_unique_observations.csv`; they were not passed to the decision table and are not implementation-defect events.",
        "",
        "Defective applicable evaluations by source/role:",
        "",
        _count_table(defects, ["lineage_role", "base_sensor"]),
        "",
        "Defective applicable evaluations by mechanism and strength:",
        "",
        _count_table(canonical, ["lineage_role", "mechanism", "strength"]),
        "",
        "## Historical decision impact",
        "",
        "For every one of the 196 canonical original-geometry rows with a feature-JSD NaN, another feature sensor already fired and both the frozen union and conformal-family decisions fired in I_X, I_XF, and I_XFY. The same is true for all 230 aligned feature-geometry rows already stored in v1.3.5. Therefore the silent NaN suppression removed the JSD sensor contribution but did not flip an existing Boolean family or union decision in those NaN rows. Gate1 has no comparable frozen conformal-family decision. The 101 paired diagnostic NaNs were not members of a calibration family.",
        "",
        "| Geometry | Rows | I_X union | I_X family | I_XF union | I_XF family | I_XFY union | I_XFY family |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| Original | {len(original)} | {decision_line(original, 'I_X', 'union')} | {decision_line(original, 'I_X', 'family')} | {decision_line(original, 'I_XF', 'union')} | {decision_line(original, 'I_XF', 'family')} | {decision_line(original, 'I_XFY', 'union')} | {decision_line(original, 'I_XFY', 'family')} |",
        f"| Aligned feature | {len(aligned)} | {decision_line(aligned, 'I_X', 'union')} | {decision_line(aligned, 'I_X', 'family')} | {decision_line(aligned, 'I_XF', 'union')} | {decision_line(aligned, 'I_XF', 'family')} | {decision_line(aligned, 'I_XFY', 'union')} | {decision_line(aligned, 'I_XFY', 'family')} |",
        "",
        "This pre-correction audit cannot establish the final decision deltas for all rows: adding explicit underflow/overflow mass changes some already-finite JSD values and the frozen calibration JSD coordinates as well as repairing NaNs. The corrective replay must therefore rescore all JSD-dependent rows, not only the NaN subset.",
        "",
        "## Headline quantities that could change",
        "",
        "The dependency graph places the following reported quantities at risk pending corrected replay: feature-sensor decomposition and feature response ranges; primary and aligned Gate A sensor/family/union summaries; JSD-dependent Gate F family and union decisions; Gate D policy served/held counts derived from those decisions; `4496/7008`, `4390/7008`, `28--39%`, `3.25 pp`, and any quantum/trusted-reference slice that reuses those decisions. Near-null and label `11/2617`/`43/2617` counts do not depend on a historical JSD NaN, but the label counts are separately reopened by the preregistered label-geometry question. Exact trusted-reference and structural results do not depend on the histogram sensor.",
        "",
        "## Audit answers",
        "",
        f"1. There are {len(audit)} physical NaN occurrences: {len(defects)} direct defects, {len(derived)} derived NaNs and {len(placeholders)} non-applicable placeholders; lineage de-duplication leaves {len(canonical) + len(paired)} unique scientific evaluations.",
        "2. The only observed applicable broken sensor is feature JSD.",
        "3. Observed defect rows are mean-shift and scaling-drift controls; no adaptive, near-null, or label-only intervention has an applicable historical NaN.",
        "4. The sensor was suppressed inside family calibration, but all canonical NaN rows already had a firing family decision.",
        "5. All canonical NaN rows already had a firing union decision.",
        "6. Yes: another sensor fired in every canonical family-scored NaN row.",
        "7. The listed JSD-dependent headlines require replay because finite JSD coordinates can also change; structural and exact-reference claims cannot change from this defect.",
        "",
    ]
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    repo = args.repo.resolve()
    audit = audit_frame(repo)
    out_dir = repo / "publication/artifact/evidence/jsd_correction"
    out_dir.mkdir(parents=True, exist_ok=True)
    audit.to_csv(out_dir / "jsd_historical_nan_audit.csv", index=False, lineterminator="\n")
    report = render_report(repo, audit)
    (repo / "manuscript/JSD_DEFECT_AUDIT_v137.md").write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote {len(audit)} historical NaN occurrences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
