# 🚀 Deployment & Getting Started Guide

## System Overview

Your CrewAI Multi-Agent Development System is now fully implemented with:

- ✅ **5 Specialized Agents** (PMO, Architect, Code Writer, Reviewer, Tester)
- ✅ **Complete Development Pipeline** (Requirements → Code → Review → Tests)
- ✅ **Feedback Loop** (PMO evaluation + user refinement cycle)
- ✅ **Git Integration** (Auto-commits, versioning, tags)
- ✅ **Output Persistence** (Structured versioning with history)
- ✅ **Terminal UI** (Interactive feedback collection)
- ✅ **Optimized Models** (Specialized LLM per agent role)

## Quick Start (5 Minutes)

### Step 1: Ensure Ollama is Running

**Windows PowerShell:**
```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
& ollama serve
```

**WSL2:**
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

Keep this terminal open.

### Step 2: Activate Environment & Run

In a **new terminal**:

```bash
# Activate virtual environment
source ~/crewai-env/bin/activate

# Navigate to project
cd ~/coding_crew/src/coding_crew

# Run the system
python main.py
```

### Step 3: Interact with the System

```
Project name: my-awesome-project

Describe your project:
> Build a REST API for managing user profiles with authentication

[System will execute all stages automatically]

📋 USER FEEDBACK & NEXT STEPS
1. [ACCEPT] - Accept solution
2. [REFINE] - Request refinements
3. [RESTART] - New project
4. [VIEW] - View outputs
5. [EXIT] - Exit

What would you like to do? (1-5): 1

✅ Solution accepted!
→ Version incremented to v2
✓ Git tag: v2-accepted

📂 Outputs saved to: outputs/my-awesome-project/
✨ CrewAI session complete!
```

## Detailed Setup

### Prerequisites

- Python 3.10+
- Git
- 8GB+ RAM (16GB recommended for 7B models)
- 20GB+ disk space

### Installation Steps

```bash
# 1. Create virtual environment
python3 -m venv ~/crewai-env

# 2. Activate it
source ~/crewai-env/bin/activate

# 3. Navigate to project
cd ~/coding_crew

# 4. Install dependencies
pip install -r requirements.txt

# 5. Pull recommended models in Ollama
ollama pull llama2:7b
ollama pull codellama:7b
```

## Project Files Overview

```
~/coding_crew/
├── README.md                      # Complete documentation
├── IMPLEMENTATION.md              # Technical architecture
├── DEPLOYMENT_GUIDE.md           # This file
├── quickstart.sh                 # Setup automation script
├── requirements.txt              # Python dependencies
│
└── src/coding_crew/
    ├── main.py                   # Entry point
    ├── crew.py                   # Main orchestrator
    ├── agents.py                 # 5 agents
    ├── tasks.py                  # Task templates
    │
    └── config/
        ├── model_config.py       # LLM management
        ├── output_manager.py     # File persistence
        └── git_manager.py        # Git automation
```

## Configuration

### Change Default Model

Edit `src/coding_crew/config/model_config.py`:

```python
# Current (recommended):
DEFAULT_MODEL = "codellama:7b"

# For faster iteration:
DEFAULT_MODEL = "mistral:7b"

# For lightweight testing:
DEFAULT_MODEL = "qwen2.5-coder:1.5b"
```

### Change Ollama Host

Edit `src/coding_crew/config/model_config.py`:

```python
# Current (for Windows→WSL2):
OLLAMA_HOST = "http://192.168.1.7:11434"

# For local machine:
OLLAMA_HOST = "http://localhost:11434"

# For remote server:
OLLAMA_HOST = "http://your-server:11434"
```

## Output Locations

All outputs are saved to: `outputs/project-name/`

- `requirements/` - Technical specifications
- `architecture/` - System designs
- `code/` - Generated implementation
- `reviews/` - Code review reports
- `tests/` - Test suites
- `.git/` - Full git repository

Each version (v1, v2, v3) has its own files with timestamps.

## Troubleshooting

### "Connection refused at 192.168.1.7:11434"

1. Check your Windows IP:
   ```bash
   ipconfig  # Look for IPv4 Address
   ```

2. Update `OLLAMA_HOST` in `model_config.py`

