"""
Structured Communication Schemas for Multi-Agent System

Defines JSON schemas for all agent-to-agent communication to replace
natural language context passing with typed, validated data contracts.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import jsonschema
from datetime import datetime


class AgentType(str, Enum):
    """Enumeration of agent types for structured communication"""
    PMO = "pmo"
    ARCHITECT = "architect"
    CODE_WRITER = "code_writer"
    CODE_REVIEWER = "code_reviewer"
    TESTER = "tester"


class EcosystemLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C_SHARP = "csharp"
    GO = "go"
    RUST = "rust"


class EcosystemFramework(str, Enum):
    """Supported frameworks per language"""
    # Python
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    
    # JavaScript/TypeScript
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NODEJS = "nodejs"
    EXPRESS = "express"
    
    # Java
    SPRING_BOOT = "spring_boot"
    HIBERNATE = "hibernate"
    
    # C#
    DOTNET_CORE = "dotnet_core"
    ENTITY_FRAMEWORK = "entity_framework"


class EcosystemDatabase(str, Enum):
    """Supported database systems"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"


class QualityScore(int, Enum):
    """Quality assessment scores"""
    EXCELLENT = 10
    VERY_GOOD = 9
    GOOD = 8
    ABOVE_AVERAGE = 7
    AVERAGE = 6
    BELOW_AVERAGE = 5
    POOR = 4
    VERY_POOR = 3
    UNACCEPTABLE = 2
    CRITICAL = 1


@dataclass
class EcosystemLock:
    """Explicit technology stack lock to prevent ecosystem mixing"""
    language: EcosystemLanguage
    framework: EcosystemFramework
    database: EcosystemDatabase
    package_manager: str  # pip, npm, yarn, cargo, etc.
    runtime: str  # python3.11, node18, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FunctionalRequirement:
    """Individual functional requirement with acceptance criteria"""
    id: str
    description: str
    priority: str  # P1, P2, P3, etc.
    acceptance_criteria: List[str]
    dependencies: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NonFunctionalRequirement:
    """Non-functional requirement specification"""
    category: str  # performance, security, reliability, etc.
    requirement: str
    measurable_criteria: str
    priority: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Constraint:
    """Project constraint or exclusion"""
    type: str  # must_not_have, must_use, performance_limit, etc.
    description: str
    rationale: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RequirementsSpecification:
    """Structured requirements specification from PMO"""
    scope: str
    business_objective: str
    functional_requirements: List[FunctionalRequirement]
    non_functional_requirements: List[NonFunctionalRequirement]
    ecosystem_lock: EcosystemLock
    constraints: List[Constraint]
    priorities: Dict[str, str]  # requirement_id -> priority
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scope": self.scope,
            "business_objective": self.business_objective,
            "functional_requirements": [req.to_dict() for req in self.functional_requirements],
            "non_functional_requirements": [req.to_dict() for req in self.non_functional_requirements],
            "ecosystem_lock": self.ecosystem_lock.to_dict(),
            "constraints": [c.to_dict() for c in self.constraints],
            "priorities": self.priorities,
            "version": self.version
        }


@dataclass
class Component:
    """System component definition"""
    name: str
    type: str  # service, database, api, frontend, etc.
    responsibilities: List[str]
    interfaces: List[str]
    dependencies: List[str]
    technology_stack: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DataModel:
    """Data model specification"""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    validation_rules: List[str]
    migration_strategy: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ApiContract:
    """API contract specification"""
    endpoint: str
    method: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    auth_required: bool
    rate_limit: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArchitectureDesign:
    """Structured architecture design from Architect"""
    components: List[Component]
    data_model: DataModel
    api_contracts: List[ApiContract]
    dependency_plan: Dict[str, List[str]]
    test_strategy: Dict[str, Any]
    documentation_plan: Dict[str, List[str]]
    implementation_phases: List[Dict[str, Any]]
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": [c.to_dict() for c in self.components],
            "data_model": self.data_model.to_dict(),
            "api_contracts": [a.to_dict() for a in self.api_contracts],
            "dependency_plan": self.dependency_plan,
            "test_strategy": self.test_strategy,
            "documentation_plan": self.documentation_plan,
            "implementation_phases": self.implementation_phases,
            "version": self.version
        }


@dataclass
class CodeFile:
    """Generated code file specification"""
    path: str
    content: str
    file_type: str  # source, test, config, docs, etc.
    dependencies: List[str]
    quality_score: QualityScore
    complexity_score: int  # 1-10 scale
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectFiles:
    """Complete project file structure"""
    source_files: List[CodeFile]
    test_files: List[CodeFile]
    config_files: List[CodeFile]
    documentation_files: List[CodeFile]
    requirements_file: Optional[CodeFile]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_files": [f.to_dict() for f in self.source_files],
            "test_files": [f.to_dict() for f in self.test_files],
            "config_files": [f.to_dict() for f in self.config_files],
            "documentation_files": [f.to_dict() for f in self.documentation_files],
            "requirements_file": self.requirements_file.to_dict() if self.requirements_file else None,
            "metadata": self.metadata
        }


