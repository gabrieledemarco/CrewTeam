#!/usr/bin/env bash
# Quick Start Script for CrewAI Multi-Agent System

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        🚀 CrewAI Multi-Agent System - QUICK START 🚀          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 PRE-REQUISITES CHECK${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓${NC} Python installed: $PYTHON_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Python not found. Please install Python 3.10+"
    exit 1
fi

# Check git
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓${NC} Git installed: $(git --version)"
else
    echo -e "${YELLOW}⚠${NC} Git not found. Please install git"
    exit 1
fi

# Check Ollama
echo ""
echo -e "${BLUE}🤖 OLLAMA STATUS${NC}"
if curl -s http://192.168.1.7:11434/api/tags &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is running and accessible"
else
    echo -e "${YELLOW}⚠${NC} Ollama not responding on 192.168.1.7:11434"
    echo "  Make sure to run:"
    echo "    PowerShell: \$env:OLLAMA_HOST = \"0.0.0.0\"; & ollama serve"
    echo "    WSL2:      OLLAMA_HOST=0.0.0.0:11434 ollama serve"
fi

echo ""
echo -e "${BLUE}📦 SETTING UP VIRTUAL ENVIRONMENT${NC}"
echo ""

# Create venv if not exists
if [ ! -d "$HOME/crewai-env" ]; then
    echo "Creating virtual environment at ~/crewai-env..."
    python3 -m venv ~/crewai-env
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

# Activate venv
source ~/crewai-env/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Install dependencies
echo ""
echo -e "${BLUE}📥 INSTALLING DEPENDENCIES${NC}"
echo ""

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} requirements.txt not found in current directory"
fi

echo ""
echo -e "${BLUE}🧠 CHECKING LLM MODELS${NC}"
echo ""

MODELS_NEEDED=("llama2:7b" "codellama:7b")

for model in "${MODELS_NEEDED[@]}"; do
    if curl -s http://192.168.1.7:11434/api/tags | grep -q "$model"; then
        echo -e "${GREEN}✓${NC} $model installed"
    else
        echo -e "${YELLOW}⚠${NC} $model not found"
        echo "  Install with: ollama pull $model"
    fi
done

echo ""
echo -e "${BLUE}✨ SETUP COMPLETE!${NC}"
echo ""
echo -e "${YELLOW}🚀 TO START THE SYSTEM:${NC}"
echo ""
echo "  1. Ensure Ollama is running with:"
echo "     PowerShell: \$env:OLLAMA_HOST = \"0.0.0.0\"; & ollama serve"
echo "     WSL2:      OLLAMA_HOST=0.0.0.0:11434 ollama serve"
echo ""
echo "  2. Run the CrewAI system:"
echo "     source ~/crewai-env/bin/activate"
echo "     cd ~/coding_crew/src/coding_crew"
echo "     python main.py"
echo ""
echo -e "${YELLOW}📚 DOCUMENTATION:${NC}"
echo "  • Main README:      ~/coding_crew/README.md"
echo "  • Implementation:   ~/coding_crew/IMPLEMENTATION.md"
echo ""
echo -e "${GREEN}Happy building! 🎉${NC}"
echo ""
