"""
CrewAI Orchestration with Full Workflow Loop
Implements: Requirements → Architecture → Code → Review → Test → User Feedback → Refinement
"""
from crewai import Crew, Process, Task
import agents as agent_factory
from config.output_manager import OutputManager
from config.git_manager import GitManager
from pathlib import Path
import threading
import time
import sys
from datetime import datetime
import re
import os
import ast
from textwrap import dedent
import subprocess
import tempfile
import shutil

NPM_ONLY_DEPENDENCIES = {
    "express",
    "body-parser",
    "cors",
    "bcryptjs",
    "jsonwebtoken",
    "sequelize",
    "ts-node",
    "typescript",
    "supertest",
    "react-router-dom",
}

PLACEHOLDER_MARKERS = [
    "add test implementation",
    "your_username",
    "your_password",
    "todo",
    "tbd",
]


class Spinner:
    """Animazione spinner per indicare attività in corso"""
    
    def __init__(self, message: str = "Elaborazione in corso"):
        self.message = message
        self.running = False
        self.thread = None
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def _spin(self):
        """Thread worker per l'animazione dello spinner"""
        i = 0
        while self.running:
            sys.stdout.write(f'\r{self.frames[i % len(self.frames)]} {self.message}... ')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
    
    def start(self):
        """Avvia lo spinner in un thread separato"""
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Ferma lo spinner"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()


class AgentTracker:
    """Tracciatore visivo per le attività degli agenti"""
    
    AGENT_ICONS = {
        "pmo": "📋",
        "architect": "🏗️",
        "code_writer": "💻",
        "code_reviewer": "🔍",
        "tester": "🧪"
    }
    
    AGENT_NAMES = {
        "pmo": "PMO",
        "architect": "Architect",
        "code_writer": "Code Writer",
        "code_reviewer": "Code Reviewer",
        "tester": "Tester"
    }
    
    @staticmethod
    def get_agent_key(agent_name: str) -> str:
        """Estrae la chiave dell'agente dal nome"""
        name_lower = agent_name.lower()
        for key in AgentTracker.AGENT_NAMES:
            if key in name_lower:
                return key
        return "pmo"
    
    @staticmethod
    def print_agent_thought(agent_name: str, thought: str):
        """Stampa il pensiero dell'agente in modo evidenziato"""
        icon = AgentTracker.AGENT_ICONS.get(
            AgentTracker.get_agent_key(agent_name), "🤖"
        )
        name = AgentTracker.AGENT_NAMES.get(
            AgentTracker.get_agent_key(agent_name), agent_name
        )
        
        print(f"\n{icon} **[{name}]** Pensiero:")
        print(f"   ┌{'─' * 60}┐")
        for line in thought.strip().split('\n')[:5]:
            if line.strip():
                print(f"   │ {line[:58]:<58} │")
        print(f"   └{'─' * 60}┘\n")
    
    @staticmethod
    def print_agent_action(agent_name: str, action: str):
        """Stampa l'azione corrente dell'agente"""
        icon = AgentTracker.AGENT_ICONS.get(
            AgentTracker.get_agent_key(agent_name), "🤖"
        )
        name = AgentTracker.AGENT_NAMES.get(
            AgentTracker.get_agent_key(agent_name), agent_name
        )
        print(f"\n{icon} **[{name}]** → {action}")
    
    @staticmethod
    def print_agent_start(agent_name: str, task: str):
        """Stampa quando un agente inizia un task"""
        icon = AgentTracker.AGENT_ICONS.get(
            AgentTracker.get_agent_key(agent_name), "🤖"
        )
        name = AgentTracker.AGENT_NAMES.get(
            AgentTracker.get_agent_key(agent_name), agent_name
        )
        
        print(f"\n{'='*60}")
        print(f"{icon} **[{name}]** STA LAVORANDO AL TASK:")
        print(f"   {task[:50]}..." if len(task) > 50 else f"   {task}")
        print(f"{'='*60}\n")
    
    @staticmethod
    def print_agent_complete(agent_name: str, result_preview: str = ""):
        """Stampa quando un agente completa un task"""
        icon = AgentTracker.AGENT_ICONS.get(
            AgentTracker.get_agent_key(agent_name), "🤖"
        )
        name = AgentTracker.AGENT_NAMES.get(
            AgentTracker.get_agent_key(agent_name), agent_name
        )
        
        preview = result_preview[:100] + "..." if len(result_preview) > 100 else result_preview
        print(f"\n✅ **[{name}]** COMPLETATO!")
        if preview.strip():
            print(f"   📝 Preview: {preview.strip()}")
        print("-" * 60)


