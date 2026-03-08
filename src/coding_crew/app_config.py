"""
Configuration flow and validation for CrewAI app.
"""
import re
import os
from pathlib import Path
import requests

from config.model_config import ModelConfig
from config.settings import Settings
from app_ui import ask_bool, section, status_ok, status_warn


def normalize_base_dir(base_dir: str) -> str:
    if not base_dir:
        return str((Path.cwd() / "outputs").resolve())
    return str(Path(base_dir).expanduser().resolve())


def check_ollama_connection(host: str) -> bool:
    print(f"\nChecking Ollama host: {host}")
    success, message = ModelConfig.check_ollama_connection(host)
    if success:
        status_ok(message)
    else:
        status_warn(message)
    return success


def validate_github_token(token: str) -> tuple[bool, str]:
    """
    Validate GitHub token with API call.
    Returns (is_valid, message).
    """
    token = (token or "").strip()
    if not token:
        return False, "Missing GitHub token."

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=15)
        if response.status_code == 200:
            login = (response.json() or {}).get("login", "unknown")
            return True, f"GitHub token valido (account: {login})."
        if response.status_code in (401, 403):
            return False, f"GitHub token non valido o non autorizzato (HTTP {response.status_code})."
        return False, f"Impossibile validare il token (HTTP {response.status_code})."
    except Exception as exc:
        return False, f"Token validation error: {exc}"


def config_issues(cfg: dict) -> list[str]:
    issues = []
    ollama_host = (cfg.get("ollama_host") or "").strip()
    github_root_url = (cfg.get("github_root_url") or "").strip()
    project_base_dir = (cfg.get("project_base_dir") or "").strip()
    persist_project_to_disk = cfg.get("persist_project_to_disk")
    github_token = (cfg.get("github_token") or "").strip()

    if not ollama_host:
        issues.append("Missing `ollama_host`.")
    elif not re.match(r"^https?://", ollama_host, re.IGNORECASE):
        issues.append("Invalid `ollama_host` format. Expected http://host:port.")

    if persist_project_to_disk not in (True, False):
        issues.append("Invalid `persist_project_to_disk` value.")

    if not project_base_dir:
        issues.append("Missing `project_base_dir`.")

    if not github_root_url:
        issues.append("Missing `github_root_url`.")
    elif not re.search(r"github\.com/[A-Za-z0-9_.-]+/?$", github_root_url, re.IGNORECASE):
        issues.append("Invalid `github_root_url` format.")

    if not github_token:
        issues.append("Missing `github_token` (required for GitHub API operations).")

    return issues


def configure_runtime_settings(existing: dict = None) -> dict:
    cfg = Settings.merge_with_defaults(existing or Settings.create_default())
    section("Configuration Setup")

    ollama_host = input(
        f"Ollama host connection [default: {cfg['ollama_host']}]: "
    ).strip() or cfg["ollama_host"]

    persist_to_disk = ask_bool(
        "Generate project on disk",
        bool(cfg.get("persist_project_to_disk", True))
    )

    default_base_dir = str((Path.cwd() / "outputs").resolve())
    current_base = cfg.get("project_base_dir") or default_base_dir
    base_dir = input(
        f"Project base directory [default: {current_base}]: "
    ).strip() or current_base

    github_root_url = input(
        f"GitHub root account URL [default: {cfg.get('github_root_url', '')}]: "
    ).strip() or cfg.get("github_root_url", "")
    token_current = (cfg.get("github_token") or "").strip()
    while True:
        token_hint = "<set>" if token_current else "<empty>"
        github_token = input(
            f"GitHub token [default: {token_hint}]: "
        ).strip() or token_current
        is_valid, message = validate_github_token(github_token)
        if is_valid:
            status_ok(message)
            break
        status_warn(message)
        if "Token validation error:" in message:
            keep_unverified = ask_bool("Cannot validate token online. Keep this token anyway", True)
            if keep_unverified and github_token:
                break
        token_current = github_token

    updated = Settings.merge_with_defaults(
        {
            **cfg,
            "ollama_host": ollama_host,
            "persist_project_to_disk": persist_to_disk,
            "project_base_dir": normalize_base_dir(base_dir),
            "github_root_url": github_root_url,
            "github_token": github_token,
        }
    )
    return updated


