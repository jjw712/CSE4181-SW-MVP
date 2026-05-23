param(
  [switch]$SkipInstall,
  [switch]$NoRun,
  [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $RootDir "frontend"

function Resolve-NodeDir {
  $pathCandidates = @()

  try {
    $pathCandidates = (& where.exe node 2>$null) | ForEach-Object {
      if ($_ -and ($_ -notmatch "\\WindowsApps\\")) {
        Split-Path -Parent $_
      }
    }
  } catch {
    $pathCandidates = @()
  }

  $candidates = @(
    (Join-Path $env:ProgramFiles "nodejs")
  )

  if (${env:ProgramFiles(x86)}) {
    $candidates += Join-Path ${env:ProgramFiles(x86)} "nodejs"
  }

  $candidates += $pathCandidates

  foreach ($candidate in $candidates) {
    $node = Join-Path $candidate "node.exe"
    $npm = Join-Path $candidate "npm.cmd"

    if ((Test-Path -LiteralPath $node) -and (Test-Path -LiteralPath $npm)) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  throw "Node.js executable was not found. Install Node.js LTS or add it to PATH."
}

$NodeDir = Resolve-NodeDir
$Node = Join-Path $NodeDir "node.exe"
$Npm = Join-Path $NodeDir "npm.cmd"
$env:Path = "$NodeDir;$env:Path"

Write-Host "Using Node: $Node"
Write-Host "Using npm: $Npm"

if ($CheckOnly) {
  exit 0
}

Set-Location $FrontendDir

if (-not $SkipInstall) {
  Write-Host "Installing frontend dependencies..."
  & $Npm install
}

if (-not $NoRun) {
  Write-Host "Starting Vite on http://localhost:5173"
  & $Npm run dev
}
