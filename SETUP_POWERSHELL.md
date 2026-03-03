# Setup CREW - Comandi PowerShell (Versione Corretta)

## COPIA E INCOLLA QUESTO INTERO BLOCCO IN POWERSHELL:

```powershell
# Vai alla cartella CREW
cd C:\Users\gabri\Desktop\CREW

# Elimina il venv vecchio (sintassi PowerShell)
Remove-Item -Path venv -Recurse -Force

# Crea nuovo venv con Python 3.12
py -3.12 -m venv venv

# Attiva il venv
.\venv\Scripts\Activate.ps1

# Aggiorna pip
python -m pip install --upgrade pip

# Installa le dipendenze
pip install crewai crewai-tools langchain langchain-openai litellm python-dotenv requests PyYAML
```

## Se vedi errore di esecuzione script:

Se PowerShell ti dice: "non è consentito l'esecuzione di script", esegui PRIMA questo:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Premi `Y` (Yes) quando chiede conferma.

Poi prova di nuovo i comandi sopra.

## Verifica finale:

```powershell
python -c "import crewai; print('✅ CREWAI OK')"
```

Dovresti vedere: `✅ CREWAI OK`

Se lo vedi → **SETUP COMPLETATO!** ✅