def repair_configuration_interactively(cfg: dict) -> dict:
    corrected = Settings.merge_with_defaults(cfg)

    issues = config_issues(corrected)
    if issues:
        section("Configuration Warnings")
        for issue in issues:
            status_warn(issue)
        status_warn("Please correct the values below.")

    while True:
        current = (corrected.get("ollama_host") or "http://localhost:11434").strip()
        value = input(f"Ollama host connection [default: {current}]: ").strip() or current
        if re.match(r"^https?://", value, re.IGNORECASE):
            corrected["ollama_host"] = value
            break
        status_warn("Invalid Ollama host format. Example: http://localhost:11434")

    corrected["persist_project_to_disk"] = ask_bool(
        "Generate project on disk",
        bool(corrected.get("persist_project_to_disk", True))
    )

    current_base = corrected.get("project_base_dir") or str((Path.cwd() / "outputs").resolve())
    base_input = input(f"Project base directory [default: {current_base}]: ").strip() or current_base
    corrected["project_base_dir"] = normalize_base_dir(base_input)

    while True:
        current_root = (corrected.get("github_root_url") or "").strip()
        value = input(f"GitHub root account URL [default: {current_root}]: ").strip() or current_root
        if re.search(r"github\.com/[A-Za-z0-9_.-]+/?$", value, re.IGNORECASE):
            corrected["github_root_url"] = value
            break
        status_warn("Invalid GitHub root URL. Example: https://github.com/gabrieledemarco/")

    while True:
        current_token = (corrected.get("github_token") or "").strip()
        hint = "<set>" if current_token else "<empty>"
        token = input(f"GitHub token [default: {hint}]: ").strip() or current_token
        is_valid, message = validate_github_token(token)
        if is_valid:
            status_ok(message)
            corrected["github_token"] = token
            break
        status_warn(message)
        if "Token validation error:" in message and token:
            keep_unverified = ask_bool("Cannot validate token online. Keep this token anyway", True)
            if keep_unverified:
                corrected["github_token"] = token
                break
        status_warn("GitHub token is required for repository listing/creation via API.")

    return Settings.merge_with_defaults(corrected)


def show_config_summary(cfg: dict):
    section("Configuration In Use")
    print(f"Ollama host           : {cfg.get('ollama_host')}")
    print(f"Generate on disk      : {cfg.get('persist_project_to_disk')}")
    print(f"Project base directory: {cfg.get('project_base_dir')}")
    print(f"GitHub root account   : {cfg.get('github_root_url')}")
    token = (cfg.get("github_token") or "").strip()
    print(f"GitHub token          : {'<set>' if token else '<empty>'}")


def apply_runtime_secrets(cfg: dict):
    """Expose configured secrets to runtime consumers (GitHub API fallback)."""
    token = (cfg.get("github_token") or "").strip()
    if token:
        os.environ["GITHUB_TOKEN"] = token
        os.environ["GH_TOKEN"] = token


def load_or_initialize_configuration() -> dict:
    if Settings.exists():
        loaded = Settings.load()
        section("Saved Configuration")
        print(f"Path: {Settings.get_config_path()}")
        use_saved = ask_bool("Use saved default configuration", True)
        if use_saved:
            cfg = Settings.merge_with_defaults(loaded or {})
            status_ok("Using saved configuration.")
        else:
            cfg = configure_runtime_settings(existing=loaded)
    else:
        section("First Run Setup")
        print(f"No configuration found. Creating: {Settings.get_config_path()}")
        cfg = configure_runtime_settings(existing=None)

    if config_issues(cfg):
        cfg = repair_configuration_interactively(cfg)

    if Settings.save(cfg):
        status_ok(f"Configuration saved in {Settings.get_config_path()}")
    else:
        status_warn("Failed to save configuration.")

    ModelConfig.apply_config(cfg)
    apply_runtime_secrets(cfg)
    return cfg


def validate_critical_settings(cfg: dict) -> bool:
    ok = True
    github_root = (cfg.get("github_root_url") or "").strip()
    if not github_root:
        status_warn("GitHub root account URL is missing in configuration.")
        ok = False
    elif not re.search(r"github\.com/[A-Za-z0-9_.-]+/?$", github_root, re.IGNORECASE):
        status_warn("GitHub root account URL format is invalid.")
        ok = False

    ollama_host = cfg.get("ollama_host", "http://localhost:11434")
    if check_ollama_connection(ollama_host):
        status_ok("Ollama connection check passed.")
    else:
        status_warn("Ollama connection check failed.")

    token = (cfg.get("github_token") or "").strip()
    token_valid, token_msg = validate_github_token(token)
    if token_valid:
        status_ok(token_msg)
    else:
        status_warn(token_msg)
        ok = False

    return ok
