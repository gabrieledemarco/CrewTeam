"""
Structured Communication Module for CrewAI Multi-Agent System

This module provides:
- JSON schemas for all agent-to-agent communication
- Message broker for validation and transformation
- Agent interfaces for easy structured communication
- Quality scoring and monitoring capabilities

Replaces natural language context passing with typed, validated data contracts
to eliminate the "telephone game" effect in multi-agent workflows.
"""

from .schemas import (
    # Enums
    AgentType,
    EcosystemLanguage,
    EcosystemFramework,
    EcosystemDatabase,
    QualityScore,
    
    # Data classes
    EcosystemLock,
    FunctionalRequirement,
    NonFunctionalRequirement,
    Constraint,
    RequirementsSpecification,
    Component,
    DataModel,
    ApiContract,
    ArchitectureDesign,
    CodeFile,
    ProjectFiles,
    ReviewFinding,
    ReviewReport,
    TestSuite,
    EvaluationReport,
    
    # Utilities
    SchemaValidator,
    create_requirements_spec,
    create_architecture_design
)

from .middleware import (
    # Core classes
    MessageBroker,
    AgentInterface,
    
    # Exceptions
    CommunicationError,
    ValidationError,
    TransformationError,
    
    # Utilities
    get_message_broker,
    create_agent_interface
)

from .dependency_resolver import (
    # Core classes
    DependencyValidator,
    DependencyManager,
    
    # Enums
    DependencyType,
    ConflictSeverity,
    
    # Data classes
    Dependency,
    Conflict,
    Resolution
)

__all__ = [
    # Enums
    'AgentType',
    'EcosystemLanguage', 
    'EcosystemFramework',
    'EcosystemDatabase',
    'QualityScore',
    'DependencyType',
    'ConflictSeverity',
    
    # Data classes
    'EcosystemLock',
    'FunctionalRequirement',
    'NonFunctionalRequirement', 
    'Constraint',
    'RequirementsSpecification',
    'Component',
    'DataModel',
    'ApiContract',
    'ArchitectureDesign',
    'CodeFile',
    'ProjectFiles',
    'ReviewFinding',
    'ReviewReport',
    'TestSuite',
    'EvaluationReport',
    'Dependency',
    'Conflict',
    'Resolution',
    
    # Middleware
    'MessageBroker',
    'AgentInterface',
    'DependencyValidator',
    'DependencyManager',
    'CommunicationError',
    'ValidationError',
    'TransformationError',
    'get_message_broker',
    'create_agent_interface',
    
    # Utilities
    'SchemaValidator',
    'create_requirements_spec',
    'create_architecture_design'
]
