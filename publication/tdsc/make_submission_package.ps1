param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path $RepositoryRoot).Path
$version = (Get-Content -Raw (Join-Path $root "VERSION")).Trim()
if (-not $OutputPath) {
    $OutputPath = Join-Path $root "publication\paper15-tdsc-source-v$version.zip"
}
$target = [System.IO.Path]::GetFullPath($OutputPath)
if (-not $target.StartsWith([System.IO.Path]::GetFullPath((Join-Path $root "publication")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Submission source ZIP must remain under publication/."
}

$stage = Join-Path $root "tmp\tdsc-source-v$version"
if (Test-Path -LiteralPath $stage) {
    $resolvedStage = [System.IO.Path]::GetFullPath($stage)
    if (-not $resolvedStage.StartsWith([System.IO.Path]::GetFullPath((Join-Path $root "tmp")), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to replace a staging directory outside tmp/."
    }
    Remove-Item -LiteralPath $resolvedStage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null

foreach ($name in @("main.tex", "supplement.tex", "references.bib", "IEEEtran.cls", "build.ps1", "README.md", "SUPPLEMENT_README.md", "CLAIMS_TRACEABILITY.md", "VERSION")) {
    $source = Join-Path $PSScriptRoot $name
    if (Test-Path -LiteralPath $source) {
        Copy-Item -LiteralPath $source -Destination $stage
    }
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "figures") -Destination $stage -Recurse
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "tables") -Destination $stage -Recurse

if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Force
}
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $target -CompressionLevel Optimal
Write-Output $target
