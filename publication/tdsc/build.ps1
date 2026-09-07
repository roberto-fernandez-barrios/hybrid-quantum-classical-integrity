$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$sourceDir = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$stageDir = Join-Path $repoRoot (Join-Path 'tmp' ('tdsc-build-' + [guid]::NewGuid().ToString('N')))
$pdfDir = Join-Path $repoRoot 'output\pdf'

New-Item -ItemType Directory -Path $stageDir | Out-Null
New-Item -ItemType Directory -Force -Path $pdfDir | Out-Null
Copy-Item -LiteralPath (Join-Path $sourceDir 'main.tex') -Destination $stageDir
Copy-Item -LiteralPath (Join-Path $sourceDir 'supplement.tex') -Destination $stageDir
Copy-Item -LiteralPath (Join-Path $sourceDir 'references.bib') -Destination $stageDir
Copy-Item -LiteralPath (Join-Path $sourceDir 'figures') -Destination $stageDir -Recurse
if (Test-Path (Join-Path $sourceDir 'tables')) {
    Copy-Item -LiteralPath (Join-Path $sourceDir 'tables') -Destination $stageDir -Recurse
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed with exit code $LASTEXITCODE"
    }
}

Push-Location $stageDir
try {
    Invoke-Checked pdflatex '-interaction=nonstopmode' '-halt-on-error' 'main.tex' | Out-Null
    Invoke-Checked bibtex 'main' | Out-Null
    Invoke-Checked pdflatex '-interaction=nonstopmode' '-halt-on-error' 'main.tex' | Out-Null
    Invoke-Checked pdflatex '-interaction=nonstopmode' '-halt-on-error' 'main.tex' | Out-Null
    Invoke-Checked pdflatex '-interaction=nonstopmode' '-halt-on-error' 'supplement.tex' | Out-Null
    Invoke-Checked pdflatex '-interaction=nonstopmode' '-halt-on-error' 'supplement.tex' | Out-Null

    $fatalPattern = 'LaTeX Warning|Overfull \\hbox|undefined references|Citation.*undefined|Reference.*undefined'
    $logProblems = Select-String -LiteralPath 'main.log','supplement.log' -Pattern $fatalPattern | Where-Object {
        # An overfull box of at most 1pt is within the production reflow tolerance; anything larger fails.
        # A supplement page made only of full-width tables is a layout notice, not a defect; the main article must not have one.
        if ($_.Line -match 'Overfull \\hbox \(([0-9.]+)pt too wide\)') { [double]$Matches[1] -gt 1.0 }
        elseif ($_.Line -match 'contains only floats' -and $_.Filename -eq 'supplement.log') { $false }
        else { $true }
    }
    if ($logProblems) {
        $rendered = $logProblems | ForEach-Object { $_.ToString() }
        throw "LaTeX preflight failed:`n$($rendered -join [Environment]::NewLine)"
    }

    $mainInfo = Invoke-Checked pdfinfo 'main.pdf'
    $supplementInfo = Invoke-Checked pdfinfo 'supplement.pdf'
    $mainPagesLine = $mainInfo | Select-String '^Pages:'
    $supplementPagesLine = $supplementInfo | Select-String '^Pages:'
    $mainPages = [int](($mainPagesLine.ToString() -split ':')[1].Trim())
    $supplementPages = [int](($supplementPagesLine.ToString() -split ':')[1].Trim())
    if ($mainPages -gt 12) {
        throw "Main article has $mainPages pages; the internal ceiling is 12."
    }

    Copy-Item -LiteralPath 'main.pdf' -Destination (Join-Path $pdfDir 'paper15_tdsc_submission.pdf') -Force
    Copy-Item -LiteralPath 'supplement.pdf' -Destination (Join-Path $pdfDir 'paper15_tdsc_supplement.pdf') -Force
    Write-Host "TDSC build passed: $mainPages main pages; $supplementPages supplement pages."
    Write-Host "Staging directory retained for audit: $stageDir"
}
finally {
    Pop-Location
}
