# 🚀 CREW - Multi-Agent Development System

## 📍 Posizione Progetto
Il progetto si trova nel percorso corrente. Tutti i comandi sono relativi a questa posizione.

```
%current_directory%
```

## ⚡ Avvio Rapido (5 minuti)

### PASSO 1️⃣: Avvia Ollama
Apri **PowerShell** ed esegui:
```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve
```

**Mantieni questo terminale aperto!**

---

### PASSO 2️⃣: Scarica Modelli (in nuovo terminale)
```bash
ollama pull llama2:7b
ollama pull codellama:7b
```

⏱️ Attendi completamento (5-10 minuti)

---

### PASSO 3️⃣: Avvia il Sistema
#### Opzione A: Windows (Doppio Click - Più Facile)
```
Doppio click su: RUN_CREW.bat
```

#### Opzione B: Windows (Da linea di comando)
```cmd
cd /d "%~dp0"
venv\Scripts\activate.bat
cd src\coding_crew
python main.py
```

#### Opzione C: Linux / WSL2
```bash
cd $(pwd)
source activate.sh
cd src/coding_crew
python3 main.py
```

---

### PASSO 4️⃣: Segui i Prompt

```
Project name: my-project
Describe your project:
> Build a REST API for e-commerce management
```

✅ Il sistema eseguirà automaticamente tutti i 6 stadi:
1. PMO Analysis (2-3 min)
2. Architecture Design (3-5 min)
3. Code Generation (5-8 min)
4. Code Review (2-3 min)
5. Test Generation (3-5 min)
6. PMO Evaluation (2 min)

**TOTALE: ~20-30 minuti**

---

### PASSO 5️⃣: Menu di Feedback

```
📋 USER FEEDBACK & NEXT STEPS

1. [ACCEPT] - Accetta soluzione ✅
2. [REFINE] - Chiedi miglioramenti (itera)
3. [RESTART] - Nuovo progetto
4. [VIEW] - Vedi output precedenti
5. [EXIT] - Esci
```

---

## 📁 Dove vengono salvati i risultati

```
outputs/my-project/
├── .git/               ← Git repository completo
├── requirements/       ← Specifiche tecniche
├── architecture/       ← Design del sistema
├── code/              ← Codice generato
├── reviews/           ← Rapporto di revisione
└── tests/             ← Suite di test
```

---

## 🔧 Comandi Utili

```bash
# Attivare ambiente (Windows)
venv\Scripts\activate.bat

# Attivare ambiente (Linux/WSL)
source /mnt/c/Users/gabri/Desktop/CREW/venv/bin/activate

# Eseguire il sistema
cd /d "%~dp0src\coding_crew"
python main.py

# Vedere i risultati di un progetto
cd outputs/my-project
git log --oneline      # Cronologia commit
ls -la                 # Lista file
cat requirements/v1_*.md  # Leggere requisiti

# Disattivare ambiente
deactivate
```

---

## ⚠️ Problemi Comuni

### ❌ "Connection refused at localhost:11434"
**Soluzione:** Assicurati che Ollama sia in esecuzione nel primo terminale con:
```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve
```

### ❌ "ModuleNotFoundError: No module named 'crewai'"
**Soluzione:** Attiva il virtual environment:
```bash
# Windows
venv\Scripts\activate.bat

# Linux/WSL
source venv/bin/activate
```

### ❌ "Model not found: llama2:7b"
**Soluzione:** Scarica il modello:
```bash
ollama pull llama2:7b
```

---

## 📖 Documentazione

| File | Descrizione |
|------|------------|
| **README.md** | Documentazione completa |
| **DEPLOYMENT_GUIDE.md** | Setup dettagliato |
| **ARCHITECTURE.md** | Diagrammi del sistema |
| **IMPLEMENTATION.md** | Dettagli tecnici |

---

## 📋 Struttura del Progetto

```
%ProjectRoot%
├── venv/                           ← Virtual Environment (✅ Già installato!)
├── RUN_CREW.bat                    ← DOPPIO CLICK PER AVVIARE
├── activate.sh                     ← Per Linux/WSL
├── README.md                       (Documentazione)
├── ENVIRONMENT_SETUP.md            (Dettagli setup)
├── DEPLOYMENT_GUIDE.md             (Setup guide)
├── ARCHITECTURE.md                 (Diagrammi)
├── IMPLEMENTATION.md               (Dettagli tecnici)
├── DELIVERABLES.md                 (Inventario)
├── requirements.txt                (Dipendenze)
│
└── src/coding_crew/                (Codice principale)
    ├── main.py                     ← ESEGUI QUESTO!
    ├── crew.py                     (Orchestrator)
    ├── agents.py                   (5 agenti)
    │
    └── config/
        ├── model_config.py
        ├── output_manager.py
        └── git_manager.py
```

---

## 🎯 Esempio Completo

```bash
# Terminale 1: Avvia Ollama
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve

# Terminale 2: Scarica modelli
ollama pull llama2:7b
ollama pull codellama:7b

# Terminale 3: Windows (Doppio click oppure:)
.\RUN_CREW.bat

# Oppure Linux/WSL: 
cd $(dirname "$0")
source activate.sh
cd src/coding_crew
python3 main.py

# Segui i prompt:
# - Project name: my-api
# - Requirements: Build a REST API for todo management
# - Attendi 20-30 minuti
# - Valuta i risultati e scegli: ACCEPT, REFINE, RESTART, VIEW, o EXIT
```

---

## ✅ Sei Pronto!

Il progetto è completamente installato. Puoi iniziare subito! 🚀

**Percorso progetto:** Percorso corrente (dinamico)

**Comando di avvio:**
```bash
cd src\coding_crew
python main.py
```

---

**Domande?** Leggi i file .md oppure contatta l'assistente! 😊
