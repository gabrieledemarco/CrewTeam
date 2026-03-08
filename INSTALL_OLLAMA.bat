@echo off
REM ============================================================================
REM  OLLAMA INSTALLATION SCRIPT
REM ============================================================================
REM
REM Questo script installa Ollama e i modelli necessari per CrewAI
REM

setlocal enabledelayedexpansion
cls

echo.
echo ============================================================================
echo                    OLLAMA INSTALLATION SCRIPT
echo                                                                            
echo   Questo script installerà Ollama e i modelli necessari per CREW          
echo ============================================================================
echo.

REM ============================================================================
REM STEP 1: Check if Ollama is already installed
REM ============================================================================
echo [STEP 1] Verifico se Ollama è gia installato...
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    echo OK - Ollama è già installato!
    ollama --version
    echo.
    goto step_download_models
) else (
    echo Ollama NON è ancora installato
    echo.
)

REM ============================================================================
REM STEP 2: Download Ollama
REM ============================================================================
echo [STEP 2] Download Ollama Setup...
echo.

set DOWNLOAD_PATH=%USERPROFILE%\Downloads\OllamaSetup.exe

if exist "%DOWNLOAD_PATH%" (
    echo OK - OllamaSetup.exe trovato in Downloads
    goto step_install
)

echo.
echo SCARICAMENTO MANUALE RICHIESTO:
echo.
echo 1. Apri questo link nel browser:
echo    https://ollama.ai/download
echo.
echo 2. Scarica "Ollama for Windows"
echo.
echo 3. Attendi il download (circa 150-200 MB)
echo.
echo 4. Una volta scaricato, torna qui e digita ENTER
echo.
pause

if not exist "%DOWNLOAD_PATH%" (
    echo.
    echo ERRORE: OllamaSetup.exe non trovato in Downloads
    echo Se lo hai salvato in un'altra cartella, per favore copialo in:
    echo %USERPROFILE%\Downloads\
    echo.
    pause
    goto :eof
)

echo.

REM ============================================================================
REM STEP 3: Install Ollama
REM ============================================================================
:step_install
if exist "%DOWNLOAD_PATH%" (
    echo [STEP 3] Avvio Ollama Setup...
    echo.
    "%DOWNLOAD_PATH%"
    echo.
    echo ⏳ Aspetto che l'installazione sia completata...
    echo    (Questo potrebbe richiedere alcuni minuti)
    echo.
    pause
) else (
    echo ❌ OllamaSetup.exe non trovato
    goto :eof
)

REM ============================================================================
REM STEP 4: Verify installation
REM ============================================================================
echo [STEP 4] Verifico l'installazione...
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama installato con successo!
    echo.
    ollama --version
    echo.
) else (
    echo ❌ Ollama non trovato. Riavvia il computer e prova di nuovo.
    pause
    goto :eof
)

REM ============================================================================
REM STEP 5: Download required models
REM ============================================================================
:step_download_models
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [STEP 5] Download dei modelli LLM necessari per CREW
echo ════════════════════════════════════════════════════════════════════════
echo.
echo Modelli da scaricare:
echo  1. codellama:7b    (Specializzato per generazione codice)
echo  2. llama2:7b       (Modello general purpose)
echo.
echo Questo richiederà alcuni minuti (dipende dalla velocità di connessione)
echo.
echo Avvio Ollama server...
echo.

REM ============================================================================
REM STEP 6: Start Ollama server in background
REM ============================================================================
echo Avviando Ollama server...
start "Ollama Server" cmd /k "ollama serve"

REM Attendi che il server si avvii
echo ⏳ Attendo avvio server Ollama (~10 secondi)...
timeout /t 10 /nobreak

REM ============================================================================
REM STEP 7: Download models
REM ============================================================================
echo.
echo Scaricando codellama:7b...
ollama pull codellama:7b
if %errorlevel% neq 0 (
    echo ⚠️  Errore durante il download di codellama:7b
)

echo.
echo Scaricando llama2:7b...
ollama pull llama2:7b
if %errorlevel% neq 0 (
    echo ⚠️  Errore durante il download di llama2:7b
)

echo.

REM ============================================================================
REM STEP 8: Verify models
REM ============================================================================
echo [STEP 6] Verifico i modelli scaricati...
echo.
ollama list
echo.

REM ============================================================================
REM COMPLETION
REM ============================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║              ✅ OLLAMA INSTALLATION COMPLETED! ✅                      ║
echo ║                                                                        ║
echo ║  Ollama server dovrebbe essere running in una finestra separata.      ║
echo ║                                                                        ║
echo ║  NEXT STEPS:                                                           ║
echo ║  1. Tornare a VS Code                                                  ║
echo ║  2. Eseguire: python src/coding_crew/main.py                           ║
echo ║  3. Il sistema CREW dovrebbe partire correttamente                     ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo Premi un tasto per chiudere...
pause
