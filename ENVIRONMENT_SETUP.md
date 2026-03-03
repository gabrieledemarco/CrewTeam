# 🌍 Configurazione Ambiente - CREW

## ✅ Setup Completato

L'ambiente è stato configurato e tutte le dipendenze sono state installate localmente nel progetto.

### Informazioni di Sistema
- **Posizione progetto**: `C:\Users\gabri\Desktop\CREW`
- **Python version**: 3.12.3
- **Virtual Environment**: Locale in `venv/`
- **Pacchetti installati**: 167 (vedi `pip list`)

### Dipendenze Installate
- ✅ **crewai** (1.10.0) - Framework CrewAI
- ✅ **crewai-tools** (1.10.0) - Strumenti CrewAI
- ✅ **langchain** (1.2.10) - LangChain framework
- ✅ **langchain-openai** (1.1.10) - OpenAI integration
- ✅ **litellm** (1.82.0) - LLM abstraction layer
- ✅ **python-dotenv** (1.1.1) - Environment variables
- ✅ **requests** (2.32.5) - HTTP client
- ✅ **PyYAML** (6.0.3) - YAML parser

---

## 🚀 Come Avviare il Sistema

### Windows (Consigliato - Doppio click)
```batch
C:\Users\gabri\Desktop\CREW\RUN_CREW.bat
```

### Windows (Da linea di comando)
```cmd
cd C:\Users\gabri\Desktop\CREW
venv\Scripts\activate.bat
cd src\coding_crew
python main.py
```

### Linux / WSL2
```bash
cd /mnt/c/Users/gabri/Desktop/CREW
source activate.sh
cd src/coding_crew
python3 main.py
```

---

## 🔧 Gestione dell'Ambiente

### Attivare il Virtual Environment

**Windows (CMD):**
```cmd
C:\Users\gabri\Desktop\CREW\venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
C:\Users\gabri\Desktop\CREW\venv\Scripts\Activate.ps1
```

**Linux / WSL:**
```bash
source /mnt/c/Users/gabri/Desktop/CREW/venv/bin/activate
```

### Disattivare il Virtual Environment
```bash
deactivate
```

### Verificare Pacchetti Installati
```bash
pip list
```

### Aggiornare Dipendenze
```bash
pip install -r requirements.txt --upgrade
```

### Installare un Nuovo Pacchetto
```bash
# Attiva il venv prima
pip install nome_pacchetto
```

---

## ⚙️ Configurazione Ollama

Il sistema usa Ollama per i modelli locali. Assicurati che Ollama sia in esecuzione:

### Modelli Necessari
- **llama2:7b** - Per PMO e Architect
- **codellama:7b** - Per Code Writer, Reviewer, Tester

### Verifica Modelli
```bash
ollama list
```

### Scarica Modelli (se necessario)
```bash
ollama pull llama2:7b
ollama pull codellama:7b
```

### Avvia Ollama (Windows)
```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve
```

### Avvia Ollama (Linux)
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

---

## 📁 Struttura del Progetto

```
C:\Users\gabri\Desktop\CREW\
├── venv/                              # Virtual environment locale ✅
├── src/
│   └── coding_crew/
│       ├── main.py                   # Entry point
│       ├── crew.py                   # CrewOrchestrator
│       ├── agents.py                 # Agenti specializzati
│       ├── tasks.py                  # Task templates
│       └── config/
│           ├── model_config.py       # Configurazione LLM
│           ├── output_manager.py     # Gestione output
│           └── git_manager.py        # Gestione Git
├── requirements.txt                   # Dipendenze (aggiornato)
├── RUN_CREW.bat                      # Script avvio Windows ✅
├── activate.sh                       # Script attivazione Linux ✅
├── pyproject.toml                    # Configurazione progetto
└── [documentazione]
```

---

## ✅ Verifica Ambiente

Per verificare che tutto funzioni correttamente:

```bash
# Attiva il venv
source venv/bin/activate  # Linux/WSL
# oppure
venv\Scripts\activate.bat  # Windows

# Verifica importazioni
python3 -c "import crewai; import langchain; import litellm; print('✅ All OK')"
```

---

## 🐛 Risoluzione Problemi

### Errore: "venv not found"
```bash
# Ricrea il venv
cd C:\Users\gabri\Desktop\CREW
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Errore: "ModuleNotFoundError"
```bash
# Verifica che il venv sia attivato
which python  # Linux/WSL
echo %VIRTUAL_ENV%  # Windows

# Se non attivato, attivalo:
source venv/bin/activate
```

### Errore: "Ollama not found"
Verifica che Ollama sia in esecuzione e accessibile su `http://192.168.1.7:11434`

### Errore: "pip list" lento
Aspetta che pip termini o usa:
```bash
pip list --format=json > packages.json
```

---

## 📊 Informazioni Ambiente

**Data setup**: 2 Mar 2026
**Python version**: 3.12.3
**Total packages**: 167
**Memoria approssimativa**: ~500 MB (venv completo)

---

## ⚡ Prossimi Passi

1. **Verifica Ollama** è in esecuzione
2. **Esegui il sistema**:
   ```bash
   python3 main.py
   ```
3. **Crea un progetto di test** tramite l'interfaccia terminale
4. **Monitora l'esecuzione** dei 5 agenti

---

**Status**: ✅ **AMBIENTE PRONTO**

Tutte le dipendenze sono installate e il sistema è pronto per essere eseguito!
