# aggregate_results.py static audit

File: `src\experiments\aggregate_results.py`

## Pattern `shared` — 0 hits

## Pattern `sharednorm` — 0 hits

## Pattern `shared_norm` — 0 hits

## Pattern `group` — 65 hits

### Around line 132
```python
0130:         m = _OOD_RE.search(name)
0131:         if m:
0132:             return f"tr{m.group(1).lower()}__te{m.group(2).lower()}"
0133:         return "trNA__teNA"
0134: 
```

### Around line 137
```python
0135:     m = _ID_RE.search(name)
0136:     if m:
0137:         return f"id{m.group(1).lower()}"
0138:     return "idNA"
0139: 
```

### Around line 213
```python
0211: 
0212: 
0213: def _group_weighted_means(
0214:     df: pd.DataFrame,
0215:     *,
```

### Around line 216
```python
0214:     df: pd.DataFrame,
0215:     *,
0216:     group_cols: List[str],
0217:     metrics: List[str],
0218:     weight_col: str = "n_seed_units",
```

### Around line 222
```python
0220:     rows: List[Dict[str, object]] = []
0221: 
0222:     for key, sub in df.groupby(group_cols, dropna=False):
0223:         if not isinstance(key, tuple):
0224:             key = (key,)
```

### Around line 226
```python
0224:             key = (key,)
0225: 
0226:         row: Dict[str, object] = {c: v for c, v in zip(group_cols, key)}
0227:         row["n_groups"] = int(len(sub))
0228: 
```

### Around line 227
```python
0225: 
0226:         row: Dict[str, object] = {c: v for c, v in zip(group_cols, key)}
0227:         row["n_groups"] = int(len(sub))
0228: 
0229:         if weight_col in sub.columns:
```

### Around line 438
```python
0436:     _ensure_numeric_round(out, ["attack_strength_nominal", "attack_strength_eff"], ndigits=12)
0437: 
0438:     # attack_priority_group / attack_suite may exist in richer runner
0439:     if "attack_priority_group" in out.columns:
0440:         out["attack_priority_group"] = out["attack_priority_group"].astype(str).str.strip()
```

### Around line 439
```python
0437: 
0438:     # attack_priority_group / attack_suite may exist in richer runner
0439:     if "attack_priority_group" in out.columns:
0440:         out["attack_priority_group"] = out["attack_priority_group"].astype(str).str.strip()
0441:     if "attack_suite" in out.columns:
```

### Around line 440
```python
0438:     # attack_priority_group / attack_suite may exist in richer runner
0439:     if "attack_priority_group" in out.columns:
0440:         out["attack_priority_group"] = out["attack_priority_group"].astype(str).str.strip()
0441:     if "attack_suite" in out.columns:
0442:         out["attack_suite"] = out["attack_suite"].astype(str).str.strip()
```

### Around line 775
```python
0773:         "scale",
0774:         "attack_suite",
0775:         "attack_priority_group",
0776:         "attack",
0777:         "attack_seed",
```

### Around line 798
```python
0796:     _ensure_numeric_round(out, ["attack_strength_nominal", "attack_strength_eff"], ndigits=12)
0797: 
0798:     group_cols = [
0799:         "protocol",
0800:         "dataset_tag",
```

### Around line 806
```python
0804:         "scale",
0805:     ]
0806:     optional_group_cols = [
0807:         "attack_suite",
0808:         "attack_priority_group",
```

### Around line 808
```python
0806:     optional_group_cols = [
0807:         "attack_suite",
0808:         "attack_priority_group",
0809:     ]
0810:     for c in optional_group_cols:
```

### Around line 810
```python
0808:         "attack_priority_group",
0809:     ]
0810:     for c in optional_group_cols:
0811:         if c in out.columns:
0812:             group_cols.append(c)
```

### Around line 812
```python
0810:     for c in optional_group_cols:
0811:         if c in out.columns:
0812:             group_cols.append(c)
0813: 
0814:     group_cols += [
```

### Around line 814
```python
0812:             group_cols.append(c)
0813: 
0814:     group_cols += [
0815:         "attack_family",
0816:         "attack_strength_nominal",
```

### Around line 820
```python
0818:     ]
0819: 
0820:     for c in group_cols:
0821:         if c not in out.columns:
0822:             raise SystemExit(f"[ERROR] Missing grouping column: {c}")
```

### Around line 822
```python
0820:     for c in group_cols:
0821:         if c not in out.columns:
0822:             raise SystemExit(f"[ERROR] Missing grouping column: {c}")
0823: 
0824:     metrics = [
```

### Around line 911
```python
0909:     metrics = [m for m in metrics if m in out.columns]
0910: 
0911:     g = out.groupby(group_cols, dropna=False)
0912:     out_rows: List[Dict[str, object]] = []
0913: 
```

## Pattern `detectability` — 67 hits

### Around line 15
```python
0013: #   - derive auditability-oriented scores:
0014: #       * impact_bal_acc_mean
0015: #       * detectability_score_mean
0016: #       * stealth_score_mean
0017: #   - export companion tables useful for the paper narrative
```

### Around line 1056
```python
1054:     out["impact_source"] = impact_source
1055: 
1056:     # Preferred detectability signals:
1057:     # prefer attack-vs-clean-eval + label-aware + prediction-aware + confusion-profile.
1058:     preferred_signal_pairs = [
```

