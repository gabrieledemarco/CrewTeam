"""
LLM Model Configuration for CrewAI with Ollama
"""
import os
import requests
from typing import Optional, List, Dict
from crewai import LLM
from .settings import Settings


class ModelConfig:
    """Centralized model configuration"""
    
    # Available models with their characteristics
    MODELS = {
        "codellama:7b": {
            "name": "CodeLlama 7B",
            "description": "Specialized for code generation, best for Code Writer and Reviewer",
            "memory_required_gb": 7,
            "recommended_for": ["code_generation", "code_review"],
            "speed": "medium",
            "quality": "high"
        },
        "llama2:7b": {
            "name": "Llama 2 7B",
            "description": "General purpose model, reliable for all tasks",
            "memory_required_gb": 7,
            "recommended_for": ["general", "architecture", "requirements"],
            "speed": "medium",
            "quality": "high"
        },
        "mistral:7b": {
            "name": "Mistral 7B",
            "description": "Fast and efficient, good balance",
            "memory_required_gb": 7,
            "recommended_for": ["general", "fast_iteration"],
            "speed": "fast",
            "quality": "medium"
        },
        "neural-chat:7b": {
            "name": "Neural Chat 7B",
            "description": "Optimized for conversations and interactions",
            "memory_required_gb": 7,
            "recommended_for": ["user_interaction", "requirements"],
            "speed": "fast",
            "quality": "medium"
        },
        "qwen2.5-coder:1.5b": {
            "name": "Qwen 2.5 Coder 1.5B",
            "description": "Lightweight model for testing",
            "memory_required_gb": 2,
            "recommended_for": ["testing", "lightweight"],
            "speed": "very_fast",
            "quality": "low"
        }
    }
    
    # Recommended model selection per agent
    AGENT_MODELS = {
        "pmo": "llama2:7b",  # General purpose, good for requirements analysis
        "architect": "llama2:7b",  # General purpose, reliable for architecture
        "code_writer": "codellama:7b",  # Specialized for code generation
        "code_reviewer": "codellama:7b",  # Specialized for code analysis
        "tester": "codellama:7b"  # Specialized for test generation
    }
    
    # Default configuration
    DEFAULT_MODEL = os.getenv("CREW_DEFAULT_MODEL", "codellama:7b")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    API_KEY = os.getenv("OLLAMA_API_KEY", "not-needed")
    
    @staticmethod
    def get_llm(model_name: str = None, base_url: str = None, api_key: str = None) -> LLM:
        """
        Get LLM instance with specified model
        
        Args:
            model_name: Model to use (default: codellama:7b)
            base_url: Ollama base URL (default: http://localhost:11434)
            api_key: API key for Ollama (default: not-needed)
        
        Returns:
            LLM instance configured for CrewAI
        """
        model = model_name or ModelConfig.DEFAULT_MODEL
        url = base_url or ModelConfig.OLLAMA_HOST
        key = api_key or ModelConfig.API_KEY
        
        return LLM(
            model=f"ollama/{model}",
            base_url=url,
            api_key=key
        )
    
    @staticmethod
    def get_llm_for_agent(agent_name: str, base_url: str = None) -> LLM:
        """
        Get LLM instance optimized for specific agent
        
        Args:
            agent_name: Name of agent (pmo, architect, code_writer, etc)
            base_url: Ollama base URL
        
        Returns:
            LLM instance configured for the agent's optimal model
        """
        model = ModelConfig.AGENT_MODELS.get(agent_name, ModelConfig.DEFAULT_MODEL)
        return ModelConfig.get_llm(model, base_url)
    
    @staticmethod
    def list_models() -> dict:
        """Get list of available models with info"""
        return ModelConfig.MODELS
    
    @staticmethod
    def get_model_info(model_name: str) -> dict:
        """Get detailed info about a specific model"""
        return ModelConfig.MODELS.get(model_name, {})
    
    @staticmethod
    def check_ollama_connection(base_url: str) -> tuple[bool, str]:
        """
        Verifica la connessione a Ollama.
        Restituisce (success: bool, message: str)
        """
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True, "Connessione riuscita"
            else:
                return False, f"Risposta non valida: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Impossibile connettersi a {base_url}"
        except requests.exceptions.Timeout:
            return False, f"Timeout 连接 a {base_url}"
        except Exception as e:
            return False, f"Errore: {str(e)}"
    
    @staticmethod
    def list_ollama_models(base_url: str) -> List[str]:
        """
        Rileva i modelli disponibili su Ollama.
        Restituisce lista di nomi modello.
        """
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return [m for m in models if m]  # Filtra vuoti
            else:
                print(f"⚠ Errore nella risposta Ollama: {response.status_code}")
                return []
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Ollama non attivo su {base_url}")
            print(f"   Assicurati che Ollama sia in esecuzione.")
            print(f"   Per avviarlo: ollama serve")
            return []
        except requests.exceptions.Timeout:
            print(f"⚠ Timeout nella connessione a {base_url}")
            return []
        except Exception as e:
            print(f"⚠ Errore nel rilevamento modelli: {e}")
            return []
    
    @staticmethod
    def update_agent_model(agent_name: str, model_name: str):
        """Aggiorna il modello per un agente specifico"""
        ModelConfig.AGENT_MODELS[agent_name] = model_name
    
    @staticmethod
    def update_ollama_host(host: str):
        """Aggiorna l'host di Ollama"""
        ModelConfig.OLLAMA_HOST = host
    
    @staticmethod
    def apply_config(config: Dict):
        """
        Applica la configurazione caricata.
        Aggiorna AGENT_MODELS e OLLAMA_HOST.
        """
        if "agent_models" in config:
            ModelConfig.AGENT_MODELS.update(config["agent_models"])
        
        if "ollama_host" in config:
            ModelConfig.OLLAMA_HOST = config["ollama_host"]
    
    @staticmethod
    def get_current_config() -> Dict:
        """Restituisce la configurazione corrente"""
        return {
            "version": 1,
            "ollama_host": ModelConfig.OLLAMA_HOST,
            "agent_models": ModelConfig.AGENT_MODELS.copy()
        }
    
    @staticmethod
    def get_available_models_from_config() -> List[str]:
        """Restituisce i nomi dei modelli definiti nella configurazione"""
        return list(ModelConfig.MODELS.keys())
