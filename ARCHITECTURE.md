# 🏗️ System Architecture

## Complete System Diagram

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION LAYER                             │
│                                   (main.py)                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  • Welcome banner & project creation                                   │  │
│  │  • Requirement input interface                                         │  │
│  │  • Real-time stage execution display                                  │  │
│  │  • Feedback menu (5 options)                                          │  │
│  │  • Error handling & retry loops                                       │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER (crew.py)                            │
│                         CrewOrchestrator Class                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  Responsibilities:                                                      │  │
│  │  • Manage workflow pipeline (6 stages)                                 │  │
│  │  • Execute stages sequentially                                         │  │
│  │  • Integrate OutputManager for persistence                            │  │
│  │  • Integrate GitManager for versioning                                │  │
│  │  • Track iteration count & versions                                   │  │
│  │  • Collect & process user feedback                                    │  │
│  │                                                                        │  │
│  │  Methods:                                                             │  │
│  │  • run_full_workflow()  - Execute all 6 stages                       │  │
│  │  • run_stage()          - Execute single stage                        │  │
│  │  • create_tasks()       - Generate task definitions                   │  │
│  │  • get_user_feedback()  - Collect user input                          │  │
│  │  • view_outputs()       - Display previous versions                   │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
                                    ↓
        ┌───────────────────────────┬───────────────────────────┐
        ↓                           ↓                           ↓
   ┌─────────────┐         ┌──────────────────┐      ┌───────────────────┐
   │ AGENT LAYER │         │ PERSISTENCE LAYER│      │ GIT INTEGRATION   │
   │ (agents.py) │         │ (output_manager) │      │ (git_manager.py)  │
   └─────────────┘         └──────────────────┘      └───────────────────┘
        │                           │                       │
        │                           │                       │
   5 AGENTS:                  OUTPUTS:                  OPERATIONS:
   • PMO                      • Save by stage           • Auto-commit
   • Architect                • Version tracking       • Create tags
   • Code Writer              • Metadata JSON          • View history
   • Code Reviewer            • File organization      • Status checks
   • Tester                   • Project summary        • Log retrieval
        │                           │                       │
        └───────────────────────────┴───────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────────┐