### Around line 1108
```python
1106: 
1107:     # Transparency / provenance
1108:     out["detectability_signal_cols_used"] = ",".join(signal_cols) if signal_cols else ""
1109:     out["detectability_signal_sources"] = ";".join(signal_sources) if signal_sources else ""
1110:     out["detectability_signal_count"] = int(len(signal_cols))
```

### Around line 1109
```python
1107:     # Transparency / provenance
1108:     out["detectability_signal_cols_used"] = ",".join(signal_cols) if signal_cols else ""
1109:     out["detectability_signal_sources"] = ";".join(signal_sources) if signal_sources else ""
1110:     out["detectability_signal_count"] = int(len(signal_cols))
1111:     out["detectability_norm_group_cols"] = ",".join(norm_group_cols) if norm_group_cols else ""
```

### Around line 1110
```python
1108:     out["detectability_signal_cols_used"] = ",".join(signal_cols) if signal_cols else ""
1109:     out["detectability_signal_sources"] = ";".join(signal_sources) if signal_sources else ""
1110:     out["detectability_signal_count"] = int(len(signal_cols))
1111:     out["detectability_norm_group_cols"] = ",".join(norm_group_cols) if norm_group_cols else ""
1112:     out["detectability_norm_q_lo"] = float(q_lo)
```

### Around line 1111
```python
1109:     out["detectability_signal_sources"] = ";".join(signal_sources) if signal_sources else ""
1110:     out["detectability_signal_count"] = int(len(signal_cols))
1111:     out["detectability_norm_group_cols"] = ",".join(norm_group_cols) if norm_group_cols else ""
1112:     out["detectability_norm_q_lo"] = float(q_lo)
1113:     out["detectability_norm_q_hi"] = float(q_hi)
```

### Around line 1112
```python
1110:     out["detectability_signal_count"] = int(len(signal_cols))
1111:     out["detectability_norm_group_cols"] = ",".join(norm_group_cols) if norm_group_cols else ""
1112:     out["detectability_norm_q_lo"] = float(q_lo)
1113:     out["detectability_norm_q_hi"] = float(q_hi)
1114: 
```

### Around line 1113
```python
1111:     out["detectability_norm_group_cols"] = ",".join(norm_group_cols) if norm_group_cols else ""
1112:     out["detectability_norm_q_lo"] = float(q_lo)
1113:     out["detectability_norm_q_hi"] = float(q_hi)
1114: 
1115:     if signal_cols:
```

### Around line 1117
```python
1115:     if signal_cols:
1116:         raw_matrix = out[signal_cols].apply(pd.to_numeric, errors="coerce")
1117:         out["detectability_raw_mean"] = raw_matrix.mean(axis=1, skipna=True)
1118:         out["detectability_raw_std"] = raw_matrix.std(axis=1, skipna=True)
1119:     else:
```

### Around line 1118
```python
1116:         raw_matrix = out[signal_cols].apply(pd.to_numeric, errors="coerce")
1117:         out["detectability_raw_mean"] = raw_matrix.mean(axis=1, skipna=True)
1118:         out["detectability_raw_std"] = raw_matrix.std(axis=1, skipna=True)
1119:     else:
1120:         out["detectability_raw_mean"] = np.nan
```

### Around line 1120
```python
1118:         out["detectability_raw_std"] = raw_matrix.std(axis=1, skipna=True)
1119:     else:
1120:         out["detectability_raw_mean"] = np.nan
1121:         out["detectability_raw_std"] = np.nan
1122: 
```

### Around line 1121
```python
1119:     else:
1120:         out["detectability_raw_mean"] = np.nan
1121:         out["detectability_raw_std"] = np.nan
1122: 
1123:     if norm_cols:
```

### Around line 1125
```python
1123:     if norm_cols:
1124:         norm_matrix = out[norm_cols].apply(pd.to_numeric, errors="coerce")
1125:         out["detectability_components_n"] = norm_matrix.notna().sum(axis=1).astype(int)
1126:         out["detectability_score_mean"] = norm_matrix.mean(axis=1, skipna=True)
1127:         out["detectability_score_std"] = norm_matrix.std(axis=1, skipna=True)
```

### Around line 1126
```python
1124:         norm_matrix = out[norm_cols].apply(pd.to_numeric, errors="coerce")
1125:         out["detectability_components_n"] = norm_matrix.notna().sum(axis=1).astype(int)
1126:         out["detectability_score_mean"] = norm_matrix.mean(axis=1, skipna=True)
1127:         out["detectability_score_std"] = norm_matrix.std(axis=1, skipna=True)
1128:         out["detectability_score_min"] = norm_matrix.min(axis=1, skipna=True)
```

### Around line 1127
```python
1125:         out["detectability_components_n"] = norm_matrix.notna().sum(axis=1).astype(int)
1126:         out["detectability_score_mean"] = norm_matrix.mean(axis=1, skipna=True)
1127:         out["detectability_score_std"] = norm_matrix.std(axis=1, skipna=True)
1128:         out["detectability_score_min"] = norm_matrix.min(axis=1, skipna=True)
1129:         out["detectability_score_max"] = norm_matrix.max(axis=1, skipna=True)
```

### Around line 1128
```python
1126:         out["detectability_score_mean"] = norm_matrix.mean(axis=1, skipna=True)
1127:         out["detectability_score_std"] = norm_matrix.std(axis=1, skipna=True)
1128:         out["detectability_score_min"] = norm_matrix.min(axis=1, skipna=True)
1129:         out["detectability_score_max"] = norm_matrix.max(axis=1, skipna=True)
1130:     else:
```

