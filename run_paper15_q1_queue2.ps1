# Paper 1.5 Q1 expansion - experiment queue 2 (multi-dataset)
#
# Waits for queue 1 (run_paper15_q1_queue.ps1: gate2a + gates 3a-3d) to finish,
# re-runs queue 1 once in resume mode (self-healing: no-op if it completed,
# finishes the remainder if it died), then runs the new-dataset gates:
#
#   Gate 5a : ID UNSW-NB15 subset   (zz,z,pauli_xyz vs SVC, 128/128, 10 seed-units)
#   Gate 5b : ID TON_IoT subset     (zz,z,pauli_xyz vs SVC, 128/128, 10 seed-units)
#   Gate 6  : OOD UNSW train->test  (zz vs SVC, 128/128, 10 seed-units)
#
# All gates use --resume: re-running this script is always safe.
# Monitor:  Get-Content results\logs\paper15_q1_queue2_console.log -Tail 20 -Wait

$ErrorActionPreference = "Continue"
# The script lives at the repository root; no machine-specific path is required.
$repo   = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$python = Join-Path $repo ".venv/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $python)) { $python = Join-Path $repo ".venv/bin/python" }
if (-not (Test-Path -LiteralPath $python)) { throw "No virtual environment found under $repo/.venv (expected Scripts/python.exe or bin/python)" }
$log    = Join-Path $repo "results/logs/paper15_q1_queue2_console.log"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $log) | Out-Null

Set-Location $repo
"[QUEUE2] start $(Get-Date -Format s)  pid=$PID" | Tee-Object -FilePath $log -Append

# ---- Wait for queue 1 (pwsh runner and/or its run_grid python) to finish ----
function Test-Queue1Alive {
    if (-not $IsWindows) { return $false }  # Win32_Process is Windows-only; on other platforms run queue 1 first
    $procs = Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' or Name='python.exe'" |
        Where-Object {
            ($_.CommandLine -like "*run_paper15_q1_queue.ps1*") -or
            ($_.CommandLine -like "*src.experiments.run_grid*")
        }
    return ($procs | Measure-Object).Count -gt 0
}

while (Test-Queue1Alive) {
    "[QUEUE2] waiting for queue 1 ... $(Get-Date -Format s)" | Tee-Object -FilePath $log -Append
    Start-Sleep -Seconds 900
}

"[QUEUE2] queue 1 no longer running $(Get-Date -Format s); re-running it in resume mode (self-heal)" |
    Tee-Object -FilePath $log -Append
& pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repo "run_paper15_q1_queue.ps1")
"[QUEUE2] queue 1 resume pass done $(Get-Date -Format s)" | Tee-Object -FilePath $log -Append

# ---- New-dataset gates ----
$commonBase = @(
    "--dims", "8,10,12",
    "--split-seeds", "42,43,44,45,46",
    "--model-seeds", "42,43",
    "--attack-suite", "paper_core",
    "--max-train", "128",
    "--max-test", "128",
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
    @{ name = "gate5a_id_unsw_fmaps"
       args = @("--protocol","id","--id-data","data/unsw_subset.csv",
                "--q-feature-maps","zz,z,pauli_xyz",
                "--outdir","results/raw/paper15_q1_gate5a_id_unsw_fmaps",
                "--log-dir","results/logs/paper15_q1_gate5a_id_unsw_fmaps") },
    @{ name = "gate5b_id_ton_iot_fmaps"
       args = @("--protocol","id","--id-data","data/ton_iot_subset.csv",
                "--q-feature-maps","zz,z,pauli_xyz",
                "--outdir","results/raw/paper15_q1_gate5b_id_ton_iot_fmaps",
                "--log-dir","results/logs/paper15_q1_gate5b_id_ton_iot_fmaps") },
    @{ name = "gate6_ood_unsw_zz_svc"
       args = @("--protocol","ood",
                "--data-train","data/processed/unsw_ood_train.csv",
                "--data-test","data/processed/unsw_ood_test.csv",
                "--q-feature-maps","zz",
                "--outdir","results/raw/paper15_q1_gate6_ood_unsw_zz_svc",
                "--log-dir","results/logs/paper15_q1_gate6_ood_unsw_zz_svc") }
)

foreach ($g in $gates) {
    "[QUEUE2] ===== $($g.name) start $(Get-Date -Format s) =====" | Tee-Object -FilePath $log -Append
    & $python -m src.experiments.run_grid @($g.args) @commonBase *>> $log
    "[QUEUE2] ===== $($g.name) end $(Get-Date -Format s) exit=$LASTEXITCODE =====" | Tee-Object -FilePath $log -Append
}

"[QUEUE2] all gates finished $(Get-Date -Format s)" | Tee-Object -FilePath $log -Append
