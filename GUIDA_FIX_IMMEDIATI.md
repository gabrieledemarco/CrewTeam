# 🔧 GUIDA AI FIX IMMEDIATI

## Quick Fix - 4 Errori Critici da Risolvere

### FIX #1: Implementare TODO in Middleware
**File:** [src/coding_crew/communication/middleware.py](src/coding_crew/communication/middleware.py#L102)  
**Tempo:** 20 minuti  
**Impatto:** ALTO

Sostituisci:
```python
# TODO: Implement actual transformation using LLM
return {}
```

Con:
```python
# Implement actual transformation using LLM
from config.model_config import ModelConfig
import json

try:
    llm = ModelConfig.get_llm_for_agent("pmo")
    prompt = f"""
Transform the following text to structured JSON format for {target_schema}:

{text}

Return ONLY valid JSON, no markdown formatting.
"""
    
    response = llm.call(prompt)
    transformed = json.loads(response)
    return transformed
except json.JSONDecodeError:
    print(f"[WARN] Failed to parse LLM response as JSON")
    return {"raw_text": text}
except Exception as e:
    print(f"[ERROR] Transformation failed: {e}")
    return {"raw_text": text, "error": str(e)}
```

---

### FIX #2: Aggiungere Validazione Ollama Pre-Execution
**File:** [src/coding_crew/main.py](src/coding_crew/main.py#L152)  
**Tempo:** 15 minuti  
**Impatto:** ALTO

Dopo `validate_critical_settings()` aggiungi:

```python
def main():
    banner()
    cfg = load_or_initialize_configuration()
    show_config_summary(cfg)

    if not validate_critical_settings(cfg):
        status_warn("Fix configuration and run again.")
        return

    # 🆕 AGGIUNTO: Verifica Ollama Connection
    status_ok("Checking Ollama connection...")
    if not check_ollama_connection(cfg["ollama_host"]):
        status_warn("⚠️  Ollama server not responding at: {}".format(cfg["ollama_host"]))
        status_warn("Please ensure Ollama is running: ollama serve")
        retry = ask_bool("Retry connection check", False)
        if not retry:
            return
    
    status_ok("✅ Ollama connection OK")
    
    # ... rest of code
```

Dove `check_ollama_connection` è:
```python
def check_ollama_connection(host: str) -> bool:
    """Verify Ollama is running and responsive"""
    import requests
    try:
        response = requests.get(f"{host.rstrip('/')}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False
```

---

### FIX #3: Implementare Logging Centralizzato
**File:** [src/coding_crew/main.py](src/coding_crew/main.py#L1)  
**Tempo:** 30 minuti  
**Impatto:** ALTO

Aggiungi all'inizio del file:

```python
#!/usr/bin/env python3
"""
CrewAI Multi-Agent System - Main Entry Point
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configure logging BEFORE other imports
def setup_logging():
    """Configure centralized logging"""
    # Create logs directory
    logs_dir = Path.cwd() / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Log filename with timestamp
    log_file = logs_dir / f"crew_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Setup handlers
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add to handlers
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 CrewAI session started")
    logger.info(f"📝 Log file: {log_file}")
    
    return logger

# CALL THIS FIRST
logger = setup_logging()

# Then import rest of modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_config import (
    load_or_initialize_configuration,
    show_config_summary,
    validate_critical_settings,
)
# ... rest of imports
```

---

### FIX #4: Risolvere Path Hardcodati in Settings
**File:** [src/coding_crew/config/settings.py](src/coding_crew/config/settings.py#L27)  
**Tempo:** 20 minuti  
**Impatto:** MEDIO

Sostituisci:
```python
@staticmethod
def get_config_path() -> Path:
    base_dir = Path(__file__).parent.parent.parent.parent
    return base_dir / Settings.CONFIG_FILE
```

Con:
```python
@staticmethod
def get_config_path() -> Path:
    """Get configuration path from environment or default location"""
    
    # Priority 1: Environment variable
    if env_path := os.getenv("CREW_CONFIG_PATH"):
        return Path(env_path)
    
    # Priority 2: User home directory (recommended)
    try:
        config_dir = Path.home() / ".crew"
        config_dir.mkdir(exist_ok=True)
        return config_dir / Settings.CONFIG_FILE
    except Exception:
        pass
    
    # Priority 3: Current working directory
    return Path.cwd() / Settings.CONFIG_FILE
```

**Aggiorna la docstring della classe:**
```python
class Settings:
    """
    Gestisce la persistenza della configurazione utente
    
    Configuration location (in order of priority):
    1. Environment: CREW_CONFIG_PATH
    2. User home: ~/.crew/crew_config.json
    3. Current dir: ./crew_config.json
    """
```

---

## Comandi di Test Rapidi

Dopo implementare i 4 fix, esegui:

```powershell
# 1. Verifica syntax
python -m py_compile src/coding_crew/main.py
python -m py_compile src/coding_crew/config/settings.py
python -m py_compile src/coding_crew/communication/middleware.py

# 2. Verifica imports
python -c "from src.coding_crew.config.settings import Settings; print('✅ Settings OK')"
python -c "from src.coding_crew.communication.middleware import CommunicationMiddleware; print('✅ Middleware OK')"

# 3. Test logging setup
python -c "
import logging
from datetime import datetime
logger = logging.getLogger(__name__)
logger.info('Test message')
print('✅ Logging OK')
"

# 4. Verifica Ollama (if available)
python -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('✅ Ollama is running')
    else:
        print('❌ Ollama not responding')
except:
    print('❌ Ollama not available')
"
```

---

## Implementazione Consigliata - Ordine

```
STEP 1: FIX #3 (Logging)      ← Fatto per primo, alle dipendenze
STEP 2: FIX #4 (Settings)     ← Necessario per configurazione
STEP 3: FIX #2 (Ollama check) ← Aggiugne validazione
STEP 4: FIX #1 (Middleware)   ← comunicazione agenti
```

**Tempo totale:** ~90 minuti  
**Difficoltà:** Bassa-Media  
**Test necessario:** Sì

---

## Checklist Finale

- [ ] FIX #1 implementato e testato
- [ ] FIX #2 implementato e testato
- [ ] FIX #3 implementato e testato
- [ ] FIX #4 implementato e testato
- [ ] Nessun syntax error post-fix
- [ ] Log directory creato (`logs/`)
- [ ] Config file salvato correttamente
- [ ] Test Ollama verification
- [ ] README aggiornato con nuove env vars
- [ ] Versione bumped a 0.2.0

