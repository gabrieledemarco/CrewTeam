# PowerShell Script to Run CrewAI Multi-Agent System
# This script properly activates the venv and runs main.py from the correct directory

# Ensure we're in the CREW directory
$CREW_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $CREW_ROOT

Write-Host "🚀 CrewAI Multi-Agent Development System Launcher" -ForegroundColor Cyan
Write-Host "📂 Working Directory: $(Get-Location)" -ForegroundColor Green
Write-Host "🐍 Checking Python environment..." -ForegroundColor Yellow
Write-Host ""

# Verify venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found at venv\Scripts\Activate.ps1" -ForegroundColor Red
    Write-Host "Please run: py -3.12 -m venv venv" -ForegroundColor Yellow
    Exit 1
}

# Activate venv
Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

# Verify crewai is installed
Write-Host "✓ Verifying CrewAI installation..." -ForegroundColor Green
py -c "import crewai; print('  ✅ CrewAI module found')" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CrewAI not found. Installing dependencies..." -ForegroundColor Red
    py -m pip install -q crewai crewai-tools langchain langchain-openai litellm python-dotenv requests PyYAML
}

# Run the main application
Write-Host ""
Write-Host "✓ Launching CrewAI application..." -ForegroundColor Green
Write-Host ""
py src/coding_crew/main.py

# Deactivate venv when done
Write-Host ""
Write-Host "👋 CrewAI session ended. Virtual environment still active." -ForegroundColor Cyan
Write-Host "Type 'deactivate' to exit the virtual environment." -ForegroundColor Gray
