param(
    [string]$Eboot = 'local/update/uroot/eboot.bin',
    [string]$BasePackage = 'E:\ROMS\PS4\Bloodborne.pkg',
    [string]$UpdatePackage = 'E:\ROMS\PS4\Bloodborne v1.09 patch.pkg'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location -LiteralPath $projectRoot
try {
    $projectPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (!(Test-Path -LiteralPath $projectPython)) { throw 'Create the project Python environment and install requirements.txt first.' }
    & $projectPython -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Parser or recompiler tests failed.' }
    & $projectPython -m tools.analyze --eboot $Eboot --pkg $BasePackage --pkg $UpdatePackage
    if ($LASTEXITCODE -ne 0) { throw 'Executable analysis failed.' }
    & $projectPython -m tools.recompiler_selftest
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic instruction translation failed.' }
    & (Join-Path $PSScriptRoot 'build-proof.cmd') selftest
    if ($LASTEXITCODE -ne 0) { throw 'Native instruction tests failed.' }
    & $projectPython -m tools.recompile --eboot $Eboot
    if ($LASTEXITCODE -ne 0) { throw 'Game leaf translation failed.' }
    & (Join-Path $PSScriptRoot 'build-proof.cmd')
    if ($LASTEXITCODE -ne 0) { throw 'Game leaf differential verification failed.' }
    Write-Output 'Verification complete. This verifies a limited recompilation proof, not a playable game.'
} finally {
    Pop-Location
}
