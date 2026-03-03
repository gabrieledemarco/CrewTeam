# CrewAI Multi-Agent Development System

A local multi-agent software development assistant built on CrewAI and Ollama.

It can:
- start a new project and generate architecture/code/tests iteratively
- resume an existing project from GitHub or local workspace
- assess repository quality and stability with prioritized issues
- persist configuration and project outputs for repeatable runs

## Purpose

This project automates a practical development workflow with specialized agents:
- `PMO`: requirements analysis and evaluation
- `Architect`: architecture and technical design
- `Code Writer`: implementation output
- `Reviewer`: quality/security/maintainability review
- `Tester`: testing strategy and stability analysis

Main goals:
- reduce setup and coordination overhead
- keep an auditable workflow (saved outputs, git commits/tags)
- support iterative refinement based on user feedback

## Team Flow

```text
New project:
PMO -> Architect -> Code Writer -> Reviewer -> Tester -> PMO Evaluation -> User Feedback Loop

Resume project:
Repository Snapshot -> Assessment -> Improvement Plan -> Assessment Review -> Stability Report
```

## Architecture

```text
src/coding_crew/
  main.py                     # slim entrypoint / orchestration
  app_ui.py                   # UI helpers (banner, sections, status, prompts)
  app_config.py               # configuration load/validate/repair/persist
  app_project_selection.py    # project mode + source selection + requirements input
  crew.py                     # CrewOrchestrator and workflow logic
  agents.py                   # agent factory
  tasks.py                    # task definitions (if used)
  config/
    settings.py               # persistent config schema (crew_config.json)
    model_config.py           # Ollama model binding
    output_manager.py         # output persistence and generated project files
    git_manager.py            # git + GitHub integration (CLI/API fallback)
```

## Prerequisites

## System
- Python `3.10+` (project metadata allows `>=3.10`)
- Git installed and available in PATH
- Ollama installed and running

Optional but recommended:
- GitHub CLI (`gh`) authenticated (`gh auth login`)
- `GITHUB_TOKEN` or `GH_TOKEN` for API fallback/private repo access

## Runtime dependencies
Installed from `requirements.txt` or project metadata:
- `crewai`
- `crewai-tools`
- `langchain-openai`
- `python-dotenv`

## Installation

1. Clone repository:

```bash
git clone <your-repo-url>
cd CREW
```

2. Create and activate virtual environment:

```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS/Linux
# source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start Ollama:

```bash
ollama serve
```

5. Pull required models (example):

```bash
ollama pull llama2:7b
ollama pull codellama:7b
```

## Configuration

Configuration is stored in:

```text
crew_config.json
```

Required persisted fields:
- `ollama_host`
- `persist_project_to_disk`
- `project_base_dir`
- `github_root_url`

Behavior:
- first run: asks for required values and saves them
- next runs: asks `Use saved default configuration (Y/n)`
- if values are missing/invalid: warns, prompts correction, auto-saves updated config

Example config:

```json
{
  "version": 2,
  "ollama_host": "http://localhost:11434",
  "persist_project_to_disk": true,
  "project_base_dir": "C:/Users/you/Desktop/CREW/outputs",
  "github_root_url": "https://github.com/your-account/",
  "agent_models": {
    "pmo": "llama2:7b",
    "architect": "llama2:7b",
    "code_writer": "codellama:7b",
    "code_reviewer": "codellama:7b",
    "tester": "codellama:7b"
  }
}
```

## How to Run

From repository root:

```bash
python src/coding_crew/main.py
```

Or via script entry point (if installed as package):

```bash
run-crew
```

## Usage

## 1) Start a new project

You will:
- choose `Start a new project`
- provide project name and repository name
- provide requirements (inline or from file path)

The system will run iterative development flow and prompt:
- accept
- refine
- restart
- exit

## 2) Resume an existing project

You will:
- choose `Resume an existing project`
- see both:
  - repositories under configured GitHub root account
  - local projects found under configured base directory
- select source (`G#` or `L#`)

Then the system:
- clones/updates (GitHub source) or loads local workspace
- runs assessment pipeline
- produces:
  - `assessment`
  - `improvement_plan`
  - `assessment_review`
  - `stability_report` (prioritized issues for triage)

## Output and Project Structure

Per project, outputs are written under:

```text
<project_base_dir>/<project_name>/
  architecture/
  code/
  review/
  test/
  evaluation/
  assessment/
  improvement_plan/
  assessment_review/
  stability_report/
  project/
    current/                  # materialized latest project files
    versions/                 # snapshots by stage/version
```

## Environment Examples

## PowerShell (Windows)

```powershell
$env:GITHUB_TOKEN="your_token_here"   # optional but recommended
python .\src\coding_crew\main.py
```

## Bash (Linux/macOS)

```bash
export GITHUB_TOKEN="your_token_here"  # optional but recommended
python src/coding_crew/main.py
```

## Troubleshooting

## 1) Cannot list GitHub repositories (`WinError 2` / `gh` not found)

Cause:
- GitHub CLI not installed, or not in PATH.

Fix:
- install GitHub CLI (`gh`) and login:
  - `gh auth login`
- or provide `GITHUB_TOKEN`/`GH_TOKEN` so API fallback can work.

## 2) GitHub repositories list is empty

Checks:
- `github_root_url` format: `https://github.com/<account>/`
- token scopes allow reading repos (especially private)
- network access to `api.github.com`

## 3) Ollama connection fails

Checks:
- Ollama service running (`ollama serve`)
- configured `ollama_host` reachable
- model pulled locally (`ollama pull ...`)

## 4) Git clone/push failures

Checks:
- git installed and in PATH
- repo permissions
- auth state (credential manager, SSH/HTTPS token)

## 5) Local resume source not found

Checks:
- configured `project_base_dir` exists
- selected project has `project/current` workspace

## Development Notes

- Keep `main.py` focused on orchestration only.
- UI/config/selection logic are intentionally split into dedicated modules.
- Prefer adding behavior in:
  - `app_ui.py`
  - `app_config.py`
  - `app_project_selection.py`
  - `crew.py` (workflow logic)
  - `config/*` (infrastructure concerns)

## License

Use and distribution policy follows your repository settings.
