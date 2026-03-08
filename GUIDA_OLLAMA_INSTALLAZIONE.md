# 🚀 GUIDA INSTALLAZIONE OLLAMA - STEP BY STEP

## ⏱️ Tempo Totale: ~30 minuti

---

## OPZIONE 1: Automated (Consigliato)

### Se sei in Windows PowerShell:

```powershell
# Apri PowerShell come Administrator:
# Tasto WINDOWS + X → Seleziona "Windows Terminal (Admin)"

# Poi esegui:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
& "c:\Users\demar\Desktop\Patch\CrewTeam-main\INSTALL_OLLAMA.ps1"

# Lo script farà tutto automaticamente:
# 1. Scaricherà OllamaSetup.exe
# 2. Lo eseguirà
# 3. Scaricherà i modelli
# 4. Avvierà il server
```

### Se hai il file batch:

```batch
REM Apri Command Prompt come Administrator
REM Poi:
cd c:\Users\demar\Desktop\Patch\CrewTeam-main
INSTALL_OLLAMA.bat
```

---

## OPZIONE 2: Manual (Se Automated non funziona)

### Step 1: Scarica Ollama (2 min)

```
1. Apri browser
2. Vai a: https://ollama.ai/download
3. Clicca "Download for Windows"
4. Il file OllamaSetup.exe si scaricherà automaticamente
   (Dimensione ~150-200 MB)
```

### Step 2: Installa Ollama (5 min)

```
1. Apri il file scaricato: OllamaSetup.exe
   Di solito in: C:\Users\demar\Downloads\
   
2. Segui il wizard di installazione
   - Click "Next"
   - Accetta license
   - Click "Install"
   
3. Attendi il completamento (2-3 minuti)

4. Al termine, Ollama sarà installato
   Default location: C:\Users\demar\AppData\Local\Programs\Ollama\
```

### Step 3: Verifica Installazione (1 min)

```powershell
# Apri PowerShell e digita:
ollama --version

# Dovresti vedere:
# ollama version 0.x.x
```

### Step 4: Avvia Ollama Server (1 min)

```powershell
# In PowerShell, digita:
ollama serve

# Dovresti vedere:
# [STARTED] listening on 127.0.0.1:11434
```

**IMPORTANTE:** Lascia questa finestra APERTA. È il server di Ollama.

### Step 5: Scarica Modelli (20 min) 

**In un NUOVO PowerShell/CMD (non chiudere il server):**

```powershell
# Modello per generazione codice
ollama pull codellama:7b

# Modello general purpose
ollama pull llama2:7b

# Ogni modello è ~4-7 GB, scaricamente sequenzialmente
# Totale: ~15-20 GB, tempo: 10-20 minuti (dipende dalla velocità)
```

### Step 6: Verifica Modelli (1 min)

```powershell
ollama list

# Dovresti vedere:
# NAME              ID              SIZE      MODIFIED
# codellama:7b      ...             3.8 GB    2 hours ago
# llama2:7b         ...             3.9 GB    1 hour ago
```

---

## ✅ Verifiche

### Ollama Running:
```powershell
# Test in PowerShell:
curl http://localhost:11434/api/tags

# Dovresti ottenere una risposta JSON con i modelli
```

### Accesso da Python:
```powershell
# Test che il progetto vede Ollama:
python -c "import requests; print('Ollama OK' if requests.get('http://localhost:11434/api/tags').status_code == 200 else 'NOT OK')"

# Output:
# Ollama OK
```

---

## 🎯 Dopo Installazione Completata

### 1. Mantieni Ollama Server Running

```powershell
# La finestra con "ollama serve" deve rimanere APERTA
# Non chiudere!

# Minimizzala se vuoi, ma non chiuderla
```

### 2. Torna al Progetto CREW

```powershell
# In un NUOVO PowerShell:
cd c:\Users\demar\Desktop\Patch\CrewTeam-main\src\coding_crew
python main.py

# Il sistema dovrebbe:
# 1. Stampare il banner
# 2. Verificare connessione Ollama ✅
# 3. Mostrarti le opzioni di progetto
```

### 3. Se tutto ok, dovresti vedere:

```
================================================================================
CREWAI MULTI-AGENT DEVELOPMENT SYSTEM
================================================================================
[OK] Configuration loaded
[OK] ✅ Ollama connection verified
--------------------------
Project Mode
  1. Start a new project
  2. Resume an existing project
Select mode (1-2):
```

---

## 🆘 Troubleshooting

### Problema: "ollama command not found"
**Soluzione:**
- Riavvia il computer (Ollama aggiunge PATH)
- O usa il path completo: `C:\Users\demar\AppData\Local\Programs\Ollama\ollama.exe`

### Problema: Il download dei modelli è lento
**Soluzione:**
- Normale! Sono file grandi (3-7 GB per modello)
- Usa una connessione veloce e stabile
- Se si blocca, prova di nuovo: `ollama pull codellama:7b`

### Problema: "Connection refused at localhost:11434"
**Soluzione:**
- Verifica se `ollama serve` è in esecuzione
- Avvia di nuovo in una finestra PowerShell

### Problema: Out of disk space
**Soluzione:**
- Modelli occupano ~15-20 GB
- Libera spazio disco (almeno 30 GB liberi consigliato)

---

## 📊 Checklist Installazione

- [ ] Downloaded OllamaSetup.exe
- [ ] Eseguito OllamaSetup.exe
- [ ] `ollama --version` funziona
- [ ] `ollama serve` avviato e running
- [ ] `ollama pull codellama:7b` completato
- [ ] `ollama pull llama2:7b` completato
- [ ] `ollama list` mostra 2 modelli
- [ ] `curl http://localhost:11434/api/tags` risponde
- [ ] `python main.py` vede Ollama (✅ Ollama connection verified)
- [ ] Progetto CREW parte normalmente

---

## ⚡ Comandi Rapidi

```powershell
# Check version
ollama --version

# Start server
ollama serve

# Download a model
ollama pull <model_name>

# List models
ollama list

# Remove model
ollama rm <model_name>

# Run model (REPL)
ollama run codellama:7b

# Test API
curl http://localhost:11434/api/tags
```

---

## 🎓 Cosa Sono These Models?

### codellama:7b (3.8 GB)
- **Specializzato per:** Generazione codice, code completion
- **Usato da:** Code Writer, Code Reviewer agents
- **Vantaggi:** Conosce sintassi di linguaggi di programmazione

### llama2:7b (3.9 GB)
- **Specializzato per:** Conversazioni, analisi generale
- **Usato da:** PMO, Architect agents
- **Vantaggi:** Buono per planning e requirements

---

## 📝 Note Finali

- **Mantieni server Ollama sempre running** quando usi CREW
- **Circa 15-20 GB di spazio disco** necessari per i modelli
- **WiFi stabile** consigliato per download modelli
- **First run potrebbe essere lento** (carica modelli in RAM)

---

**Una volta completato, torna a:**
```bash
python src/coding_crew/main.py
```

The system dovrebbe funzionare! 🚀
