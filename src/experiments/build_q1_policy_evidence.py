"""Build the policy-level evidence package for Paper 1.5 (artifact 1.2.0).

Two prespecified gates (``manuscript/paper15_v12_policy_prereg.md``), both
computed from frozen 1.1.1 outputs without re-executing any kernel or draw:

Gate F  family-wise (policy-level) calibration of each batch-level information
        regime from the existing calibration draws, evaluated on the disjoint
        evaluation draws and on the frozen ``paper_core`` interventions, side by
        side with the uncalibrated union rule of artifact 1.1.0;
Gate D  end-to-end ``allow/hold/block`` evaluation of four policies over five
        information regimes on the same frozen observations, with the unsafe
        allow count as primary endpoint, plus the composition with the six
        frozen HSaaS contract envelopes and the counterexample witnesses of the
        formal section.

The builder fails closed: any failed consistency check aborts without writing
a manifest. Family thresholds are computed from calibration draws only.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.experiments.build_q1_gate1_evidence import _mean_ci, _sha256
from src.experiments.build_q1_reinforcement_evidence import (
    CALIBRATED_SENSORS,
    EXACT_ITEM_ALIGNED_SENSORS,
    NULL_GATES,
    REGIMES as BATCH_REGIMES,
    SPLIT_SEEDS,
    _order_statistic_rank,
)
from src.hsaas.policy import BOUNDARIES, POLICIES, REGIMES as POLICY_REGIMES, Decision, Evidence, compose, decide, unverified_boundaries
from src.integrity.family_calibration import family_scores, family_threshold, rank_scores


ALPHA = 0.05
TOL = 1e-12
N_CAL_EXPECTED = 200
N_EVAL_EXPECTED = 200
CELL = ["gate", "svd_dim", "model"]
TAUS = (0.0, 0.02, 0.05)
RULES = ("union", "family")
BATCH_REGIME_NAMES = tuple(BATCH_REGIMES)  # I_X, I_XF, I_Ym, I_XFY
POLICY_REGIME_NAMES = tuple(POLICY_REGIMES)  # + I_XFY_trusted
BATCH_FOR_POLICY = {r: (r if r in BATCH_REGIMES else "I_XFY") for r in POLICY_REGIME_NAMES}
NEAR_NULL_SHAMS = ("sham_tiny_gaussian_sigma_0.001", "sham_tiny_scaling_alpha_0.001")

# Structural blind sets by construction (prereg): rows whose view under the regime
# is identical to the reference view.
STRUCTURAL_BLIND = {
    "I_X": lambda f: f["attack_family"].eq("target_shift"),
    "I_XF": lambda f: f["attack_family"].eq("target_shift"),
    "I_Ym": lambda f: f["attack_family"].ne("target_shift") | f["attack"].str.contains("prior_preserving", regex=False),
    "I_XFY": lambda f: pd.Series(False, index=f.index),
    "I_XFY_trusted": lambda f: pd.Series(False, index=f.index),
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load(repo: Path) -> dict[str, object]:
    reinforcement = repo / "results/paper_digest/paper15_v11_reinforcement"
    paths = {
        "null": reinforcement / "null_unique_observations.csv",
        "thresholds": reinforcement / "null_calibration_thresholds.csv",
        "pool": reinforcement / "null_pool_design.csv",
        "expansion": repo / "results/paper_digest/paper15_q1_expansion/expansion_unique_observations.csv",
        "envelopes": repo / "results/paper_digest/paper15_hsaas_demo/hsaas_audit_envelopes.jsonl",
        "prereg": repo / "manuscript/paper15_v12_policy_prereg.md",
    }
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"frozen inputs missing: {missing}")
    null = pd.read_csv(paths["null"], low_memory=False)
    thresholds = pd.read_csv(paths["thresholds"])
    pool = pd.read_csv(paths["pool"])
    expansion = pd.read_csv(paths["expansion"], low_memory=False)
    gates = [str(s["gate"]) for s in NULL_GATES]
    intervened = expansion[(expansion["attack"] != "clean") & expansion["gate"].isin(gates)].copy()
    clean_rows = expansion[(expansion["attack"] == "clean") & expansion["gate"].isin(gates)].copy()
    envelopes = [json.loads(line) for line in paths["envelopes"].read_text(encoding="utf-8").splitlines() if line.strip()]
    inputs = [{"role": role, "path": _rel(repo, p), "sha256": _sha256(p)} for role, p in paths.items()]
    return {
        "null": null,
        "thresholds": thresholds,
        "pool": pool,
        "intervened": intervened,
        "clean_rows": clean_rows,
        "envelopes": envelopes,
        "inputs": inputs,
        "prereg": paths["prereg"],
    }


# ---------------------------------------------------------------------------
# Gate F: family calibration and fire matrices
# ---------------------------------------------------------------------------


def _delta(frame: pd.DataFrame) -> pd.Series:
    """Signed change of the reported balanced accuracy, clean minus observed."""

    return pd.to_numeric(frame["bal_acc_clean"], errors="coerce") - pd.to_numeric(frame["bal_acc"], errors="coerce")


def _score_frames(
    cal: pd.DataFrame,
    frozen_thresholds: pd.DataFrame,
    targets: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, bool]]:
    """Calibrate every cell and score every target frame; return thresholds, scored frames, checks."""

    thr = frozen_thresholds[frozen_thresholds["order_statistic_rank"] > 0].pivot_table(index=CELL, columns="sensor", values="threshold", aggfunc="first")
    rank = _order_statistic_rank(N_CAL_EXPECTED, ALPHA)
    records: list[dict[str, object]] = []
    scored = {name: [] for name in targets}
    reproduced = True
    for key, group in cal.groupby(CELL, sort=True):
        if len(group) != N_CAL_EXPECTED:
            raise ValueError(f"{key}: {len(group)} calibration draws, expected {N_CAL_EXPECTED}")
        calibration = {s: pd.to_numeric(group[s], errors="coerce").to_numpy(dtype=float) for s in CALIBRATED_SENSORS}
        for s in CALIBRATED_SENSORS:
            if np.isnan(calibration[s]).any():
                raise ValueError(f"{key}: NaN calibration values for {s}")
            recomputed = float(np.sort(calibration[s])[rank - 1])
            if abs(recomputed - float(thr.loc[key, s])) > 1e-12:
                reproduced = False
        family_thr: dict[str, float] = {}
        for regime, sensors in BATCH_REGIMES.items():
            cal_scores = family_scores(calibration, calibration, sensors)
            q = family_threshold(cal_scores, ALPHA)
            family_thr[regime] = q
            records.append({
                "gate": key[0], "svd_dim": int(key[1]), "model": key[2], "regime": regime,
                "n_sensors": len(sensors), "n_cal": int(len(group)), "alpha": ALPHA,
                "order_statistic_rank": rank, "family_threshold": q,
                "calibration_family_fire_fraction": float(np.mean(cal_scores > q)),
                "rule": "fire if max calibration rank score over the family > threshold",
            })
        for name, frame in targets.items():
            rows = frame[(frame["gate"] == key[0]) & (frame["svd_dim"] == key[1]) & (frame["model"] == key[2])]
            if len(rows) == 0:
                continue
            out = rows.copy()
            values = {s: pd.to_numeric(rows[s], errors="coerce").to_numpy(dtype=float) for s in CALIBRATED_SENSORS}
            for s in CALIBRATED_SENSORS:
                out[f"fire_sensor__{s}"] = values[s] > float(thr.loc[key, s])
                out[f"rank__{s}"] = rank_scores(values[s], calibration[s])
            for regime, sensors in BATCH_REGIMES.items():
                out[f"fire_union__{regime}"] = out[[f"fire_sensor__{s}" for s in sensors]].any(axis=1)
                score = family_scores(values, calibration, sensors)
                out[f"score_family__{regime}"] = score
                out[f"fire_family__{regime}"] = score > family_thr[regime]
            scored[name].append(out)
    checks = {"F0_frozen_per_sensor_thresholds_reproduced": bool(reproduced)}
    frames = {name: (pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()) for name, parts in scored.items()}
    return pd.DataFrame.from_records(records), frames, checks


def _exact_fire(frame: pd.DataFrame) -> pd.Series:
    if len(frame) == 0:
        return pd.Series(dtype=bool)
    vals = frame[EXACT_ITEM_ALIGNED_SENSORS].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs()
    return vals.max(axis=1) > TOL


def _rate_rows(frame: pd.DataFrame, group_cols: list[str], *, label: str) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for key, group in frame.groupby(group_cols, sort=True, dropna=False):
        key_tuple = key if isinstance(key, tuple) else (key,)
        base = dict(zip(group_cols, key_tuple, strict=True))
        for regime in BATCH_REGIME_NAMES:
            for rule in RULES:
                col = f"fire_{rule}__{regime}"
                n = int(len(group))
                k = int(group[col].sum())
                records.append({**base, "regime": regime, "rule": rule, "n": n, "n_fire": k, label: (k / n if n else math.nan)})
    return pd.DataFrame.from_records(records)


def build_gate_f(data: dict[str, object]) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, bool]]:
    null: pd.DataFrame = data["null"]  # type: ignore[assignment]
    cal = null[null["attack_priority_group"] == "null_calibration"]
    ev = null[null["attack_priority_group"] == "null_evaluation"]
    sham = null[null["attack_priority_group"] == "sham"]
    intervened: pd.DataFrame = data["intervened"]  # type: ignore[assignment]
    clean_rows: pd.DataFrame = data["clean_rows"]  # type: ignore[assignment]
    counts = ev.groupby(CELL).size()
    if not bool((counts == N_EVAL_EXPECTED).all()):
        raise ValueError("evaluation draw count per cell is not 200")

    thresholds, scored, checks = _score_frames(cal, data["thresholds"], {"evaluation": ev, "sham": sham, "intervened": intervened, "clean_rows": clean_rows})  # type: ignore[arg-type]
    ev_s, sham_s, int_s, clean_s = scored["evaluation"], scored["sham"], scored["intervened"], scored["clean_rows"]
    if len(int_s) != len(intervened) or len(ev_s) != len(ev):
        raise ValueError("scoring lost rows")
    for frame in (sham_s, int_s, clean_s):
        frame["fire_exact"] = _exact_fire(frame).to_numpy()
    int_s["delta_bal_acc"] = _delta(int_s).to_numpy()
    sham_s["delta_bal_acc"] = _delta(sham_s).to_numpy()

    # F1: false alarms on disjoint evaluation draws.
    fpr_cell = _rate_rows(ev_s, CELL, label="false_alarm_rate")
    fpr_cluster = _rate_rows(ev_s, ["gate", "split_seed"], label="false_alarm_rate")
    env_records: list[dict[str, object]] = []
    pool: pd.DataFrame = data["pool"]  # type: ignore[assignment]
    pool_first = pool.groupby("gate")[["n_calibration_half", "n_evaluation_half", "n_test"]].first()
    for gate, block in ev_s.groupby("gate", sort=True):
        for regime in BATCH_REGIME_NAMES:
            for rule in RULES:
                col = f"fire_{rule}__{regime}"
                per_split = block.groupby("split_seed")[col].mean()
                ci = _mean_ci(per_split)
                env_records.append({
                    "gate": gate, "regime": regime, "rule": rule, "n_draws": int(len(block)), "n_fire": int(block[col].sum()),
                    "pooled_rate": float(block[col].mean()), "n_clusters": int(len(per_split)),
                    "cluster_mean": ci["mean"], "cluster_ci95_low": ci["ci95_low"], "cluster_ci95_high": ci["ci95_high"],
                    "n_test": int(pool_first.loc[gate, "n_test"]), "n_pool_half": int(pool_first.loc[gate, "n_evaluation_half"]),
                    "max_disjoint_draws_per_half": int(pool_first.loc[gate, "n_evaluation_half"] // pool_first.loc[gate, "n_test"]),
                    "unit": "environment x split-seed cluster; two-sided 95% Student-t over 5 clusters",
                })
    fpr_env = pd.DataFrame.from_records(env_records)
    overall_records: list[dict[str, object]] = []
    for regime in BATCH_REGIME_NAMES:
        for rule in RULES:
            col = f"fire_{rule}__{regime}"
            env_means = fpr_env[(fpr_env["regime"] == regime) & (fpr_env["rule"] == rule)]["cluster_mean"]
            overall_records.append({
                "regime": regime, "rule": rule, "n_draws": int(len(ev_s)), "n_fire": int(ev_s[col].sum()), "pooled_rate": float(ev_s[col].mean()),
                "environment_cluster_mean_min": float(env_means.min()), "environment_cluster_mean_max": float(env_means.max()),
                "n_environments": int(env_means.size), "nominal_alpha": ALPHA,
                "note": "pooled rate is descriptive: draws within a cell overlap; inference is per environment over split clusters",
            })
    fpr_overall = pd.DataFrame.from_records(overall_records)

    # F2: detection on frozen interventions; near-null control response.
    det_pooled = _rate_rows(int_s.assign(all="all_environments"), ["all", "attack_family", "attack"], label="detection_rate")
    det_env = _rate_rows(int_s, ["gate", "attack_family", "attack"], label="detection_rate")
    benign = _rate_rows(sham_s.assign(all="all_environments"), ["all", "attack"], label="fire_rate")

    # F3: label-path consistency.
    label_side = int_s[int_s["attack_family"] == "target_shift"]
    prior = label_side[label_side["attack"].str.contains("prior_preserving", regex=False)]
    positive = label_side[label_side["delta_bal_acc"].abs() > TOL]
    lp_records = []
    for subset, block in (("all_label_interventions", label_side), ("prior_preserving_label_interventions", prior), ("material_label_interventions", positive)):
        for regime in BATCH_REGIME_NAMES:
            for rule in RULES:
                col = f"fire_{rule}__{regime}"
                lp_records.append({"subset": subset, "regime": regime, "rule": rule, "n": int(len(block)), "n_fire": int(block[col].sum()), "detection_rate": float(block[col].mean()) if len(block) else math.nan})
        lp_records.append({"subset": subset, "regime": "I_XFY_trusted", "rule": "exact", "n": int(len(block)), "n_fire": int(block["fire_exact"].sum()), "detection_rate": float(block["fire_exact"].mean()) if len(block) else math.nan})
    label_path = pd.DataFrame.from_records(lp_records)
    checks["F3_family_I_X_zero_on_label_rows"] = bool(label_side["fire_family__I_X"].sum() == 0)
    checks["F3_family_I_XF_zero_on_label_rows"] = bool(label_side["fire_family__I_XF"].sum() == 0)
    checks["F3_family_I_Ym_zero_on_prior_preserving_rows"] = bool(prior["fire_family__I_Ym"].sum() == 0)

    # Inference units.
    n_runs = int(ev.groupby(["gate", "split_seed", "model_seed", "svd_dim"]).ngroups)
    units = pd.DataFrame.from_records([{
        "n_environments": int(ev["gate"].nunique()), "n_cells": int(ev.groupby(CELL).ngroups), "n_runs": n_runs,
        "n_env_split_clusters": int(ev.groupby(["gate", "split_seed"]).ngroups), "n_evaluation_draws": int(len(ev)),
        "n_calibration_draws": int(len(cal)), "draws_per_cell": N_EVAL_EXPECTED,
        "dependence": "20 draws per run are overlapping simple random subsets of one pool half; 200 draws per cell come from 10 pool halves (5 split seeds x 2 model seeds)",
        "inferential_unit": "environment x split-seed cluster (5 per environment)",
        "descriptive_only": "pooled rates over draws and Clopper-Pearson intervals of artifact 1.1.0",
    }])

    outputs = {
        "family_calibration_thresholds.csv": thresholds,
        "family_false_alarm_by_cell.csv": fpr_cell,
        "family_false_alarm_by_cluster.csv": fpr_cluster,
        "family_false_alarm_by_environment.csv": fpr_env,
        "family_false_alarm_overall.csv": fpr_overall,
        "family_detection_pooled.csv": det_pooled,
        "family_detection_by_environment.csv": det_env,
        "family_benign_control_response.csv": benign,
        "family_label_path_summary.csv": label_path,
        "inference_units.csv": units,
    }
    return outputs, {"evaluation": ev_s, "sham": sham_s, "intervened": int_s, "clean_rows": clean_s}, checks


# ---------------------------------------------------------------------------
# Gate D: end-to-end decisions
# ---------------------------------------------------------------------------


def _decide_frame(frame: pd.DataFrame, regime: str, policy: str, *, exact_defined: bool) -> tuple[list[str], list[str]]:
    batch = BATCH_FOR_POLICY[regime]
    spec = POLICY_REGIMES[regime]
    actions: list[str] = []
    reasons: list[str] = []
    union = frame[f"fire_union__{batch}"].to_numpy(dtype=bool)
    family = frame[f"fire_family__{batch}"].to_numpy(dtype=bool)
    exact = frame["fire_exact"].to_numpy(dtype=bool) if (spec.trusted_reference and exact_defined) else None
    for i in range(len(frame)):
        ev = Evidence(bool(union[i]), bool(family[i]), (bool(exact[i]) if exact is not None else (False if spec.trusted_reference else None)))
        d: Decision = decide(policy, spec, ev)
        d2: Decision = decide(policy, spec, ev)
        if d != d2:
            raise RuntimeError("decision function is not deterministic")
        actions.append(d.action)
        reasons.append("|".join(d.reasons))
    return actions, reasons


def build_gate_d(scored: dict[str, pd.DataFrame], envelopes: list[dict[str, object]]) -> tuple[dict[str, pd.DataFrame], dict[str, bool]]:
    ev_s, sham_s, int_s, clean_s = scored["evaluation"], scored["sham"], scored["intervened"], scored["clean_rows"]
    near_null = sham_s[sham_s["attack"].isin(NEAR_NULL_SHAMS)].copy()
    identity = sham_s[sham_s["attack"] == "sham_identity"].copy()
    exact_zero = pd.concat([clean_s, identity], ignore_index=True)
    if not bool((exact_zero["fire_exact"] == False).all()):  # noqa: E712
        raise ValueError("exact-zero rows have non-zero item-aligned sensors")

    decisions_int = int_s[["gate", "svd_dim", "split_seed", "model_seed", "model", "attack", "attack_family", "delta_bal_acc", "fire_exact"] + [f"fire_{r}__{g}" for r in RULES for g in BATCH_REGIME_NAMES]].copy()
    decisions_null = ev_s[["gate", "svd_dim", "split_seed", "model_seed", "model", "attack"] + [f"fire_{r}__{g}" for r in RULES for g in BATCH_REGIME_NAMES]].copy()
    decisions_benign = near_null[["gate", "svd_dim", "split_seed", "model_seed", "model", "attack", "delta_bal_acc", "fire_exact"] + [f"fire_{r}__{g}" for r in RULES for g in BATCH_REGIME_NAMES]].copy()

    class_frames = {"clean": ev_s, "benign": near_null, "intervened": int_s, "clean_exact": exact_zero}
    action_store: dict[tuple[str, str, str], dict[str, np.ndarray]] = {}
    reason_counts: dict[tuple[str, str, str, str], int] = {}
    for regime in POLICY_REGIME_NAMES:
        trusted = POLICY_REGIMES[regime].trusted_reference
        for policy in POLICIES:
            for cls, frame in class_frames.items():
                if cls == "clean" and trusted:
                    continue  # clean class of the trusted regime is the exact-zero set
                if cls == "clean_exact" and not trusted:
                    continue
                acts, reas = _decide_frame(frame, regime, policy, exact_defined=(cls != "clean"))
                action_store[(regime, policy, cls)] = {"action": np.asarray(acts), "reason": np.asarray(reas)}
                for r in reas:
                    for code in r.split("|"):
                        reason_counts[(regime, policy, cls, code)] = reason_counts.get((regime, policy, cls, code), 0) + 1
                if cls == "intervened":
                    decisions_int[f"decision__{regime}__{policy}"] = acts
                elif cls == "clean":
                    decisions_null[f"decision__{regime}__{policy}"] = acts
                elif cls == "benign":
                    decisions_benign[f"decision__{regime}__{policy}"] = acts

    delta_int = int_s["delta_bal_acc"].to_numpy(dtype=float)
    metric_records: list[dict[str, object]] = []
    family_records: list[dict[str, object]] = []
    env_records: list[dict[str, object]] = []
    count_records: list[dict[str, object]] = []
    checks: dict[str, bool] = {}
    d1 = d2_allow = d2_hold = d3 = True
    fam = int_s["attack_family"].to_numpy()
    gates = int_s["gate"].to_numpy()
    for regime in POLICY_REGIME_NAMES:
        trusted = POLICY_REGIMES[regime].trusted_reference
        clean_cls = "clean_exact" if trusted else "clean"
        blind_mask = STRUCTURAL_BLIND[regime](int_s).to_numpy(dtype=bool)
        for policy in POLICIES:
            a_int = action_store[(regime, policy, "intervened")]["action"]
            a_clean = action_store[(regime, policy, clean_cls)]["action"]
            a_ben = action_store[(regime, policy, "benign")]["action"]
            for cls, arr in (("clean", a_clean), ("benign", a_ben), ("intervened", a_int)):
                for action in ("allow", "hold", "block"):
                    count_records.append({"regime": regime, "policy": policy, "observation_class": cls, "action": action, "n": int(np.sum(arr == action))})
            for tau in TAUS:
                material = np.abs(delta_int) > (tau if tau > 0 else TOL)
                held = a_int == "hold"
                blocked = a_int == "block"
                allowed = a_int == "allow"
                n_mat = int(material.sum())
                rec = {
                    "regime": regime, "policy": policy, "tau": tau, "trusted_reference": trusted,
                    "n_clean": int(len(a_clean)), "false_hold": int(np.sum(a_clean == "hold")), "false_block": int(np.sum(a_clean == "block")),
                    "n_benign": int(len(a_ben)), "benign_hold": int(np.sum(a_ben == "hold")), "benign_block": int(np.sum(a_ben == "block")),
                    "n_intervened": int(len(a_int)), "n_material": n_mat, "n_immaterial": int((~material).sum()),
                    "unsafe_allow": int(np.sum(allowed & material)), "true_hold": int(np.sum(held & material)), "true_block": int(np.sum(blocked & material)),
                    "immaterial_allow": int(np.sum(allowed & ~material)), "integrity_only_hold_block": int(np.sum((held | blocked) & ~material)),
                    "residual_blind_material": int(np.sum(material & blind_mask)),
                }
                rec["decision_fpr"] = (rec["false_hold"] + rec["false_block"]) / rec["n_clean"] if rec["n_clean"] else math.nan
                rec["benign_hold_block_rate"] = (rec["benign_hold"] + rec["benign_block"]) / rec["n_benign"] if rec["n_benign"] else math.nan
                rec["safe_allow"] = int(np.sum(a_clean == "allow")) + int(np.sum(a_ben == "allow")) + rec["immaterial_allow"]
                rec["containment"] = (rec["true_hold"] + rec["true_block"]) / n_mat if n_mat else math.nan
                rec["unsafe_allow_rate"] = rec["unsafe_allow"] / n_mat if n_mat else math.nan
                rec["coverage"] = 1.0 - rec["residual_blind_material"] / n_mat if n_mat else math.nan
                metric_records.append(rec)
                if policy == "serve_always" and rec["unsafe_allow"] != n_mat:
                    d1 = False
                for family_name in ("target_shift", "corruption", "covariate_shift", "pipeline"):
                    m = fam == family_name
                    nm = int(np.sum(material & m))
                    family_records.append({
                        "regime": regime, "policy": policy, "tau": tau, "attack_family": family_name, "n": int(m.sum()), "n_material": nm,
                        "unsafe_allow": int(np.sum(allowed & material & m)), "true_hold_block": int(np.sum((held | blocked) & material & m)),
                        "integrity_only_hold_block": int(np.sum((held | blocked) & ~material & m)),
                        "containment": (int(np.sum((held | blocked) & material & m)) / nm) if nm else math.nan,
                    })
                if tau == 0.0:
                    clean_gate = (exact_zero["gate"].to_numpy() if trusted else ev_s["gate"].to_numpy())
                    for gate in sorted(set(gates)):
                        g = gates == gate
                        cg = clean_gate == gate
                        nm = int(np.sum(material & g))
                        env_records.append({
                            "gate": gate, "regime": regime, "policy": policy, "tau": tau, "n_clean": int(cg.sum()),
                            "decision_fpr": float(np.mean(a_clean[cg] != "allow")) if cg.sum() else math.nan,
                            "n_material": nm, "unsafe_allow": int(np.sum(allowed & material & g)),
                            "containment": (int(np.sum((held | blocked) & material & g)) / nm) if nm else math.nan,
                        })
            label_rows = fam == "target_shift"
            if regime in ("I_X", "I_XF"):
                if policy in ("serve_always", "union_uncalibrated", "family_calibrated") and not bool(np.all(a_int[label_rows] == "allow")):
                    d2_allow = False
                if policy == "family_calibrated_strict" and not bool(np.all(a_int[label_rows] == "hold")):
                    d2_hold = False
            if regime == "I_XFY_trusted" and policy != "serve_always":
                material0 = np.abs(delta_int) > TOL
                decreased = delta_int > TOL
                exact = int_s["fire_exact"].to_numpy(dtype=bool)
                # Amendment A1: all material label rows (signed definition), of which the
                # 2,184 decreased-accuracy rows of the frozen count are a subset.
                if not bool(np.all(a_int[label_rows & material0] == "block")) or int(np.sum(label_rows & decreased)) != 2184:
                    d3 = False
                if not bool(np.all(a_int[exact] == "block")):
                    d3 = False
    checks["D1_serve_always_unsafe_allow_equals_material"] = d1
    checks["D2_structural_blindness_reproduced_by_decisions"] = bool(d2_allow and d2_hold)
    checks["D3_trusted_regime_blocks_all_material_label_rows_and_exact_violations"] = d3
    total = all(len(v["action"]) == len(v["reason"]) and all(bool(r) for r in v["reason"]) for v in action_store.values())
    checks["D4_decisions_total_with_reason_codes"] = bool(total)

    # D5: composition with the six frozen envelopes.
    comp_records: list[dict[str, object]] = []
    d5 = True
    for env in envelopes:
        contracts = {c["name"]: c for c in env["contracts"]}
        circuit = contracts["circuit_kernel"]["evidence"]
        execution = contracts["execution_result"]["evidence"]
        evaluation = contracts["evaluation_report"]["evidence"]
        approved_rewrite = bool(circuit["approved_circuit_rewrite"])
        approved_stochastic = bool(execution["approved_stochastic_estimation"])
        semantic_mismatch = float(circuit["semantic_kernel_max_abs_delta"]) > float(circuit["semantic_tolerance"])
        exact_fire = bool(evaluation["label_changed"]) or (float(execution["prediction_disagreement"]) > 0 and not approved_stochastic) \
            or (bool(circuit["circuit_changed"]) and not approved_rewrite) or (semantic_mismatch and not approved_stochastic)
        d = decide("family_calibrated", "I_XFY_trusted", Evidence(False, False, exact_fire))
        composed = compose(env["fail_closed_action"], d.action)
        if d.action == "allow" and composed != env["fail_closed_action"]:
            d5 = False
        comp_records.append({
            "scenario": env["scenario"], "contract_action": env["fail_closed_action"], "policy_regime": "I_XFY_trusted",
            "exact_invariant_violated": exact_fire, "approved_circuit_rewrite": approved_rewrite, "approved_stochastic_estimation": approved_stochastic,
            "policy_action": d.action, "policy_reasons": "|".join(d.reasons), "composed_action": composed,
            "agreement": composed == env["fail_closed_action"],
        })
    checks["D5_contract_composition_consistent"] = d5

    reasons = pd.DataFrame.from_records([{"regime": k[0], "policy": k[1], "observation_class": k[2], "reason": k[3], "n": v} for k, v in sorted(reason_counts.items())])
    boundary_records = []
    for regime, spec in POLICY_REGIMES.items():
        boundary_records.append({"regime": regime, "trusted_reference": spec.trusted_reference, **{f"coverage_{b}": spec.coverage[b] for b in BOUNDARIES}, "unverified_boundaries": "+".join(unverified_boundaries(spec)) or "none"})
    outputs = {
        "policy_metrics.csv": pd.DataFrame.from_records(metric_records),
        "policy_metrics_by_family.csv": pd.DataFrame.from_records(family_records),
        "policy_metrics_by_environment.csv": pd.DataFrame.from_records(env_records),
        "policy_decision_counts.csv": pd.DataFrame.from_records(count_records),
        "policy_reason_counts.csv": reasons,
        "policy_regime_coverage.csv": pd.DataFrame.from_records(boundary_records),
        "policy_intervened_decisions.csv": decisions_int,
        "policy_null_decisions.csv": decisions_null,
        "policy_benign_decisions.csv": decisions_benign,
        "policy_contract_composition.csv": pd.DataFrame.from_records(comp_records),
    }
    return outputs, checks


# ---------------------------------------------------------------------------
# Counterexample witnesses (formal section)
# ---------------------------------------------------------------------------


def build_witnesses(intervened: pd.DataFrame) -> pd.DataFrame:
    f = intervened.copy()
    delta = _delta(f)
    label = f["attack_family"].eq("target_shift")
    prior = f["attack"].str.contains("prior_preserving", regex=False)
    pred = pd.to_numeric(f["integrity_pred_disagreement"], errors="coerce").fillna(0.0).abs() > TOL
    conf = f[["integrity_confusion_profile_l1_delta", "integrity_confusion_profile_jsd_delta"]].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs().max(axis=1) > TOL
    marginal = f[["integrity_label_prior_shift", "integrity_label_jsd"]].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs().max(axis=1) > TOL
    flipped = pd.to_numeric(f["label_flip_rate"], errors="coerce").fillna(0.0) > TOL
    material = delta.abs() > TOL
    rows = [
        ("W1", "identity change without joint-outcome or conclusion change", "label rows with flips, zero confusion-profile delta, zero conclusion change", int((label & flipped & ~conf & ~material).sum()), int(label.sum())),
        ("W2", "conclusion change without model-output change", "label rows with non-zero conclusion change and zero prediction disagreement", int((label & material & ~pred).sum()), int(label.sum())),
        ("W3", "marginal invariance with conclusion change", "prior-preserving rows with zero marginal change and non-zero conclusion change", int((prior & ~marginal & material).sum()), int(prior.sum())),
        ("W4", "confusion-profile change without conclusion change", "label rows with non-zero confusion-profile delta and zero conclusion change", int((label & conf & ~material).sum()), int(label.sum())),
        ("W5", "model-output change without conclusion change", "feature rows with non-zero prediction disagreement and zero conclusion change", int((~label & pred & ~material).sum()), int((~label).sum())),
        ("W6", "representation change without output change", "feature rows with zero prediction disagreement", int((~label & ~pred).sum()), int((~label).sum())),
        ("W7", "apparent improvement under intervention", "intervened rows whose reported balanced accuracy increased", int((delta < -TOL).sum()), int(len(f))),
        ("W8", "material conclusion change always changes the confusion profile (label path)", "material label rows with non-zero confusion-profile delta", int((label & material & conf).sum()), int((label & material).sum())),
    ]
    return pd.DataFrame.from_records([{"witness": w, "property": p, "condition": c, "count": n, "denominator": d} for w, p, c, n, d in rows])


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build(repo: Path, out_dir: Path) -> None:
    data = _load(repo)
    f_out, scored, checks = build_gate_f(data)
    d_out, d_checks = build_gate_d(scored, data["envelopes"])  # type: ignore[arg-type]
    checks.update(d_checks)
    witnesses = build_witnesses(data["intervened"])  # type: ignore[arg-type]
    w8 = witnesses.set_index("witness")
    checks["W8_material_label_rows_all_change_confusion_profile"] = bool(w8.loc["W8", "count"] == w8.loc["W8", "denominator"])
    outputs = {**f_out, **d_out, "counterexample_witnesses.csv": witnesses}

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"Consistency checks failed; no manifest written: {failed}")

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(out_dir / name, index=False)
    prereg: Path = data["prereg"]  # type: ignore[assignment]
    manifest = {
        "analysis": "paper15_v12_policy",
        "status": "complete",
        "preregistration": {"file": _rel(repo, prereg), "sha256": _sha256(prereg)},
        "gate_f": {
            "alpha_per_decision": ALPHA,
            "statistic": "maximum calibration rank score over the regime (one minus the minimum calibration p-value); ties count against firing",
            "threshold": f"{_order_statistic_rank(N_CAL_EXPECTED, ALPHA)}th smallest calibration family score per (environment, dimension, model) cell",
            "regimes": {k: v for k, v in BATCH_REGIMES.items()},
            "inferential_unit": "environment x split-seed cluster; pooled rates descriptive",
        },
        "gate_d": {
            "policies": list(POLICIES),
            "regimes": {name: {"trusted_reference": spec.trusted_reference, "coverage": spec.coverage} for name, spec in POLICY_REGIMES.items()},
            "materiality": {"primary": "|delta balanced accuracy| > 1e-12", "sensitivity": [0.02, 0.05]},
            "observation_classes": {"clean": "12,000 disjoint clean evaluation draws (exact-zero rows for the trusted regime)", "benign": "near-null in-place shams", "intervened": "frozen paper_core observations of the eight Gate N environments"},
            "composition": "max in the lattice allow < hold < block over the six frozen HSaaS envelopes",
        },
        "acceptance_checks": checks,
        "input_files": data["inputs"],
        "outputs": {name: {"rows": int(len(frame)), "sha256": _sha256(out_dir / name)} for name, frame in outputs.items()},
    }
    (out_dir / "policy_evidence_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "acceptance_checks": checks, "outputs": len(outputs)}, indent=2))
    print(f"Wrote {len(outputs)} tables and manifest to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=Path("results/paper_digest/paper15_v12_policy"))
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.out_dir)


if __name__ == "__main__":
    main()
