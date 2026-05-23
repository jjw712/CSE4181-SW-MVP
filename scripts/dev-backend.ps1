param(
  [switch]$SkipInstall,
  [switch]$NoRun,
  [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"
$VenvDir = Join-Path $BackendDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

function Resolve-Python {
  $pathCandidates = @()

  try {
    $pathCandidates = (& where.exe python 2>$null) | Where-Object {
      $_ -and ($_ -notmatch "\\Microsoft\\WindowsApps\\")
    }
  } catch {
    $pathCandidates = @()
  }

  $candidates = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
    (Join-Path $env:ProgramFiles "Python312\python.exe"),
    (Join-Path $env:ProgramFiles "Python311\python.exe")
  ) + $pathCandidates

  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  throw "Python executable was not found. Install Python 3.12 or add it to PATH."
}

$SystemPython = Resolve-Python
Write-Host "Using Python: $SystemPython"

if ($CheckOnly) {
  exit 0
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
  Write-Host "Creating backend virtual environment..."
  & $SystemPython -m venv $VenvDir
}

if (-not $SkipInstall) {
  Write-Host "Installing backend dependencies..."
  & $VenvPython -m pip install --upgrade pip
  & $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt")
}

if (-not $NoRun) {
  Set-Location $BackendDir
  Write-Host "Starting FastAPI on http://127.0.0.1:8000"
  & $VenvPython -m uvicorn app.main:app --reload
}