│                    MODEL MANAGEMENT LAYER (model_config.py)                   │
│                              ModelConfig Class                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  LLM Instances:                                                         │  │
│  │  • llm_pmo          → llama2:7b   (requirements analysis)             │  │
│  │  • llm_architect    → llama2:7b   (system design)                     │  │
│  │  • llm_code_writer  → codellama:7b (code generation)                 │  │
│  │  • llm_code_reviewer→ codellama:7b (code analysis)                   │  │
│  │  • llm_tester       → codellama:7b (test generation)                 │  │
│  │                                                                        │  │
│  │  Configuration:                                                       │  │
│  │  • OLLAMA_HOST = "http://192.168.1.7:11434"                          │  │
│  │  • DEFAULT_MODEL = "codellama:7b"                                    │  │
│  │  • AGENT_MODELS dict for per-agent selection                         │  │
│  │  • 5 model definitions with specs                                    │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                         │  │
│  │  OLLAMA (Local LLM Server)          GIT (Version Control)              │  │
│  │  ┌──────────────────────────┐      ┌──────────────────────────┐       │  │
│  │  │ Runs models locally      │      │ Tracks all changes       │       │  │
│  │  │ No cloud APIs needed     │      │ Creates commits          │       │  │
│  │  │ Port: 11434              │      │ Tags versions            │       │  │
│  │  │                          │      │ Maintains history        │       │  │
│  │  │ Models:                  │      │                          │       │  │
│  │  │ • llama2:7b              │      │ Repos created per project│       │  │
│  │  │ • codellama:7b           │      │ Auto-commits after each │       │  │
│  │  │ • mistral:7b (optional)  │      │ stage (v#: stage name)  │       │  │
│  │  │ • qwen (testing)         │      │ Tags: v#-complete,      │       │  │
│  │  │                          │      │       v#-accepted       │       │  │
│  │  └──────────────────────────┘      └──────────────────────────┘       │  │
│  │                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────────┐
│                        FILESYSTEM STORAGE                                     │
│                                                                               │
│  outputs/project-name/                                                        │
│  ├── .git/                    (Git repository)                               │
│  ├── requirements/            (PMO specifications)                           │
│  │   ├── v1_timestamp.md                                                    │
│  │   ├── v1_timestamp.json                                                  │
│  │   └── v2_timestamp.md      (Refined with feedback)                       │
│  │                                                                           │
│  ├── architecture/            (Architecture designs)                         │
│  │   ├── v1_timestamp.md                                                    │
│  │   └── v2_timestamp.md                                                    │
│  │                                                                           │
│  ├── code/                    (Generated implementation)                      │
│  │   ├── v1/                  (File structure per version)                  │
│  │   │   ├── main.py                                                       │
│  │   │   ├── models/                                                       │
│  │   │   └── routes/                                                       │
│  │   └── v2/                  (Updated based on feedback)                   │
│  │                                                                           │
│  ├── reviews/                 (Code review reports)                          │
│  │   ├── v1_timestamp.md                                                    │
│  │   └── v2_timestamp.md                                                    │
│  │                                                                           │
│  └── tests/                   (Test suites)                                  │
│      ├── v1/                  (Test files per version)                       │
│      │   ├── test_models.py                                                │
│      │   └── test_routes.py                                                │
│      └── v2/                  (Updated tests)                               │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Execution Flow

```
START (main.py)
  ├─ print_banner()
  ├─ get_project_name()
  ├─ CrewOrchestrator.__init__()
  │   ├─ OutputManager()
  │   │   ├─ _setup_directories()
  │   │   └─ _init_git_repo()
  │   └─ GitManager()
  │
  └─ ITERATION LOOP:
      │
      ├─ run_full_workflow(requirements, feedback)
      │   │
      │   ├─ create_tasks(requirements, feedback)
      │   │   ├─ PMO Task (with feedback if provided)
      │   │   ├─ Architecture Task
      │   │   ├─ Code Task
      │   │   ├─ Review Task
      │   │   ├─ Test Task
      │   │   └─ PMO Evaluation Task
      │   │
      │   └─ For each stage in [pmo, architecture, code, review, test, evaluation]:
      │       │
      │       ├─ run_stage(tasks, stage)
      │       │   │
      │       │   ├─ Crew.kickoff([task])
      │       │   │   └─ [Agent executes with LLM]
      │       │   │
      │       │   ├─ OutputManager.save_stage_output()
      │       │   │   ├─ Create versioned markdown file
      │       │   │   ├─ Save JSON metadata
      │       │   │   └─ Store in memory
      │       │   │
      │       │   └─ GitManager.commit()
      │       │       └─ "v#: stage stage completed"
      │       │
      │       [Logs displayed in real-time]
      │
      ├─ get_user_feedback()
      │   ├─ Display menu with 5 options
      │   └─ Collect user choice + optional text
      │
      └─ Process feedback:
          ├─ [ACCEPT]
          │   ├─ OutputManager.increment_version()
          │   ├─ GitManager.create_tag("v#-accepted")
          │   └─ EXIT
          │
          ├─ [REFINE]
          │   ├─ iteration += 1
          │   ├─ LOOP BACK TO run_full_workflow() with feedback
          │   └─ (stages re-run with v# incremented)
          │
          ├─ [RESTART]
          │   ├─ Get new requirements
          │   ├─ iteration = 1
          │   └─ LOOP BACK with new project
          │
          ├─ [VIEW]
          │   ├─ view_outputs()
          │   │   └─ Display all versions of each stage
          │   └─ Continue (loop back to feedback menu)
          │
          └─ [EXIT]
              ├─ Print project summary
              ├─ Print output directory path
              └─ EXIT

END
```

## Data Flow

```
USER INPUT
    ↓
┌─────────────────────────────────┐
│ user_request (string)           │
│ project_name (string)           │
│ iteration (int)                 │
└─────────────────────────────────┘
    ↓
ORCHESTRATOR LAYER
    ↓
┌─────────────────────────────────┐
│ Tasks (CrewAI Task objects)     │
│ Results (string outputs)        │
│ Version tracking (v#)           │
└─────────────────────────────────┘
    ↓
DUAL OUTPUT PATH
    ├─ PERSISTENCE PATH            ├─ GIT PATH
    │  ↓                           │  ↓
    │  OutputManager              GitManager
    │  ├─ save_stage_output()     ├─ commit()
    │  ├─ save_code_files()       ├─ create_tag()
    │  ├─ save_test_files()       └─ get_log()
    │  └─ increment_version()
    │  ↓                          │  ↓
    │  FILESYSTEM                │  GIT REPO
    │  ├─ requirements/          │  ├─ .git/objects
    │  ├─ architecture/          │  ├─ .git/refs
    │  ├─ code/                  │  └─ HEAD
    │  ├─ reviews/
    │  └─ tests/
    │
    └─ UI DISPLAY PATH
        ↓
        Console Output
        (logs + results)
        ↓
        USER FEEDBACK
        (menu + input)
```

## Agent Pipeline

```
INPUT: user_request (with optional feedback)
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ AGENT 1: PMO (llama2:7b)                                        │
│ • Analyzes requirements                                         │
│ • Creates technical specification                              │
│ • If feedback: incorporates it into spec                       │
│ OUTPUT: Technical spec markdown                                │
└─────────────────────────────────────────────────────────────────┘
    ↓
    └─→ OutputManager.save_stage_output("pmo", result)
    └─→ GitManager.commit("v#: pmo stage completed")
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ AGENT 2: Architect (llama2:7b)                                  │
│ • Receives PMO specification                                   │
│ • Designs system architecture                                  │
│ • Selects technology stack                                     │
│ OUTPUT: Architecture design markdown                           │
└─────────────────────────────────────────────────────────────────┘
    ↓
    └─→ OutputManager.save_stage_output("architecture", result)
    └─→ GitManager.commit("v#: architecture stage completed")
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ AGENT 3: Code Writer (codellama:7b)                             │
│ • Receives architecture design                                 │
│ • Writes production-ready code                                 │
│ • Creates file structure & modules                             │
│ OUTPUT: Multiple code files + structure                        │
└─────────────────────────────────────────────────────────────────┘
    ↓
    ├─→ OutputManager.save_code_files(code_dict)
    └─→ GitManager.commit("v#: code stage completed")
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ AGENT 4: Code Reviewer (codellama:7b)                           │
│ • Receives generated code                                      │
│ • Reviews for quality & security                               │
│ • Provides recommendations                                     │
│ OUTPUT: Code review report markdown                            │
└─────────────────────────────────────────────────────────────────┘
    ↓
    └─→ OutputManager.save_stage_output("review", result)
    └─→ GitManager.commit("v#: review stage completed")
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ AGENT 5: Tester (codellama:7b)                                  │
│ • Receives code and review feedback                            │
│ • Generates comprehensive test suites                          │
│ • Unit, integration, E2E tests                                 │
│ OUTPUT: Multiple test files                                    │
└─────────────────────────────────────────────────────────────────┘
    ↓
    ├─→ OutputManager.save_test_files(test_dict)
    └─→ GitManager.commit("v#: test stage completed")
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ AGENT 6: PMO Evaluation (llama2:7b)                             │
│ • Re-uses PMO agent for evaluation                             │
│ • Reviews all outputs                                          │
│ • Validates against original requirements                      │
│ • Determines satisfaction score (1-10)                         │
│ • Lists gaps or issues                                         │
│ OUTPUT: Evaluation report markdown                             │
└─────────────────────────────────────────────────────────────────┘
    ↓
    ├─→ OutputManager.save_stage_output("evaluation", result)
    ├─→ GitManager.commit("v#: evaluation complete")
    ├─→ GitManager.create_tag("v#-complete")
    └─→ USER FEEDBACK LOOP

USER FEEDBACK
    ├─ [ACCEPT] → version increment → EXIT
    ├─ [REFINE] → feedback → LOOP BACK TO PMO WITH FEEDBACK
    ├─ [RESTART] → new requirements → EXIT & RESTART
    ├─ [VIEW] → display history → CONTINUE
    └─ [EXIT] → EXIT
```

## Model Assignment Logic

```
Agent Role Selection:
    ↓
    ├─ "pmo"           → llama2:7b       (general, reliable)
    ├─ "architect"     → llama2:7b       (general, reliable)
    ├─ "code_writer"   → codellama:7b    (specialized)
    ├─ "code_reviewer" → codellama:7b    (specialized)
    └─ "tester"        → codellama:7b    (specialized)

Fallback:
    └─ DEFAULT_MODEL  → codellama:7b

Configuration location:
    └─ config/model_config.py
        ├─ AGENT_MODELS dict
        ├─ DEFAULT_MODEL
        ├─ OLLAMA_HOST
        └─ Available models list
```

## Version Tracking Schema

```
Project Lifecycle:

ITERATION 1 (v1):
  pmo_task           → requirements/v1_TIMESTAMP.md
  architecture_task  → architecture/v1_TIMESTAMP.md
  code_task          → code/v1/* (files)
  review_task        → reviews/v1_TIMESTAMP.md
  test_task          → tests/v1/* (files)
  evaluation_task    → evaluation/v1_TIMESTAMP.md
  Git: v1-complete tag

ITERATION 2 (v2) - WITH FEEDBACK:
  pmo_task           → requirements/v2_TIMESTAMP.md (incorporates feedback)
  architecture_task  → architecture/v2_TIMESTAMP.md
  code_task          → code/v2/* (updated files)
  review_task        → reviews/v2_TIMESTAMP.md
  test_task          → tests/v2/* (updated tests)
  evaluation_task    → evaluation/v2_TIMESTAMP.md
  Git: v2-complete tag

ITERATION 3 (v3):
  ... (same pattern)
  Git: v3-complete tag → v3-accepted tag (if user accepts)

FINAL STATE:
  ├─ Latest version: v3 (accepted)
  ├─ Full history: v1, v2, v3
  ├─ Git log: All commits and tags
  └─ Comparison: Diffs between versions
```

---

This architecture ensures:
- ✅ Separation of concerns (UI, orchestration, persistence, models)
- ✅ Scalability (easy to add more agents)
- ✅ Offline operation (Ollama-based)
- ✅ Full auditability (git history)
- ✅ Version management (v1, v2, v3...)
- ✅ Feedback integration (iterative refinement)
- ✅ Persistence (structured outputs)
