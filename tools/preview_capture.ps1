param([Parameter(Mandatory=$true)][string]$Source,[Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$previewPath = [System.IO.Path]::GetFullPath($Destination)
if ([System.IO.File]::Exists($previewPath)) { throw 'Use a new preview filename.' }
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($previewPath)) | Out-Null
$previewImage = [System.Drawing.Image]::FromFile([System.IO.Path]::GetFullPath($Source))
try { $previewImage.Save($previewPath, [System.Drawing.Imaging.ImageFormat]::Jpeg) } finally { $previewImage.Dispose() }
Write-Output $previewPath
