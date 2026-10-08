Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$repo = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$temporary = Join-Path ([System.IO.Path]::GetTempPath()) ("sensorsieve-check-" + [guid]::NewGuid().ToString('N'))
$env:UV_CACHE_DIR = Join-Path $repo '.uv-cache'

function Assert-ExitCode([int]$Expected, [string]$Label) {
    if ($LASTEXITCODE -ne $Expected) {
        throw "$Label returned $LASTEXITCODE; expected $Expected"
    }
}

function Assert-DirectoryEqual([string]$Expected, [string]$Actual) {
    $expectedFiles = @(Get-ChildItem -LiteralPath $Expected -File | Sort-Object Name)
    $actualFiles = @(Get-ChildItem -LiteralPath $Actual -File | Sort-Object Name)
    if (($expectedFiles.Name -join "`n") -ne ($actualFiles.Name -join "`n")) {
        throw "artifact names differ between $Expected and $Actual"
    }
    foreach ($expectedFile in $expectedFiles) {
        $actualFile = Join-Path $Actual $expectedFile.Name
        $expectedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $expectedFile.FullName).Hash
        $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $actualFile).Hash
        if ($expectedHash -ne $actualHash) {
            throw "artifact differs: $($expectedFile.Name)"
        }
    }
}

Push-Location -LiteralPath $repo
try {
    New-Item -ItemType Directory -Path $temporary | Out-Null

    & uv sync --frozen --extra dev
    Assert-ExitCode 0 'uv sync'

    & uv run ruff check .
    Assert-ExitCode 0 'ruff check'

    & uv run ruff format --check .
    Assert-ExitCode 0 'ruff format check'

    & uv run mypy src tests scripts
    Assert-ExitCode 0 'mypy'

    & uv run pytest --basetemp (Join-Path $temporary 'pytest') --cov=sensorsieve --cov-branch --cov-fail-under=90
    Assert-ExitCode 0 'pytest'

    if (Test-Path -LiteralPath (Join-Path $repo 'dist')) {
        Remove-Item -LiteralPath (Join-Path $repo 'dist') -Recurse -Force
    }
    & uv --cache-dir (Join-Path $temporary 'build-cache') build
    Assert-ExitCode 0 'package build'

    & uv run pip-audit --cache-dir (Join-Path $temporary 'audit-cache')
    Assert-ExitCode 0 'dependency audit'

    & uv run python scripts/build_examples.py
    Assert-ExitCode 0 'example generation'

    & git -c "safe.directory=$($repo.Replace('\', '/'))" diff --exit-code -- examples
    Assert-ExitCode 0 'example determinism'

    $beforeOutput = Join-Path $temporary 'before'
    $comparisonOutput = Join-Path $temporary 'comparison'
    $cleanOutput = Join-Path $temporary 'clean'
    $invalidOutput = Join-Path $temporary 'invalid'

    & uv run sensorsieve inspect examples/before --output $beforeOutput
    Assert-ExitCode 1 'dirty example inspect'

    & uv run sensorsieve compare examples/before examples/after --output $comparisonOutput
    Assert-ExitCode 1 'before/after example compare'

    & uv run sensorsieve inspect examples/clean --output $cleanOutput
    Assert-ExitCode 0 'clean example inspect'

    & uv run sensorsieve inspect examples/invalid-too-few --output $invalidOutput
    Assert-ExitCode 2 'invalid example inspect'
    if (Test-Path -LiteralPath $invalidOutput) {
        throw 'invalid example created an output directory'
    }

    Assert-DirectoryEqual (Join-Path $repo 'docs/demo/before') $beforeOutput
    Assert-DirectoryEqual (Join-Path $repo 'docs/demo/comparison') $comparisonOutput

    $wheel = Get-ChildItem -Path (Join-Path $repo 'dist/*.whl') | Select-Object -First 1
    if ($null -eq $wheel) {
        throw 'wheel was not built'
    }
    & uvx --from $wheel.FullName sensorsieve --version
    Assert-ExitCode 0 'wheel version smoke'

    $wheelOutput = Join-Path $temporary 'wheel-clean'
    & uvx --from $wheel.FullName sensorsieve inspect examples/clean --output $wheelOutput
    Assert-ExitCode 0 'wheel clean-example smoke'

    Write-Output 'SENSORSIEVE_RELEASE_GATE=PASS'
}
finally {
    Pop-Location
    if (Test-Path -LiteralPath $temporary) {
        Remove-Item -LiteralPath $temporary -Recurse -Force
    }
}
