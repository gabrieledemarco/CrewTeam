"""
Structured Agent Factory

Replaces the original agents.py with structured communication capabilities.
Each agent now uses typed contracts and validation for all inter-agent communication.
"""

from crewai import Agent
from config.model_config import ModelConfig
from communication import (
    AgentInterface, 
    AgentType,
    RequirementsSpecification,
    ArchitectureDesign,
    ProjectFiles,
    ReviewReport,
    TestSuite,
    EvaluationReport,
    QualityScore
)


class StructuredAgentFactory:
    """Factory for creating agents with structured communication capabilities"""
    
    @staticmethod
    def create_pmo():
        """Create PMO agent with structured communication"""
        llm = ModelConfig.get_llm_for_agent("pmo")
        agent_interface = AgentInterface(AgentType.PMO, None)  # Will be set by broker
        
        return Agent(
            role="PMO (Project Management Officer)",
            goal="Analyze user requirements and create structured technical specifications",
            backstory="""You are an experienced PMO with deep technical knowledge. 
        You excel at:
        - Understanding user business needs and translating them into structured requirements
        - Creating detailed technical specification documents with explicit ecosystem locks
        - Prioritizing features and managing scope
        
        IMPORTANT: You MUST output structured data using the RequirementsSpecification schema.
        Use the agent_interface to send structured messages to the Architect.
        Do NOT use natural language context passing.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            agent_interface=agent_interface
        )
    
    @staticmethod
    def create_architect():
        """Create Architect agent with structured communication"""
        llm = ModelConfig.get_llm_for_agent("architect")
        agent_interface = AgentInterface(AgentType.ARCHITECT, None)
        
        return Agent(
            role="Software Architect",
            goal="Design scalable and maintainable software solutions using structured architecture",
            backstory="""You are a solution architect with expertise in distributed systems and modern software design patterns.
        
        IMPORTANT: You MUST:
        - Receive structured RequirementsSpecification from PMO
        - Output structured ArchitectureDesign using the ArchitectureDesign schema
        - Use agent_interface to send structured messages to Code Writer
        - Do NOT use natural language context passing""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            agent_interface=agent_interface
        )
    
    @staticmethod
    def create_code_writer():
        """Create Code Writer agent with structured communication"""
        llm = ModelConfig.get_llm_for_agent("code_writer")
        agent_interface = AgentInterface(AgentType.CODE_WRITER, None)
        
        return Agent(
            role="Code Writer",
            goal="Write clean, efficient, and maintainable code using structured project specifications",
            backstory="""You are a senior developer known for writing elegant solutions. You follow clean code principles and write well-documented code.
        
        IMPORTANT: You MUST:
        - Receive structured ArchitectureDesign from Architect
        - Output structured ProjectFiles using the ProjectFiles schema
        - Use agent_interface to send structured messages to Code Reviewer
        - Do NOT use natural language context passing""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            agent_interface=agent_interface
        )
    
    @staticmethod
    def create_code_reviewer():
        """Create Code Reviewer agent with structured communication"""
        llm = ModelConfig.get_llm_for_agent("code_reviewer")
        agent_interface = AgentInterface(AgentType.CODE_REVIEWER, None)
        
        return Agent(
            role="Code Reviewer",
            goal="Review code for bugs, security issues, and best practices using structured review reports",
            backstory="""You are an experienced software engineer with 15 years of experience. You specialize in code quality, security, and best practices.
        
        IMPORTANT: You MUST:
        - Receive structured ProjectFiles from Code Writer
        - Output structured ReviewReport using the ReviewReport schema
        - Use agent_interface to send structured messages to Tester
        - Do NOT use natural language context passing""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            agent_interface=agent_interface
        )
    
    @staticmethod
    def create_tester():
        """Create Tester agent with structured communication"""
        llm = ModelConfig.get_llm_for_agent("tester")
        agent_interface = AgentInterface(AgentType.TESTER, None)
        
        return Agent(
            role="Tester",
            goal="Write comprehensive tests to ensure code quality using structured test specifications",
            backstory="""You are a QA engineer specialized in writing thorough test suites. You believe testing is crucial for software reliability.
        
        IMPORTANT: You MUST:
        - Receive structured ReviewReport from Code Reviewer
        - Output structured TestSuite using the TestSuite schema
        - Use agent_interface to send structured messages to PMO for evaluation
        - Do NOT use natural language context passing""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            agent_interface=agent_interface
        )


# Backward compatibility - keep original factory functions
def create_pmo():
    """Backward compatible PMO creation"""
    return StructuredAgentFactory.create_pmo()

def create_architect():
    """Backward compatible Architect creation"""
    return StructuredAgentFactory.create_architect()

def create_code_writer():
    """Backward compatible Code Writer creation"""
    return StructuredAgentFactory.create_code_writer()

def create_code_reviewer():
    """Backward compatible Code Reviewer creation"""
    return StructuredAgentFactory.create_code_reviewer()

def create_tester():
    """Backward compatible Tester creation"""
    return StructuredAgentFactory.create_tester()


def get_all_agents():
    """Get all structured agents"""
    return {
        "pmo": create_pmo(),
        "architect": create_architect(),
        "code_writer": create_code_writer(),
        "code_reviewer": create_code_reviewer(),
        "tester": create_tester()
    }


# Global instances for backward compatibility
pmo = create_pmo()
architect = create_architect()
code_writer = create_code_writer()
code_reviewer = create_code_reviewer()
tester = create_tester()