# Paper 1.5 Q1 expansion - stable exact-statevector queue
#
# Replaces the stalled pairwise compute-uncompute evaluator with the validated
# exact-statevector engine.  The output tag records qbexact_statevector, so these
# artifacts cannot be confused with shot-based or hardware execution.
#
# Re-running is safe: every gate uses --resume.
# Monitor:
#   Get-Content results\logs\paper15_q1_exact_queue_console.log -Tail 30 -Wait

$ErrorActionPreference = "Continue"
$repo = "C:\Users\masteria.DOMINE\rf\paper_HAIS"
$python = Join-Path $repo ".venv\Scripts\python.exe"
$log = Join-Path $repo "results\logs\paper15_q1_exact_queue_console.log"

Set-Location $repo
$env:PYTHONUNBUFFERED = "1"
"[EXACT-QUEUE] start $(Get-Date -Format s) pid=$PID" |
    Tee-Object -FilePath $log -Append

$common128 = @(
    "--dims", "8,10,12",
    "--split-seeds", "42,43,44,45,46",
    "--model-seeds", "42,43",
    "--attack-suite", "paper_core",
    "--max-train", "128",
    "--max-test", "128",
    "--q-reps", "1",
    "--q-backend-method", "exact_statevector",
    "--q-shots", "1024",
    "--q-max-iter", "1000",
    "--n-jobs", "2",
    "--allow-parallel-quantum",
    "--resume",
    "--retries", "1",
    "--max-fails", "5"
)

$gates = @(
    @{ name = "gate2a_id_size256_zz_svc"
       common = $common128
       args = @("--protocol", "id", "--id-data", "data/cicids_subset.csv",
                "--q-feature-maps", "zz",
                "--outdir", "results/raw/paper15_q1_gate2a_id_size256_zz_svc",
                "--log-dir", "results/logs/paper15_q1_gate2a_exact",
                "--max-train", "256", "--max-test", "256") },
    @{ name = "gate3a_ood_tue_wed_zz_svc"
       common = $common128
       args = @("--protocol", "ood",
                "--data-train", "data/processed/cicids_ood_tuesday_train.csv",
                "--data-test", "data/processed/cicids_ood_wednesday_test.csv",
                "--q-feature-maps", "zz",
                "--outdir", "results/raw/paper15_q1_gate3a_ood_tue_wed_zz_svc",
                "--log-dir", "results/logs/paper15_q1_gate3a_exact") },
    @{ name = "gate3b_ood_tue_fri_portscan_zz_svc"
       common = $common128
       args = @("--protocol", "ood",
                "--data-train", "data/processed/cicids_ood_tuesday_train_portscan.csv",
                "--data-test", "data/processed/cicids_ood_friday_portscan_test.csv",
                "--q-feature-maps", "zz",
                "--outdir", "results/raw/paper15_q1_gate3b_ood_tue_fri_portscan_zz_svc",
                "--log-dir", "results/logs/paper15_q1_gate3b_exact") },
    @{ name = "gate3c_ood_wed_thu_webattacks_zz_svc"
       common = $common128
       args = @("--protocol", "ood",
                "--data-train", "data/processed/cicids_ood_wednesday_train.csv",
                "--data-test", "data/processed/cicids_ood_thursday_webattacks_test.csv",
                "--q-feature-maps", "zz",
                "--outdir", "results/raw/paper15_q1_gate3c_ood_wed_thu_webattacks_zz_svc",
                "--log-dir", "results/logs/paper15_q1_gate3c_exact") },
    @{ name = "gate3d_ood_wed_fri_morning_zz_svc"
       common = $common128
       args = @("--protocol", "ood",
                "--data-train", "data/processed/cicids_ood_wednesday_train.csv",
                "--data-test", "data/processed/cicids_ood_friday_morning_test.csv",
                "--q-feature-maps", "zz",
                "--outdir", "results/raw/paper15_q1_gate3d_ood_wed_fri_morning_zz_svc",
                "--log-dir", "results/logs/paper15_q1_gate3d_exact") },
    @{ name = "gate5a_id_unsw_fmaps"
       common = $common128
       args = @("--protocol", "id", "--id-data", "data/unsw_subset.csv",
                "--q-feature-maps", "zz,z,pauli_xyz",
                "--outdir", "results/raw/paper15_q1_gate5a_id_unsw_fmaps",
                "--log-dir", "results/logs/paper15_q1_gate5a_exact") },
    @{ name = "gate5b_id_ton_iot_fmaps"
       common = $common128
       args = @("--protocol", "id", "--id-data", "data/ton_iot_subset.csv",
                "--q-feature-maps", "zz,z,pauli_xyz",
                "--outdir", "results/raw/paper15_q1_gate5b_id_ton_iot_fmaps",
                "--log-dir", "results/logs/paper15_q1_gate5b_exact") },
    @{ name = "gate6_ood_unsw_zz_svc"
       common = $common128
       args = @("--protocol", "ood",
                "--data-train", "data/processed/unsw_ood_train.csv",
                "--data-test", "data/processed/unsw_ood_test.csv",
                "--q-feature-maps", "zz",
                "--outdir", "results/raw/paper15_q1_gate6_ood_unsw_zz_svc",
                "--log-dir", "results/logs/paper15_q1_gate6_exact") }
)

foreach ($gate in $gates) {
    "[EXACT-QUEUE] ===== $($gate.name) start $(Get-Date -Format s) =====" |
        Tee-Object -FilePath $log -Append
    & $python -m src.experiments.run_grid @($gate.common) @($gate.args) *>> $log
    "[EXACT-QUEUE] ===== $($gate.name) end $(Get-Date -Format s) exit=$LASTEXITCODE =====" |
        Tee-Object -FilePath $log -Append
}

"[EXACT-QUEUE] all gates finished $(Get-Date -Format s)" |
    Tee-Object -FilePath $log -Append
