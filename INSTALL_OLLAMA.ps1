# ============================================================================
# OLLAMA INSTALLATION SCRIPT (PowerShell Version)
# ============================================================================
# Installa Ollama e scarica i modelli necessari per CrewAI
#

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                        ║" -ForegroundColor Cyan
Write-Host "║                  🚀 OLLAMA INSTALLATION SCRIPT 🚀                      ║" -ForegroundColor Cyan
Write-Host "║                                                                        ║" -ForegroundColor Cyan
Write-Host "║   Questo script installerà Ollama e i modelli per CREW                ║" -ForegroundColor Cyan
Write-Host "║                                                                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# STEP 1: Check if Ollama is already installed
# ============================================================================
Write-Host "[STEP 1] Verifico se Ollama è già installato..." -ForegroundColor Yellow
$OllamaExists = $null -ne (Get-Command ollama -ErrorAction SilentlyContinue)

if ($OllamaExists) {
    Write-Host "✅ Ollama è già installato!" -ForegroundColor Green
    ollama --version
    Write-Host ""
    $InstallNeeded = $false
} else {
    Write-Host "❌ Ollama NON è ancora installato" -ForegroundColor Red
    Write-Host ""
    $InstallNeeded = $true
}

# ============================================================================
# STEP 2: Download Ollama if needed
# ============================================================================
if ($InstallNeeded) {
    Write-Host "[STEP 2] Download Ollama Setup..." -ForegroundColor Yellow
    Write-Host ""
    
    $DownloadUrl = "https://ollama.ai/download/OllamaSetup.exe"
    $DownloadPath = "$env:USERPROFILE\Downloads\OllamaSetup.exe"
    
    if (Test-Path $DownloadPath) {
        Write-Host "✅ OllamaSetup.exe trovato in Downloads" -ForegroundColor Green
    } else {
        Write-Host "Scaricando da: $DownloadUrl" -ForegroundColor Cyan
        Write-Host "Salvo in: $DownloadPath" -ForegroundColor Cyan
        Write-Host ""
        
        try {
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $DownloadUrl -OutFile $DownloadPath -TimeoutSec 300
            $FileSize = (Get-Item $DownloadPath).Length / 1MB
            Write-Host "✅ Download completato!" -ForegroundColor Green
            Write-Host "📦 Dimensione: $([math]::Round($FileSize, 2)) MB" -ForegroundColor Green
        } catch {
            Write-Host "❌ Download automatico fallito: $_" -ForegroundColor Red
            Write-Host ""
            Write-Host "🔗 Scarica manualmente da: https://ollama.ai/download" -ForegroundColor Yellow
            $DownloadPath = Read-Host "Inserisci il percorso completo di OllamaSetup.exe"
            
            if (-not (Test-Path $DownloadPath)) {
                Write-Host "❌ File non trovato: $DownloadPath" -ForegroundColor Red
                exit 1
            }
        }
    }
    
    Write-Host ""
    
    # ============================================================================
    # STEP 3: Install Ollama
    # ============================================================================
    Write-Host "[STEP 3] Avvio Ollama Setup..." -ForegroundColor Yellow
    Write-Host ""
    
    & $DownloadPath
    
    Write-Host ""
    Write-Host "⏳ Attendo completamento installazione..." -ForegroundColor Yellow
    Write-Host "   (Potrebbe richiedere alcuni minuti)" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Premi ENTER quando l'installazione è completata"
    Write-Host ""
}

# ============================================================================
# STEP 4: Verify installation
# ============================================================================
Write-Host "[STEP 4] Verifico l'installazione..." -ForegroundColor Yellow

$OllamaExists = $null -ne (Get-Command ollama -ErrorAction SilentlyContinue)

if ($OllamaExists) {
    Write-Host "✅ Ollama installato con successo!" -ForegroundColor Green
    Write-Host ""
    ollama --version
    Write-Host ""
} else {
    Write-Host "❌ Ollama non trovato." -ForegroundColor Red
    Write-Host "💡 Prova a riavviare il computer" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# STEP 5: Start Ollama server and download models
# ============================================================================
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "[STEP 5] Download dei modelli LLM" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Modelli da scaricare:" -ForegroundColor Cyan
Write-Host "  1. codellama:7b    (Specializzato per codice)" -ForegroundColor White
Write-Host "  2. llama2:7b       (General purpose)" -ForegroundColor White
Write-Host ""
Write-Host "Questo richiederà alcuni minuti (dipende dalla connessione)" -ForegroundColor Yellow
Write-Host ""

Write-Host "Avvio Ollama server in background..." -ForegroundColor Yellow
$OllamaProcess = Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized -PassThru

Write-Host "⏳ Attendo avvio server (~10 secondi)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# ============================================================================
# STEP 6: Download models
# ============================================================================
Write-Host "Scaricamento modelli in corso..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📥 Scaricando codellama:7b..." -ForegroundColor Yellow
& ollama pull codellama:7b

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ codellama:7b scaricato con successo" -ForegroundColor Green
} else {
    Write-Host "⚠️  Errore durante il download di codellama:7b" -ForegroundColor Yellow
}

Write-Host ""

Write-Host "📥 Scaricando llama2:7b..." -ForegroundColor Yellow
& ollama pull llama2:7b

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ llama2:7b scaricato con successo" -ForegroundColor Green
} else {
    Write-Host "⚠️  Errore durante il download di llama2:7b" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 7: List available models
# ============================================================================
Write-Host "[STEP 6] Modelli disponibili:" -ForegroundColor Yellow
Write-Host ""
& ollama list
Write-Host ""

# ============================================================================
# Completion message
# ============================================================================
Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                        ║" -ForegroundColor Green
Write-Host "║              ✅ OLLAMA INSTALLATION COMPLETED! ✅                      ║" -ForegroundColor Green
Write-Host "║                                                                        ║" -ForegroundColor Green
Write-Host "║  Ollama server è in esecuzione (minimizzato in background).            ║" -ForegroundColor Green
Write-Host "║                                                                        ║" -ForegroundColor Green
Write-Host "║  NEXT STEPS:                                                           ║" -ForegroundColor Green
Write-Host "║  1. Torna a VS Code / PowerShell                                       ║" -ForegroundColor Green
Write-Host "║  2. Esegui: python src/coding_crew/main.py                            ║" -ForegroundColor Green
Write-Host "║  3. Il sistema CREW dovrebbe partire!                                  ║" -ForegroundColor Green
Write-Host "║                                                                        ║" -ForegroundColor Green
Write-Host "║  ⚠️  IMPORTANTE: Mantieni la finestra Ollama server aperta!            ║" -ForegroundColor Green
Write-Host "║                                                                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Read-Host "Premi ENTER per terminare"
