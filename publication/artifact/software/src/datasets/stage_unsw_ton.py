# src/datasets/stage_unsw_ton.py
#
# Stage UNSW-NB15 and TON_IoT raw CSVs into a cleaned form consumable by
# src/datasets/prepare_cicids_subset.py (which is dataset-agnostic).
#
# Why staging is needed (leakage control):
#   - UNSW-NB15 official train/test sets carry `id` (row index) and `label`
#     (binary ground truth). Both would survive numeric coercion and leak the
#     target. We drop them and keep `attack_cat` as the label column
#     (benign token: "normal").
#   - TON_IoT train_test_network.csv carries `label` (binary ground truth)
#     plus src/dst ports. We drop `label` and ports (ports are also dropped in
#     the CICIDS prep via the leakage-column list) and keep `type` as the
#     label column (benign token: "normal").
#
# Output: data/raw/staging/{unsw_nb15,ton_iot}/*.csv + stage report JSON.
#
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw"
STAGING = RAW / "staging"


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _stage(
    src: Path,
    dst: Path,
    drop_cols: list[str],
    label_src: str,
    max_sparse_frac: float = 0.5,
) -> dict:
    df = pd.read_csv(src, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    present = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=present)
    if label_src not in df.columns:
        raise RuntimeError(f"{src.name}: label source column '{label_src}' not found")

    # Drop feature columns that are mostly missing after numeric coercion
    # (e.g. TON_IoT protocol-specific fields that are '-' for most flows).
    # Keeping them would make the effective feature count split-dependent
    # (all-NaN columns get silently dropped by the imputer on some splits).
    sparse_cols = []
    for c in df.columns:
        if c == label_src:
            continue
        coerced = pd.to_numeric(df[c], errors="coerce")
        if coerced.notna().any() and coerced.isna().mean() > max_sparse_frac:
            sparse_cols.append(c)
    df = df.drop(columns=sparse_cols)
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dst, index=False)
    return {
        "src": str(src),
        "src_sha256": _sha256_file(src),
        "dst": str(dst),
        "dst_sha256": _sha256_file(dst),
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "dropped_cols": present,
        "dropped_sparse_cols": sparse_cols,
        "max_sparse_frac": max_sparse_frac,
        "label_source_col": label_src,
    }


def main() -> None:
    report = {}

    unsw_dir = RAW / "unsw_nb15" / "Training and Testing Sets"
    unsw_drop = ["id", "label"]  # keep attack_cat as label source
    report["unsw_train"] = _stage(
        unsw_dir / "UNSW_NB15_training-set.csv",
        STAGING / "unsw_nb15" / "unsw_train.csv",
        unsw_drop,
        "attack_cat",
    )
    report["unsw_test"] = _stage(
        unsw_dir / "UNSW_NB15_testing-set.csv",
        STAGING / "unsw_nb15" / "unsw_test.csv",
        unsw_drop,
        "attack_cat",
    )

    ton_drop = ["label", "src_port", "dst_port"]  # keep type as label source
    report["ton_iot"] = _stage(
        RAW / "ton_iot" / "train_test_network.csv",
        STAGING / "ton_iot" / "ton_network.csv",
        ton_drop,
        "type",
    )

    out = STAGING / "stage_report.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[OK] Stage report -> {out}")
    for k, v in report.items():
        print(f"  {k}: rows={v['rows']} cols={v['cols']} dropped={v['dropped_cols']}")


if __name__ == "__main__":
    main()
