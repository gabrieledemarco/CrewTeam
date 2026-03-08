@echo off
REM Script per guidare all'installazione di Python 3.12
REM Se eseguito su Windows 10/11, apre direttamente il link di download

color 0A
cls

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║              🐍 Download Python 3.12 - Apertura Automatica 🐍         ║
echo ║                                                                        ║
echo ║          Questo script ti porterà direttamente al download             ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

echo ⏳ Apertura browser al link di download...
echo.
echo Attendi... Dovrebbe aprirsi una finestra del browser
echo.

REM Apri il link di download di Python 3.12 su python.org
start https://www.python.org/downloads/

echo.
echo ✓ Browser aperto!
echo.
echo Istruzioni:
echo   1. Scarica "Windows installer (64-bit)" dalla pagina Python 3.12
echo   2. Esegui il file scaricato
echo   3. ⚠️  IMPORTANTE: Spunta "Add Python 3.12 to PATH"
echo   4. Clicca "Install Now"
echo   5. Attendi completamento
echo   6. Riavvia il computer
echo   7. Esegui di nuovo SETUP_FIX.bat
echo.
echo.

REM Attendi 5 secondi prima di mostrare il riepilogo
timeout /t 5

echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║                    📋 RIEPILOGO PROCEDURA                             ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo PASSO 1: Python.org dovrebbe essersi aperto nel browser
echo          Se no, visita manualmente: https://www.python.org/downloads/
echo.
echo PASSO 2: Nella pagina, scorri e trova "Python 3.12.x"
echo          Clicca: "Windows installer (64-bit)"
echo.
echo PASSO 3: File .exe sarà nella cartella Download
echo          Doppio click su python-3.12.x-amd64.exe
echo.
echo PASSO 4: Nella finestra di setup:
echo          ☑ Spunta "Add Python 3.12 to PATH"
echo          Clicca "Install Now"
echo.
echo PASSO 5: Dopo installazione, RIAVVIA IL COMPUTER
echo          (Importante per aggiornare le variabili di sistema)
echo.
echo PASSO 6: Dopo riavvio, esegui di nuovo:
echo          C:\Users\gabri\Desktop\CREW\SETUP_FIX.bat
echo.
echo.
pause

echo.
echo Grazie! Quando hai completato l'installazione di Python 3.12 e riavviato,
echo torna a eseguire SETUP_FIX.bat
echo.
echo Lo script troverà Python 3.12 e completerà il setup automaticamente!
echo.
pause
