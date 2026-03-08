@echo off
REM ============================================================================
REM  CREW Setup Fixer - Risolve automaticamente problemi Python e dipendenze
REM ============================================================================
REM
REM Questo script:
REM  1. Verifica versioni Python disponibili
REM  2. Sceglie Python 3.12/3.13 (stabile)
REM  3. Ricrea il venv
REM  4. Installa tutte le dipendenze senza errori di compilazione
REM
REM ============================================================================

setlocal enabledelayedexpansion
color 0A
cls

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║              🔧 CREW Setup Fixer - Riparazione Automatica 🔧           ║
echo ║                                                                        ║
echo ║   Questo script ricrea il venv con Python stabile (3.12 o 3.13)       ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM STEP 1: Verifica versioni Python disponibili
REM ============================================================================
echo [STEP 1/5] Ricerca versioni Python disponibili...
echo.

set PYTHON_312=0
set PYTHON_313=0
set PYTHON_311=0

for /f "tokens=*" %%i in ('py --list-paths 2^>nul') do (
    echo %%i | find "-3.12" >nul && set PYTHON_312=1
    echo %%i | find "-3.13" >nul && set PYTHON_313=1
    echo %%i | find "-3.11" >nul && set PYTHON_311=1
)

echo Python disponibili:
if !PYTHON_312! equ 1 echo   ✓ Python 3.12 trovato
if !PYTHON_313! equ 1 echo   ✓ Python 3.13 trovato
if !PYTHON_311! equ 1 echo   ✓ Python 3.11 trovato
echo.

REM ============================================================================
REM STEP 2: Scegli la versione da usare
REM ============================================================================
set PYTHON_VERSION=none

if !PYTHON_313! equ 1 (
    echo [STEP 2/5] Selezionata automaticamente: Python 3.13 (più recente)
    set PYTHON_VERSION=3.13
) else if !PYTHON_312! equ 1 (
    echo [STEP 2/5] Selezionata automaticamente: Python 3.12 (stabile)
    set PYTHON_VERSION=3.12
) else if !PYTHON_311! equ 1 (
    echo [STEP 2/5] Selezionata automaticamente: Python 3.11 (legacy)
    set PYTHON_VERSION=3.11
) else (
    echo.
    echo ❌ ERRORE: Nessuna versione Python stabile trovata!
    echo.
    echo Devi installare Python 3.12 o 3.13 da https://www.python.org/downloads/
    echo.
    echo Istruzioni:
    echo   1. Scarica Python 3.12.x (oppure 3.13.x)
    echo   2. Durante l'installazione, SPUNTA: "Add Python to PATH"
    echo   3. Riavvia questo script
    echo.
    pause
    exit /b 1
)

echo ✓ Versione scelta: Python !PYTHON_VERSION!
echo.

REM ============================================================================
REM STEP 3: Elimina venv precedente
REM ============================================================================
echo [STEP 3/5] Eliminazione venv precedente...
if exist venv (
    rmdir /s /q venv
    echo ✓ venv eliminato
) else (
    echo ✓ venv non esiste (non necessario eliminare)
)
echo.

REM ============================================================================
REM STEP 4: Ricrea venv con Python stabile
REM ============================================================================
echo [STEP 4/5] Creazione nuovo venv con Python !PYTHON_VERSION!...
py -!PYTHON_VERSION! -m venv venv

if errorlevel 1 (
    echo ❌ ERRORE: Non posso creare venv con Python !PYTHON_VERSION!
    pause
    exit /b 1
)

echo ✓ venv creato
echo.

REM ============================================================================
REM STEP 5: Attiva venv e installa dipendenze
REM ============================================================================
echo [STEP 5/5] Attivazione venv e installazione dipendenze...
call venv\Scripts\activate.bat

REM Aggiorna pip (CRITICO per evitare errori di compilazione)
echo.
echo   - Aggiornamento pip...
python -m pip install --upgrade pip --quiet

echo   - Installazione crewai e dipendenze...
pip install --no-cache-dir --quiet ^
    crewai ^
    crewai-tools ^
    langchain ^
    langchain-openai ^
    litellm ^
    python-dotenv ^
    requests ^
    PyYAML

if errorlevel 1 (
    echo.
    echo ⚠️  ERRORE durante l'installazione. Tentativo con opzioni alternative...
    echo.
    pip install --only-binary :all: crewai crewai-tools langchain langchain-openai litellm
)

echo.
echo ✓ Dipendenze installate
echo.

REM ============================================================================
REM VERIFICA FINALE
REM ============================================================================
echo ════════════════════════════════════════════════════════════════════════
echo VERIFICA FINALE...
echo ════════════════════════════════════════════════════════════════════════
echo.

python --version
echo.

python -c "import crewai; print(f'CrewAI: {crewai.__version__} ✓')" 2>nul
if errorlevel 1 (
    echo ❌ CrewAI non è installato correttamente
    pause
    exit /b 1
)

python -c "import langchain; print('LangChain ✓')" 2>nul
python -c "import litellm; print('LiteLLM ✓')" 2>nul
python -c "import crewai_tools; print('CrewAI Tools ✓')" 2>nul

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║                    ✅ SETUP COMPLETATO CON SUCCESSO! ✅               ║
echo ║                                                                        ║
echo ║              Tutte le dipendenze sono ora installate                  ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo Il venv è già attivato. Puoi ora eseguire:
echo.
echo   cd src\coding_crew
echo   python main.py
echo.
echo oppure disattivare e usare RUN_CREW.bat la prossima volta:
echo.
echo   deactivate
echo   .\RUN_CREW.bat
echo.
pause
