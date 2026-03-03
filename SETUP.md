# 🎯 SETUP INIZIALE - CREW

## 📍 Progetto Spostato a:
```
C:\Users\gabri\Desktop\CREW\
```

---

## ✅ CHECKLIST SETUP

### ✔️ Passo 1: Verificare Ollama

Apri **PowerShell** ed esegui:

```powershell
# Verifica se Ollama è installato
ollama list
```

Se vedi una lista di modelli, Ollama è già installato ✅

Se no, scarica da: https://ollama.ai

---

### ✔️ Passo 2: Avviare Ollama

**IMPORTANTE:** Questo terminale deve rimanere SEMPRE aperto!

In **PowerShell**:

```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve
```

Dovresti vedere:
```
Ollama is running at http://127.0.0.1:11434
```

✅ **MANTIENI QUESTO TERMINALE APERTO**

---

### ✔️ Passo 3: Scaricare i Modelli

Apri un **NUOVO terminale** PowerShell e esegui:

```powershell
ollama pull llama2:7b
ollama pull codellama:7b
```

⏱️ Attendi il completamento (2-3 minuti per modello)

Quando finisce, vedrai:
```
✓ Pulling llama2:7b - done
✓ Pulling codellama:7b - done
```

---

### ✔️ Passo 4: Verificare Virtual Environment

Apri un **TERZO terminale** PowerShell e controlla:

```powershell
# Verifica che esista l'ambiente
ls $PROFILE\..\Scripts\activate.bat

# Se non esiste, crealo:
python -m venv $HOME\crewai-env

# Attiva l'ambiente
& "$HOME\crewai-env\Scripts\Activate.ps1"

# Dovresti vedere: (crewai-env) nel prompt
```

Se vedi errore di permission, esegui:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Poi riprova ad attivare l'ambiente.

---

### ✔️ Passo 5: Installare Dipendenze

Nel **terzo terminale** (con ambiente attivato):

```powershell
cd C:\Users\gabri\Desktop\CREW
pip install -r requirements.txt
```

Attendi il completamento (2-5 minuti).

---

### ✔️ Passo 6: Esegui il Progetto

Nel **terzo terminale**:

```powershell
# Assicurati di essere nel percorso corretto
cd C:\Users\gabri\Desktop\CREW\src\coding_crew

# Esegui il sistema
python main.py
```

Alternativamente, fai doppio click su:
```
C:\Users\gabri\Desktop\CREW\RUN_CREW.bat
```

---

## 🚀 Primo Progetto - Step by Step

Una volta avviato il sistema, vedrai:

```
╔════════════════════════════════════════════════════════════════╗
║        🚀 CrewAI Multi-Agent Development System 🚀            ║
╚════════════════════════════════════════════════════════════════╝

📁 Let's start with your project name:
Project name: _
```

### Step 1: Inserisci il nome del progetto

```
Project name: my-first-project
```

### Step 2: Scrivi i requisiti

```
📝 Describe your project requirement:

> Build a simple TODO REST API with Python FastAPI that supports:
> - Create, read, update, delete todos
> - Store todos in a database
> - Add basic authentication
```

### Step 3: Attendi l'esecuzione

Il sistema eseguirà automaticamente:
- ✅ PMO Analysis (2-3 min)
- ✅ Architecture Design (3-5 min)
- ✅ Code Generation (5-8 min)
- ✅ Code Review (2-3 min)
- ✅ Test Generation (3-5 min)
- ✅ PMO Evaluation (2 min)

**TOTALE: ~20-30 minuti**

Vedrai log in tempo reale mentre procede.

### Step 4: Valuta i Risultati

Dopo l'esecuzione, vedrai il menu:

```
📋 USER FEEDBACK & NEXT STEPS

Options:
1. [ACCEPT] - Accept solution, increment version
2. [REFINE] - Request specific refinements
3. [RESTART] - Start over with new requirements
4. [VIEW] - View previous outputs
5. [EXIT] - Exit the system

What would you like to do? (1-5): _
```

#### Scegli un'opzione:

**OPZIONE 1: ACCEPT** (Accetta la soluzione)
```
What would you like to do? (1-5): 1

✅ Solution accepted!
→ Version incremented to v2
✓ Git tag: v2-accepted

Outputs saved to: outputs/my-first-project/
```

**OPZIONE 2: REFINE** (Chiedi miglioramenti)
```
What would you like to do? (1-5): 2

📝 Describe what needs to be refined/improved:
> Add JWT authentication and improve error handling
```
Il sistema rieseguirà tutti i 6 stadi con i tuoi feedback incorporati!

**OPZIONE 3: RESTART** (Nuovo progetto)
```
New requirement:
> Build a different project...
```

**OPZIONE 4: VIEW** (Vedi output precedenti)
Mostra la cronologia di tutti gli output.

**OPZIONE 5: EXIT** (Esci)
Chiude il sistema.

---

## 📁 Dove sono i Risultati

Dopo l'esecuzione, troverai i file qui:

```
outputs/my-first-project/
├── .git/               ← Git repository completo
│   └── (commits e history di tutti gli stadi)
│
├── requirements/       ← Specifiche tecniche dal PMO
│   ├── v1_20240302_120000.md
│   └── v1_20240302_120000.json
│
├── architecture/       ← Design del sistema
│   ├── v1_20240302_121000.md
│   └── v1_20240302_121000.json
│
├── code/              ← Codice generato
│   └── v1/
│       ├── main.py
│       ├── models.py
│       ├── database.py
│       └── requirements.txt
│
├── reviews/           ← Rapporto di code review
│   ├── v1_20240302_123000.md
│   └── v1_20240302_123000.json
│
└── tests/             ← Suite di test
    └── v1/
        ├── test_models.py
        ├── test_routes.py
        └── test_database.py
```

### Visualizzare i Risultati

```bash
# Aprire il progetto
cd outputs/my-first-project

# Vedere la storia dei commit
git log --oneline

# Leggere i requisiti
cat requirements/v1_*.md

# Leggere l'architettura
cat architecture/v1_*.md

# Leggere il rapporto di revisione
cat reviews/v1_*.md

# Eseguire il codice generato
cd code/v1
python main.py
```

---

## 🔧 Risoluzione Problemi

### ❌ "Ollama non è raggiungibile"

```
⚠️  ATTENZIONE: Ollama non è raggiungibile!
```

**Soluzione:**

1. Verifica che il primo terminale abbia:
```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve
```

2. Verifica che sia in esecuzione (non deve mostrare errori)

3. Prova in un nuovo terminale:
```powershell
curl http://192.168.1.7:11434/api/tags
```

Dovresti vedere una lista di modelli.

---

### ❌ "ModuleNotFoundError: No module named 'crewai'"

**Soluzione:**

Assicurati che il virtual environment sia attivato:

```powershell
# Attiva l'ambiente
& "$HOME\crewai-env\Scripts\Activate.ps1"

# Dovresti vedere: (crewai-env) nel prompt

# Reinstalla dipendenze
cd C:\Users\gabri\Desktop\CREW
pip install -r requirements.txt

# Riprova
python src\coding_crew\main.py
```

---

### ❌ "Model not found: llama2:7b"

**Soluzione:**

Scarica manualmente i modelli:

```powershell
ollama pull llama2:7b
ollama pull codellama:7b

# Verifica che siano scaricati
ollama list
```

---

### ❌ "Permission denied" con PowerShell

**Soluzione:**

Esegui PowerShell come **Amministratore** e poi:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Poi riprova ad attivare l'ambiente.

---

## 📊 Struttura Cartelle Progetto

```
C:\Users\gabri\Desktop\CREW\
│
├── START_HERE.md                ← Leggi questo prima!
├── RUN_CREW.bat                 ← Doppio click per eseguire!
├── README.md                    ← Documentazione completa
├── DEPLOYMENT_GUIDE.md          ← Setup dettagliato
├── ARCHITECTURE.md              ← Diagrammi del sistema
├── IMPLEMENTATION.md            ← Dettagli tecnici
├── DELIVERABLES.md              ← Inventario progetto
├── requirements.txt             ← Dipendenze Python
├── quickstart.sh                ← Script automatico (Linux)
├── pyproject.toml               ← Configurazione progetto
│
└── src/coding_crew/             ← Codice principale
    ├── main.py                  ← ESEGUI QUESTO per avviare
    ├── crew.py                  ← Orchestrator
    ├── agents.py                ← 5 agenti specializzati
    ├── tasks.py                 ← Template task
    │
    └── config/
        ├── model_config.py      ← Configurazione LLM
        ├── output_manager.py    ← Gestione output e versioning
        └── git_manager.py       ← Integrazione Git
```

---

## 🎯 Comandi Veloci

```powershell
# Attivare ambiente
& "$HOME\crewai-env\Scripts\Activate.ps1"

# Eseguire il sistema
cd C:\Users\gabri\Desktop\CREW\src\coding_crew
python main.py

# Visualizzare risultati di un progetto
cd outputs/my-project
git log --oneline
ls -la

# Disattivare ambiente quando finito
deactivate
```

---

## ✅ Sei Pronto!

Segui questi passi in ordine:

1. ✅ **Avvia Ollama** (Terminale 1)
2. ✅ **Scarica Modelli** (Terminale 2)
3. ✅ **Setup Ambiente** (Terminale 3)
4. ✅ **Esegui il Progetto** (Terminale 3)
5. ✅ **Crea il tuo primo progetto**
6. ✅ **Valuta i risultati**

---

## 🚀 Avvio Veloce

**Opzione A - Doppio Click:**
1. Vai a: `C:\Users\gabri\Desktop\CREW\`
2. Doppio click su: `RUN_CREW.bat`

**Opzione B - Manuale:**
```powershell
cd C:\Users\gabri\Desktop\CREW\src\coding_crew
python main.py
```

---

**Domande?** Leggi i file .md oppure chiedi! 😊

**Buon lavoro!** 🚀