### Around line 1129
```python
1127:         out["detectability_score_std"] = norm_matrix.std(axis=1, skipna=True)
1128:         out["detectability_score_min"] = norm_matrix.min(axis=1, skipna=True)
1129:         out["detectability_score_max"] = norm_matrix.max(axis=1, skipna=True)
1130:     else:
1131:         out["detectability_components_n"] = 0
```

### Around line 1131
```python
1129:         out["detectability_score_max"] = norm_matrix.max(axis=1, skipna=True)
1130:     else:
1131:         out["detectability_components_n"] = 0
1132:         out["detectability_score_mean"] = np.nan
1133:         out["detectability_score_std"] = np.nan
```

### Around line 1132
```python
1130:     else:
1131:         out["detectability_components_n"] = 0
1132:         out["detectability_score_mean"] = np.nan
1133:         out["detectability_score_std"] = np.nan
1134:         out["detectability_score_min"] = np.nan
```

### Around line 1133
```python
1131:         out["detectability_components_n"] = 0
1132:         out["detectability_score_mean"] = np.nan
1133:         out["detectability_score_std"] = np.nan
1134:         out["detectability_score_min"] = np.nan
1135:         out["detectability_score_max"] = np.nan
```

## Pattern `stealth` — 43 hits

### Around line 16
```python
0014: #       * impact_bal_acc_mean
0015: #       * detectability_score_mean
0016: #       * stealth_score_mean
0017: #   - export companion tables useful for the paper narrative
0018: #
```

### Around line 1153
```python
1151:     out["detectability_missing"] = (attacked_mask & det_score.isna()).astype(bool)
1152: 
1153:     # Stealth:
1154:     # keep detectability_score_mean as-is (NaN if unsupported),
1155:     # but for stealth ranking treat missing detectability as 0 evidence.
```

### Around line 1155
```python
1153:     # Stealth:
1154:     # keep detectability_score_mean as-is (NaN if unsupported),
1155:     # but for stealth ranking treat missing detectability as 0 evidence.
1156:     det_for_stealth = det_score.fillna(0.0).clip(lower=0.0, upper=1.0)
1157:     out["detectability_score_for_stealth"] = det_for_stealth
```

### Around line 1156
```python
1154:     # keep detectability_score_mean as-is (NaN if unsupported),
1155:     # but for stealth ranking treat missing detectability as 0 evidence.
1156:     det_for_stealth = det_score.fillna(0.0).clip(lower=0.0, upper=1.0)
1157:     out["detectability_score_for_stealth"] = det_for_stealth
1158: 
```

### Around line 1157
```python
1155:     # but for stealth ranking treat missing detectability as 0 evidence.
1156:     det_for_stealth = det_score.fillna(0.0).clip(lower=0.0, upper=1.0)
1157:     out["detectability_score_for_stealth"] = det_for_stealth
1158: 
1159:     out["stealth_score_mean"] = pd.to_numeric(out["impact_bal_acc_mean"], errors="coerce") * (1.0 - det_for_stealth)
```

### Around line 1159
```python
1157:     out["detectability_score_for_stealth"] = det_for_stealth
1158: 
1159:     out["stealth_score_mean"] = pd.to_numeric(out["impact_bal_acc_mean"], errors="coerce") * (1.0 - det_for_stealth)
1160:     out.loc[clean_mask, "stealth_score_mean"] = 0.0
1161: 
```

### Around line 1160
```python
1158: 
1159:     out["stealth_score_mean"] = pd.to_numeric(out["impact_bal_acc_mean"], errors="coerce") * (1.0 - det_for_stealth)
1160:     out.loc[clean_mask, "stealth_score_mean"] = 0.0
1161: 
1162:     out["stealth_missing_detectability_assumed_zero"] = (
```

### Around line 1162
```python
1160:     out.loc[clean_mask, "stealth_score_mean"] = 0.0
1161: 
1162:     out["stealth_missing_detectability_assumed_zero"] = (
1163:         attacked_mask & pd.to_numeric(out["detectability_score_mean"], errors="coerce").isna()
1164:     ).astype(bool)
```

### Around line 1166
```python
1164:     ).astype(bool)
1165: 
1166:     out["stealth_rank_overall"] = np.nan
1167:     out["stealth_rank_within_model"] = np.nan
1168:     out["stealth_rank_within_protocol_dataset"] = np.nan
```

### Around line 1167
```python
1165: 
1166:     out["stealth_rank_overall"] = np.nan
1167:     out["stealth_rank_within_model"] = np.nan
1168:     out["stealth_rank_within_protocol_dataset"] = np.nan
1169:     out["stealth_rank_within_protocol_dataset_model"] = np.nan
```

### Around line 1168
```python
1166:     out["stealth_rank_overall"] = np.nan
1167:     out["stealth_rank_within_model"] = np.nan
1168:     out["stealth_rank_within_protocol_dataset"] = np.nan
1169:     out["stealth_rank_within_protocol_dataset_model"] = np.nan
1170: 
```

### Around line 1169
```python
1167:     out["stealth_rank_within_model"] = np.nan
1168:     out["stealth_rank_within_protocol_dataset"] = np.nan
1169:     out["stealth_rank_within_protocol_dataset_model"] = np.nan
1170: 
1171:     if len(attacked_idx) > 0:
```

