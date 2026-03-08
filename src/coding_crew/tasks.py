from crewai import Task
from crewai import Agent
from textwrap import dedent

def create_code_review_task(agent: Agent, code: str):
    return Task(
        description=dedent(f"""\
            Review the following code for bugs, security issues, and best practices:
            
            ```{code}
            ```
            
            Provide a detailed report with specific issues and recommendations.
        """),
        agent=agent,
        expected_output="A detailed code review report with specific issues and recommendations"
    )

def create_code_task(agent: Agent, requirement: str):
    return Task(
        description=dedent(f"""\
            Implement the following feature or fix:
            
            {requirement}
            
            Write clean, efficient, and well-documented code.
        """),
        agent=agent,
        expected_output="Complete, working code with comments"
    )

def create_test_task(agent: Agent, code: str):
    return Task(
        description=dedent(f"""\
            Write comprehensive tests for the following code:
            
            ```{code}
            ```
            
            Include unit tests, integration tests, and edge cases.
        """),
        agent=agent,
        expected_output="Complete test suite with good coverage"
    )

def create_architecture_task(agent: Agent, requirements: str):
    return Task(
        description=dedent(f"""\
            Design an architecture for the following system requirements:
            
            {requirements}
            
            Provide a detailed architecture document with diagrams and explanations.
        """),
        agent=agent,
        expected_output="Detailed architecture document with components and interactions"
    )
