# Helper scripts

## `verify_datasets.py`

Cross-platform (standard library only) hash verifier for the benchmark data
used by the frozen evidence. It reads the staging reports written when the
tables were produced (`data/*.prep_report.json`,
`data/processed/*.prep_report.json`, `data/raw/staging/stage_report.json`) and
recomputes the SHA-256 of

- every staged table under `data/` and `data/processed/` that exists, and
- every raw source file that exists under
  `data/raw/cicids2017/MachineLearningCVE/`,
  `data/raw/unsw_nb15/Training and Testing Sets/` and `data/raw/ton_iot/`.

It prints one line per file (`OK`, `MISMATCH`, `MISSING`) and exits with a
non-zero code on any mismatch. Missing raw sources are reported but do not
fail the run unless `--require-raw` is given; missing staged tables do not
fail unless `--require-staged` is given.

```powershell
# PowerShell 7 (Windows, Linux, macOS)
python scripts/verify_datasets.py            # staged tables; raw sources if present
python scripts/verify_datasets.py --require-raw --require-staged   # full replay precondition
```

```bash
# POSIX shell
python3 scripts/verify_datasets.py
python3 scripts/verify_datasets.py --require-raw --require-staged
```

The datasets themselves are not redistributed with this repository; see
`REPRODUCIBILITY.md` for their official sources, staging commands and the
expected hashes.