### Around line 1172
```python
1170: 
1171:     if len(attacked_idx) > 0:
1172:         out.loc[attacked_idx, "stealth_rank_overall"] = (
1173:             out.loc[attacked_idx, "stealth_score_mean"].rank(method="dense", ascending=False)
1174:         )
```

### Around line 1173
```python
1171:     if len(attacked_idx) > 0:
1172:         out.loc[attacked_idx, "stealth_rank_overall"] = (
1173:             out.loc[attacked_idx, "stealth_score_mean"].rank(method="dense", ascending=False)
1174:         )
1175: 
```

### Around line 1177
```python
1175: 
1176:         if "model" in out.columns:
1177:             out.loc[attacked_idx, "stealth_rank_within_model"] = (
1178:                 out.loc[attacked_idx]
1179:                 .groupby("model", dropna=False)["stealth_score_mean"]
```

### Around line 1179
```python
1177:             out.loc[attacked_idx, "stealth_rank_within_model"] = (
1178:                 out.loc[attacked_idx]
1179:                 .groupby("model", dropna=False)["stealth_score_mean"]
1180:                 .rank(method="dense", ascending=False)
1181:             )
```

### Around line 1185
```python
1183:         rank_group = [c for c in ["protocol", "dataset_tag"] if c in out.columns]
1184:         if rank_group:
1185:             out.loc[attacked_idx, "stealth_rank_within_protocol_dataset"] = (
1186:                 out.loc[attacked_idx]
1187:                 .groupby(rank_group, dropna=False)["stealth_score_mean"]
```

### Around line 1187
```python
1185:             out.loc[attacked_idx, "stealth_rank_within_protocol_dataset"] = (
1186:                 out.loc[attacked_idx]
1187:                 .groupby(rank_group, dropna=False)["stealth_score_mean"]
1188:                 .rank(method="dense", ascending=False)
1189:             )
```

### Around line 1193
```python
1191:         rank_group_model = [c for c in ["protocol", "dataset_tag", "model"] if c in out.columns]
1192:         if rank_group_model:
1193:             out.loc[attacked_idx, "stealth_rank_within_protocol_dataset_model"] = (
1194:                 out.loc[attacked_idx]
1195:                 .groupby(rank_group_model, dropna=False)["stealth_score_mean"]
```

### Around line 1195
```python
1193:             out.loc[attacked_idx, "stealth_rank_within_protocol_dataset_model"] = (
1194:                 out.loc[attacked_idx]
1195:                 .groupby(rank_group_model, dropna=False)["stealth_score_mean"]
1196:                 .rank(method="dense", ascending=False)
1197:             )
```

## Pattern `mean` — 108 hits

### Around line 14
```python
0012: #       * richer future runner outputs
0013: #   - derive auditability-oriented scores:
0014: #       * impact_bal_acc_mean
0015: #       * detectability_score_mean
0016: #       * stealth_score_mean
```

### Around line 15
```python
0013: #   - derive auditability-oriented scores:
0014: #       * impact_bal_acc_mean
0015: #       * detectability_score_mean
0016: #       * stealth_score_mean
0017: #   - export companion tables useful for the paper narrative
```

### Around line 16
```python
0014: #       * impact_bal_acc_mean
0015: #       * detectability_score_mean
0016: #       * stealth_score_mean
0017: #   - export companion tables useful for the paper narrative
0018: #
```

### Around line 141
```python
0139: 
0140: 
0141: def _safe_mean(s: pd.Series) -> float:
0142:     return float(s.mean(skipna=True))
0143: 
```

### Around line 142
```python
0140: 
0141: def _safe_mean(s: pd.Series) -> float:
0142:     return float(s.mean(skipna=True))
0143: 
0144: 
```

### Around line 200
```python
0198: 
0199: 
0200: def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
0201:     v = pd.to_numeric(values, errors="coerce").astype(float)
0202:     w = pd.to_numeric(weights, errors="coerce").astype(float)
```

### Around line 213
```python
0211: 
0212: 
0213: def _group_weighted_means(
0214:     df: pd.DataFrame,
0215:     *,
```

### Around line 237
```python
0235: 
0236:         for m in metrics:
0237:             row[m] = _weighted_mean(sub[m], w) if m in sub.columns else float("nan")
0238: 
0239:         rows.append(row)
```

### Around line 317
```python
0315:         "clean_integrity_jsd": ["integrity_jsd_clean"],
0316:         "clean_integrity_mmd": ["integrity_mmd_clean"],
0317:         "clean_integrity_ks_mean": ["integrity_ks_mean_clean"],
0318:         "clean_integrity_ks_reject05": ["integrity_ks_reject05_clean"],
0319:         "clean_integrity_score_jsd": ["integrity_score_jsd_clean"],
```

### Around line 380
```python
0378:             "integrity_jsd",
0379:             "integrity_mmd",
0380:             "integrity_ks_mean",
0381:             "integrity_ks_reject05",
0382:             "integrity_score_jsd",
```

### Around line 386
```python
0384:             "clean_integrity_jsd",
0385:             "clean_integrity_mmd",
0386:             "clean_integrity_ks_mean",
0387:             "clean_integrity_ks_reject05",
0388:             "clean_integrity_score_jsd",
```

### Around line 394
```python
0392:             "integrity_jsd_delta",
0393:             "integrity_mmd_delta",
0394:             "integrity_ks_mean_delta",
0395:             "integrity_ks_reject05_delta",
0396:             "integrity_score_jsd_delta",
```

