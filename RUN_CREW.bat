@echo off
REM Script di avvio per CREW - CrewAI Multi-Agent Development System
REM Questo script attiva l'ambiente virtuale e avvia il sistema

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║        🚀 CREW - Multi-Agent Development System 🚀            ║
echo ║                                                                ║
echo ║     PMO → Architect → Code Writer → Reviewer → Tester        ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verifica che Ollama sia accessibile
echo ⏳ Checking Ollama connection...
curl -s http://192.168.1.7:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  ATTENZIONE: Ollama non è raggiungibile!
    echo.
    echo Per favore assicurati che Ollama sia in esecuzione:
    echo.
    echo 1. Apri PowerShell
    echo 2. Esegui:
    echo    $env:OLLAMA_HOST = "0.0.0.0:11434"
    echo    ^& ollama serve
    echo.
    echo 3. Poi riprova questo script
    echo.
    pause
    goto end
)

echo ✅ Ollama trovato!
echo.

REM Attiva il virtual environment locale
echo Attivazione ambiente virtuale locale...
call "%~dp0venv\Scripts\activate.bat"

if errorlevel 1 (
    echo.
    echo ❌ Errore: Virtual environment locale non trovato!
    echo.
    echo Per favore installa prima l'ambiente:
    echo   cd "%~dp0"
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    goto end
)

echo ✅ Ambiente attivato!
echo.

REM Naviga al progetto
cd /d "%~dp0src\coding_crew"

if errorlevel 1 (
    echo ❌ Errore: Non riesco a navigare alla cartella del progetto!
    pause
    goto end
)

REM Esegui il sistema
echo Avvio CREW...
echo.
python main.py

:end
pause
