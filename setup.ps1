# PowerShell Setup Script for TradingAgents Antigravity Plugin

Write-Host "Setting up Python Virtual Environment for TradingAgents..." -ForegroundColor Cyan

$VenvDir = Join-Path $PSScriptRoot ".venv"

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment at $VenvDir..."
    python -m venv $VenvDir
}

$PipExe = Join-Path $VenvDir "Scripts\pip.exe"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "Upgrading pip..."
& $PipExe install --upgrade pip

Write-Host "Installing dependencies from pyproject.toml..."
& $PipExe install -e $PSScriptRoot

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "To configure your API keys, copy .env.example to .env and set your GOOGLE_API_KEY." -ForegroundColor Yellow
