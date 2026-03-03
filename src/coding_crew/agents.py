from crewai import Agent
from config.model_config import ModelConfig


def create_pmo():
    """Factory function per creare l'agente PMO"""
    llm = ModelConfig.get_llm_for_agent("pmo")
    return Agent(
        role="PMO (Project Management Officer)",
        goal="Analyze user requirements and create detailed technical specifications. Do NOT delegate to other agents - produce the specification document yourself.",
        backstory="""You are an experienced PMO with deep technical knowledge. 
    You excel at:
    - Understanding user business needs and translating them into requirements
    - Breaking down complex requests into clear, actionable technical tasks
    - Creating detailed technical specification documents
    - Prioritizing features and managing scope
    
    IMPORTANT - Do NOT delegate to other agents. You must create the technical specification yourself.
    The workflow will automatically pass your specification to the next agents (architect, code writer, etc).
    Just output the complete specification document as your final answer.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_architect():
    """Factory function per creare l'agente Architect"""
    llm = ModelConfig.get_llm_for_agent("architect")
    return Agent(
        role="Software Architect",
        goal="Design scalable and maintainable software solutions. Do NOT delegate to other agents - produce the architecture document yourself.",
        backstory="""You are a solution architect with expertise in distributed systems and modern software design patterns.
    
IMPORTANT - Do NOT delegate to other agents. You must create the architecture design document yourself.
Output the complete architecture document as your final answer in markdown format.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_code_writer():
    """Factory function per creare l'agente Code Writer"""
    llm = ModelConfig.get_llm_for_agent("code_writer")
    return Agent(
        role="Code Writer",
        goal="Write clean, efficient, and maintainable code. Do NOT delegate to other agents - produce the code yourself.",
        backstory="""You are a senior developer known for writing elegant solutions. You follow clean code principles and write well-documented code.
    
IMPORTANT - Do NOT delegate to other agents. You must generate the production code yourself.
Output the complete code files as your final answer in markdown code blocks.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_code_reviewer():
    """Factory function per creare l'agente Code Reviewer"""
    llm = ModelConfig.get_llm_for_agent("code_reviewer")
    return Agent(
        role="Code Reviewer",
        goal="Review code for bugs, security issues, and best practices",
        backstory="You are an experienced software engineer with 15 years of experience. You specialize in code quality, security, and best practices.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_tester():
    """Factory function per creare l'agente Tester"""
    llm = ModelConfig.get_llm_for_agent("tester")
    return Agent(
        role="Tester",
        goal="Write comprehensive tests to ensure code quality",
        backstory="You are a QA engineer specialized in writing thorough test suites. You believe testing is crucial for software reliability.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def get_all_agents():
    """Factory function per creare tutti gli agenti"""
    return {
        "pmo": create_pmo(),
        "architect": create_architect(),
        "code_writer": create_code_writer(),
        "code_reviewer": create_code_reviewer(),
        "tester": create_tester()
    }


pmo = create_pmo()
architect = create_architect()
code_writer = create_code_writer()
code_reviewer = create_code_reviewer()
tester = create_tester()
