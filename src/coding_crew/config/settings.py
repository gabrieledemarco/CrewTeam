import json
import os
from pathlib import Path
from typing import Optional, Dict


class Settings:
    """
    Gestisce la persistenza della configurazione utente
    
    Configuration location (in order of priority):
    1. Environment: CREW_CONFIG_PATH
    2. User home: ~/.crew/crew_config.json
    3. Current dir: ./crew_config.json
    """
    
    CONFIG_FILE = "crew_config.json"
    DEFAULT_CONFIG = {
        "version": 2,
        "ollama_host": "http://localhost:11434",
        "persist_project_to_disk": True,
        "project_base_dir": "outputs",
        "github_root_url": "",
        "github_token": "",
        "agent_models": {
            "pmo": "llama2:7b",
            "architect": "llama2:7b",
            "code_writer": "codellama:7b",
            "code_reviewer": "codellama:7b",
            "tester": "codellama:7b"
        }
    }
    
    @staticmethod
    def get_config_path() -> Path:
        """Get configuration path with proper fallback strategy"""
        
        # Priority 1: Environment variable
        if env_path := os.getenv("CREW_CONFIG_PATH"):
            path = Path(env_path)
            return path
        
        # Priority 2: User home directory (recommended)
        try:
            config_dir = Path.home() / ".crew"
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir / Settings.CONFIG_FILE
        except Exception:
            pass
        
        # Priority 3: Current working directory
        return Path.cwd() / Settings.CONFIG_FILE
    
    @staticmethod
    def load() -> Optional[Dict]:
        """Carica la configurazione dal file JSON"""
        config_path = Settings.get_config_path()
        
        if not config_path.exists():
            return None
            
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                return Settings.merge_with_defaults(loaded)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Errore nel caricamento config: {e}")
            return None
    
    @staticmethod
    def save(config: Dict) -> bool:
        """Salva la configurazione su file JSON"""
        config_path = Settings.get_config_path()
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            return True
        except IOError as e:
            print(f"⚠ Errore nel salvataggio config: {e}")
            return False
    
    @staticmethod
    def exists() -> bool:
        """Verifica se esiste un file di configurazione"""
        return Settings.get_config_path().exists()
    
    @staticmethod
    def create_default() -> Dict:
        """Crea configurazione di default"""
        return Settings.DEFAULT_CONFIG.copy()

    @staticmethod
    def merge_with_defaults(config: Dict) -> Dict:
        """Merge configurazione caricata con i default per compatibilita'."""
        merged = Settings.DEFAULT_CONFIG.copy()
        merged.update({k: v for k, v in config.items() if k != "agent_models"})
        merged["agent_models"] = Settings.DEFAULT_CONFIG["agent_models"].copy()
        merged["agent_models"].update(config.get("agent_models", {}))
        return merged