class CrewOrchestrator:
    """Manages the complete workflow loop with feedback integration"""
    
    def __init__(
        self,
        project_name: str,
        base_dir: str = "outputs",
        enable_git: bool = True,
        auto_refinement_passes: int = 2,
        github_root_url: str = "",
        repository_name: str = ""
    ):
        self.project_name = project_name
        self.output_manager = OutputManager(project_name, base_dir=base_dir, enable_git=False)
        self.repo_worktree = self.output_manager.generated_project_dir / "current"
        self.git_manager = GitManager(
            self.repo_worktree,
            enable_git=enable_git,
            github_root_url=github_root_url,
            project_name=repository_name or project_name
        )
        self.enable_git = enable_git
        self.iteration = 1
        self.auto_refinement_passes = max(1, auto_refinement_passes)
        self._last_runtime_validation = {}
        self._acceptance_block_reason = ""

    def _collect_repository_snapshot(
        self,
        max_files: int = 120,
        max_chars_per_file: int = 3000
    ) -> str:
        """Build a compact snapshot of the checked-out repository for assessment."""
        root = self.repo_worktree
        if not root.exists():
            return "Repository worktree not found."

        exclude_dirs = {
            ".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".idea", ".vscode"
        }
        include_ext = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cs",
            ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".ini", ".cfg",
            ".env.example", ".sql", ".sh", ".ps1", ".html", ".css"
        }

        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in exclude_dirs]
            for filename in filenames:
                file_path = Path(dirpath) / filename
                rel = file_path.relative_to(root)
                if any(part in exclude_dirs for part in rel.parts):
                    continue
                if file_path.suffix.lower() in include_ext or filename.lower() in {
                    "readme", "readme.md", "package.json", "pyproject.toml",
                    "requirements.txt", "dockerfile", "makefile"
                }:
                    files.append(file_path)

        files = sorted(files)[:max_files]
        tree_lines = [str(path.relative_to(root)).replace("\\", "/") for path in files]

        sections = ["[REPOSITORY TREE]", "\n".join(tree_lines) if tree_lines else "(empty)"]
        for file_path in files:
            rel = str(file_path.relative_to(root)).replace("\\", "/")
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            clipped = content[:max_chars_per_file]
            suffix = "\n...[truncated]" if len(content) > max_chars_per_file else ""
            sections.append(f"[FILE] {rel}\n{clipped}{suffix}")

        return "\n\n".join(sections)

    def run_repository_assessment(self) -> dict:
        """
        Analyze an existing repository and produce structured technical assessment
        and concrete implementation improvements.
        """
        snapshot = self._collect_repository_snapshot()

        assessment_task = Task(
            description=f"""Perform a full technical assessment of this existing software repository.

Repository snapshot:
{snapshot}

Produce a structured report covering:
1. Codebase structure and module organization
2. Architecture strengths/weaknesses
3. Dependencies and potential risks (security/outdated coupling)
4. Documentation quality and gaps
5. Test coverage quality and missing tests
6. Missing components/features inferred from structure
7. High-priority issues and technical debt

Output format:
- Executive summary
- Detailed findings by section
- Risk matrix (high/medium/low)""",
            agent=agent_factory.create_pmo(),
            expected_output="Structured technical assessment of the existing repository"
        )

        improvement_task = Task(
            description="""Based on the assessment, propose concrete implementation improvements
and a development execution plan.

Include:
1. Specific code-level improvements (refactors, fixes, modules to add)
2. Architecture improvements and migration path
3. Dependency upgrade/remediation plan
4. Documentation improvements with file-level suggestions
5. Test strategy improvements (unit/integration/e2e)
6. Ordered implementation steps with priorities and estimated effort

Output format:
- Quick wins (1-2 days)
- Mid-term actions (1-2 weeks)
- Long-term improvements
- Step-by-step delivery roadmap""",
            agent=agent_factory.create_architect(),
            expected_output="Concrete implementation improvements and roadmap",
            context=[assessment_task]
        )

        review_task = Task(
            description="""Review the assessment and improvement plan for completeness and practicality.

Validate:
1. Whether critical risks were captured
2. Whether improvement steps are concrete and actionable
3. Whether sequencing is realistic
4. Any missing high-impact opportunities

Return a final consolidated recommendation document.""",
            agent=agent_factory.create_code_reviewer(),
            expected_output="Final consolidated technical recommendation",
            context=[assessment_task, improvement_task]
        )

        stability_task = Task(
            description="""Evaluate overall project stability based on the repository assessment outputs.

Your goal is to detect and report bugs, reliability risks, and operational weaknesses.

Produce a detailed, prioritized issues report with:
1. Stability verdict (Stable / At Risk / Unstable) and rationale
2. List of detected bugs/issues with one item per entry
3. For each issue include:
   - Title
   - Severity (Critical/High/Medium/Low)
   - Priority order (P1, P2, P3...)
   - Affected area/files/components
   - Symptoms / probable impact
   - Likely root cause
   - Suggested fix direction
4. Suggested execution order for remediation
5. Explicit note if no significant issues are detected

Output format:
- Stability summary
- Prioritized issue table/list
- Recommended remediation sequence""",
            agent=agent_factory.create_tester(),
            expected_output="Detailed project stability report with prioritized issues and remediation order",
            context=[assessment_task, improvement_task, review_task]
        )

        task_map = [
            ("assessment", assessment_task),
            ("improvement_plan", improvement_task),
            ("assessment_review", review_task),
            ("stability_report", stability_task),
        ]

        results = {}
        for stage_name, task in task_map:
            crew = Crew(
                agents=[
                    agent_factory.create_pmo(),
                    agent_factory.create_architect(),
                    agent_factory.create_code_reviewer(),
                    agent_factory.create_tester(),
                ],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )
            result = crew.kickoff()
            text = str(result)
            results[stage_name] = text
            self.output_manager.save_stage_output(stage_name, text)

        return results
        
    def create_tasks(self, user_request: str, previous_feedback: str = None):
        """Create all tasks for the current iteration"""
        
        # PMO Task: Analyze requirements and create specification
        pmo_task = Task(
            description=f"""Analyze the user's request and create an implementation-grade technical specification.

{"Previous feedback from user: " + previous_feedback if previous_feedback else ""}

User's request: {user_request}

You must produce a structured specification with these mandatory sections:
1. Scope and business objective
2. Functional requirements with acceptance criteria (testable)
3. Non-functional requirements (security, performance, reliability)
4. Explicit ecosystem lock:
   - primary language
   - framework/runtime
   - package manager
   - database/cache/service dependencies
5. Constraints and exclusions (what must NOT be introduced)
6. Delivery priorities (P1/P2/P3)

Important:
- Be concrete and implementation-ready.
- Avoid generic statements.
- The next agents must strictly follow your ecosystem lock.""",
            agent=agent_factory.create_pmo(),
            expected_output="Implementation-grade technical specification with explicit ecosystem lock",
        )
        
        # Architect Task: Design system architecture
        architecture_task = Task(
            description="""Design the architecture strictly from the PMO specification.

Mandatory output sections:
1. Component architecture and interaction flows
2. Data model/schema and migration approach
3. API contracts (routes, payloads, status codes, auth)
4. Dependency plan with exact versions and compatibility notes
5. Test strategy overview (unit/integration/e2e scope)
6. Documentation plan (what each doc file must contain)
7. Rollout/implementation phases

Hard constraints:
- Do NOT change technology stack defined in the PMO ecosystem lock.
- Do NOT mix incompatible ecosystems.
- Do NOT output placeholders.

Output only the architecture document (no tools).""",
            agent=agent_factory.create_architect(),
            expected_output="Detailed architecture design with dependency and documentation plan",
            context=[pmo_task],
        )
        
        # Code Writer Task: Generate implementation code
        code_task = Task(
            description="""Implement the project exactly from architecture and PMO specification.

Required outputs (all mandatory):
- Source code files for a runnable project
- README.md (detailed setup, run, test, troubleshooting)
- docs/ARCHITECTURE.md
- docs/DEPENDENCIES.md (runtime/dev deps, version rationale, compatibility notes)
- docs/TEST_PLAN.md (coverage scope, edge cases, execution commands)
- requirements.txt
- requirements-dev.txt

Quality constraints:
- No pseudo-code, no TODO/TBD placeholders, no "your_username/your_password".
- No fallback files like generated/file_*.*
- Keep dependency set minimal and coherent with chosen ecosystem.
- If Python stack is chosen, dependency files must contain Python packages only.
- Every import must resolve to a file/module in the project or valid external dependency.

Output format (strict):
For every file:
File: relative/path/to/file.ext
```language
<complete file content>
```

Do not output prose outside file blocks.""",
            agent=agent_factory.create_code_writer(),
            expected_output="Complete, runnable project files with detailed documentation and coherent dependencies",
            context=[architecture_task],
        )
        
        # Code Reviewer Task: Review code quality
        review_task = Task(
            description="""Review the generated project as a production readiness gate.

Report must include:
1. Blocking issues (bugs, security, runtime/dependency conflicts)
2. Documentation quality assessment (specific gaps by file)
3. Test quality assessment (missing scenarios, flaky tests, weak assertions)
4. Ecosystem consistency check (stack mismatch, invalid dependency manager usage)
5. Prioritized remediation plan (P1/P2/P3)

Important:
- Be specific with file-level findings.
- Do not claim code is missing; use provided context.""",
            agent=agent_factory.create_code_reviewer(),
            expected_output="Production-readiness review with prioritized findings and remediation plan",
            context=[code_task],
        )
        
        # Tester Task: Generate comprehensive tests
        test_task = Task(
            description="""Generate and refine tests for the implemented project.

Mandatory test qualities:
1. Real assertions (no placeholders)
2. Happy path + failure path + edge cases
3. Clear fixtures/mocks only where needed
4. Deterministic tests (no flaky sleeps/randomness without control)
5. Coverage aligned with PMO acceptance criteria

Output format (strict):
For every file:
File: relative/path/to/test_file.ext
```language
<complete file content>
```

Do not output prose outside file blocks.""",
            agent=agent_factory.create_tester(),
            expected_output="Runnable test suite with meaningful assertions and coverage",
            context=[code_task],
        )
        
        # PMO Evaluation Task: Validate results and decide next steps
        pmo_evaluation_task = Task(
            description="""Evaluate whether the solution is acceptable for delivery.

Validation checklist:
1. Requirements coverage against PMO spec
2. Ecosystem/stack consistency
3. Dependency coherence and conflict risk
4. Documentation depth and operational usefulness
5. Test adequacy and quality
6. Remaining risks and blockers

Output:
- Completion summary
- Blocking issues (if any)
- Recommended next actions
- Overall satisfaction score (1-10)""",
            agent=agent_factory.create_pmo(),
            expected_output="Delivery evaluation with score, blockers, and concrete next actions",
            context=[pmo_task, architecture_task, code_task, review_task, test_task],
        )
        
        return {
            "pmo": pmo_task,
            "architecture": architecture_task,
            "code": code_task,
            "review": review_task,
            "test": test_task,
            "evaluation": pmo_evaluation_task
        }

    @staticmethod
    def _build_evaluation_inputs(stage_results: dict, max_chars_per_stage: int = 6000) -> str:
        """Builds a structured artifact bundle for PMO evaluation."""
        stage_order = ["pmo", "architecture", "code", "review", "test"]
        sections = []
        for stage in stage_order:
            output = str(stage_results.get(stage, ""))
            clipped = output[:max_chars_per_stage]
            suffix = "\n...[truncated]" if len(output) > max_chars_per_stage else ""
            sections.append(f"[{stage.upper()} OUTPUT]\n{clipped}{suffix}")
        return "\n\n".join(sections)
    
    def run_stage(self, tasks: dict, stage_key: str) -> str:
        """Run a specific stage of the workflow"""
        
        stage_info = {
            "pmo": {"icon": "📋", "name": "PMO - Analisi Requisiti", "desc": "Analizzo i requisiti e creo la specifica tecnica"},
            "architecture": {"icon": "🏗️", "name": "Architect - Progettazione", "desc": "Progetto l'architettura del sistema"},
            "code": {"icon": "💻", "name": "Code Writer - Sviluppo", "desc": "Genero il codice sorgente"},
            "review": {"icon": "🔍", "name": "Code Reviewer - Revisione", "desc": "Revisiono qualità e sicurezza"},
            "test": {"icon": "🧪", "name": "Tester - Test", "desc": "Creo la suite di test"},
            "evaluation": {"icon": "📊", "name": "PMO - Valutazione", "desc": "Valuto la soluzione finale"}
        }
        
        info = stage_info.get(stage_key, {"icon": "⚙️", "name": stage_key.upper(), "desc": "Elaborazione"})
        
        start_time = datetime.now()
        start_str = start_time.strftime("%H:%M:%S")
        
        print(f"\n{'='*70}")
        print(f"{info['icon']} STAGE: {info['name']}")
        print(f"{'='*70}")
        print(f"📝 {info['desc']}")
        print(f"🕐 Inizio: {start_str}")
        print(f"{'='*70}\n")
        
        task = tasks[stage_key]
        print(f"📌 Task: {task.description[:80]}...")
        print(f"\n🚀 L'agente sta elaborando...\n")
        
        crew = Crew(
            agents=[
                agent_factory.create_pmo(),
                agent_factory.create_architect(),
                agent_factory.create_code_writer(),
                agent_factory.create_code_reviewer(),
                agent_factory.create_tester()
            ],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        spinner = Spinner(f"{info['name']}")
        
        spinner.start()
        try:
            result = crew.kickoff()
        finally:
            spinner.stop()
        
        end_time = datetime.now()
        end_str = end_time.strftime("%H:%M:%S")
        duration = end_time - start_time
        duration_str = str(duration).split('.')[0]
        
        print(f"\n{'='*70}")
        print(f"✅ STAGE COMPLETATO: {info['name']}")
        print(f"{'='*70}")
        print(f"🕐 Inizio: {start_str}")
        print(f"🕐 Fine:   {end_str}")
        print(f"⏱️  Durata: {duration_str}")
        print(f"📄 Output: {len(str(result))} caratteri")
        print(f"{'='*70}")
        
        preview = str(result)[:150].replace('\n', ' ')
        print(f"\n📝 Preview: {preview}{'...' if len(str(result)) > 150 else ''}")
        
        result_text = str(result)
        self.output_manager.save_stage_output(stage_key, result_text)

        if stage_key in ("code", "test"):
            self._materialize_generated_files(stage_key, result_text)

        self.git_manager.commit(f"v{self.output_manager.version}: {stage_key} stage completed")
        
        return result_text

    def _materialize_generated_files(self, stage_key: str, result_text: str) -> None:
        """Extract code blocks and write real project files to disk."""
        files = self.output_manager.extract_files_from_markdown(
            result_text,
            allow_generated_fallback=False,
        )
        files = self._split_embedded_file_markers(files)
        if not files:
            print(f"[warn] No explicit project files detected in {stage_key} output.")
            print("[warn] Ensure each code block is preceded by 'File: relative/path.ext'.")
            return

        if stage_key == "code":
            files = self._ensure_project_mandatory_files(files)
        elif stage_key == "test":
            files = self._filter_test_stage_files(files)
            if not files:
                print("[warn] Test stage output did not include valid test files after filtering.")
                return

        snapshot_label = f"v{self.output_manager.version}_it{self.iteration}_{stage_key}"
        saved_files, snapshot_root = self.output_manager.write_generated_project_files(
            files=files,
            snapshot_label=snapshot_label
        )
        print(f"[ok] Materialized {len(saved_files)} files into {self.output_manager.generated_project_dir / 'current'}")
        if snapshot_root:
            print(f"[ok] Snapshot saved in {snapshot_root}")

    @staticmethod
    def _split_embedded_file_markers(files: dict[str, str]) -> dict[str, str]:
        """
        Some model outputs accidentally include extra `File: ...` markers inside a code block.
        Split those blocks to avoid contaminating file contents.
        """
        marker_pattern = re.compile(r"^\s*File:\s+(.+?)\s*$", re.IGNORECASE)
        expanded: dict[str, str] = {}

        for file_path, content in files.items():
            lines = (content or "").splitlines()
            current_path = file_path
            buffer: list[str] = []
            saw_embedded_marker = False

            def flush(target_path: str, collected: list[str]) -> None:
                body = "\n".join(collected).strip("\n")
                if not body:
                    return
                expanded[target_path] = body.rstrip() + "\n"

            for line in lines:
                match = marker_pattern.match(line)
                if match:
                    saw_embedded_marker = True
                    flush(current_path, buffer)
                    buffer = []
                    candidate = OutputManager._sanitize_relative_path(match.group(1))
                    if candidate:
                        current_path = candidate
                    continue
                buffer.append(line)

            flush(current_path, buffer)

            if saw_embedded_marker:
                print(f"[warn] Detected embedded file markers inside {file_path}; auto-split applied.")

        return expanded

    @staticmethod
    def _filter_test_stage_files(files: dict[str, str]) -> dict[str, str]:
        """Keep only test-related files from tester stage to avoid clobbering project metadata."""
        filtered: dict[str, str] = {}
        dropped: list[str] = []

        for path, content in files.items():
            norm = path.lower().replace("\\", "/")
            name = Path(norm).name
            is_test_file = (
                norm.startswith("tests/")
                or "/tests/" in norm
                or "/test/" in norm
                or name.startswith("test_")
                or name.endswith("_test.py")
                or ".test." in name
            )
            is_test_doc = norm in {"docs/test_plan.md", "docs/testing.md", "docs/tests.md"}
            if is_test_file or is_test_doc:
                filtered[path] = content
            else:
                dropped.append(path)

        if dropped:
            preview = ", ".join(dropped[:5])
            suffix = " ..." if len(dropped) > 5 else ""
            print(f"[warn] Ignored non-test files in test stage output: {preview}{suffix}")

        return filtered

    def _ensure_project_mandatory_files(self, files: dict[str, str]) -> dict[str, str]:
        """
        Ensure mandatory project docs/dependency files exist.
        If missing, create safe templates so the generated project is runnable/documented.
        """
        normalized = dict(files)
        lower_paths = [path.lower().replace("\\", "/") for path in normalized.keys()]
        has_root_readme = "readme.md" in lower_paths
        has_any_readme = any(path.endswith("/readme.md") or path == "readme.md" for path in lower_paths)
        has_root_requirements = "requirements.txt" in lower_paths
        requirements_candidates = [
            path for path in normalized.keys()
            if path.lower().replace("\\", "/").endswith("requirements.txt")
        ]

        if not has_root_readme:
            normalized["README.md"] = dedent(
                f"""\
                # {self.project_name}

                ## Overview
                Auto-generated project produced by CrewAI.

                ## Project Structure
                - Source files: project root/subfolders
                - Dependencies: `requirements.txt`

                ## Setup
                1. Create a virtual environment
                2. Install dependencies:
                   `pip install -r requirements.txt`

                ## Run
                Follow the application entrypoint documented in source files.

                ## Notes
                This README was added automatically because the generated output did not include one.
                """
            ).rstrip() + "\n"
            if has_any_readme:
                print("[warn] Root README.md missing; added a root README template (another README exists in subfolders).")
            else:
                print("[warn] Generated output missed README.md; added a default README template.")

        if not has_root_requirements:
            if requirements_candidates:
                merged_lines = []
                seen = set()
                for candidate in requirements_candidates:
                    for line in self._requirements_lines_from_text(normalized.get(candidate, "")):
                        if line not in seen:
                            seen.add(line)
                            merged_lines.append(line)

                inferred = self._infer_runtime_requirements_from_files(normalized)
                for package in inferred:
                    if package not in seen:
                        seen.add(package)
                        merged_lines.append(package)

                if merged_lines:
                    normalized["requirements.txt"] = (
                        "# Root dependency file auto-generated by Crew from generated project files.\n"
                        + "\n".join(merged_lines).rstrip()
                        + "\n"
                    )
                    print("[warn] Root requirements.txt missing; generated merged dependency file from project outputs.")
                else:
                    normalized["requirements.txt"] = (
                        "# Root dependency file auto-generated by Crew.\n"
                        "# Populate dependencies before runtime.\n"
                    )
                    print("[warn] Root requirements.txt missing and no dependencies detected from generated output.")
            else:
                inferred = self._infer_runtime_requirements_from_files(normalized)
                if inferred:
                    normalized["requirements.txt"] = (
                        "# Root dependency file auto-generated by Crew from detected imports.\n"
                        + "\n".join(inferred).rstrip()
                        + "\n"
                    )
                    print("[warn] Generated output missed requirements.txt; generated dependencies from detected imports.")
                else:
                    normalized["requirements.txt"] = (
                        "# Root dependency file auto-generated by Crew.\n"
                        "# Populate dependencies before runtime.\n"
                    )
                    print("[warn] Generated output missed requirements.txt and no imports were detected to infer dependencies.")
        else:
            current_root_content = normalized.get("requirements.txt", "")
            if self._is_placeholder_requirements_content(current_root_content):
                inferred = self._infer_runtime_requirements_from_files(normalized)
                if inferred:
                    normalized["requirements.txt"] = (
                        "# Root dependency file refreshed by Crew from detected imports.\n"
                        + "\n".join(inferred).rstrip()
                        + "\n"
                    )
                    print("[warn] Root requirements.txt was placeholder-only; replaced with inferred dependencies.")

        return normalized

    @staticmethod
    def _requirements_lines_from_text(requirements_text: str) -> list[str]:
        lines = []
        for raw in (requirements_text or "").splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            lines.append(stripped)
        return lines

    @staticmethod
    def _is_placeholder_requirements_content(requirements_text: str) -> bool:
        lines = CrewOrchestrator._requirements_lines_from_text(requirements_text)
        if lines:
            return False
        placeholder_markers = [
            "auto-created because it was missing",
            "populate dependencies before runtime",
            "add all runtime dependencies required",
        ]
        lower = (requirements_text or "").lower()
        return any(marker in lower for marker in placeholder_markers)

    @staticmethod
    def _infer_runtime_requirements_from_files(files: dict[str, str]) -> list[str]:
        """
        Infer runtime dependencies from generated Python imports.
        Uses conservative mapping for common packages and ignores stdlib/local modules.
        """
        module_to_package = {
            "flask": "Flask",
            "flask_sqlalchemy": "Flask-SQLAlchemy",
            "flask_login": "Flask-Login",
            "flask_security": "Flask-Security-Too",
            "flask_jwt_extended": "flask-jwt-extended",
            "sqlalchemy": "SQLAlchemy",
            "psycopg2": "psycopg2-binary",
            "dotenv": "python-dotenv",
            "yaml": "PyYAML",
            "jwt": "PyJWT",
            "requests": "requests",
            "fastapi": "fastapi",
            "uvicorn": "uvicorn",
            "pydantic": "pydantic",
            "numpy": "numpy",
            "pandas": "pandas",
            "sklearn": "scikit-learn",
            "matplotlib": "matplotlib",
            "seaborn": "seaborn",
        }

        local_modules = set()
        for path in files:
            norm = path.replace("\\", "/")
            if not norm.endswith(".py"):
                continue
            parts = [p for p in norm.split("/") if p]
            if parts:
                top = parts[0]
                if top not in {"src", "app", "backend", "frontend"}:
                    local_modules.add(top)
            stem = Path(norm).stem
            if stem and stem != "__init__":
                local_modules.add(stem)

        detected_packages = set()
        stdlib_modules = set(getattr(sys, "stdlib_module_names", set()))

        for path, content in files.items():
            norm = path.replace("\\", "/").lower()
            if not norm.endswith(".py"):
                continue
            if "/test" in norm or norm.startswith("test_") or "/tests/" in norm:
                continue

            try:
                tree = ast.parse(content)
            except Exception:
                continue

            imported_modules = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name:
                            imported_modules.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.level and node.level > 0:
                        continue
                    if node.module:
                        imported_modules.add(node.module.split(".")[0])

            for module in imported_modules:
                if not module or module in stdlib_modules or module in local_modules:
                    continue
                mapped = module_to_package.get(module)
                if mapped:
                    detected_packages.add(mapped)

        return sorted(detected_packages, key=lambda value: value.lower())

    @staticmethod
    def _python_bin_from_venv(venv_dir: Path) -> Path:
        if os.name == "nt":
            return venv_dir / "Scripts" / "python.exe"
        return venv_dir / "bin" / "python"

    def _detect_smoke_command(self, project_root: Path) -> list[str]:
        """
        Detect a safe smoke-test command for Python projects.
        Priority:
        1) main.py --help
        2) app.py --help
        3) python -m py_compile on all .py files (fallback)
        """
        main_candidates = [
            project_root / "main.py",
            project_root / "app.py",
            project_root / "src" / "main.py",
        ]
        for candidate in main_candidates:
            if candidate.exists():
                return ["{python}", str(candidate), "--help"]

        py_files = list(project_root.rglob("*.py"))
        if py_files:
            return ["{python}", "-m", "py_compile"] + [str(path) for path in py_files[:200]]

        return []

    def _upsert_runtime_readme_section(self, project_root: Path, validation: dict) -> None:
        readme_path = project_root / "README.md"
        if not readme_path.exists():
            return

        start_marker = "<!-- CREW-RUNTIME-SECTION:START -->"
        end_marker = "<!-- CREW-RUNTIME-SECTION:END -->"

        status = "PASS" if validation.get("success") else "FAIL"
        quality_status = "PASS" if validation.get("quality_success", True) else "FAIL"
        smoke_cmd = validation.get("smoke_command") or "N/A"
        install_cmd = validation.get("install_command") or "python -m pip install -r requirements.txt"
        details = validation.get("details") or ""
        quality_issues = validation.get("quality_issues") or []

        tree_preview = []
        for path in sorted(project_root.rglob("*")):
            if len(tree_preview) >= 40:
                tree_preview.append("... (truncated)")
                break
            rel = path.relative_to(project_root)
            if any(part in {".git", ".venv", "venv", "__pycache__"} for part in rel.parts):
                continue
            prefix = "[D]" if path.is_dir() else "[F]"
            tree_preview.append(f"{prefix} {str(rel).replace(os.sep, '/')}")

        requirements_file_used = validation.get("requirements_file_used") or "requirements.txt"

        section = dedent(
            f"""\
            {start_marker}
            ## Runtime Prerequisites And Validation

            ### Prerequisites
            - Python distribution: CPython 3.10+ (recommended 3.11 on Windows x64)
            - Operating system: Windows/macOS/Linux
            - Tooling: `pip`, virtual environment support (`python -m venv`)
            - External services (if used by project): database/cache/message broker as described in source configs

            ### Install Dependencies
            ```bash
            {install_cmd}
            ```
            - Requirements file used: `{requirements_file_used}`

            ### Windows Setup (PowerShell)
            ```powershell
            python -m venv .venv
            .\\.venv\\Scripts\\Activate.ps1
            {install_cmd}
            ```

            ### Smoke Test
            ```bash
            {smoke_cmd}
            ```

            ### Project Structure Snapshot
            ```text
            {chr(10).join(tree_preview) if tree_preview else "(no files detected)"}
            ```

            ### Execution Notes
            - Run command should target the generated project entrypoint (for example `python app.py` or `python main.py`).
            - If runtime validation fails, resolve dependency conflicts first, then re-run install and smoke test.

            ### Latest Validation Status
            - Result: **{status}**
            - Notes: {details if details else "No additional details."}

            ### Artifact Quality Gate
            - Result: **{quality_status}**
            - Notes: {" | ".join(quality_issues[:5]) if quality_issues else "No quality issues detected."}
            {end_marker}
            """
        ).strip() + "\n"

        content = readme_path.read_text(encoding="utf-8", errors="ignore")
        if start_marker in content and end_marker in content:
            pattern = re.compile(
                re.escape(start_marker) + r".*?" + re.escape(end_marker),
                flags=re.DOTALL
            )
            content = pattern.sub(section.strip(), content)
        else:
            if not content.endswith("\n"):
                content += "\n"
            content += "\n" + section

        readme_path.write_text(content, encoding="utf-8")

    @staticmethod
    def _requirements_lines(requirements_path: Path) -> list[str]:
        try:
            raw = requirements_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return []
        lines = []
        for line in raw:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            lines.append(stripped)
        return lines

    @staticmethod
    def _is_requirement_directive(line: str) -> bool:
        stripped = (line or "").strip().lower()
        return stripped.startswith("-r ") or stripped.startswith("--requirement ")

    @staticmethod
    def _extract_requirement_name(line: str) -> str:
        stripped = (line or "").strip()
        if not stripped:
            return ""
        return re.split(r"[<>=!~\[\] ;@]", stripped, maxsplit=1)[0].strip().lower()

    @staticmethod
    def _is_known_npm_dependency(requirement_name: str) -> bool:
        return requirement_name in NPM_ONLY_DEPENDENCIES

    def _invalid_python_dependency_lines(self, lines: list[str]) -> list[str]:
        invalid = []
        for line in lines:
            if self._is_requirement_directive(line):
                continue
            req_name = self._extract_requirement_name(line)
            if not req_name:
                continue
            if self._is_known_npm_dependency(req_name):
                invalid.append(line)
                continue
            if not re.match(r"^[a-z0-9][a-z0-9._-]*$", req_name):
                invalid.append(line)
        return invalid

    def _has_real_dependency_lines(self, requirements_path: Path) -> bool:
        lines = self._requirements_lines(requirements_path)
        return any(not self._is_requirement_directive(line) for line in lines)

    def _normalize_requirement_lines(self, lines: list[str]) -> list[str]:
        alias_map = {
            "sklearn": "scikit-learn",
            "aws-sdk-boto3": "boto3",
        }
        normalized = []
        seen = set()
        for raw in lines:
            line = (raw or "").strip()
            if not line:
                continue
            if self._is_requirement_directive(line):
                continue
            pkg_key = self._extract_requirement_name(line)
            if not pkg_key:
                continue
            if pkg_key in alias_map:
                line = alias_map[pkg_key]
                pkg_key = line.lower()
            if self._is_known_npm_dependency(pkg_key):
                continue
            if not re.match(r"^[a-z0-9][a-z0-9._-]*$", pkg_key):
                continue
            if pkg_key in seen:
                continue
            seen.add(pkg_key)
            normalized.append(line)
        return normalized

    def _ensure_root_requirements(self, project_root: Path, selected_requirements: Path | None) -> Path:
        """
        Ensure root requirements.txt exists and contains concrete dependency lines.
        If root is missing/placeholder, populate it from selected requirements.
        """
        root_req = project_root / "requirements.txt"
        root_valid = root_req.exists() and self._has_real_dependency_lines(root_req)
        if root_valid:
            normalized_root = self._normalize_requirement_lines(self._requirements_lines(root_req))
            if normalized_root:
                root_req.write_text("\n".join(normalized_root).rstrip() + "\n", encoding="utf-8")
            return root_req

        source_lines = []
        if selected_requirements and selected_requirements.exists():
            source_lines = self._requirements_lines(selected_requirements)
        source_lines = self._normalize_requirement_lines(source_lines)

        if source_lines:
            root_req.write_text(
                "# Root dependency file auto-generated by Crew from validated project requirements.\n"
                + "\n".join(source_lines).rstrip()
                + "\n",
                encoding="utf-8",
            )
            print("[warn] Root requirements.txt was missing/placeholder; regenerated with concrete dependencies.")
        return root_req

    def _select_requirements_file_for_validation(self, project_root: Path) -> Path | None:
        """
        Select the most meaningful requirements file.
        Prefer root requirements.txt if it has real dependency content.
        Otherwise choose the best nested requirements.txt.
        """
        root_req = project_root / "requirements.txt"
        if root_req.exists():
            if self._has_real_dependency_lines(root_req):
                return root_req

        candidates = [path for path in project_root.rglob("requirements.txt") if path.is_file()]
        scored = []
        for path in candidates:
            lines = self._requirements_lines(path)
            dep_lines = [line for line in lines if not self._is_requirement_directive(line)]
            if not dep_lines:
                continue
            invalid_lines = self._invalid_python_dependency_lines(dep_lines)
            valid_count = len(dep_lines) - len(invalid_lines)
            if valid_count <= 0:
                continue
            # favor files closer to root and with more dependencies
            depth_penalty = len(path.relative_to(project_root).parts)
            scored.append((valid_count, -len(invalid_lines), -depth_penalty, path))

        if not scored:
            return root_req if root_req.exists() else None

        scored.sort(reverse=True)
        return scored[0][2]

    def _collect_artifact_quality_issues(self, project_root: Path) -> list[str]:
        """Run lightweight quality checks on generated files before runtime validation."""
        issues: list[str] = []

        generated_fallbacks = [
            path for path in project_root.rglob("generated/file_*")
            if path.is_file()
        ]
        if generated_fallbacks:
            preview = ", ".join(str(path.relative_to(project_root)).replace("\\", "/") for path in generated_fallbacks[:3])
            suffix = " ..." if len(generated_fallbacks) > 3 else ""
            issues.append(f"Fallback generated files detected ({preview}{suffix}).")

        required_docs = [
            "README.md",
            "docs/ARCHITECTURE.md",
            "docs/DEPENDENCIES.md",
            "docs/TEST_PLAN.md",
        ]
        for rel_doc in required_docs:
            if not (project_root / rel_doc).exists():
                issues.append(f"Missing required documentation file: {rel_doc}")

        exclude_dirs = {
            ".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"
        }
        scan_ext = {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".txt"}
        placeholder_hits = 0

        for path in project_root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(project_root)
            if any(part in exclude_dirs for part in rel.parts):
                continue
            if path.suffix.lower() not in scan_ext:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                continue

            if path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx"}:
                if re.search(r"(?mi)^\s*file:\s+.+$", content):
                    issues.append(
                        f"Embedded markdown file marker detected inside code file {str(rel).replace(os.sep, '/')}."
                    )
                    continue

            for marker in PLACEHOLDER_MARKERS:
                if marker in content:
                    issues.append(f"Placeholder marker '{marker}' found in {str(rel).replace(os.sep, '/')}.")
                    placeholder_hits += 1
                    break
            if placeholder_hits >= 5:
                break

        return issues

    def _validate_project_runtime(self) -> dict:
        """
        1) Test dependency installation (`pip install -r requirements.txt`)
        2) Run smoke test command
        3) Update generated project README with runtime instructions/result
        """
        project_root = self.repo_worktree
        requirements_path = self._select_requirements_file_for_validation(project_root)

        result = {
            "success": False,
            "quality_success": True,
            "install_success": False,
            "smoke_success": False,
            "install_command": "python -m pip install -r requirements.txt",
            "smoke_command": "",
            "requirements_file_used": "",
            "root_requirements_ok": False,
            "quality_issues": [],
            "details": "",
        }

        if not requirements_path or not requirements_path.exists():
            result["details"] = "No valid requirements.txt with dependency content found in generated project."
            self._upsert_runtime_readme_section(project_root, result)
            return result

        requirements_path = self._ensure_root_requirements(project_root, requirements_path)
        result["requirements_file_used"] = "requirements.txt"
        if not requirements_path.exists() or not self._has_real_dependency_lines(requirements_path):
            result["details"] = "Root requirements.txt is missing or still placeholder-only."
            self._upsert_runtime_readme_section(project_root, result)
            return result
        result["root_requirements_ok"] = True

        requirement_lines = self._requirements_lines(requirements_path)
        invalid_requirements = self._invalid_python_dependency_lines(requirement_lines)
        if invalid_requirements:
            bad_preview = ", ".join(invalid_requirements[:5])
            result["details"] = (
                "requirements.txt includes non-Python/incompatible dependencies "
                f"(e.g. {bad_preview}). Regenerate with Python-compatible dependencies only."
            )
            self._upsert_runtime_readme_section(project_root, result)
            return result

        quality_issues = self._collect_artifact_quality_issues(project_root)
        result["quality_issues"] = quality_issues
        if quality_issues:
            result["quality_success"] = False
            result["details"] = "Artifact quality gate failed: " + " | ".join(quality_issues[:5])
            self._upsert_runtime_readme_section(project_root, result)
            return result

        temp_root = Path(tempfile.mkdtemp(prefix="crew_runtime_check_"))
        venv_dir = temp_root / ".venv"
        try:
            create_venv = subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)],
                capture_output=True,
                text=True,
                timeout=180,
            )
            if create_venv.returncode != 0:
                result["details"] = f"venv creation failed: {create_venv.stderr.strip()}"
                self._upsert_runtime_readme_section(project_root, result)
                return result

            py_bin = self._python_bin_from_venv(venv_dir)
            install_cmd = [str(py_bin), "-m", "pip", "install", "-r", str(requirements_path)]
            install = subprocess.run(
                install_cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if install.returncode != 0:
                result["details"] = f"Dependency installation failed: {install.stderr.strip()[:800]}"
                self._upsert_runtime_readme_section(project_root, result)
                return result
            result["install_success"] = True

            pip_check = subprocess.run(
                [str(py_bin), "-m", "pip", "check"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if pip_check.returncode != 0:
                result["details"] = f"Dependency conflict detected by pip check: {pip_check.stdout.strip()[:800]}"
                self._upsert_runtime_readme_section(project_root, result)
                return result

            smoke_cmd_template = self._detect_smoke_command(project_root)
            if not smoke_cmd_template:
                result["details"] = "No Python smoke-test target found."
                self._upsert_runtime_readme_section(project_root, result)
                return result

            smoke_cmd = [part.replace("{python}", str(py_bin)) for part in smoke_cmd_template]
            result["smoke_command"] = " ".join(
                [part.replace("{python}", "python") for part in smoke_cmd_template]
            )
            smoke = subprocess.run(
                smoke_cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if smoke.returncode != 0:
                result["details"] = f"Smoke test failed: {smoke.stderr.strip()[:800]}"
                self._upsert_runtime_readme_section(project_root, result)
                return result

            result["smoke_success"] = True
            result["success"] = True
            result["details"] = "Dependencies installed and smoke test passed."
            self._upsert_runtime_readme_section(project_root, result)
            return result
        except Exception as exc:
            result["details"] = f"Runtime validation exception: {exc}"
            self._upsert_runtime_readme_section(project_root, result)
            return result
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

    @staticmethod
    def _extract_satisfaction_score(evaluation_text: str) -> int | None:
        """Extract first 1-10 numeric score from evaluation output."""
        score_patterns = [
            r"satisfaction score[^0-9]*(10|[1-9])",
            r"overall score[^0-9]*(10|[1-9])",
            r"\b(10|[1-9])\s*/\s*10\b",
            r"\bscore[^0-9]*(10|[1-9])\b",
        ]
        for pattern in score_patterns:
            match = re.search(pattern, evaluation_text, flags=re.IGNORECASE)
            if match:
                try:
                    value = int(match.group(1))
                    if 1 <= value <= 10:
                        return value
                except ValueError:
                    continue
        return None

    def _compute_acceptance_gate(self) -> tuple[bool, str]:
        validation = self._last_runtime_validation or {}
        if not validation:
            return (True, "")
        if not validation.get("quality_success", True):
            return (False, "Artifact quality gate failed.")
        if not validation.get("root_requirements_ok"):
            return (False, "Root requirements.txt is missing or invalid.")
        if not validation.get("install_success"):
            return (False, "Dependency installation failed.")
        if not validation.get("smoke_success"):
            return (False, "Smoke test failed or missing.")
        if not validation.get("success"):
            return (False, validation.get("details") or "Runtime validation failed.")
        return (True, "")
    
    def run_full_workflow(self, user_request: str, previous_feedback: str = None):
        """Execute the complete workflow with all stages"""
        
        print(f"\n{'='*70}")
        print(f"🚀 ITERATION #{self.iteration}")
        print(f"{'='*70}")
        
        if previous_feedback:
            print(f"\n📝 Incorporating feedback:\n{previous_feedback}\n")
        
        # Create all tasks
        tasks = self.create_tasks(user_request, previous_feedback)
        
        # Execute core planning stages
        results = {}
        for stage in ["pmo", "architecture"]:
            results[stage] = self.run_stage(tasks, stage)

        # Automatic internal build/review refinement cycles
        cycle_feedback = previous_feedback or ""
        for cycle in range(1, self.auto_refinement_passes + 1):
            print(f"\n{'='*60}")
            print(f"AUTO REFINEMENT CYCLE {cycle}/{self.auto_refinement_passes}")
            print(f"{'='*60}\n")

            if cycle_feedback:
                tasks["code"].description = (
                    f"{tasks['code'].description}\n\n"
                    "Apply the following concrete feedback in this pass:\n"
                    f"{cycle_feedback}\n"
                )

            results["code"] = self.run_stage(tasks, "code")
            results["review"] = self.run_stage(tasks, "review")
            results["test"] = self.run_stage(tasks, "test")

            validation = self._validate_project_runtime()
            self._last_runtime_validation = validation
            validation_text = dedent(
                f"""\
                Runtime Validation
                - Success: {validation.get('success')}
                - Artifact quality success: {validation.get('quality_success')}
                - Dependency install success: {validation.get('install_success')}
                - Smoke test success: {validation.get('smoke_success')}
                - Install command: {validation.get('install_command')}
                - Smoke command: {validation.get('smoke_command')}
                - Quality issues: {validation.get('quality_issues')}
                - Details: {validation.get('details')}
                """
            )
            self.output_manager.save_stage_output("runtime_validation", validation_text)
            if validation.get("success"):
                print("[ok] Runtime validation passed (dependency install + smoke test).")
            else:
                print("[warn] Runtime validation failed. Check runtime_validation output and README runtime section.")

            cycle_feedback = (
                "Review findings to address:\n"
                f"{results['review']}\n\n"
                "Testing findings/coverage to address:\n"
                f"{results['test']}"
            )
            if not validation.get("success"):
                cycle_feedback += (
                    "\n\nRuntime validation findings to address:\n"
                    f"{validation.get('details')}"
                )

        gate_ok, gate_reason = self._compute_acceptance_gate()
        self._acceptance_block_reason = gate_reason
        if gate_ok:
            print("[ok] Acceptance gate passed: quality, dependency, and runtime checks are valid.")
        else:
            print(f"[warn] Acceptance gate active: {gate_reason}")
        
        # Run evaluation
        print(f"\n{'='*60}")
        print(f"🎯 PMO EVALUATION")
        print(f"{'='*60}\n")
        tasks["evaluation"].description = (
            f"{tasks['evaluation'].description}\n\n"
            "Use the following outputs from previous stages as the source artifacts for your assessment:\n\n"
            f"{self._build_evaluation_inputs(results)}"
        )
        evaluation = self.run_stage(tasks, "evaluation")
        results["evaluation"] = evaluation

        score = self._extract_satisfaction_score(evaluation)
        if score is not None:
            print(f"[info] PMO satisfaction score detected: {score}/10")
        else:
            print("[warn] Could not detect a numeric PMO satisfaction score.")
        
        # Create project summary and tag version
        summary = self.output_manager.create_project_summary()
        self.git_manager.create_tag(
            f"v{self.output_manager.version}-complete",
            f"Iteration {self.iteration} complete with PMO evaluation"
        )
        
        return results
    
    def get_user_feedback(self) -> tuple:
        """Collect feedback from user"""
        print(f"\n{'='*70}")
        print(f"📋 USER FEEDBACK & NEXT STEPS")
        print(f"{'='*70}\n")
        
        print("Options:")
        print("1. [ACCEPT] - Accept the solution, increment version")
        print("2. [REFINE] - Request specific refinements or improvements")
        print("3. [RESTART] - Start over with new requirements")
        print("4. [VIEW] - View previous outputs")
        print("5. [EXIT] - Exit the system")
        print("6. [REPORT] - Analyze a report file and continue refinement\n")
        
        choice = input("What would you like to do? (1-6): ").strip()
        
        if choice == "1":
            gate_ok, gate_reason = self._compute_acceptance_gate()
            if not gate_ok:
                print("\n[warn] Acceptance blocked by runtime gate.")
                print(f"[warn] Reason: {gate_reason}")
                print("[info] Run a refinement cycle to fix quality/dependency/runtime issues before accepting.")
                return ("continue", None)
            print("\n✅ Solution accepted!")
            accepted_version = self.output_manager.version
            self.git_manager.create_tag(
                f"v{accepted_version}-accepted",
                f"Iteration {self.iteration} accepted by user"
            )
            self.output_manager.increment_version()
            return ("accept", None)
        
        elif choice == "2":
            feedback = input("\n📝 Describe what needs to be refined/improved:\n> ")
            return ("refine", feedback)
        
        elif choice == "3":
            return ("restart", None)
        
        elif choice == "4":
            self.view_outputs()
            return ("continue", None)
        
        elif choice == "5":
            return ("exit", None)

        elif choice == "6":
            report_path = input("\nðŸ“„ Enter report file path to analyze:\n> ").strip()
            if not report_path:
                print("No path provided.")
                return ("continue", None)
            try:
                report_content = Path(report_path).read_text(encoding="utf-8", errors="ignore").strip()
                if not report_content:
                    print("Report file is empty.")
                    return ("continue", None)
                report_feedback = (
                    "Analyze and apply the following report findings as actionable refinement input:\n\n"
                    f"Report path: {report_path}\n\n"
                    f"{report_content}"
                )
                print("\nâœ… Report loaded and attached to refinement context.")
                return ("refine", report_feedback)
            except Exception as exc:
                print(f"\nâš  Could not read report file: {exc}")
                return ("continue", None)
        
        else:
            print("Invalid choice. Please try again.")
            return self.get_user_feedback()
    
    def view_outputs(self):
        """Display previous outputs"""
        print(f"\n{'='*70}")
        print(f"📂 PREVIOUS OUTPUTS")
        print(f"{'='*70}\n")
        
        stages = ["pmo", "architecture", "code", "review", "test"]
        
        for stage in stages:
            history = self.output_manager.get_stage_history(stage)
            if history:
                print(f"\n{stage.upper()}:")
                for i, file in enumerate(history[:3], 1):
                    print(f"  {i}. {Path(file).name}")


def get_crew(project_name: str):
    """Factory function for backward compatibility"""
    return CrewOrchestrator(project_name)