### Around line 402
```python
0400:             "integrity_jsd_vs_clean_eval",
0401:             "integrity_mmd_vs_clean_eval",
0402:             "integrity_ks_mean_vs_clean_eval",
0403:             "integrity_ks_reject05_vs_clean_eval",
0404:             "integrity_score_jsd_vs_clean_eval",
```

### Around line 578
```python
0576:         "integrity_jsd",
0577:         "integrity_mmd",
0578:         "integrity_ks_mean",
0579:         "integrity_ks_reject05",
0580:         "integrity_score_jsd",
```

### Around line 583
```python
0581:         "integrity_jsd_vs_clean_eval",
0582:         "integrity_mmd_vs_clean_eval",
0583:         "integrity_ks_mean_vs_clean_eval",
0584:         "integrity_ks_reject05_vs_clean_eval",
0585:         "integrity_score_jsd_vs_clean_eval",
```

### Around line 674
```python
0672:         "integrity_jsd",
0673:         "integrity_mmd",
0674:         "integrity_ks_mean",
0675:         "integrity_ks_reject05",
0676:         "integrity_score_jsd",
```

### Around line 679
```python
0677:         "integrity_jsd_vs_clean_eval",
0678:         "integrity_mmd_vs_clean_eval",
0679:         "integrity_ks_mean_vs_clean_eval",
0680:         "integrity_ks_reject05_vs_clean_eval",
0681:         "integrity_score_jsd_vs_clean_eval",
```

### Around line 852
```python
0850:         "integrity_jsd",
0851:         "integrity_mmd",
0852:         "integrity_ks_mean",
0853:         "integrity_ks_reject05",
0854:         "integrity_score_jsd",
```

### Around line 857
```python
0855:         "integrity_jsd_delta",
0856:         "integrity_mmd_delta",
0857:         "integrity_ks_mean_delta",
0858:         "integrity_ks_reject05_delta",
0859:         "integrity_score_jsd_delta",
```

### Around line 863
```python
0861:         "integrity_jsd_vs_clean_eval",
0862:         "integrity_mmd_vs_clean_eval",
0863:         "integrity_ks_mean_vs_clean_eval",
0864:         "integrity_ks_reject05_vs_clean_eval",
0865:         "integrity_score_jsd_vs_clean_eval",
```

## Pattern `protocol` — 35 hits

### Around line 121
```python
0119: 
0120: 
0121: def _dataset_tag_from_path(csv_path: Path, protocol: str) -> str:
0122:     """
0123:     Parse dataset tags from runner filenames.
```

### Around line 129
```python
0127:     """
0128:     name = csv_path.name
0129:     if str(protocol).lower() == "ood":
0130:         m = _OOD_RE.search(name)
0131:         if m:
```

### Around line 480
```python
0478:         out,
0479:         [
0480:             "protocol",
0481:             "svd_dim",
0482:             "model_family",
```

### Around line 500
```python
0498:         out,
0499:         [
0500:             "protocol",
0501:             "model_family",
0502:             "model",
```

### Around line 510
```python
0508:         ],
0509:     )
0510:     if "protocol" in out.columns:
0511:         out["protocol"] = out["protocol"].astype(str).str.lower()
0512: 
```

### Around line 511
```python
0509:     )
0510:     if "protocol" in out.columns:
0511:         out["protocol"] = out["protocol"].astype(str).str.lower()
0512: 
0513:     out = normalize_runner_schema(out, verbose=verbose)
```

### Around line 520
```python
0518:     src = out["__source_file"].astype(str)
0519:     file_to_proto = (
0520:         out.drop_duplicates("__source_file")[["__source_file", "protocol"]]
0521:         .set_index("__source_file")["protocol"]
0522:     )
```

### Around line 521
```python
0519:     file_to_proto = (
0520:         out.drop_duplicates("__source_file")[["__source_file", "protocol"]]
0521:         .set_index("__source_file")["protocol"]
0522:     )
0523: 
```

### Around line 525
```python
0523: 
0524:     unique_files = pd.DataFrame({"__source_file": src.unique()})
0525:     unique_files["protocol"] = unique_files["__source_file"].map(file_to_proto).fillna("id").astype(str)
0526:     unique_files["dataset_tag_from_file"] = unique_files.apply(
0527:         lambda row: _dataset_tag_from_path(Path(row["__source_file"]), str(row["protocol"])),
```

### Around line 527
```python
0525:     unique_files["protocol"] = unique_files["__source_file"].map(file_to_proto).fillna("id").astype(str)
0526:     unique_files["dataset_tag_from_file"] = unique_files.apply(
0527:         lambda row: _dataset_tag_from_path(Path(row["__source_file"]), str(row["protocol"])),
0528:         axis=1,
0529:     )
```

### Around line 540
```python
0538: 
0539:     if verbose:
0540:         n_bad = int(((out["protocol"] == "ood") & (~out["dataset_tag"].astype(str).str.startswith("tr"))).sum())
0541:         if n_bad:
0542:             print(f"[WARN] {n_bad} OOD rows have dataset_tag not starting with 'tr' (filename tags missing?).")
```

### Around line 555
```python
0553: 
0554:     IMPORTANT:
0555:     We scope the clean join by (protocol, dataset_tag, run_id, attack_seed),
0556:     not just (run_id, attack_seed). This prevents cross-dataset contamination
0557:     when different datasets / OOD pairs share the same logical run_id.
```

