# File di setup environment per Windows PowerShell


Write-Host "🔧 Configurando variabili d'ambiente CREW..." -ForegroundColor Cyan
Write-Host

# Configurazione Ollama
$env:OLLAMA_HOST = "http://localhost:11434"
$env:OLLAMA_API_KEY = "not-needed"

# Configurazione Modello Predefinito
$env:CREW_DEFAULT_MODEL = "codellama:7b"

# Verifica configurazione
Write-Host "✅ Variabili d'ambiente configurate:" -ForegroundColor Green
Write-Host "   OLLAMA_HOST=$env:OLLAMA_HOST"
Write-Host "   CREW_DEFAULT_MODEL=$env:CREW_DEFAULT_MODEL"
Write-Host "   OLLAMA_API_KEY=$env:OLLAMA_API_KEY"
Write-Host

# Attiva venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔌 Attivazione virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Ambiente attivato" -ForegroundColor Green
} else {
    Write-Host "❌ Errore: virtual environment non trovato!" -ForegroundColor Red
    Write-Host "Crea con: python -m venv venv"
    exit 1
}

Write-Host
Write-Host "✨ Setup completato! Puoi ora eseguire il progetto:" -ForegroundColor Cyan
Write-Host "   cd src\coding_crew"
Write-Host "   python main.py"
Write-Host

# Opzione: esegui direttamente
# $response = Read-Host "Vuoi eseguire il progetto adesso? (S/N)"
# if ($response -eq "S" -or $response -eq "s") {
#     cd src\coding_crew
#     python main.py
# }
