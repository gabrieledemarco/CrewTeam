# 🚀 FIX RAPIDO - SETUP_FIX.bat

## Il Problema
```
ERROR: Failed building wheel for tiktoken, regex
(Python 3.14 non supportato - serve compilazione Rust)
```

## La Soluzione (30 secondi)

### Opzione 1: Automatica (CONSIGLIATA)

**Doppio click su**:
```
C:\Users\gabri\Desktop\CREW\SETUP_FIX.bat
```

Lo script farà tutto automaticamente:
- ✅ Trova Python 3.12 o 3.13
- ✅ Elimina il vecchio venv
- ✅ Crea nuovo venv
- ✅ Installa tutte le dipendenze
- ✅ Verifica che funziona

### Opzione 2: Manuale (Se preferisci controllare)

```powershell
cd C:\Users\gabri\Desktop\CREW

# Elimina venv vecchio
rmdir /s /q venv

# Ricrea con Python 3.12
py -3.12 -m venv venv

# Attiva
venv\Scripts\activate.bat

# Installa
pip install --upgrade pip
pip install crewai crewai-tools langchain langchain-openai litellm python-dotenv requests PyYAML
```

---

## ✅ Verificare che Funziona

```powershell
python -c "import crewai; print('✅ OK')"
```

Dovresti vedere: **`✅ OK`**

---

## 🎯 Dopo la Correzione

```powershell
# Opzione 1: Continuare dal terminale attuale
cd src\coding_crew
python main.py

# Opzione 2: Usare il batch script la prossima volta
.\RUN_CREW.bat
```

---

## ⚠️ Se Persiste il Problema

### Errore: "Python 3.12 non trovato"

Scarica Python 3.12:
1. Vai a https://www.python.org/downloads/
2. Scarica **Python 3.12.x**
3. Installa e **SPUNTA** "Add Python to PATH"
4. Riavvia SETUP_FIX.bat

### Errore: "ModuleNotFoundError"

```powershell
# Verifica che venv sia attivato
echo %VIRTUAL_ENV%

# Se vuoto, attiva manualmente
venv\Scripts\activate.bat

# Reinstalla
pip install crewai
```

---

**Data**: 2 Marzo 2026
**Status**: Pronto all'uso