### Around line 603
```python
0601:     current_metric_cols = [c for c in current_metric_cols if c in out.columns]
0602: 
0603:     scope_cols = [c for c in ["protocol", "dataset_tag"] if c in out.columns]
0604: 
0605:     baseline = out[out["is_clean"]][scope_cols + ["run_id", "attack_seed"] + current_metric_cols].copy()
```

### Around line 751
```python
0749: 
0750:     IMPORTANT:
0751:     We must include protocol + dataset_tag when using run_id-based de-duplication.
0752:     Otherwise, identical logical run_ids across different datasets / OOD pairs
0753:     can incorrectly collapse into a single row.
```

### Around line 756
```python
0754:     """
0755:     if prefer_run_id and "run_id" in df.columns:
0756:         subset = [c for c in ["protocol", "dataset_tag", "run_id", "attack_seed"] if c in df.columns]
0757:         before = int(len(df))
0758:         df2 = df.drop_duplicates(subset=subset, keep="last").copy()
```

### Around line 766
```python
0764:     key: List[str] = []
0765:     for c in [
0766:         "protocol",
0767:         "dataset_tag",
0768:         "split_seed",
```

### Around line 799
```python
0797: 
0798:     group_cols = [
0799:         "protocol",
0800:         "dataset_tag",
0801:         "svd_dim",
```

### Around line 942
```python
0940:     agg["__sort_clean"] = agg["attack"].astype(str).str.strip().str.lower().eq("clean").astype(int)
0941:     sort_cols = [
0942:         "protocol",
0943:         "dataset_tag",
0944:         "model_family",
```

### Around line 1083
```python
1081: 
1082:     if norm_group_cols is None:
1083:         norm_group_cols = [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in out.columns]
1084:     else:
1085:         norm_group_cols = [c for c in norm_group_cols if c in out.columns]
```

### Around line 1168
```python
1166:     out["stealth_rank_overall"] = np.nan
1167:     out["stealth_rank_within_model"] = np.nan
1168:     out["stealth_rank_within_protocol_dataset"] = np.nan
1169:     out["stealth_rank_within_protocol_dataset_model"] = np.nan
1170: 
```

## Pattern `dataset_tag` — 36 hits

### Around line 121
```python
0119: 
0120: 
0121: def _dataset_tag_from_path(csv_path: Path, protocol: str) -> str:
0122:     """
0123:     Parse dataset tags from runner filenames.
```

### Around line 301
```python
0299:     out = df.copy()
0300: 
0301:     # Prefer dataset_tag already written by richer runners. Fall back to filename parsing later.
0302:     if "dataset_tag" in out.columns:
0303:         out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()
```

### Around line 302
```python
0300: 
0301:     # Prefer dataset_tag already written by richer runners. Fall back to filename parsing later.
0302:     if "dataset_tag" in out.columns:
0303:         out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()
0304: 
```

### Around line 303
```python
0301:     # Prefer dataset_tag already written by richer runners. Fall back to filename parsing later.
0302:     if "dataset_tag" in out.columns:
0303:         out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()
0304: 
0305:     # Canonical clean-reference columns:
```

### Around line 515
```python
0513:     out = normalize_runner_schema(out, verbose=verbose)
0514: 
0515:     # dataset_tag:
0516:     # 1) prefer existing non-empty dataset_tag from runner
0517:     # 2) fallback to parsing from source filename
```

### Around line 516
```python
0514: 
0515:     # dataset_tag:
0516:     # 1) prefer existing non-empty dataset_tag from runner
0517:     # 2) fallback to parsing from source filename
0518:     src = out["__source_file"].astype(str)
```

### Around line 526
```python
0524:     unique_files = pd.DataFrame({"__source_file": src.unique()})
0525:     unique_files["protocol"] = unique_files["__source_file"].map(file_to_proto).fillna("id").astype(str)
0526:     unique_files["dataset_tag_from_file"] = unique_files.apply(
0527:         lambda row: _dataset_tag_from_path(Path(row["__source_file"]), str(row["protocol"])),
0528:         axis=1,
```

### Around line 527
```python
0525:     unique_files["protocol"] = unique_files["__source_file"].map(file_to_proto).fillna("id").astype(str)
0526:     unique_files["dataset_tag_from_file"] = unique_files.apply(
0527:         lambda row: _dataset_tag_from_path(Path(row["__source_file"]), str(row["protocol"])),
0528:         axis=1,
0529:     )
```

### Around line 530
```python
0528:         axis=1,
0529:     )
0530:     file_to_tag = unique_files.set_index("__source_file")["dataset_tag_from_file"].to_dict()
0531: 
0532:     if "dataset_tag" not in out.columns:
```

### Around line 532
```python
0530:     file_to_tag = unique_files.set_index("__source_file")["dataset_tag_from_file"].to_dict()
0531: 
0532:     if "dataset_tag" not in out.columns:
0533:         out["dataset_tag"] = src.map(file_to_tag).fillna("idNA").astype(str).str.strip()
0534:     else:
```

### Around line 533
```python
0531: 
0532:     if "dataset_tag" not in out.columns:
0533:         out["dataset_tag"] = src.map(file_to_tag).fillna("idNA").astype(str).str.strip()
0534:     else:
0535:         missing = out["dataset_tag"].astype(str).str.strip().isin({"", "nan", "None"})
```

### Around line 535
```python
0533:         out["dataset_tag"] = src.map(file_to_tag).fillna("idNA").astype(str).str.strip()
0534:     else:
0535:         missing = out["dataset_tag"].astype(str).str.strip().isin({"", "nan", "None"})
0536:         out.loc[missing, "dataset_tag"] = src[missing].map(file_to_tag).fillna("idNA")
0537:         out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()
```

