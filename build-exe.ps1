param()

$ErrorActionPreference = "Stop"

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "Virtualenv belum ada. Jalankan dulu: .\build-windows.ps1"
}

Write-Host "Install/Update PyInstaller..."
& $venvPython -m pip install --upgrade pyinstaller

$distDir = Join-Path $PSScriptRoot "dist-exe"
$buildDir = Join-Path $PSScriptRoot "build-exe"
$specDir = Join-Path $PSScriptRoot "spec-exe"

if (-not (Test-Path $specDir)) {
  New-Item -ItemType Directory -Path $specDir | Out-Null
}

Write-Host "Building GUI EXE..."
& $venvPython -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name printer-tool-gui `
  --distpath $distDir `
  --workpath $buildDir `
  --specpath $specDir `
  "$PSScriptRoot\gui.py"

Write-Host "Building CLI EXE..."
& $venvPython -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --console `
  --name printer-tool-cli `
  --distpath $distDir `
  --workpath $buildDir `
  --specpath $specDir `
  "$PSScriptRoot\main.py"

Write-Host "Selesai. EXE ada di: $distDir"

