import pandas as pd
from pathlib import Path

infile = Path("results/plots/paper_core_full_zz_128/summary_stealth_by_model.csv")
outdir = Path("results/tables/paper_core_full_zz_128")
outdir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(infile)

proto_col = "__protocol_norm" if "__protocol_norm" in df.columns else "protocol"

keep = [
    proto_col,
    "dataset_tag",
    "model",
    "svd_dim",
    "impact_bal_acc_mean",
    "detectability_score_mean",
    "stealth_score_mean",
]
df = df[keep].copy()
df["svd_dim"] = df["svd_dim"].astype(int)

wide = df.pivot_table(
    index=[proto_col, "dataset_tag", "svd_dim"],
    columns="model",
    values=["impact_bal_acc_mean", "detectability_score_mean", "stealth_score_mean"],
    aggfunc="mean"
)

wide.columns = [f"{metric}__{model}" for metric, model in wide.columns]
wide = wide.reset_index()

for metric in ["impact_bal_acc_mean", "detectability_score_mean", "stealth_score_mean"]:
    q = f"{metric}__qsvc_zz_r1"
    c = f"{metric}__svc_rbf"
    if q in wide.columns and c in wide.columns:
        wide[f"{metric}__qsvc_minus_rbf"] = wide[q] - wide[c]
        wide[f"{metric}__qsvc_over_rbf"] = wide[q] / wide[c].replace(0, pd.NA)

wide = wide.sort_values([proto_col, "svd_dim"])

out = outdir / "table_qsvc_vs_rbf_by_protocol_dim.csv"
wide.to_csv(out, index=False)

print("[OK]", out)
print(wide.to_string(index=False))
