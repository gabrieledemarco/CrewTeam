#!/bin/bash
# File di setup environment per Linux/WSL
# Fonte: ENVIRONMENT_VARIABLES.md

echo "🔧 Configurando variabili d'ambiente CREW..."
echo

# Configurazione Ollama
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_API_KEY="not-needed"

# Configurazione Modello Predefinito
export CREW_DEFAULT_MODEL="codellama:7b"

# Verifica configurazione
echo "✅ Variabili d'ambiente configurate:"
echo "   OLLAMA_HOST=$OLLAMA_HOST"
echo "   CREW_DEFAULT_MODEL=$CREW_DEFAULT_MODEL"
echo "   OLLAMA_API_KEY=$OLLAMA_API_KEY"
echo

# Attiva venv
if [ -d "venv" ]; then
    echo "🔌 Attivazione virtual environment..."
    source venv/bin/activate
    echo "✅ Ambiente attivato"
else
    echo "❌ Errore: virtual environment non trovato!"
    echo "Crea con: python3 -m venv venv"
    exit 1
fi

echo
echo "✨ Setup completato! Puoi ora eseguire il progetto:"
echo "   cd src/coding_crew"
echo "   python3 main.py"
echo