3. Ensure Ollama is running with `OLLAMA_HOST=0.0.0.0`

### "Model not found: codellama:7b"

```bash
# Pull the model manually
ollama pull codellama:7b

# List installed models
ollama list
```

### "Out of memory"

1. Switch to smaller model:
   ```python
   DEFAULT_MODEL = "mistral:7b"  # Instead of llama2:7b
   ```

2. Or use quantized version:
   ```bash
   ollama pull codellama:7b-q4  # Quantized version
   ```

3. Close other applications consuming RAM

### CrewAI import errors

Ensure virtual environment is activated:
```bash
source ~/crewai-env/bin/activate
```

## Performance Expectations

Typical execution times for small projects (using 7B models on 8GB system):

- PMO Requirements Analysis: 2-3 min
- Architecture Design: 3-5 min
- Code Generation: 5-8 min
- Code Review: 2-3 min
- Test Generation: 3-5 min
- **Total per iteration: 15-25 min**

## Example Workflow

### Iteration 1: MVP

```
User Input: "Build a REST API for todo management"
→ Full pipeline executes
→ PMO evaluates: "Basic functionality complete, missing authentication"
User: [REFINE]
```

### Iteration 2: Add Auth

```
User Feedback: "Add JWT authentication and user profiles"
→ v2 of all stages execute with feedback incorporated
→ PMO evaluates: "Authentication added, database schema improved"
User: [REFINE]
```

### Iteration 3: Optimization

```
User Feedback: "Improve query performance and add caching"
→ v3 of all stages execute
→ PMO evaluates: "Optimization complete, all requirements met"
User: [ACCEPT]
→ Version finalized as v3
```

### Git History

```bash
cd outputs/todo-api
git log --oneline

# Output:
# v3-accepted                     - Accepted by user
# v3: evaluation stage completed
# v3: test stage completed
# v3: review stage completed
# v3: code stage completed
# v3: architecture stage completed
# v3: pmo stage completed
# v2-complete                     - Previous iteration
# v2: evaluation stage completed
# ... (more commits)
```

## Advanced Features

### View Iteration History

```bash
cd outputs/my-project

# See all commits
git log --oneline --all

# View specific version
cat requirements/v2_20240315_150000.md

# Compare versions
diff requirements/v1_*.md requirements/v2_*.md
```

### Access Generated Code

```bash
cd outputs/my-project/code

# View v2 code structure
tree v2/
# or
ls -la v2/

# Run generated code
cd v2
python main.py
```

### Review Stage Outputs

```bash
# View code review report
cat outputs/my-project/reviews/v1_*.md

# View test suite
cat outputs/my-project/tests/v1/test_*.py
```

## Next Steps

1. **Run your first project**
   ```bash
   python ~/coding_crew/src/coding_crew/main.py
   ```

2. **Explore generated outputs**
   ```bash
   cd outputs/my-project
   ls -la
   ```

3. **Check git history**
   ```bash
   cd outputs/my-project
   git log --oneline
   ```

4. **Customize agent behavior** (optional)
   - Edit `agents.py` to modify agent instructions
   - Edit `crew.py` to change task definitions

## Support & Documentation

- **README.md** - Complete feature documentation
- **IMPLEMENTATION.md** - Technical architecture details
- **Model configurations** - See `config/model_config.py`
- **Output examples** - Check `outputs/` directory structure

## Known Limitations

- Models run on CPU by default (slower) - GPU support via CUDA environment variables
- Small models (1.5B) have lower quality outputs
- Iterations take 15-25 min with 7B models
- Ollama requires separate window/terminal to run

## Next Enhancements (Optional)

1. **Parallel execution** - Run independent stages simultaneously
2. **Web UI** - Playground interface for visualization
3. **API endpoints** - REST interface for programmatic access
4. **Custom tools** - Add domain-specific tools for agents
5. **Model quantization** - Faster inference with Q4 models

---

**Ready to build?** 🚀

```bash
source ~/crewai-env/bin/activate
cd ~/coding_crew/src/coding_crew
python main.py
```

**Questions?** Check README.md and IMPLEMENTATION.md for detailed documentation.

**Happy building!** ✨