### Around line 536
```python
0534:     else:
0535:         missing = out["dataset_tag"].astype(str).str.strip().isin({"", "nan", "None"})
0536:         out.loc[missing, "dataset_tag"] = src[missing].map(file_to_tag).fillna("idNA")
0537:         out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()
0538: 
```

### Around line 537
```python
0535:         missing = out["dataset_tag"].astype(str).str.strip().isin({"", "nan", "None"})
0536:         out.loc[missing, "dataset_tag"] = src[missing].map(file_to_tag).fillna("idNA")
0537:         out["dataset_tag"] = out["dataset_tag"].astype(str).str.strip()
0538: 
0539:     if verbose:
```

### Around line 540
```python
0538: 
0539:     if verbose:
0540:         n_bad = int(((out["protocol"] == "ood") & (~out["dataset_tag"].astype(str).str.startswith("tr"))).sum())
0541:         if n_bad:
0542:             print(f"[WARN] {n_bad} OOD rows have dataset_tag not starting with 'tr' (filename tags missing?).")
```

### Around line 542
```python
0540:         n_bad = int(((out["protocol"] == "ood") & (~out["dataset_tag"].astype(str).str.startswith("tr"))).sum())
0541:         if n_bad:
0542:             print(f"[WARN] {n_bad} OOD rows have dataset_tag not starting with 'tr' (filename tags missing?).")
0543: 
0544:     return out
```

### Around line 555
```python
0553: 
0554:     IMPORTANT:
0555:     We scope the clean join by (protocol, dataset_tag, run_id, attack_seed),
0556:     not just (run_id, attack_seed). This prevents cross-dataset contamination
0557:     when different datasets / OOD pairs share the same logical run_id.
```

### Around line 603
```python
0601:     current_metric_cols = [c for c in current_metric_cols if c in out.columns]
0602: 
0603:     scope_cols = [c for c in ["protocol", "dataset_tag"] if c in out.columns]
0604: 
0605:     baseline = out[out["is_clean"]][scope_cols + ["run_id", "attack_seed"] + current_metric_cols].copy()
```

### Around line 751
```python
0749: 
0750:     IMPORTANT:
0751:     We must include protocol + dataset_tag when using run_id-based de-duplication.
0752:     Otherwise, identical logical run_ids across different datasets / OOD pairs
0753:     can incorrectly collapse into a single row.
```

### Around line 756
```python
0754:     """
0755:     if prefer_run_id and "run_id" in df.columns:
0756:         subset = [c for c in ["protocol", "dataset_tag", "run_id", "attack_seed"] if c in df.columns]
0757:         before = int(len(df))
0758:         df2 = df.drop_duplicates(subset=subset, keep="last").copy()
```

## Pattern `svd_dim` — 14 hits

### Around line 340
```python
0338:         out,
0339:         [
0340:             "svd_dim",
0341:             "seed",
0342:             "split_seed",
```

### Around line 481
```python
0479:         [
0480:             "protocol",
0481:             "svd_dim",
0482:             "model_family",
0483:             "model",
```

### Around line 770
```python
0768:         "split_seed",
0769:         "model_seed",
0770:         "svd_dim",
0771:         "model_family",
0772:         "model",
```

### Around line 801
```python
0799:         "protocol",
0800:         "dataset_tag",
0801:         "svd_dim",
0802:         "model_family",
0803:         "model",
```

### Around line 947
```python
0945:         "model",
0946:         "scale",
0947:         "svd_dim",
0948:     ]
0949:     for c in ["attack_suite", "attack_priority_group"]:
```

### Around line 1083
```python
1081: 
1082:     if norm_group_cols is None:
1083:         norm_group_cols = [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in out.columns]
1084:     else:
1085:         norm_group_cols = [c for c in norm_group_cols if c in out.columns]
```

### Around line 1227
```python
1225:     # 1) Clean summary by model/dim
1226:     if not clean.empty:
1227:         group_cols = [c for c in ["protocol", "dataset_tag", "model_family", "model", "svd_dim"] if c in clean.columns]
1228:         metrics = [
1229:             c for c in [
```

### Around line 1244
```python
1242:             clean_summary = clean[group_cols + metrics].copy()
1243:             clean_summary = clean_summary.sort_values(
1244:                 [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in clean_summary.columns],
1245:                 ascending=True,
1246:                 na_position="last",
```

### Around line 1254
```python
1252:     # 2) Attacked summary by model/dim/family/severity
1253:     if not attacked.empty:
1254:         group_cols = [c for c in ["protocol", "dataset_tag", "model_family", "model", "svd_dim", "attack_family", "attack_strength_nominal"] if c in attacked.columns]
1255:         if "attack_priority_group" in attacked.columns:
1256:             group_cols.append("attack_priority_group")
```

### Around line 1278
```python
1276:             )
1277:             attacked_summary = attacked_summary.sort_values(
1278:                 [c for c in ["protocol", "dataset_tag", "model", "svd_dim", "attack_family", "attack_strength_nominal"] if c in attacked_summary.columns],
1279:                 ascending=True,
1280:                 na_position="last",
```

### Around line 1292
```python
1290:                 "protocol",
1291:                 "dataset_tag",
1292:                 "svd_dim",
1293:                 "model_family",
1294:                 "model",
```

