param()

$ErrorActionPreference = "Stop"

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "Virtualenv belum ada. Jalankan build dulu: .\build-windows.ps1"
}

Write-Host "Menjalankan printer-tool..."
& $venvPython (Join-Path $PSScriptRoot "main.py") @args
