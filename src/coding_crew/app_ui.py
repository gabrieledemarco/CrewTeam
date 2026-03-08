"""
CLI UI utilities for CrewAI app.
"""


def banner():
    print("\n" + "=" * 78)
    print("CREWAI MULTI-AGENT DEVELOPMENT SYSTEM")
    print("=" * 78)
    print("Team Flow")
    print("  PMO -> Architect -> Code Writer -> Reviewer -> Tester")
    print("-" * 78)
    print("Agents")
    print("  [PMO] Requirements, planning, final evaluation")
    print("  [Architect] System design, structure, implementation strategy")
    print("  [Code Writer] Application code and concrete project files")
    print("  [Reviewer] Quality, security, maintainability checks")
    print("  [Tester] Test strategy and coverage improvements")
    print("=" * 78)


def section(title: str):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def status_ok(message: str):
    print(f"[OK] {message}")


def status_warn(message: str):
    print(f"[WARN] {message}")


def ask_bool(prompt: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    raw = input(f"{prompt} ({suffix}): ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes", "s", "si")