@dataclass
class ReviewFinding:
    """Code review finding"""
    type: str  # bug, security, performance, style, etc.
    severity: str  # critical, high, medium, low
    file_path: str
    line_number: Optional[int]
    description: str
    suggestion: str
    category: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewReport:
    """Code review report"""
    overall_score: QualityScore
    findings: List[ReviewFinding]
    blocking_issues: List[str]
    recommendations: List[str]
    remediation_plan: Dict[str, List[str]]
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "findings": [f.to_dict() for f in self.findings],
            "blocking_issues": self.blocking_issues,
            "recommendations": self.recommendations,
            "remediation_plan": self.remediation_plan,
            "version": self.version
        }


@dataclass
class TestSuite:
    """Test suite specification"""
    test_files: List[CodeFile]
    coverage_target: int
    test_types: List[str]  # unit, integration, e2e, performance
    test_framework: str
    mock_strategy: Dict[str, Any]
    quality_score: QualityScore
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_files": [f.to_dict() for f in self.test_files],
            "coverage_target": self.coverage_target,
            "test_types": self.test_types,
            "test_framework": self.test_framework,
            "mock_strategy": self.mock_strategy,
            "quality_score": self.quality_score
        }


@dataclass
class EvaluationReport:
    """Final evaluation report"""
    requirements_coverage: Dict[str, bool]
    ecosystem_consistency: bool
    dependency_coherence: bool
    documentation_quality: QualityScore
    test_adequacy: QualityScore
    remaining_risks: List[str]
    blockers: List[str]
    satisfaction_score: int  # 1-10
    recommended_actions: List[str]
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirements_coverage": self.requirements_coverage,
            "ecosystem_consistency": self.ecosystem_consistency,
            "dependency_coherence": self.dependency_coherence,
            "documentation_quality": self.documentation_quality,
            "test_adequacy": self.test_adequacy,
            "remaining_risks": self.remaining_risks,
            "blockers": self.blockers,
            "satisfaction_score": self.satisfaction_score,
            "recommended_actions": self.recommended_actions,
            "version": self.version
        }


class SchemaValidator:
    """JSON Schema validator for structured communication"""
    
    SCHEMAS = {
        "requirements": {
            "type": "object",
            "properties": {
                "scope": {"type": "string"},
                "business_objective": {"type": "string"},
                "functional_requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {"type": "string"},
                            "acceptance_criteria": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["id", "description", "priority", "acceptance_criteria"]
                    }
                },
                "ecosystem_lock": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string"},
                        "framework": {"type": "string"},
                        "database": {"type": "string"},
                        "package_manager": {"type": "string"},
                        "runtime": {"type": "string"}
                    },
                    "required": ["language", "framework", "database", "package_manager", "runtime"]
                }
            },
            "required": ["scope", "business_objective", "functional_requirements", "ecosystem_lock"]
        }
    }
    
    @classmethod
    def validate(cls, data: Dict[str, Any], schema_type: str) -> bool:
        """Validate data against schema"""
        try:
            schema = cls.SCHEMAS.get(schema_type)
            if not schema:
                raise ValueError(f"Unknown schema type: {schema_type}")
            
            jsonschema.validate(data, schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"Schema validation error: {e}")
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False


# Convenience functions for creating structured data
def create_requirements_spec(
    scope: str,
    business_objective: str,
    functional_requirements: List[Dict[str, Any]],
    ecosystem_lock: Dict[str, str],
    non_functional_requirements: List[Dict[str, Any]] = None,
    constraints: List[Dict[str, Any]] = None
) -> RequirementsSpecification:
    """Create a structured requirements specification"""
    return RequirementsSpecification(
        scope=scope,
        business_objective=business_objective,
        functional_requirements=[
            FunctionalRequirement(**req) for req in functional_requirements
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(**req) for req in (non_functional_requirements or [])
        ],
        ecosystem_lock=EcosystemLock(**ecosystem_lock),
        constraints=[Constraint(**c) for c in (constraints or [])],
        priorities={}
    )


def create_architecture_design(
    components: List[Dict[str, Any]],
    data_model: Dict[str, Any],
    api_contracts: List[Dict[str, Any]]
) -> ArchitectureDesign:
    """Create a structured architecture design"""
    return ArchitectureDesign(
        components=[Component(**c) for c in components],
        data_model=DataModel(**data_model),
        api_contracts=[ApiContract(**a) for a in api_contracts],
        dependency_plan={},
        test_strategy={},
        documentation_plan={},
        implementation_phases=[]
    )