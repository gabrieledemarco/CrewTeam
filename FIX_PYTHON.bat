@echo off
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║         Ricreazione Virtual Environment - Python 3.12         ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Verifico versioni Python disponibili...
py --list-paths
echo.

echo.
echo Opzioni disponibili:
echo  1. Ricrea venv con Python 3.12 (CONSIGLIATO)
echo  2. Ricrea venv con Python 3.13
echo  3. Usa Python 3.14 (potrebbe non funzionare)
echo.

set /p CHOICE="Scegli (1, 2 o 3): "

if "%CHOICE%"=="1" (
    echo.
    echo Eliminazione venv precedente...
    rmdir /s /q venv
    echo.
    echo Creazione venv con Python 3.12...
    py -3.12 -m venv venv
    if errorlevel 1 (
        echo Errore: Python 3.12 non trovato!
        pause
        exit /b 1
    )
) else if "%CHOICE%"=="2" (
    echo.
    echo Eliminazione venv precedente...
    rmdir /s /q venv
    echo.
    echo Creazione venv con Python 3.13...
    py -3.13 -m venv venv
    if errorlevel 1 (
        echo Errore: Python 3.13 non trovato!
        pause
        exit /b 1
    )
) else if "%CHOICE%"=="3" (
    echo Prosegui con Python 3.14 (non supportato)
) else (
    echo Scelta non valida!
    pause
    exit /b 1
)

echo.
echo Attivazione venv...
call venv\Scripts\activate.bat

echo.
echo Aggiornamento pip...
python -m pip install --upgrade pip

echo.
echo Installazione dipendenze...
pip install crewai crewai-tools langchain langchain-openai litellm python-dotenv requests PyYAML

echo.
echo ✅ Setup completato!
echo.
pause
