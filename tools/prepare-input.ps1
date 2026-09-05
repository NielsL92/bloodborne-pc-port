param(
    [Parameter(Mandatory=$true)][string]$Package,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [switch]$AllFiles
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pkgPath = (Resolve-Path -LiteralPath $Package).Path
$outputPath = [IO.Path]::GetFullPath($OutputDirectory)
$pkgToolDirectory = Join-Path $projectRoot 'external\bin\PkgTool'
$library = Join-Path $pkgToolDirectory 'LibOrbisPkg.dll'
if (!(Test-Path -LiteralPath $library)) { throw 'The official LibOrbisPkg DLL must be in external/bin/PkgTool.' }
if ((Test-Path -LiteralPath $outputPath) -and (Get-ChildItem -LiteralPath $outputPath -Force | Select-Object -First 1)) {
    throw 'Use an empty output directory. Existing extracted files will not be overwritten.'
}
$compilerCSharp = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$extractorExe = Join-Path $pkgToolDirectory 'ExtractCode.exe'
& $compilerCSharp /nologo /platform:x64 /target:exe "/out:$extractorExe" "/reference:$library" (Join-Path $PSScriptRoot 'ExtractCode.cs')
if ($LASTEXITCODE -ne 0) { throw 'Could not compile the selective extractor.' }
if ($AllFiles) { & $extractorExe $pkgPath $outputPath --all }
else { & $extractorExe $pkgPath $outputPath }
if ($LASTEXITCODE -ne 0) { throw 'Extraction failed.' }
