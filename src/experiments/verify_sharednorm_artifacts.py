"""
Verify the archived shared-normalized artefacts used in Paper 1.5.

Important note:
The aggregate CSV contains model-local detectability columns whose
normalization metadata includes `model` in the normalization group.
Those columns reproduce the old model-local stealth ratios and must not
be used for cross-model stealth claims.

The corrected cross-model results are stored in the derived artefacts
under:

    results/paper_digest/<tag>/shared_norm/

This verifier checks that the manuscript's main QSVC-ZZ vs SVC-RBF
ratios are reproduced exactly from the archived shared-normalized
summary and ratio tables.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


EXPECTED = {
    8: {
        "impact_ratio_vs_svc": 2.972153,
        "stealth_sharednorm_ratio_vs_svc": 1.588016,
    },
    10: {
        "impact_ratio_vs_svc": 3.662994,
        "stealth_sharednorm_ratio_vs_svc": 1.805480,
    },
    12: {
        "impact_ratio_vs_svc": 3.393358,
        "stealth_sharednorm_ratio_vs_svc": 1.666626,
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--shared-dir",
        default="results/paper_digest/paper_core_all_fmaps_plus_baseline/shared_norm",
        help="Directory containing archived shared-normalized artefacts.",
    )
    parser.add_argument(
        "--agg",
        default="results/aggregated/agg_paper_core_all_fmaps_plus_baseline.csv",
        help="Optional aggregate CSV used only to check whether its detectability metadata is model-local.",
    )
    parser.add_argument("--tol", type=float, default=1e-6)
    args = parser.parse_args()

    shared_dir = Path(args.shared_dir)
    ratio_path = shared_dir / "table_model_vs_svc_ratios_sharednorm.csv"
    summary_path = shared_dir / "summary_by_model_dim_protocol_sharednorm.csv"

    if not ratio_path.exists():
        raise SystemExit(f"[ERROR] Missing {ratio_path}")

    if not summary_path.exists():
        raise SystemExit(f"[ERROR] Missing {summary_path}")

    ratios = pd.read_csv(ratio_path)
    summary = pd.read_csv(summary_path)

    print("[INFO] Loaded shared-normalized artefacts:")
    print(f"  - {ratio_path} rows={len(ratios)}")
    print(f"  - {summary_path} rows={len(summary)}")

    selected = ratios[
        (ratios["protocol"] == "id")
        & (ratios["model"] == "qsvc_zz_r1")
        & (ratios["svd_dim"].isin([8, 10, 12]))
    ].copy()

    print("\n=== QSVC-ZZ vs SVC-RBF ID ratios from archived shared_norm ===")
    print(
        selected[
            [
                "protocol",
                "model",
                "svd_dim",
                "impact_ratio_vs_svc",
                "stealth_sharednorm_ratio_vs_svc",
            ]
        ].to_string(index=False)
    )

    ok = True

    for dim, expected in EXPECTED.items():
        row = selected[selected["svd_dim"] == dim]
        if row.empty:
            print(f"[FAIL] Missing dim={dim}")
            ok = False
            continue

        row = row.iloc[0]

        for col, exp in expected.items():
            got = float(row[col])
            diff = abs(got - exp)
            status = "OK" if diff <= args.tol else "FAIL"
            print(f"[{status}] dim={dim} {col}: got={got:.12f} expected={exp:.12f} diff={diff:.3e}")
            if diff > args.tol:
                ok = False

    # Optional diagnostic: warn if agg detectability metadata is model-local.
    agg_path = Path(args.agg)
    if agg_path.exists():
        agg = pd.read_csv(agg_path)
        if "detectability_norm_group_cols" in agg.columns:
            vals = sorted(set(agg["detectability_norm_group_cols"].dropna().astype(str)))
            print("\n=== aggregate detectability normalization metadata ===")
            for v in vals:
                print(f"  - {v}")

            if any("model" in v.split(",") for v in vals):
                print(
                    "\n[INFO] Aggregate detectability columns are model-local because "
                    "`model` appears in detectability_norm_group_cols. They are not the "
                    "source for the manuscript's shared-normalized cross-model ratios."
                )

    if not ok:
        raise SystemExit("[FAIL] Archived shared-normalized artefacts do not match expected manuscript ratios.")

    print("\n[OK] Archived shared-normalized artefacts reproduce the manuscript ratios.")


if __name__ == "__main__":
    main()
