#!/bin/bash

# Script di attivazione del virtual environment locale per CREW

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        🚀 CREW - Multi-Agent Development System 🚀            ║"
echo "║                                                                ║"
echo "║     PMO → Architect → Code Writer → Reviewer → Tester        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# Ottiene la directory dello script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verifica che il venv esista
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${RED}❌ Errore: Virtual environment non trovato!${NC}"
    echo
    echo "Per attivare il venv:"
    echo "  cd $SCRIPT_DIR"
    echo "  source venv/bin/activate"
    echo
    exit 1
fi

# Attiva il venv
echo -e "${YELLOW}Attivazione ambiente virtuale locale...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Ambiente attivato!${NC}"
    echo
    echo "Virtual environment: $VIRTUAL_ENV"
    echo "Python: $(python3 --version)"
    echo
    echo "Per avviare CREW:"
    echo "  cd src/coding_crew"
    echo "  python3 main.py"
else
    echo -e "${RED}❌ Errore nell'attivazione del venv${NC}"
    exit 1
fi
