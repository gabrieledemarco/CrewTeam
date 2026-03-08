"""
Output Manager: Handles file persistence, versioning, and git integration
"""
import json
import re
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict, Optional, Tuple, List


class OutputManager:
    """Manages project outputs with versioning and git integration"""

    def __init__(self, project_name: str, base_dir: str = "outputs", enable_git: bool = True):
        self.project_name = project_name
        self.base_dir = Path(base_dir)
        self.project_dir = self.base_dir / project_name
        self.generated_project_dir = self.project_dir / "project"
        self.version = 1
        self.current_stage = None
        self.stage_outputs = {}
        self.enable_git = enable_git

        # Create project directory structure
        self._setup_directories()
        if self.enable_git:
            self._init_git_repo()

    def _setup_directories(self):
        """Create necessary directory structure"""
        dirs = [
            self.project_dir,
            self.project_dir / "versions",
            self.project_dir / "requirements",
            self.project_dir / "architecture",
            self.project_dir / "code",
            self.project_dir / "tests",
            self.project_dir / "reviews",
            self.generated_project_dir,
            self.generated_project_dir / "current",
            self.generated_project_dir / "versions",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _init_git_repo(self):
        """Initialize git repository if not already present"""
        git_dir = self.project_dir / ".git"
        if not git_dir.exists():
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=self.project_dir,
                    capture_output=True,
                    check=True,
                )
                # Configure git user for commits
                subprocess.run(
                    ["git", "config", "user.email", "crew@local.dev"],
                    cwd=self.project_dir,
                    capture_output=True,
                )
                subprocess.run(
                    ["git", "config", "user.name", "CrewAI Agent"],
                    cwd=self.project_dir,
                    capture_output=True,
                )
                print(f"[ok] Git repository initialized for project: {self.project_name}")
            except Exception as exc:
                print(f"[warn] Could not initialize git: {exc}")

    def save_stage_output(self, stage: str, output: str, metadata: Optional[Dict] = None):
        """Save output from a stage with metadata"""
        self.current_stage = stage

        # Create stage-specific directory
        stage_dir = self.project_dir / stage.lower()
        stage_dir.mkdir(exist_ok=True)

        # Save main output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = stage_dir / f"v{self.version}_{timestamp}.md"

        with open(output_file, "w", encoding="utf-8") as file_handle:
            file_handle.write(f"# {stage.upper()}\n")
            file_handle.write(f"**Version:** {self.version}\n")
            file_handle.write(f"**Generated:** {timestamp}\n\n")
            file_handle.write(output)

        # Save metadata
        metadata_file = stage_dir / f"v{self.version}_{timestamp}.json"
        if metadata is None:
            metadata = {}
        metadata.update(
            {
                "stage": stage,
                "version": self.version,
                "timestamp": timestamp,
                "output_file": str(output_file),
            }
        )

        with open(metadata_file, "w", encoding="utf-8") as file_handle:
            json.dump(metadata, file_handle, indent=2)

        # Store in memory
        self.stage_outputs[stage] = {
            "output": output,
            "file": str(output_file),
            "metadata_file": str(metadata_file),
            "timestamp": timestamp,
        }

        print(f"[ok] Saved {stage} output to: {output_file}")
        return output_file

    @staticmethod
    def _sanitize_relative_path(file_path: str) -> str:
        """Normalize model-provided file path into a safe relative path."""
        cleaned = (file_path or "").strip()
        cleaned = re.sub(r"^(?:file|filename|path)\s*[:=]\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip().strip("`").strip("'").strip('"').strip("*").strip("_")
        cleaned = cleaned.replace("\\", "/")
        cleaned = cleaned.splitlines()[0].strip()
        if " " in cleaned:
            cleaned = cleaned.split()[0]
        cleaned = re.sub(r"^[A-Za-z]:", "", cleaned)  # remove Windows drive prefix
        cleaned = cleaned.lstrip("/").lstrip("./")

        parts: List[str] = []
        for part in cleaned.split("/"):
            part = part.strip().strip("`").strip("'").strip('"').strip("*").strip("_")
            part = re.sub(r"[<>:\"|?*]", "", part)
            part = part.rstrip(" .,:;!?)[]{}")
            if not part or part in (".", ".."):
                continue
            parts.append(part)

        return "/".join(parts)

    @staticmethod
    def _infer_ext_from_lang(lang: str) -> str:
        lang = (lang or "").strip().lower()
        mapping = {
            "python": ".py",
            "py": ".py",
            "javascript": ".js",
            "js": ".js",
            "typescript": ".ts",
            "ts": ".ts",
            "tsx": ".tsx",
            "jsx": ".jsx",
            "json": ".json",
            "yaml": ".yaml",
            "yml": ".yml",
            "toml": ".toml",
            "markdown": ".md",
            "md": ".md",
            "html": ".html",
            "css": ".css",
            "scss": ".scss",
            "java": ".java",
            "go": ".go",
            "rust": ".rs",
            "bash": ".sh",
            "sh": ".sh",
            "sql": ".sql",
            "xml": ".xml",
        }
        return mapping.get(lang, ".txt")

    def extract_files_from_markdown(
        self,
        markdown: str,
        allow_generated_fallback: bool = True,
    ) -> Dict[str, str]:
        """
        Extract file paths and contents from markdown code blocks.
        Supports:
        - ```lang filename=path/to/file.ext
        - ```lang file:path/to/file.ext
        - ```lang path/to/file.ext
        - Previous line markers like "File: path/to/file.ext"
        """
        pattern = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)
        matches = list(pattern.finditer(markdown))
        files: Dict[str, str] = {}

        for index, match in enumerate(matches, start=1):
            header = (match.group(1) or "").strip()
            code = match.group(2) or ""
            file_path = None

            # Strategy 1: filename markers in fence header.
            header_patterns = [
                r"(?:^|\s)(?:file|filename|path)\s*[:=]\s*([^\s]+)",
                r"^[a-zA-Z0-9_+-]+\s+([^\s]+)$",
            ]
            for hdr_pattern in header_patterns:
                hdr_match = re.search(hdr_pattern, header)
                if hdr_match:
                    file_path = hdr_match.group(1)
                    break

            # Strategy 2: check preceding lines before the block.
            if not file_path:
                prefix = markdown[: match.start()]
                recent_lines = prefix.splitlines()[-4:]
                line_patterns = [
                    r"(?:^|\b)(?:file|filename|path)\s*[:=]\s*([^\s]+)",
                    r"^#+\s*([A-Za-z0-9_\-./\\]+\.[A-Za-z0-9]+)\s*$",
                    r"^\*\*([A-Za-z0-9_\-./\\]+\.[A-Za-z0-9]+)\*\*\s*$",
                ]
                for line in reversed(recent_lines):
                    stripped = line.strip()
                    for line_pattern in line_patterns:
                        line_match = re.search(line_pattern, stripped, flags=re.IGNORECASE)
                        if line_match:
                            file_path = line_match.group(1)
                            break
                    if file_path:
                        break

            # Strategy 3: fallback generated file name.
            if not file_path:
                if not allow_generated_fallback:
                    continue
                language = header.split()[0] if header else ""
                ext = self._infer_ext_from_lang(language)
                file_path = f"generated/file_{index}{ext}"

            safe_path = self._sanitize_relative_path(file_path)
            if not safe_path:
                continue
            files[safe_path] = code.rstrip() + "\n"

        return files

    def write_generated_project_files(
        self, files: Dict[str, str], snapshot_label: Optional[str] = None
    ) -> Tuple[List[str], Optional[Path]]:
        """
        Write generated files into:
        - project/current (latest state)
        - project/versions/<snapshot_label> (optional immutable snapshot)
        """
        current_root = self.generated_project_dir / "current"
        snapshot_root = None
        if snapshot_label:
            snapshot_root = self.generated_project_dir / "versions" / snapshot_label
            snapshot_root.mkdir(parents=True, exist_ok=True)

        saved = []
        for rel_path, content in files.items():
            current_path = current_root / rel_path
            current_path.parent.mkdir(parents=True, exist_ok=True)
            with open(current_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(content)
            saved.append(str(current_path))

            if snapshot_root:
                snap_path = snapshot_root / rel_path
                snap_path.parent.mkdir(parents=True, exist_ok=True)
                with open(snap_path, "w", encoding="utf-8") as file_handle:
                    file_handle.write(content)

        return saved, snapshot_root

    def save_code_files(self, files: Dict[str, str]):
        """Save generated code files"""
        code_dir = self.project_dir / "code" / f"v{self.version}"
        code_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for filename, content in files.items():
            file_path = code_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(content)
            saved_files.append(str(file_path))
            print(f"[ok] Saved code file: {file_path}")

        return saved_files

    def save_test_files(self, files: Dict[str, str]):
        """Save generated test files"""
        test_dir = self.project_dir / "tests" / f"v{self.version}"
        test_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for filename, content in files.items():
            file_path = test_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(content)
            saved_files.append(str(file_path))
            print(f"[ok] Saved test file: {file_path}")

        return saved_files

    def auto_commit(self, stage: str, message: str = None):
        """Automatically commit changes to git"""
        if not self.enable_git:
            return

        try:
            # Add all changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_dir,
                capture_output=True,
                check=True,
            )

            # Commit with automatic message if not provided
            if message is None:
                message = f"v{self.version}: {stage} complete"

            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"[ok] Git commit: {message}")
            elif "nothing to commit" in result.stdout:
                print(f"[warn] No changes to commit for {stage}")
            else:
                print(f"[warn] Git commit failed: {result.stderr}")

        except Exception as exc:
            print(f"[warn] Could not commit to git: {exc}")

    def increment_version(self):
        """Increment version after successful completion"""
        self.version += 1
        print(f"-> Version incremented to v{self.version}")

    def get_stage_history(self, stage: str) -> list:
        """Get all versions of a stage"""
        stage_dir = self.project_dir / stage.lower()
        if not stage_dir.exists():
            return []

        files = sorted(stage_dir.glob("*.md"), reverse=True)
        return [str(file_path) for file_path in files]

    def load_stage_output(self, stage: str, version: Optional[int] = None) -> Optional[str]:
        """Load output from a specific stage version"""
        stage_dir = self.project_dir / stage.lower()
        if not stage_dir.exists():
            return None

        files = sorted(stage_dir.glob("*.md"), reverse=True)
        if not files:
            return None

        # Get latest version if not specified
        target_file = files[0]
        if version is not None:
            version_files = [file_path for file_path in files if f"v{version}" in file_path.name]
            if version_files:
                target_file = version_files[0]

        with open(target_file, "r", encoding="utf-8") as file_handle:
            return file_handle.read()

    def create_project_summary(self) -> str:
        """Create a summary of all project outputs"""
        summary = f"# Project: {self.project_name}\n\n"
        summary += f"**Current Version:** {self.version}\n\n"
        summary += f"**Generated Project Folder:** {self.generated_project_dir / 'current'}\n\n"

        for stage in ["requirements", "architecture", "code", "tests", "reviews"]:
            history = self.get_stage_history(stage)
            if history:
                summary += f"## {stage.upper()}\n"
                for file_path in history[:3]:  # Show last 3 versions
                    summary += f"- {Path(file_path).name}\n"
                summary += "\n"

        return summary
