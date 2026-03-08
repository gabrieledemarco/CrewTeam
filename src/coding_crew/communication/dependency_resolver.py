"""
Dependency Conflict Resolution System

Solves the problem of agents generating conflicting dependencies in requirements.txt.
Implements version resolution, conflict detection, and ecosystem consistency checks.
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import subprocess
import tempfile
import os
from pathlib import Path

from .schemas import EcosystemLanguage, EcosystemFramework, EcosystemDatabase


class DependencyType(str, Enum):
    """Types of dependencies"""
    RUNTIME = "runtime"
    DEVELOPMENT = "development"
    TEST = "test"
    OPTIONAL = "optional"


class ConflictSeverity(str, Enum):
    """Severity levels for dependency conflicts"""
    CRITICAL = "critical"      # Blocks installation
    HIGH = "high"             # Version incompatibility
    MEDIUM = "medium"         # Ecosystem mixing
    LOW = "low"               # Style/organization issues


@dataclass
class Dependency:
    """Represents a single dependency"""
    name: str
    version: str
    type: DependencyType
    source: str  # Which agent generated this
    ecosystem: str
    
    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class Conflict:
    """Represents a dependency conflict"""
    type: ConflictSeverity
    dependency_name: str
    conflicting_versions: List[str]
    sources: List[str]
    description: str
    suggested_fix: str


@dataclass
class Resolution:
    """Represents a dependency resolution"""
    dependency_name: str
    resolved_version: str
    reasoning: str
    affected_agents: List[str]


class DependencyValidator:
    """Validates and resolves dependency conflicts"""
    
    # Known dependency mappings and compatibility
    COMPATIBILITY_MAP = {
        "flask": {
            "compatible_with": ["requests", "python-dotenv"],
            "conflicts_with": ["django"],
            "version_constraints": {
                ">=2.0.0": ["python>=3.7"],
                ">=3.0.0": ["python>=3.9"]
            }
        },
        "django": {
            "compatible_with": ["psycopg2", "pillow"],
            "conflicts_with": ["flask"],
            "version_constraints": {
                ">=4.0.0": ["python>=3.8"],
                ">=5.0.0": ["python>=3.10"]
            }
        },
        "fastapi": {
            "compatible_with": ["uvicorn", "pydantic"],
            "conflicts_with": [],
            "version_constraints": {
                ">=0.100.0": ["python>=3.8"],
                ">=0.110.0": ["python>=3.9"]
            }
        }
    }
    
    # Ecosystem-specific package managers
    ECOSYSTEM_PACKAGES = {
        "python": {
            "pip": ["pip", "pip-tools"],
            "conda": ["conda", "mamba"],
            "poetry": ["poetry"],
            "pipenv": ["pipenv"]
        },
        "javascript": {
            "npm": ["npm"],
            "yarn": ["yarn"],
            "pnpm": ["pnpm"]
        }
    }
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.conflicts: List[Conflict] = []
        self.resolutions: List[Resolution] = []
        
        if self.enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
    
    def parse_requirements(self, requirements_text: str, source: str, ecosystem: str) -> List[Dependency]:
        """Parse requirements.txt content into Dependency objects"""
        dependencies = []
        
        for line in requirements_text.splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('-'):
                continue
            
            # Parse dependency line
            dep = self._parse_dependency_line(line, source, ecosystem)
            if dep:
                dependencies.append(dep)
        
        return dependencies
    
    def _parse_dependency_line(self, line: str, source: str, ecosystem: str) -> Optional[Dependency]:
        """Parse a single dependency line"""
        # Remove comments
        line = line.split('#')[0].strip()
        
        # Handle various version specifiers
        patterns = [
            r'^([a-zA-Z0-9_-]+)\s*==\s*([0-9.]+(?:[a-z0-9]+)?)$',  # exact version
            r'^([a-zA-Z0-9_-]+)\s*>=\s*([0-9.]+(?:[a-z0-9]+)?)$',  # minimum version
            r'^([a-zA-Z0-9_-]+)\s*<=\s*([0-9.]+(?:[a-z0-9]+)?)$',  # maximum version
            r'^([a-zA-Z0-9_-]+)\s*>\s*([0-9.]+(?:[a-z0-9]+)?)$',   # greater than
            r'^([a-zA-Z0-9_-]+)\s*<\s*([0-9.]+(?:[a-z0-9]+)?)$',   # less than
            r'^([a-zA-Z0-9_-]+)\s*!=\s*([0-9.]+(?:[a-z0-9]+)?)$',  # not equal
            r'^([a-zA-Z0-9_-]+)\s*~=([0-9.]+(?:[a-z0-9]+)?)$',     # compatible release
            r'^([a-zA-Z0-9_-]+)\s*([0-9.]+(?:[a-z0-9]+)?)$',       # simple version
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                name = match.group(1).lower()
                version = match.group(2)
                
                # Determine dependency type
                dep_type = self._classify_dependency(name, ecosystem)
                
                return Dependency(
                    name=name,
                    version=version,
                    type=dep_type,
                    source=source,
                    ecosystem=ecosystem
                )
        
        # Handle packages without version
        if re.match(r'^[a-zA-Z0-9_-]+$', line):
            return Dependency(
                name=line.lower(),
                version="latest",
                type=DependencyType.RUNTIME,
                source=source,
                ecosystem=ecosystem
            )
        
        return None
    
    def _classify_dependency(self, name: str, ecosystem: str) -> DependencyType:
        """Classify dependency type based on name and ecosystem"""
        name_lower = name.lower()
        
        # Test dependencies
        test_patterns = [
            "test", "pytest", "unittest", "mocha", "jest", "vitest",
            "supertest", "chai", "sinon", "mock", "faker"
        ]
        
        # Development dependencies
        dev_patterns = [
            "dev", "debug", "lint", "format", "prettier", "eslint",
            "black", "flake8", "mypy", "type", "types"
        ]
        
        # Optional dependencies
        optional_patterns = [
            "optional", "extra", "plugin", "extension"
        ]
        
        if any(pattern in name_lower for pattern in test_patterns):
            return DependencyType.TEST
        elif any(pattern in name_lower for pattern in dev_patterns):
            return DependencyType.DEVELOPMENT
        elif any(pattern in name_lower for pattern in optional_patterns):
            return DependencyType.OPTIONAL
        else:
            return DependencyType.RUNTIME
    
    def detect_conflicts(self, dependencies: List[Dependency]) -> List[Conflict]:
        """Detect conflicts between dependencies"""
        self.conflicts = []
        
        # Group by dependency name
        dep_groups = {}
        for dep in dependencies:
            if dep.name not in dep_groups:
                dep_groups[dep.name] = []
            dep_groups[dep.name].append(dep)
        
        # Check for conflicts in each group
        for dep_name, dep_list in dep_groups.items():
            if len(dep_list) > 1:
                self._check_version_conflicts(dep_name, dep_list)
        
        # Check for ecosystem mixing
        self._check_ecosystem_mixing(dependencies)
        
        # Check for known incompatibilities
        self._check_known_incompatibilities(dependencies)
        
        return self.conflicts
    
    def _check_version_conflicts(self, dep_name: str, dep_list: List[Dependency]):
        """Check for version conflicts within the same dependency"""
        versions = [dep.version for dep in dep_list]
        sources = [dep.source for dep in dep_list]
        
        # If all versions are the same, no conflict
        if len(set(versions)) == 1:
            return
        
        # Check for exact version conflicts
        exact_versions = [v for v in versions if v != "latest" and not any(op in v for op in [">", "<", "!", "~"])]
        if len(set(exact_versions)) > 1:
            conflict = Conflict(
                type=ConflictSeverity.HIGH,
                dependency_name=dep_name,
                conflicting_versions=exact_versions,
                sources=sources,
                description=f"Multiple exact versions specified for {dep_name}: {', '.join(exact_versions)}",
                suggested_fix=f"Choose one version. Latest stable: {max(exact_versions)}"
            )
            self.conflicts.append(conflict)
    
    def _check_ecosystem_mixing(self, dependencies: List[Dependency]):
        """Check for mixing different ecosystems"""
        ecosystems = set(dep.ecosystem for dep in dependencies)
        
        if len(ecosystems) > 1:
            conflict = Conflict(
                type=ConflictSeverity.MEDIUM,
                dependency_name="ecosystem_mixing",
                conflicting_versions=list(ecosystems),
                sources=[dep.source for dep in dependencies],
                description=f"Mixed ecosystems detected: {', '.join(ecosystems)}",
                suggested_fix="Use single ecosystem per project. Choose primary language/framework."
            )
            self.conflicts.append(conflict)
    
    def _check_known_incompatibilities(self, dependencies: List[Dependency]):
        """Check for known incompatible dependencies"""
        dep_names = [dep.name for dep in dependencies]
        
        for dep in dependencies:
            if dep.name in self.COMPATIBILITY_MAP:
                incompatibilities = self.COMPATIBILITY_MAP[dep.name].get("conflicts_with", [])
                for incompatible in incompatibilities:
                    if incompatible in dep_names:
                        conflict = Conflict(
                            type=ConflictSeverity.CRITICAL,
                            dependency_name=dep.name,
                            conflicting_versions=[dep.version],
                            sources=[dep.source],
                            description=f"{dep.name} is incompatible with {incompatible}",
                            suggested_fix=f"Remove {incompatible} or use alternative to {dep.name}"
                        )
                        self.conflicts.append(conflict)
    
    def resolve_conflicts(self, dependencies: List[Dependency]) -> Tuple[List[Dependency], List[Resolution]]:
        """Resolve detected conflicts"""
        self.resolutions = []
        
        # Create dependency map
        dep_map = {}
        for dep in dependencies:
            dep_map[dep.name] = dep
        
        # Resolve conflicts
        for conflict in self.conflicts:
            if conflict.type == ConflictSeverity.HIGH:
                resolution = self._resolve_version_conflict(conflict, dep_map)
                if resolution:
                    self.resolutions.append(resolution)
                    # Update the dependency map with resolved version
                    dep_map[resolution.dependency_name] = Dependency(
                        name=resolution.dependency_name,
                        version=resolution.resolved_version,
                        type=DependencyType.RUNTIME,  # Default to runtime
                        source="conflict_resolver",
                        ecosystem=dep_map[resolution.dependency_name].ecosystem
                    )
            elif conflict.type == ConflictSeverity.CRITICAL:
                resolution = self._resolve_critical_conflict(conflict, dep_map)
                if resolution:
                    self.resolutions.append(resolution)
        
        # Return resolved dependencies
        resolved_deps = list(dep_map.values())
        return resolved_deps, self.resolutions
    
    def _resolve_version_conflict(self, conflict: Conflict, dep_map: Dict[str, Dependency]) -> Optional[Resolution]:
        """Resolve version conflicts by choosing the most compatible version"""
        dep_name = conflict.dependency_name
        current_deps = [dep for dep in dep_map.values() if dep.name == dep_name]
        
        # Strategy: choose the highest version that's compatible
        versions = [dep.version for dep in current_deps if dep.version != "latest"]
        
        if not versions:
            return None
        
        # For simplicity, choose the highest version
        # In a real implementation, you'd check compatibility matrices
        resolved_version = max(versions)
        
        resolution = Resolution(
            dependency_name=dep_name,
            resolved_version=resolved_version,
            reasoning=f"Chose highest version {resolved_version} from conflicting versions: {', '.join(versions)}",
            affected_agents=[dep.source for dep in current_deps]
        )
        
        return resolution
    
    def _resolve_critical_conflict(self, conflict: Conflict, dep_map: Dict[str, Dependency]) -> Optional[Resolution]:
        """Resolve critical conflicts (incompatible dependencies)"""
        dep_name = conflict.dependency_name
        
        # For critical conflicts, we need to remove one of the dependencies
        # This is a simplified approach - in practice, you'd need more sophisticated logic
        resolution = Resolution(
            dependency_name=dep_name,
            resolved_version="removed",
            reasoning=f"Removed {dep_name} due to critical incompatibility",
            affected_agents=conflict.sources
        )
        
        return resolution
    
    def generate_resolved_requirements(self, dependencies: List[Dependency]) -> str:
        """Generate resolved requirements.txt content"""
        # Group by type for organization
        runtime_deps = [dep for dep in dependencies if dep.type == DependencyType.RUNTIME]
        dev_deps = [dep for dep in dependencies if dep.type == DependencyType.DEVELOPMENT]
        test_deps = [dep for dep in dependencies if dep.type == DependencyType.TEST]
        optional_deps = [dep for dep in dependencies if dep.type == DependencyType.OPTIONAL]
        
        lines = []
        
        # Runtime dependencies
        if runtime_deps:
            lines.append("# Runtime Dependencies")
            for dep in sorted(runtime_deps, key=lambda x: x.name):
                lines.append(f"{dep.name}=={dep.version}")
            lines.append("")
        
        # Development dependencies
        if dev_deps:
            lines.append("# Development Dependencies")
            for dep in sorted(dev_deps, key=lambda x: x.name):
                lines.append(f"{dep.name}=={dep.version}")
            lines.append("")
        
        # Test dependencies
        if test_deps:
            lines.append("# Test Dependencies")
            for dep in sorted(test_deps, key=lambda x: x.name):
                lines.append(f"{dep.name}=={dep.version}")
            lines.append("")
        
        # Optional dependencies
        if optional_deps:
            lines.append("# Optional Dependencies")
            for dep in sorted(optional_deps, key=lambda x: x.name):
                lines.append(f"{dep.name}=={dep.version}")
        
        return "\n".join(lines)
    
    def validate_installation(self, requirements_content: str, ecosystem: str) -> Dict[str, Any]:
        """Validate that requirements can be installed without conflicts"""
        try:
            # Create temporary requirements file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(requirements_content)
                temp_file = f.name
            
            # Try to install in a virtual environment
            result = self._test_installation(temp_file, ecosystem)
            
            # Clean up
            os.unlink(temp_file)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "Installation validation failed"
            }
    
    def _test_installation(self, requirements_file: str, ecosystem: str) -> Dict[str, Any]:
        """Test installation in a temporary environment"""
        try:
            # Create temporary virtual environment
            with tempfile.TemporaryDirectory() as temp_dir:
                venv_dir = Path(temp_dir) / "test_venv"
                
                # Create virtual environment
                if ecosystem == "python":
                    subprocess.run(
                        ["python", "-m", "venv", str(venv_dir)],
                        check=True,
                        capture_output=True,
                        timeout=60
                    )
                    
                    # Get Python executable path
                    if os.name == "nt":  # Windows
                        python_exe = venv_dir / "Scripts" / "python.exe"
                    else:  # Unix-like
                        python_exe = venv_dir / "bin" / "python"
                    
                    # Try to install requirements
                    result = subprocess.run(
                        [str(python_exe), "-m", "pip", "install", "-r", requirements_file],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        # Check for conflicts
                        check_result = subprocess.run(
                            [str(python_exe), "-m", "pip", "check"],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        
                        return {
                            "success": True,
                            "conflict_check": check_result.returncode == 0,
                            "details": check_result.stdout if check_result.returncode == 0 else check_result.stderr
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.stderr,
                            "details": "Installation failed"
                        }
                
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported ecosystem: {ecosystem}",
                        "details": "Only Python ecosystem is currently supported"
                    }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timeout",
                "details": "Installation took too long"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "Installation validation error"
            }
    
    def get_conflict_summary(self) -> Dict[str, Any]:
        """Get summary of all conflicts and resolutions"""
        return {
            "total_conflicts": len(self.conflicts),
            "conflicts_by_severity": {
                severity.value: len([c for c in self.conflicts if c.type == severity])
                for severity in ConflictSeverity
            },
            "total_resolutions": len(self.resolutions),
            "resolutions": [asdict(r) for r in self.resolutions],
            "conflicts": [asdict(c) for c in self.conflicts]
        }


class DependencyManager:
    """High-level dependency management for the multi-agent system"""
    
    def __init__(self, enable_logging: bool = True):
        self.validator = DependencyValidator(enable_logging)
        self.enable_logging = enable_logging
        self.logger = self.validator.logger
    
    def process_agent_dependencies(
        self, 
        agent_name: str, 
        requirements_text: str, 
        ecosystem: str
    ) -> Dict[str, Any]:
        """Process dependencies from a specific agent"""
        try:
            # Parse dependencies
            dependencies = self.validator.parse_requirements(
                requirements_text, agent_name, ecosystem
            )
            
            if self.enable_logging and self.logger:
                self.logger.info(f"Parsed {len(dependencies)} dependencies from {agent_name}")
            
            return {
                "agent": agent_name,
                "dependencies": [dep.to_dict() for dep in dependencies],
                "ecosystem": ecosystem,
                "success": True
            }
            
        except Exception as e:
            return {
                "agent": agent_name,
                "dependencies": [],
                "ecosystem": ecosystem,
                "success": False,
                "error": str(e)
            }
    
    def resolve_all_conflicts(
        self, 
        agent_dependencies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve conflicts across all agents"""
        try:
            # Collect all dependencies
            all_dependencies = []
            for agent_data in agent_dependencies:
                if agent_data.get("success"):
                    for dep_dict in agent_data.get("dependencies", []):
                        dep = Dependency(**dep_dict)
                        all_dependencies.append(dep)
            
            # Detect conflicts
            conflicts = self.validator.detect_conflicts(all_dependencies)
            
            # Resolve conflicts
            resolved_deps, resolutions = self.validator.resolve_conflicts(all_dependencies)
            
            # Generate resolved requirements
            resolved_requirements = self.validator.generate_resolved_requirements(resolved_deps)
            
            # Validate installation
            if resolved_deps:
                first_dep = resolved_deps[0]
                validation = self.validator.validate_installation(
                    resolved_requirements, first_dep.ecosystem
                )
            else:
                validation = {"success": False, "error": "No dependencies to validate"}
            
            return {
                "success": True,
                "resolved_dependencies": [dep.to_dict() for dep in resolved_deps],
                "resolved_requirements": resolved_requirements,
                "conflicts": self.validator.get_conflict_summary(),
                "installation_validation": validation,
                "total_agents": len(agent_dependencies),
                "processed_dependencies": len(all_dependencies)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_dependencies": agent_dependencies
            }
    
    def get_dependency_report(self) -> Dict[str, Any]:
        """Get comprehensive dependency report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "conflicts_summary": self.validator.get_conflict_summary(),
            "compatibility_matrix": self.validator.COMPATIBILITY_MAP
        }