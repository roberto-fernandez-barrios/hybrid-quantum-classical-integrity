"""Build the adversarial evidence package for Paper 1.5 (artifact 1.3.0, Gate A).

Prespecified in ``manuscript/paper15_v13_prereg.md``. Gate A executes the
adaptive cluster-preserving perturbation (adversary class F5) of the two
feature-side drift mechanisms in the eight null-calibration environments, with
the executed mechanisms at the frozen strengths as matched controls, and
scores every observation with the same calibration draws, thresholds and rules
as Gate F (union of per-sensor rules, superseded 1.2.0 family rule, adopted
conformal family rule) and the same policy layer as Gate D.

The builder fails closed: a missing job, a design mismatch, a replay
inconsistency with the frozen expansion or a failed acceptance check aborts
without writing a manifest.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.experiments.build_q1_gate1_evidence import _sha256
from src.experiments.build_q1_policy_evidence import (
    ALPHA,
    BATCH_FOR_POLICY,
    BATCH_REGIME_NAMES,
    CELL,
    RULES,
    TAUS,
    TOL,
    _delta,
    _exact_fire,
    decision_metrics,
    score_frame,
)
from src.experiments.build_q1_reinforcement_evidence import (
    CALIBRATED_SENSORS,
    DIMS,
    EXACT_REFERENCE_SENSORS,
    EXPECTED_FILES_PER_GATE,
    MODEL_SEEDS,
    NULL_GATES,
    SPLIT_SEEDS,
    _load_dir,
)
from src.hsaas.policy import POLICIES, POLICY_CLASS, REGIMES as POLICY_REGIMES, Evidence, decide


N_F5_ATTACKS = 16 + 1  # six matched controls, ten adaptive conditions, clean
F5_STRENGTHS = (0.02, 0.05, 0.10, 0.25, 0.50)
MATCHED = {
    "mean_shift": ("mean_shift_pf_delta_{s:.3f}", "cluster_preserving_mean_shift_delta_{s:.3f}"),
    "scaling_drift": ("scaling_drift_alpha_{s:.3f}", "cluster_preserving_scaling_alpha_{s:.3f}"),
}
REPLAY_COLUMNS = ["bal_acc", "bal_acc_clean", "integrity_pred_disagreement"] + CALIBRATED_SENSORS
POLICY_REGIMES_EVALUATED = ("I_X", "I_XF", "I_XFY", "I_XFY_trusted")
POLICIES_EVALUATED = ("union_uncalibrated", "family_calibrated", "family_calibrated_strict")


def _rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _mechanism(attack: str) -> tuple[str, str, float]:
    """(class, mechanism, strength) of an attack tag of the paper_f5 suite."""

    strength = float(attack.rsplit("_", 1)[-1])
    if attack.startswith("cluster_preserving_mean_shift"):
        return "adaptive", "mean_shift", strength
    if attack.startswith("cluster_preserving_scaling"):
        return "adaptive", "scaling_drift", strength
    if attack.startswith("mean_shift_pf"):
        return "control", "mean_shift", strength
    if attack.startswith("scaling_drift"):
        return "control", "scaling_drift", strength
    raise ValueError(attack)


def load_gate_a(repo: Path) -> tuple[pd.DataFrame, list[dict[str, object]], list[dict[str, object]]]:
    frames, designs, inputs = [], [], []
    for spec in NULL_GATES:
        raw_dir = repo / f"results/raw/paper15_v13_f5_{spec['gate']}"
        frame, design, files = _load_dir(raw_dir, str(spec["gate"]), expected_files=EXPECTED_FILES_PER_GATE, expected_models=set(spec["models"]), expected_attacks=N_F5_ATTACKS, repo=repo)
        design["gate_family"] = "A_cluster_preserving"
        frames.append(frame)
        designs.append(design)
        inputs.extend(files)
    return pd.concat(frames, ignore_index=True, sort=False), designs, inputs


def replay_consistency(f5: pd.DataFrame, expansion: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """AC1: clean rows and matched controls reproduce the frozen expansion rows within 1e-9."""

    keys = ["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"]
    controls = f5[~f5["attack"].str.startswith("cluster_preserving")]
    merged = controls.merge(expansion[keys + REPLAY_COLUMNS], on=keys, how="left", suffixes=("", "__frozen"), validate="one_to_one")
    records = []
    ok = bool(merged[f"{REPLAY_COLUMNS[0]}__frozen"].notna().all())
    for col in REPLAY_COLUMNS:
        a = pd.to_numeric(merged[col], errors="coerce").to_numpy(dtype=float)
        b = pd.to_numeric(merged[f"{col}__frozen"], errors="coerce").to_numpy(dtype=float)
        both_nan = np.isnan(a) & np.isnan(b)
        diff = np.abs(a - b)
        diff[both_nan] = 0.0
        max_diff = float(np.nanmax(diff)) if len(diff) else 0.0
        n_missing = int(np.isnan(b).sum() - both_nan.sum())
        records.append({"column": col, "n_rows": int(len(merged)), "max_abs_difference": max_diff, "n_frozen_missing": n_missing, "within_1e-9": bool(max_diff <= 1e-9 and n_missing == 0)})
        ok = ok and bool(max_diff <= 1e-9 and n_missing == 0)
    return pd.DataFrame.from_records(records), ok


def score_gate_a(f5: pd.DataFrame, null: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    cal = null[null["attack_priority_group"] == "null_calibration"]
    thr = thresholds[thresholds["order_statistic_rank"] > 0].pivot_table(index=CELL, columns="sensor", values="threshold", aggfunc="first")
    parts = []
    intervened = f5[f5["attack"] != "clean"]
    for key, group in cal.groupby(CELL, sort=True):
        rows = intervened[(intervened["gate"] == key[0]) & (intervened["svd_dim"] == key[1]) & (intervened["model"] == key[2])]
        if len(rows) == 0:
            raise ValueError(f"no Gate A rows for calibrated cell {key}")
        calibration = {s: pd.to_numeric(group[s], errors="coerce").to_numpy(dtype=float) for s in CALIBRATED_SENSORS}
        cell_thr = {s: float(thr.loc[key, s]) for s in CALIBRATED_SENSORS}
        parts.append(score_frame(rows, calibration, cell_thr))
    scored = pd.concat(parts, ignore_index=True)
    if len(scored) != len(intervened):
        raise ValueError("scoring lost Gate A rows (an intervened row belongs to no calibrated cell)")
    scored["fire_exact"] = _exact_fire(scored).to_numpy()
    scored["delta_bal_acc"] = _delta(scored).to_numpy()
    meta = scored["attack"].apply(lambda a: pd.Series(_mechanism(a), index=["attack_class", "mechanism", "strength"]))
    return pd.concat([scored, meta], axis=1)


def build(repo: Path, out_dir: Path) -> None:
    reinforcement = repo / "results/paper_digest/paper15_v11_reinforcement"
    null_path = reinforcement / "null_unique_observations.csv"
    thr_path = reinforcement / "null_calibration_thresholds.csv"
    expansion_path = repo / "results/paper_digest/paper15_q1_expansion/expansion_unique_observations.csv"
    prereg = repo / "manuscript/paper15_v13_prereg.md"
    for p in (null_path, thr_path, expansion_path, prereg):
        if not p.is_file():
            raise FileNotFoundError(p)
    null = pd.read_csv(null_path, low_memory=False)
    thresholds = pd.read_csv(thr_path)
    expansion = pd.read_csv(expansion_path, low_memory=False)

    f5, designs, inputs = load_gate_a(repo)
    checks: dict[str, bool] = {}
    design_frame = pd.DataFrame.from_records(designs)
    checks["A0_all_240_jobs_complete_with_17_rows_per_cell"] = bool(design_frame["complete"].all() and len(design_frame) == 8 and int(f5.groupby(["gate", "svd_dim", "split_seed", "model_seed"]).ngroups) == 8 * len(DIMS) * len(SPLIT_SEEDS) * len(MODEL_SEEDS))
    replay, ac1 = replay_consistency(f5, expansion)
    checks["AC1_clean_and_matched_controls_reproduce_frozen_expansion"] = ac1

    scored = score_gate_a(f5, null, thresholds)
    adaptive = scored[scored["attack_class"] == "adaptive"]
    label_cols = ["integrity_label_prior_shift", "integrity_label_jsd", "label_flip_rate"]
    lab = adaptive[label_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs()
    checks["AC2_labels_untouched_on_adaptive_rows"] = bool((lab.to_numpy().max(initial=0.0) <= TOL))
    frozen_frac = pd.to_numeric(adaptive["atk_frozen_entry_fraction"], errors="coerce")
    checks["AC3_frozen_entry_fraction_recorded_on_every_adaptive_row"] = bool(frozen_frac.notna().all() and ((frozen_frac > 0) & (frozen_frac <= 1)).all())
    material = adaptive["delta_bal_acc"].abs() > TOL
    pred_change = pd.to_numeric(adaptive["integrity_pred_disagreement"], errors="coerce").fillna(0.0) > TOL
    checks["AC4_every_material_adaptive_row_has_a_prediction_change"] = bool((pred_change | ~material).all())

    # A1: detection per attack, regime, rule (pooled and per environment); controls alongside.
    def _rates(frame: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
        records = []
        for key, group in frame.groupby(group_cols, sort=True):
            key_tuple = key if isinstance(key, tuple) else (key,)
            base = dict(zip(group_cols, key_tuple, strict=True))
            first = group.iloc[0]
            base.update({"attack_class": first["attack_class"], "mechanism": first["mechanism"], "strength": float(first["strength"])})
            for regime in BATCH_REGIME_NAMES:
                for rule in RULES:
                    col = f"fire_{rule}__{regime}"
                    records.append({**base, "regime": regime, "rule": rule, "n": int(len(group)), "n_fire": int(group[col].sum()), "detection_rate": float(group[col].mean())})
            records.append({**base, "regime": "I_XFY_trusted", "rule": "exact", "n": int(len(group)), "n_fire": int(group["fire_exact"].sum()), "detection_rate": float(group["fire_exact"].mean())})
        return pd.DataFrame.from_records(records)

    det_pooled = _rates(scored.assign(all="all_environments"), ["all", "attack"])
    det_env = _rates(scored, ["gate", "attack"])
    det_model = _rates(scored.assign(branch=np.where(scored["model"] == "svc_rbf", "classical", "quantum")), ["branch", "attack"])

    # A2: materiality.
    mat_records = []
    for attack, group in scored.groupby("attack", sort=True):
        d = group["delta_bal_acc"].to_numpy(dtype=float)
        pc = pd.to_numeric(group["integrity_pred_disagreement"], errors="coerce").fillna(0.0).to_numpy(dtype=float) > TOL
        cls, mech, strength = _mechanism(attack)
        mat_records.append({
            "attack": attack, "attack_class": cls, "mechanism": mech, "strength": strength, "n": int(len(group)),
            "prediction_change_rate": float(pc.mean()), "mean_prediction_disagreement": float(pd.to_numeric(group["integrity_pred_disagreement"], errors="coerce").fillna(0.0).mean()),
            "material_fraction_tau0": float((np.abs(d) > TOL).mean()), "material_fraction_tau002": float((np.abs(d) > 0.02).mean()), "material_fraction_tau005": float((np.abs(d) > 0.05).mean()),
            "mean_signed_delta": float(np.mean(d)), "mean_abs_delta": float(np.mean(np.abs(d))), "raised_fraction": float((d < -TOL).mean()), "lowered_fraction": float((d > TOL).mean()),
            "mean_perturbed_entry_fraction": float(pd.to_numeric(group.get("atk_perturbed_entry_fraction"), errors="coerce").mean()) if "atk_perturbed_entry_fraction" in group else math.nan,
        })
    materiality = pd.DataFrame.from_records(mat_records)

    # A3: policy decisions on the adaptive rows (and controls) with the policy layer of Gate D.
    delta = scored["delta_bal_acc"].to_numpy(dtype=float)
    pol_records = []
    dec_cols = {}
    for regime in POLICY_REGIMES_EVALUATED:
        spec = POLICY_REGIMES[regime]
        batch = BATCH_FOR_POLICY[regime]
        union = scored[f"fire_union__{batch}"].to_numpy(dtype=bool)
        family = scored[f"fire_family__{batch}"].to_numpy(dtype=bool)
        exact = scored["fire_exact"].to_numpy(dtype=bool)
        for policy in POLICIES_EVALUATED:
            actions = np.asarray([
                decide(policy, spec, Evidence(bool(union[i]), bool(family[i]), (bool(exact[i]) if spec.trusted_reference else None))).action
                for i in range(len(scored))
            ])
            dec_cols[f"decision__{regime}__{policy}"] = actions
            for attack, idx in scored.groupby("attack", sort=True).indices.items():
                cls, mech, strength = _mechanism(attack)
                for tau in TAUS:
                    a = actions[idx]
                    dd = delta[idx]
                    mat = np.abs(dd) > (tau if tau > 0 else TOL)
                    nm = int(mat.sum())
                    pol_records.append({
                        "regime": regime, "policy": policy, "policy_class": POLICY_CLASS[policy], "tau": tau, "attack": attack, "attack_class": cls, "mechanism": mech, "strength": strength,
                        "n": int(len(idx)), "n_material": nm, "unsafe_allow": int(np.sum((a == "allow") & mat)), "true_hold": int(np.sum((a == "hold") & mat)), "true_block": int(np.sum((a == "block") & mat)),
                        "immaterial_allow": int(np.sum((a == "allow") & ~mat)), "integrity_only_hold_block": int(np.sum((a != "allow") & ~mat)),
                        "containment": (int(np.sum((a != "allow") & mat)) / nm) if nm else math.nan, "unsafe_allow_rate": (int(np.sum((a == "allow") & mat)) / nm) if nm else math.nan,
                    })
    policy_frame = pd.DataFrame.from_records(pol_records)
    decisions = pd.concat([scored[["gate", "svd_dim", "split_seed", "model_seed", "model", "attack", "attack_class", "mechanism", "strength", "delta_bal_acc", "fire_exact"] + [f"fire_{r}__{g}" for r in RULES for g in BATCH_REGIME_NAMES]].reset_index(drop=True), pd.DataFrame(dec_cols)], axis=1)

    # A4: evasion ratios at matched strengths.
    det_idx = det_pooled.set_index(["attack", "regime", "rule"])
    mat_idx = materiality.set_index("attack")
    ratio_records = []
    for mech, (ctrl_fmt, adapt_fmt) in MATCHED.items():
        for s in (0.02, 0.05, 0.10):
            ctrl, adapt = ctrl_fmt.format(s=s), adapt_fmt.format(s=s)
            for regime in BATCH_REGIME_NAMES:
                for rule in RULES:
                    dc = float(det_idx.loc[(ctrl, regime, rule), "detection_rate"])
                    da = float(det_idx.loc[(adapt, regime, rule), "detection_rate"])
                    ratio_records.append({"mechanism": mech, "strength": s, "regime": regime, "rule": rule, "detection_control": dc, "detection_adaptive": da, "detection_ratio_adaptive_over_control": (da / dc) if dc > 0 else math.nan,
                                          "material_control": float(mat_idx.loc[ctrl, "material_fraction_tau0"]), "material_adaptive": float(mat_idx.loc[adapt, "material_fraction_tau0"]),
                                          "material_ratio_adaptive_over_control": (float(mat_idx.loc[adapt, "material_fraction_tau0"]) / float(mat_idx.loc[ctrl, "material_fraction_tau0"])) if float(mat_idx.loc[ctrl, "material_fraction_tau0"]) > 0 else math.nan})
    ratios = pd.DataFrame.from_records(ratio_records)

    # A5: attacker budget.
    budget_records = []
    adaptive_b = adaptive.assign(branch=np.where(adaptive["model"] == "svc_rbf", "classical", "quantum"))
    for (gate, branch, dim), group in adaptive_b.groupby(["gate", "branch", "svd_dim"], sort=True):
        frac = pd.to_numeric(group["atk_perturbed_entry_fraction"], errors="coerce")
        rows_frozen = pd.to_numeric(group["atk_fully_frozen_row_fraction"], errors="coerce")
        budget_records.append({"gate": gate, "branch": branch, "svd_dim": int(dim), "n": int(len(group)), "perturbed_entry_fraction_mean": float(frac.mean()), "perturbed_entry_fraction_min": float(frac.min()), "perturbed_entry_fraction_max": float(frac.max()), "fully_frozen_row_fraction_mean": float(rows_frozen.mean())})
    budget = pd.DataFrame.from_records(budget_records)

    # Summary of the primary security endpoint (unsafe allows under P2 on adaptive rows).
    p2 = policy_frame[(policy_frame["policy"] == "family_calibrated") & (policy_frame["tau"] == 0.0) & (policy_frame["attack_class"] == "adaptive")]
    summary = p2.groupby(["regime"]).agg(n_adaptive=("n", "sum"), n_material=("n_material", "sum"), unsafe_allow=("unsafe_allow", "sum"), true_hold_block=("true_hold", "sum")).reset_index()
    summary["true_hold_block"] = p2.groupby("regime")[["true_hold", "true_block"]].sum().sum(axis=1).to_numpy()
    summary["unsafe_allow_rate"] = summary["unsafe_allow"] / summary["n_material"]

    keep = ["gate", "protocol", "dataset_tag", "svd_dim", "split_seed", "model_seed", "model", "attack", "attack_family", "attack_priority_group", "attack_class", "mechanism", "strength", "impact_bal_acc", "bal_acc", "bal_acc_clean", "delta_bal_acc"] + CALIBRATED_SENSORS + EXACT_REFERENCE_SENSORS + [c for c in scored.columns if c.startswith("atk_")]
    unique = scored[[c for c in keep if c in scored.columns]].reset_index(drop=True)
    clean_rows = f5[f5["attack"] == "clean"][[c for c in ["gate", "protocol", "dataset_tag", "svd_dim", "split_seed", "model_seed", "model", "attack", "bal_acc", "bal_acc_clean"] if c in f5.columns]]

    outputs = {
        "adversarial_gate_completeness.csv": design_frame,
        "adversarial_replay_consistency.csv": replay,
        "adversarial_unique_observations.csv": pd.concat([unique, clean_rows], ignore_index=True, sort=False),
        "adversarial_detection_pooled.csv": det_pooled,
        "adversarial_detection_by_environment.csv": det_env,
        "adversarial_detection_by_branch.csv": det_model,
        "adversarial_materiality.csv": materiality,
        "adversarial_policy_metrics.csv": policy_frame,
        "adversarial_decisions.csv": decisions,
        "adversarial_evasion_ratios.csv": ratios,
        "adversarial_budget.csv": budget,
        "adversarial_primary_endpoint.csv": summary,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"Acceptance checks failed; no manifest written: {failed}")
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(out_dir / name, index=False)
    manifest = {
        "analysis": "paper15_v13_adversarial",
        "artifact_version": "1.3.0",
        "status": "complete",
        "backend_filter": "qbexact_statevector",
        "preregistration": {"file": _rel(repo, prereg), "sha256": _sha256(prereg)},
        "gate_a": {
            "attack_class": "F5 adaptive cluster-preserving perturbation",
            "mechanisms": list(MATCHED),
            "strengths": list(F5_STRENGTHS),
            "cluster_rule": "entry frozen when at least ceil(0.05 n) rows (itself included, never fewer than two) lie within 0.01 batch standard deviations of it; constant features frozen",
            "matched_controls": "frozen paper_core mechanisms at 0.02/0.05/0.10 with identical tags and attack seeds",
            "environments": [str(s["gate"]) for s in NULL_GATES],
            "rules": list(RULES),
            "policies": list(POLICIES_EVALUATED),
            "alpha": ALPHA,
        },
        "acceptance_checks": checks,
        "gates": design_frame.to_dict(orient="records"),
        "input_files": [{"role": "null_draws", "path": _rel(repo, null_path), "sha256": _sha256(null_path)}, {"role": "thresholds", "path": _rel(repo, thr_path), "sha256": _sha256(thr_path)}, {"role": "expansion", "path": _rel(repo, expansion_path), "sha256": _sha256(expansion_path)}] + inputs,
        "outputs": {name: {"rows": int(len(frame)), "sha256": _sha256(out_dir / name)} for name, frame in outputs.items()},
    }
    (out_dir / "adversarial_evidence_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "acceptance_checks": checks, "outputs": len(outputs)}, indent=2))
    print(f"Wrote {len(outputs)} tables and manifest to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=Path("results/paper_digest/paper15_v13_adversarial"))
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.out_dir)


if __name__ == "__main__":
    main()
