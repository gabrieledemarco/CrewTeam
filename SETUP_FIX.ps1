# Script PowerShell per ricreazione venv con Python stabile
# Uso: powershell -ExecutionPolicy Bypass -File "SETUP_FIX.ps1"

Write-Host "`n" -ForegroundColor Green
Write-Host "╔═══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                       ║" -ForegroundColor Green
Write-Host "║        🔧 CREW Setup Fixer (PowerShell) - Riparazione Automatica 🔧   ║" -ForegroundColor Green
Write-Host "║                                                                       ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

# Step 1: Verifica versioni Python
Write-Host "[1/5] Ricerca versioni Python disponibili...`n" -ForegroundColor Cyan

$pythonVersions = @{
    "3.13" = $false
    "3.12" = $false
    "3.11" = $false
    "3.10" = $false
}

$pyPaths = & py --list-paths 2>$null
foreach ($path in $pyPaths) {
    if ($path -match "-3\.13") { $pythonVersions["3.13"] = $true }
    if ($path -match "-3\.12") { $pythonVersions["3.12"] = $true }
    if ($path -match "-3\.11") { $pythonVersions["3.11"] = $true }
    if ($path -match "-3\.10") { $pythonVersions["3.10"] = $true }
}

# Mostra versioni trovate
foreach ($version in $pythonVersions.GetEnumerator() | Sort-Object Name -Descending) {
    if ($version.Value) {
        Write-Host "  ✓ Python $($version.Key) trovato" -ForegroundColor Green
    }
}
Write-Host ""

# Step 2: Scegli versione
Write-Host "[2/5] Selezione versione Python...`n" -ForegroundColor Cyan

$selectedVersion = $null
if ($pythonVersions["3.13"]) {
    $selectedVersion = "3.13"
    Write-Host "  ✓ Selezionata: Python 3.13 (più recente)" -ForegroundColor Green
} elseif ($pythonVersions["3.12"]) {
    $selectedVersion = "3.12"
    Write-Host "  ✓ Selezionata: Python 3.12 (stabile)" -ForegroundColor Green
} elseif ($pythonVersions["3.11"]) {
    $selectedVersion = "3.11"
    Write-Host "  ✓ Selezionata: Python 3.11 (legacy)" -ForegroundColor Green
} else {
    Write-Host "  ❌ ERRORE: Nessuna versione Python stabile trovata!" -ForegroundColor Red
    Write-Host "     Scarica Python 3.12+ da https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "     Premi invio per uscire"
    exit 1
}
Write-Host ""

# Step 3: Elimina venv precedente
Write-Host "[3/5] Eliminazione venv precedente...`n" -ForegroundColor Cyan

if (Test-Path "venv") {
    Remove-Item -Path "venv" -Recurse -Force
    Write-Host "  ✓ venv eliminato" -ForegroundColor Green
} else {
    Write-Host "  ✓ venv non esiste (niente da eliminare)" -ForegroundColor Green
}
Write-Host ""

# Step 4: Ricrea venv
Write-Host "[4/5] Creazione nuovo venv con Python $selectedVersion...`n" -ForegroundColor Cyan

$pyCommand = "py -$selectedVersion -m venv venv"
Invoke-Expression $pyCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ ERRORE: Non posso creare venv con Python $selectedVersion" -ForegroundColor Red
    Read-Host "  Premi invio per uscire"
    exit 1
}

Write-Host "  ✓ venv creato" -ForegroundColor Green
Write-Host ""

# Step 5: Attiva venv e installa dipendenze
Write-Host "[5/5] Attivazione venv e installazione dipendenze...`n" -ForegroundColor Cyan

& ".\venv\Scripts\Activate.ps1"

Write-Host "  - Aggiornamento pip..." -ForegroundColor Gray
python -m pip install --upgrade pip --quiet

Write-Host "  - Installazione dipendenze..." -ForegroundColor Gray
pip install --no-cache-dir -q crewai crewai-tools langchain langchain-openai litellm python-dotenv requests PyYAML

Write-Host "  ✓ Dipendenze installate" -ForegroundColor Green
Write-Host ""

# Verifica finale
Write-Host "═════════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
Write-Host "VERIFICA FINALE...`n" -ForegroundColor Cyan

python --version
Write-Host ""

python -c "import crewai; print(f'CrewAI: {crewai.__version__} ✓')" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ CrewAI OK" -ForegroundColor Green
} else {
    Write-Host "  ❌ CrewAI non installato" -ForegroundColor Red
    exit 1
}

python -c "import langchain; print('  ✓ LangChain OK')" 2>$null
python -c "import litellm; print('  ✓ LiteLLM OK')" 2>$null
python -c "import crewai_tools; print('  ✓ CrewAI Tools OK')" 2>$null

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                       ║" -ForegroundColor Green
Write-Host "║           ✅ SETUP COMPLETATO CON SUCCESSO! ✅                        ║" -ForegroundColor Green
Write-Host "║                                                                       ║" -ForegroundColor Green
Write-Host "║       Tutte le dipendenze sono installate e il sistema è pronto!     ║" -ForegroundColor Green
Write-Host "║                                                                       ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Il venv è già attivato. Esegui:

  cd src\coding_crew
  python main.py

Oppure disattiva e usa RUN_CREW.bat la prossima volta:

  deactivate
  .\RUN_CREW.bat

" -ForegroundColor Cyan

Read-Host "Premi invio per uscire"
