"""
Project mode and selection utilities.
"""
import re
from pathlib import Path

from config.git_manager import GitManager
from app_ui import section, status_warn


def choose_project_mode() -> str:
    section("Project Mode")
    print("  1. Start a new project")
    print("  2. Resume an existing project")
    choice = input("Select mode (1-2): ").strip()
    return "resume" if choice == "2" else "new"


def list_github_repositories(github_root_url: str) -> list[dict]:
    repos = GitManager.list_repositories_from_root(github_root_url, limit=200)
    if not repos:
        status_warn("No repositories found (or GitHub access unavailable).")
        return []
    return repos


def list_local_projects(base_dir: str) -> list[str]:
    base_path = Path(base_dir)
    if not base_path.exists():
        status_warn(f"Project base directory not found: {base_path}")
        return []

    projects = []
    for child in sorted(base_path.iterdir()):
        if child.is_dir():
            projects.append(child.name)
    return projects


def choose_resume_target(github_root_url: str, base_dir: str) -> tuple[str, str]:
    repos = list_github_repositories(github_root_url)
    locals_found = list_local_projects(base_dir)

    section("Resume - Available Sources")
    print("GitHub repositories:")
    if repos:
        for idx, repo in enumerate(repos, start=1):
            name = repo.get("name", "unknown")
            desc = (repo.get("description") or "").strip()
            short_desc = desc[:70] + "..." if len(desc) > 70 else desc
            print(f"  G{idx:>2}. {name}" + (f" | {short_desc}" if short_desc else ""))
    else:
        print("  (none)")

    print("\nLocal projects in base directory:")
    if locals_found:
        for idx, name in enumerate(locals_found, start=1):
            print(f"  L{idx:>2}. {name}")
    else:
        print("  (none)")

    raw = input("\nSelect target (e.g., G1 or L2): ").strip().upper()
    if len(raw) < 2:
        return ("", "")

    source = raw[0]
    number = raw[1:]
    if not number.isdigit():
        return ("", "")
    pos = int(number)

    if source == "G":
        if 1 <= pos <= len(repos):
            return ("github", repos[pos - 1].get("name", ""))
    if source == "L":
        if 1 <= pos <= len(locals_found):
            return ("local", locals_found[pos - 1])

    return ("", "")


def read_requirements_input() -> str:
    section("Initial Requirements")
    print("Provide a file path or write requirements directly.")
    user_request = input("> ").strip()
    if not user_request:
        return ""

    path_patterns = [
        r"([A-Za-z]:\\[^\s]+)",
        r"(/[^\s]+\.[a-zA-Z]+)",
        r"(\.\./[^\s]+)",
        r"(\./[^\s]+)",
    ]

    req_file = None
    for pattern in path_patterns:
        match = re.search(pattern, user_request)
        if match:
            candidate = Path(match.group(1))
            if candidate.exists():
                req_file = candidate
                break

    if req_file and req_file.exists():
        try:
            return req_file.read_text(encoding="utf-8").strip()
        except Exception:
            return user_request

    return user_request
