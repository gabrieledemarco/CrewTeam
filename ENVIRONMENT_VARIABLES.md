# 🔧 Configurazione Variabili d'Ambiente

## 📍 Variabili Disponibili

### OLLAMA_HOST
**Descrizione:** URL dove Ollama è in esecuzione  
**Default:** `http://localhost:11434`  
**Esempio:** `http://192.168.1.100:11434`

```powershell
# Windows PowerShell
$env:OLLAMA_HOST = "http://localhost:11434"

# Windows CMD
set OLLAMA_HOST=http://localhost:11434

# Linux/WSL/Mac
export OLLAMA_HOST="http://localhost:11434"
```

---

### CREW_DEFAULT_MODEL
**Descrizione:** Modello LLM da usare di default  
**Default:** `codellama:7b`  
**Opzioni disponibili:** `llama2:7b`, `mistral:7b`, `neural-chat:7b`, `qwen2.5-coder:1.5b`

```powershell
# Windows PowerShell
$env:CREW_DEFAULT_MODEL = "llama2:7b"

# Linux/WSL
export CREW_DEFAULT_MODEL="llama2:7b"
```

---

### OLLAMA_API_KEY  
**Descrizione:** API Key per Ollama (se necessaria)  
**Default:** `not-needed`  
**Nota:** Ollama locale non richiede API key

```powershell
# Windows PowerShell
$env:OLLAMA_API_KEY = "your-api-key-here"

# Linux/WSL
export OLLAMA_API_KEY="your-api-key-here"
```

---

## 🚀 Script Automatici

### Windows PowerShell - Configurazione Permanente

Crea file `setup_environment.ps1`:

```powershell
# Setup Ollama locale (default)
$env:OLLAMA_HOST = "http://localhost:11434"
$env:CREW_DEFAULT_MODEL = "codellama:7b"

# Per renderlo permanente (opzionale):
# [Environment]::SetEnvironmentVariable("OLLAMA_HOST", "http://localhost:11434", "User")

Write-Host "✅ Variabili d'ambiente configurate"
Write-Host "   OLLAMA_HOST: $env:OLLAMA_HOST"
Write-Host "   CREW_DEFAULT_MODEL: $env:CREW_DEFAULT_MODEL"
```

Esegui prima di `RUN_CREW.bat`:
```powershell
.\setup_environment.ps1
.\RUN_CREW.bat
```

---

### Linux/WSL - Configurazione Permanente

Aggiungi a `~/.bashrc` o `~/.zshrc`:

```bash
# Crew AI Configuration
export OLLAMA_HOST="http://localhost:11434"
export CREW_DEFAULT_MODEL="codellama:7b"
export OLLAMA_API_KEY="not-needed"
```

Poi ricarica:
```bash
source ~/.bashrc
./activate.sh
cd src/coding_crew
python3 main.py
```

---

## 🔄 Casi di Uso Comuni

### 1. Setup Locale Semplice (Default)
```powershell
# Niente da configurare - usa default
.\RUN_CREW.bat
```

---

### 2. Ollama su Server Remoto
```powershell
# Configurazione temporanea (sessione)
$env:OLLAMA_HOST = "http://192.168.1.100:11434"
.\RUN_CREW.bat

# Alternativa: Configurazione permanente (richiede privilegios)
# [Environment]::SetEnvironmentVariable("OLLAMA_HOST", "http://192.168.1.100:11434", "Machine")
```

---

### 3. Modello Leggero per Testing
```powershell
# Usa qwen2.5-coder:1.5b (più veloce, meno accurato)
$env:CREW_DEFAULT_MODEL = "qwen2.5-coder:1.5b"
.\RUN_CREW.bat
```

---

### 4. Modello General Purpose
```powershell
# Usa llama2:7b (più accurato, un po' più lento)
$env:CREW_DEFAULT_MODEL = "llama2:7b"
.\RUN_CREW.bat
```

---

## ⚙️ Verificare Configurazione

### Verificare Variabili Impostate
```powershell
# Windows
echo %OLLAMA_HOST%
echo %CREW_DEFAULT_MODEL%

# Linux/WSL
echo $OLLAMA_HOST
echo $CREW_DEFAULT_MODEL
```

### Verificare Connessione Ollama
```powershell
# Windows
curl http://localhost:11434/api/tags

# Linux/WSL
curl http://localhost:11434/api/tags
```

### Verificare Modeli Disponibili
```powershell
# Windows
curl http://localhost:11434/api/tags | convertfrom-json | select-object -expandproperty models

# Linux/WSL
curl http://localhost:11434/api/tags | jq '.models[] | .name'
```

---

## 🐛 Troubleshooting

### ❌ "Connection refused"
**Problema:** Ollama non è raggiungibile  
**Soluzione:**
```powershell
# Verifica che Ollama sia in esecuzione
ollama list

# Se non funziona, avvia Ollama
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve

# Poi in altro terminale, configura client
$env:OLLAMA_HOST = "http://localhost:11434"
.\RUN_CREW.bat
```

---

### ❌ "Model not found"
**Problema:** Il modello configurato non è scaricato  
**Soluzione:**
```powershell
# Scarica il modello
ollama pull codellama:7b
ollama pull llama2:7b

# Verifica lista
ollama list

# Riprova
.\RUN_CREW.bat
```

---

### ⚠️ Variabili non persistenti
**Problema:** Le variabili d'ambiente scompaiono dopo chiudere il terminale  
**Soluzione permanente (Windows):**
```
1. Tasto Win + Pause/Break
2. Variabili d'ambiente avanzate
3. Add user/system variable:
   - Name: OLLAMA_HOST
   - Value: http://localhost:11434
4. OK e riavvia terminale
```

---

## 📚 Riferimenti

- [START_HERE.md](START_HERE.md) - Guida rapida
- [SETUP.md](SETUP.md) - Setup dettagliato
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - Correzioni applicate
- [src/coding_crew/config/model_config.py](src/coding_crew/config/model_config.py) - Codice configurazione

---

**Domande?** Controlla i file .md nella cartella principale! 🚀
