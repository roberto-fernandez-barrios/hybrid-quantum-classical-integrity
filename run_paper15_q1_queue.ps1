# Paper 1.5 Q1 expansion - experiment queue
# Runs sequentially (each gate is --resume, so this script can be re-run safely):
#   Gate 2a : ID sample-size 256, ZZ vs SVC          (classical done -> only 30 quantum runs pending)
#   Gate 3a : OOD tuesday -> wednesday               (ZZ vs SVC, 128/128, 10 seed-units)
#   Gate 3b : OOD tuesday_portscan -> friday_portscan
#   Gate 3c : OOD wednesday -> thursday_webattacks
#   Gate 3d : OOD wednesday -> friday_morning
#
# Monitor:  Get-Content results\logs\paper15_q1_queue_console.log -Tail 20 -Wait
# Stop:     Get-Process | Where-Object { $_.ProcessName -match 'python' } | Stop-Process
#           (or kill the pwsh process whose PID is written at the top of the log)

$ErrorActionPreference = "Continue"
$repo   = "C:\Users\masteria.DOMINE\rf\paper_HAIS"
$python = Join-Path $repo ".venv\Scripts\python.exe"
$log    = Join-Path $repo "results\logs\paper15_q1_queue_console.log"

Set-Location $repo
"[QUEUE] start $(Get-Date -Format s)  pid=$PID" | Tee-Object -FilePath $log -Append

$common = @(
    "--dims", "8,10,12",
    "--split-seeds", "42,43,44,45,46",
    "--model-seeds", "42,43",
    "--q-feature-maps", "zz",
    "--attack-suite", "paper_core",
    "--q-reps", "1",
    "--q-backend-method", "statevector",
    "--q-shots", "1024",
    "--q-max-iter", "1000",
    "--n-jobs", "10",
    "--allow-parallel-quantum",
    "--run-both",
    "--resume",
    "--retries", "1",
    "--max-fails", "5"
)

$gates = @(
    @{ name = "gate2a_id_size256_zz_svc"
       args = @("--protocol","id","--id-data","data/cicids_subset.csv",
                "--outdir","results/raw/paper15_q1_gate2a_id_size256_zz_svc",
                "--log-dir","results/logs/paper15_q1_gate2a_id_size256_zz_svc",
                "--max-train","256","--max-test","256") },
    @{ name = "gate3a_ood_tue_wed_zz_svc"
       args = @("--protocol","ood",
                "--data-train","data/processed/cicids_ood_tuesday_train.csv",
                "--data-test","data/processed/cicids_ood_wednesday_test.csv",
                "--outdir","results/raw/paper15_q1_gate3a_ood_tue_wed_zz_svc",
                "--log-dir","results/logs/paper15_q1_gate3a_ood_tue_wed_zz_svc",
                "--max-train","128","--max-test","128") },
    @{ name = "gate3b_ood_tue_fri_portscan_zz_svc"
       args = @("--protocol","ood",
                "--data-train","data/processed/cicids_ood_tuesday_train_portscan.csv",
                "--data-test","data/processed/cicids_ood_friday_portscan_test.csv",
                "--outdir","results/raw/paper15_q1_gate3b_ood_tue_fri_portscan_zz_svc",
                "--log-dir","results/logs/paper15_q1_gate3b_ood_tue_fri_portscan_zz_svc",
                "--max-train","128","--max-test","128") },
    @{ name = "gate3c_ood_wed_thu_webattacks_zz_svc"
       args = @("--protocol","ood",
                "--data-train","data/processed/cicids_ood_wednesday_train.csv",
                "--data-test","data/processed/cicids_ood_thursday_webattacks_test.csv",
                "--outdir","results/raw/paper15_q1_gate3c_ood_wed_thu_webattacks_zz_svc",
                "--log-dir","results/logs/paper15_q1_gate3c_ood_wed_thu_webattacks_zz_svc",
                "--max-train","128","--max-test","128") },
    @{ name = "gate3d_ood_wed_fri_morning_zz_svc"
       args = @("--protocol","ood",
                "--data-train","data/processed/cicids_ood_wednesday_train.csv",
                "--data-test","data/processed/cicids_ood_friday_morning_test.csv",
                "--outdir","results/raw/paper15_q1_gate3d_ood_wed_fri_morning_zz_svc",
                "--log-dir","results/logs/paper15_q1_gate3d_ood_wed_fri_morning_zz_svc",
                "--max-train","128","--max-test","128") }
)

foreach ($g in $gates) {
    "[QUEUE] ===== $($g.name) start $(Get-Date -Format s) =====" | Tee-Object -FilePath $log -Append
    & $python -m src.experiments.run_grid @($g.args) @common *>> $log
    "[QUEUE] ===== $($g.name) end $(Get-Date -Format s) exit=$LASTEXITCODE =====" | Tee-Object -FilePath $log -Append
}

"[QUEUE] all gates finished $(Get-Date -Format s)" | Tee-Object -FilePath $log -Append
