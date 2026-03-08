#!/usr/bin/env python3
"""
CrewAI Multi-Agent System - Main Entry Point
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_config import (
    load_or_initialize_configuration,
    show_config_summary,
    validate_critical_settings,
)
from app_project_selection import (
    choose_project_mode,
    choose_resume_target,
    read_requirements_input,
)
from app_ui import ask_bool, banner, section, status_ok, status_warn
from config.git_manager import GitManager
from crew import CrewOrchestrator


def setup_logging():
    """Configure centralized logging with file and console output"""
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
    logger.info("[*] CrewAI session started")
    logger.info(f"[LOG] Log file: {log_file}")
    
    return logger


def check_ollama_connection(host: str) -> bool:
    """Verify Ollama is running and responsive"""
    try:
        response = requests.get(f"{host.rstrip('/')}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def run_resume_flow(orchestrator: CrewOrchestrator, cfg: dict, repository_name: str, resume_source: str) -> None:
    status_ok("Preparing local repository workspace...")

    if resume_source == "github":
        clone_ok = GitManager.clone_or_update_repository(
            github_root_url=cfg["github_root_url"],
            repo_name=repository_name,
            destination_path=orchestrator.repo_worktree,
        )
        if not clone_ok:
            status_warn("Failed to clone/update selected repository.")
            return
    else:
        local_base = cfg.get("project_base_dir") or str((Path.cwd() / "outputs").resolve())
        local_path = Path(local_base) / repository_name / "project" / "current"
        if not local_path.exists():
            status_warn(f"Local project path not found: {local_path}")
            return
        orchestrator.repo_worktree = local_path
        status_ok(f"Using local project workspace: {local_path}")

    section("Repository Assessment")
    results = orchestrator.run_repository_assessment()
    status_ok("Assessment completed.")
    for stage in ("assessment", "improvement_plan", "assessment_review", "stability_report"):
        if stage in results:
            print(f"  - {stage}: {len(results[stage])} chars")

    print(f"\nOutputs saved to: {orchestrator.output_manager.project_dir}")
    print(f"Repository path: {orchestrator.repo_worktree}")
    if orchestrator.git_manager.github_repo_url:
        print(f"GitHub repository: {orchestrator.git_manager.github_repo_url}")

    section("Post-Assessment Next Steps")
    status_ok("Choose whether the current result is satisfactory or additional actions are required.")

    base_request = (
        f"Continue development/refinement for project '{repository_name}' "
        "using the existing codebase and latest assessment artifacts."
    )
    feedback = None
    loop_active = True

    while loop_active:
        action, action_feedback = orchestrator.get_user_feedback()

        if action == "accept":
            status_ok("Resume flow finalized by user.")
            break

        if action == "refine":
            feedback = action_feedback
            orchestrator.iteration += 1
            status_ok(f"Running additional refinement iteration {orchestrator.iteration}...")
            orchestrator.run_full_workflow(base_request, feedback)
            continue

        if action == "restart":
            new_request = read_requirements_input()
            if not new_request:
                status_warn("No new request provided.")
                continue
            orchestrator.iteration = 1
            orchestrator.run_full_workflow(new_request, None)
            continue

        if action == "continue":
            continue

        if action == "exit":
            print("\nSession closed.")
            loop_active = False


def run_new_project_flow(orchestrator: CrewOrchestrator) -> None:
    user_request = read_requirements_input()
    if not user_request:
        status_warn("No requirements provided. Exiting.")
        return

    feedback = None
    loop_active = True

    while loop_active:
        try:
            orchestrator.run_full_workflow(user_request, feedback)

            while True:
                action, action_feedback = orchestrator.get_user_feedback()

                if action == "accept":
                    status_ok("Solution finalized and saved.")
                    loop_active = False
                    break

                if action == "refine":
                    feedback = action_feedback
                    orchestrator.iteration += 1
                    status_ok(f"Starting iteration {orchestrator.iteration} with refinements.")
                    break

                if action == "restart":
                    user_request = read_requirements_input()
                    orchestrator.iteration = 1
                    feedback = None
                    break

                if action == "continue":
                    continue

                if action == "exit":
                    print("\nSession closed.")
                    loop_active = False
                    break

        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break
        except Exception as exc:
            status_warn(f"Runtime error: {exc}")
            retry = ask_bool("Retry current workflow", True)
            if not retry:
                break


def main():
    # Initialize logging FIRST
    logger = setup_logging()
    
    banner()
    logger.info("Loading configuration...")
    cfg = load_or_initialize_configuration()
    show_config_summary(cfg)

    if not validate_critical_settings(cfg):
        status_warn("Fix configuration and run again.")
        logger.error("Configuration validation failed")
        return

    # Verify Ollama connection before proceeding
    logger.info("Checking Ollama connection...")
    if not check_ollama_connection(cfg["ollama_host"]):
        status_warn(f"⚠️  Ollama server not responding at: {cfg['ollama_host']}")
        status_warn("Please ensure Ollama is running: ollama serve")
        retry = ask_bool("Retry connection check", False)
        if not retry:
            logger.warning("Ollama connection check failed, user chose not to retry")
            return
        # Retry check
        if not check_ollama_connection(cfg["ollama_host"]):
            status_warn("Ollama still not available. Exiting.")
            logger.error("Ollama connection failed after retry")
            return
    
    logger.info("✅ Ollama connection OK")
    status_ok("✅ Ollama connection verified")

    mode = choose_project_mode()
    project_name = ""
    repository_name = ""
    resume_source = ""

    if mode == "new":
        section("New Project Setup")
        project_name = input("\nProject name: ").strip() or "my-project"
        repository_name = input(
            f"Repository name [default: {project_name}]: "
        ).strip() or project_name
        status_ok(f"New project selected: {project_name} (repo: {repository_name})")
    else:
        resume_source, selected_name = choose_resume_target(
            cfg["github_root_url"],
            cfg.get("project_base_dir") or str((Path.cwd() / "outputs").resolve()),
        )
        repository_name = selected_name
        if not repository_name:
            status_warn("Project selection failed.")
            return
        project_name = repository_name
        status_ok(f"Resuming project: {repository_name} (source: {resume_source})")

    passes_input = input(
        "Automatic code/review/test passes before user prompt [default: 2]: "
    ).strip()
    try:
        auto_refinement_passes = int(passes_input) if passes_input else 2
    except ValueError:
        auto_refinement_passes = 2

    persist_to_disk = bool(cfg.get("persist_project_to_disk", True))
    configured_base_dir = cfg.get("project_base_dir") or str((Path.cwd() / "outputs").resolve())
    base_dir = configured_base_dir if persist_to_disk else str((Path.cwd() / ".crew_temp_outputs").resolve())

    orchestrator = CrewOrchestrator(
        project_name=project_name,
        base_dir=base_dir,
        enable_git=True,
        auto_refinement_passes=auto_refinement_passes,
        github_root_url=cfg["github_root_url"],
        repository_name=repository_name,
    )

    if mode == "resume":
        run_resume_flow(orchestrator, cfg, repository_name, resume_source)
        return

    run_new_project_flow(orchestrator)

    print("\n" + "=" * 78)
    print("PROJECT SUMMARY")
    print("=" * 78)
    print(orchestrator.output_manager.create_project_summary())
    print(f"Outputs saved to: {orchestrator.output_manager.project_dir}")
    if orchestrator.git_manager.github_repo_url:
        print(f"GitHub repository: {orchestrator.git_manager.github_repo_url}")


if __name__ == "__main__":
    main()
