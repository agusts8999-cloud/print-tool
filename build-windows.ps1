param()

$ErrorActionPreference = "Stop"

Write-Host "Membuat virtualenv (.venv)..."
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  & $py.Source -3 -m venv .venv
} else {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    throw "Python tidak ditemukan. Install Python 3.11+ dulu."
  }
  & $python.Source -m venv .venv
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "Gagal membuat virtualenv."
}

Write-Host "Meng-install dependency Python..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "Selesai. Jalankan tool dengan: .\run-printer-tool.ps1 <args>"