### Around line 1332
```python
1330:     # 4) Stealth by model
1331:     if not attacked.empty and "model" in attacked.columns:
1332:         group_cols = [c for c in ["protocol", "dataset_tag", "model_family", "model", "svd_dim"] if c in attacked.columns]
1333:         metrics = [
1334:             c for c in [
```

### Around line 1358
```python
1356:             )
1357: 
1358:             sort_cols = [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in by_model.columns] + ["stealth_score_mean"]
1359:             ascending = [True] * (len(sort_cols) - 1) + [False]
1360:             by_model = by_model.sort_values(sort_cols, ascending=ascending, na_position="last")
```

### Around line 1423
```python
1421:         "--norm-group-cols",
1422:         type=str,
1423:         default="protocol,dataset_tag,model,svd_dim",
1424:         help="Comma-separated grouping columns for detectability normalization.",
1425:     )
```

## Pattern `model` — 43 hits

### Around line 9
```python
0007: #   - join each attacked row with its clean baseline
0008: #   - aggregate across seeds into a paper-friendly table
0009: #   - preserve per-model granularity (do NOT collapse all QSVC under one family)
0010: #   - remain compatible with BOTH:
0011: #       * legacy/current runner outputs
```

### Around line 343
```python
0341:             "seed",
0342:             "split_seed",
0343:             "model_seed",
0344:             "attack_seed",
0345:             "clean_ref_attack_seed",
```

### Around line 482
```python
0480:             "protocol",
0481:             "svd_dim",
0482:             "model_family",
0483:             "model",
0484:             "scale",
```

### Around line 483
```python
0481:             "svd_dim",
0482:             "model_family",
0483:             "model",
0484:             "scale",
0485:             "attack",
```

### Around line 501
```python
0499:         [
0500:             "protocol",
0501:             "model_family",
0502:             "model",
0503:             "scale",
```

### Around line 502
```python
0500:             "protocol",
0501:             "model_family",
0502:             "model",
0503:             "scale",
0504:             "attack",
```

### Around line 769
```python
0767:         "dataset_tag",
0768:         "split_seed",
0769:         "model_seed",
0770:         "svd_dim",
0771:         "model_family",
```

### Around line 771
```python
0769:         "model_seed",
0770:         "svd_dim",
0771:         "model_family",
0772:         "model",
0773:         "scale",
```

### Around line 772
```python
0770:         "svd_dim",
0771:         "model_family",
0772:         "model",
0773:         "scale",
0774:         "attack_suite",
```

### Around line 802
```python
0800:         "dataset_tag",
0801:         "svd_dim",
0802:         "model_family",
0803:         "model",
0804:         "scale",
```

### Around line 803
```python
0801:         "svd_dim",
0802:         "model_family",
0803:         "model",
0804:         "scale",
0805:     ]
```

### Around line 918
```python
0916:         row["n_runs"] = int(len(sub))
0917: 
0918:         seed_unit_cols = [c for c in ["split_seed", "model_seed"] if c in sub.columns]
0919:         if seed_unit_cols:
0920:             row["n_seed_units"] = int(sub[seed_unit_cols].drop_duplicates().shape[0])
```

### Around line 944
```python
0942:         "protocol",
0943:         "dataset_tag",
0944:         "model_family",
0945:         "model",
0946:         "scale",
```

### Around line 945
```python
0943:         "dataset_tag",
0944:         "model_family",
0945:         "model",
0946:         "scale",
0947:         "svd_dim",
```

### Around line 1083
```python
1081: 
1082:     if norm_group_cols is None:
1083:         norm_group_cols = [c for c in ["protocol", "dataset_tag", "model", "svd_dim"] if c in out.columns]
1084:     else:
1085:         norm_group_cols = [c for c in norm_group_cols if c in out.columns]
```

### Around line 1167
```python
1165: 
1166:     out["stealth_rank_overall"] = np.nan
1167:     out["stealth_rank_within_model"] = np.nan
1168:     out["stealth_rank_within_protocol_dataset"] = np.nan
1169:     out["stealth_rank_within_protocol_dataset_model"] = np.nan
```

### Around line 1169
```python
1167:     out["stealth_rank_within_model"] = np.nan
1168:     out["stealth_rank_within_protocol_dataset"] = np.nan
1169:     out["stealth_rank_within_protocol_dataset_model"] = np.nan
1170: 
1171:     if len(attacked_idx) > 0:
```

### Around line 1176
```python
1174:         )
1175: 
1176:         if "model" in out.columns:
1177:             out.loc[attacked_idx, "stealth_rank_within_model"] = (
1178:                 out.loc[attacked_idx]
```

### Around line 1177
```python
1175: 
1176:         if "model" in out.columns:
1177:             out.loc[attacked_idx, "stealth_rank_within_model"] = (
1178:                 out.loc[attacked_idx]
1179:                 .groupby("model", dropna=False)["stealth_score_mean"]
```

### Around line 1179
```python
1177:             out.loc[attacked_idx, "stealth_rank_within_model"] = (
1178:                 out.loc[attacked_idx]
1179:                 .groupby("model", dropna=False)["stealth_score_mean"]
1180:                 .rank(method="dense", ascending=False)
1181:             )
```

# Heuristic checks
- MISSING: mentions shared normalization
- OK: mentions detectability
- OK: mentions stealth
- OK: mentions protocol
- OK: mentions dataset_tag
- OK: mentions svd_dim
- OK: mentions model