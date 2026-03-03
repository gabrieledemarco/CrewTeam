"""
Git integration for CrewAI projects
"""
import subprocess
from pathlib import Path
from typing import Optional
import re
import os
import requests
import json


class GitManager:
    """Manages git operations for the project"""

    def __init__(
        self,
        repo_path: Path,
        enable_git: bool = True,
        github_root_url: Optional[str] = None,
        project_name: Optional[str] = None,
    ):
        self.repo_path = Path(repo_path)
        self.enable_git = enable_git
        self.github_root_url = github_root_url or ""
        self.github_owner = self._extract_github_owner(self.github_root_url)
        self.repo_name = self._slugify_repo_name(project_name or self.repo_path.name)
        self.github_repo_full_name = (
            f"{self.github_owner}/{self.repo_name}" if self.github_owner else None
        )
        self.github_repo_url = (
            f"https://github.com/{self.github_repo_full_name}.git"
            if self.github_repo_full_name
            else None
        )

        if self.enable_git:
            self._ensure_repo_exists()
            if self.github_repo_full_name:
                self._ensure_github_remote()

    @staticmethod
    def _extract_github_owner(root_url: str) -> Optional[str]:
        """Extract GitHub owner/account from root URL."""
        if not root_url:
            return None
        cleaned = root_url.strip().rstrip("/")
        match = re.search(r"github\.com/([A-Za-z0-9_.-]+)$", cleaned, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _slugify_repo_name(name: str) -> str:
        """Create safe repository slug from project name."""
        slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip().lower())
        slug = slug.strip("-._")
        return slug or "crew-project"

    def _run(self, cmd: list, check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check,
        )

    @staticmethod
    def _github_token() -> str:
        return (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()

    @staticmethod
    def _has_gh_cli() -> bool:
        try:
            check = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            return check.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    @classmethod
    def _list_repositories_via_api(cls, owner: str, limit: int = 100) -> list[dict]:
        token = cls._github_token()
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            if token:
                # Includes private repositories for the authenticated account.
                url = f"https://api.github.com/user/repos?per_page={min(max(limit, 1), 100)}&sort=updated"
            else:
                # Public-only fallback without token.
                url = f"https://api.github.com/users/{owner}/repos?per_page={min(max(limit, 1), 100)}&sort=updated"

            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                print(f"[warn] GitHub API list failed: HTTP {response.status_code}")
                return []

            data = response.json()
            if not isinstance(data, list):
                return []

            repos = []
            for repo in data:
                repo_owner = ((repo.get("owner") or {}).get("login") or "").lower()
                if repo_owner and repo_owner != owner.lower():
                    continue
                repos.append(
                    {
                        "name": repo.get("name"),
                        "url": repo.get("html_url"),
                        "description": repo.get("description"),
                        "isPrivate": repo.get("private"),
                        "updatedAt": repo.get("updated_at"),
                    }
                )
                if len(repos) >= limit:
                    break
            return repos
        except Exception as exc:
            print(f"[warn] GitHub API list failed: {exc}")
            return []

    @classmethod
    def _ensure_repo_via_api(cls, owner: str, repo_name: str) -> bool:
        token = cls._github_token()
        if not token:
            print("[warn] Missing GITHUB_TOKEN/GH_TOKEN; cannot auto-create repo via API.")
            return False

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        try:
            check_resp = requests.get(repo_url, headers=headers, timeout=20)
            if check_resp.status_code == 200:
                return True
            if check_resp.status_code not in (404,):
                print(f"[warn] GitHub API repo check failed: HTTP {check_resp.status_code}")
                return False

            create_resp = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                data=json.dumps({"name": repo_name, "private": True, "auto_init": False}),
                timeout=20,
            )
            if create_resp.status_code in (201, 422):
                return True

            print(f"[warn] GitHub API repo create failed: HTTP {create_resp.status_code}")
            return False
        except Exception as exc:
            print(f"[warn] GitHub API repo create/check failed: {exc}")
            return False

    @classmethod
    def list_repositories_from_root(cls, github_root_url: str, limit: int = 100) -> list[dict]:
        """List repositories under a GitHub account URL using gh CLI or API fallback."""
        owner = cls._extract_github_owner(github_root_url)
        if not owner:
            return []

        try:
            if cls._has_gh_cli():
                auth_status = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
                if auth_status.returncode == 0:
                    result = subprocess.run(
                        [
                            "gh",
                            "repo",
                            "list",
                            owner,
                            "--limit",
                            str(limit),
                            "--json",
                            "name,url,description,isPrivate,updatedAt",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        repos = json.loads(result.stdout or "[]")
                        return repos if isinstance(repos, list) else []
                else:
                    print("[warn] GitHub CLI not authenticated. Falling back to API.")
            else:
                print("[warn] GitHub CLI (gh) not found. Falling back to API.")

            return cls._list_repositories_via_api(owner, limit=limit)
        except Exception as exc:
            print(f"[warn] Failed to list repositories: {exc}")
            return []

    @classmethod
    def clone_or_update_repository(
        cls, github_root_url: str, repo_name: str, destination_path: Path
    ) -> bool:
        """Clone repository if missing; otherwise fetch/pull latest changes."""
        owner = cls._extract_github_owner(github_root_url)
        if not owner:
            return False

        repo_full_name = f"{owner}/{cls._slugify_repo_name(repo_name)}"
        repo_url = f"https://github.com/{repo_full_name}.git"
        destination_path = Path(destination_path)

        try:
            git_dir = destination_path / ".git"
            if git_dir.exists():
                fetch_result = subprocess.run(
                    ["git", "fetch", "--all"],
                    cwd=destination_path,
                    capture_output=True,
                    text=True,
                )
                if fetch_result.returncode != 0:
                    print(f"[warn] git fetch failed: {fetch_result.stderr.strip()}")
                    return False

                pull_result = subprocess.run(
                    ["git", "pull"],
                    cwd=destination_path,
                    capture_output=True,
                    text=True,
                )
                if pull_result.returncode != 0:
                    print(f"[warn] git pull failed: {pull_result.stderr.strip()}")
                    return False

                print(f"[ok] Updated local repository: {destination_path}")
                return True

            destination_path.parent.mkdir(parents=True, exist_ok=True)
            clone_result = subprocess.run(
                ["git", "clone", repo_url, str(destination_path)],
                capture_output=True,
                text=True,
            )
            if clone_result.returncode != 0:
                print(f"[warn] git clone failed: {clone_result.stderr.strip()}")
                return False

            print(f"[ok] Cloned repository into: {destination_path}")
            return True
        except Exception as exc:
            print(f"[warn] Clone/update failed: {exc}")
            return False

    def _ensure_repo_exists(self):
        """Ensure repository exists"""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            self._init_repo()

    def _init_repo(self):
        """Initialize git repository"""
        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "crew@local.dev"],
                cwd=self.repo_path,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "CrewAI Agent"],
                cwd=self.repo_path,
                capture_output=True,
            )
        except Exception as exc:
            print(f"[warn] Git initialization failed: {exc}")

    def _ensure_github_remote(self):
        """Ensure GitHub repo exists and origin is configured."""
        if not self.github_repo_full_name or not self.github_repo_url:
            return

        try:
            repo_ensured = False
            if self._has_gh_cli():
                auth_status = subprocess.run(
                    ["gh", "auth", "status"],
                    capture_output=True,
                    text=True,
                )
                if auth_status.returncode == 0:
                    repo_view = subprocess.run(
                        ["gh", "repo", "view", self.github_repo_full_name],
                        capture_output=True,
                        text=True,
                    )
                    if repo_view.returncode != 0:
                        repo_create = subprocess.run(
                            ["gh", "repo", "create", self.github_repo_full_name, "--private"],
                            capture_output=True,
                            text=True,
                        )
                        if repo_create.returncode == 0:
                            print(f"[ok] GitHub repository created: {self.github_repo_full_name}")
                            repo_ensured = True
                        else:
                            print(f"[warn] Failed to create GitHub repository via gh: {repo_create.stderr.strip()}")
                    else:
                        repo_ensured = True
                else:
                    print("[warn] GitHub CLI not authenticated. Trying API fallback.")
            else:
                print("[warn] GitHub CLI (gh) not found. Trying API fallback.")

            if not repo_ensured and self.github_owner:
                repo_ensured = self._ensure_repo_via_api(self.github_owner, self.repo_name)

            if not repo_ensured:
                print("[warn] Unable to ensure remote GitHub repository.")
                return

            remote_check = self._run(["git", "remote", "get-url", "origin"])
            if remote_check.returncode == 0:
                self._run(["git", "remote", "set-url", "origin", self.github_repo_url])
            else:
                self._run(["git", "remote", "add", "origin", self.github_repo_url])

            push_result = self._run(["git", "push", "-u", "origin", "HEAD"])
            if push_result.returncode == 0 or "set up to track" in (push_result.stderr or "").lower():
                print(f"[ok] GitHub remote configured: {self.github_repo_url}")
            else:
                combined = f"{push_result.stdout or ''}\n{push_result.stderr or ''}".lower()
                if "src refspec head does not match any" in combined or "does not have any commits yet" in combined:
                    print("[ok] GitHub repository created and remote configured. Initial push deferred until first commit.")
                else:
                    print(f"[warn] Initial GitHub push failed: {push_result.stderr.strip()}")
        except Exception as exc:
            print(f"[warn] GitHub remote setup failed: {exc}")

    def _push_current_branch(self):
        if not self.github_repo_url:
            return
        remote_check = self._run(["git", "remote", "get-url", "origin"])
        if remote_check.returncode != 0:
            print("[warn] Remote 'origin' not configured. Attempting auto-setup...")
            self._ensure_github_remote()
            remote_check = self._run(["git", "remote", "get-url", "origin"])
            if remote_check.returncode != 0:
                print("[warn] GitHub push skipped: remote 'origin' is still not configured.")
                return
        result = self._run(["git", "push", "origin", "HEAD"])
        if result.returncode != 0:
            print(f"[warn] GitHub push failed: {result.stderr.strip()}")

    def _push_tags(self):
        if not self.github_repo_url:
            return
        remote_check = self._run(["git", "remote", "get-url", "origin"])
        if remote_check.returncode != 0:
            print("[warn] Remote 'origin' not configured for tags. Attempting auto-setup...")
            self._ensure_github_remote()
            remote_check = self._run(["git", "remote", "get-url", "origin"])
            if remote_check.returncode != 0:
                print("[warn] GitHub tag push skipped: remote 'origin' is still not configured.")
                return
        result = self._run(["git", "push", "origin", "--tags"])
        if result.returncode != 0:
            print(f"[warn] GitHub tag push failed: {result.stderr.strip()}")

    def commit(self, message: str, files: Optional[list] = None) -> bool:
        """Commit changes with message"""
        if not self.enable_git:
            return False
        try:
            if files:
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True,
                )
            else:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True,
                )

            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"[ok] Commit: {message}")
                self._push_current_branch()
                return True
            if "nothing to commit" in result.stdout or "nothing added to commit" in result.stdout:
                return False

            print(f"[warn] Commit failed: {result.stderr}")
            return False

        except Exception as exc:
            print(f"[warn] Error committing: {exc}")
            return False

    def create_tag(self, tag: str, message: str = None) -> bool:
        """Create annotated tag"""
        if not self.enable_git:
            return False
        try:
            cmd = ["git", "tag"]
            if message:
                cmd.extend(["-a", tag, "-m", message])
            else:
                cmd.append(tag)

            subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )
            print(f"[ok] Tag created: {tag}")
            self._push_tags()
            return True
        except Exception as exc:
            print(f"[warn] Tag creation failed: {exc}")
            return False

    def get_log(self, limit: int = 10) -> list:
        """Get git log"""
        if not self.enable_git:
            return []
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--oneline"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip().split("\n") if result.stdout else []
        except Exception as exc:
            print(f"[warn] Could not get git log: {exc}")
            return []

    def get_status(self) -> str:
        """Get git status"""
        if not self.enable_git:
            return "git disabled"
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout if result.stdout else "clean"
        except Exception as exc:
            print(f"[warn] Could not get git status: {exc}")
            return ""
