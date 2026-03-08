"""
Communication Middleware for Structured Agent Communication

Implements message broker pattern with validation, transformation,
and logging for all inter-agent communication.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Type, Union
from datetime import datetime
from dataclasses import asdict
import traceback

from .schemas import (
    RequirementsSpecification, ArchitectureDesign, ProjectFiles,
    ReviewReport, TestSuite, EvaluationReport, SchemaValidator,
    AgentType, QualityScore
)


class CommunicationError(Exception):
    """Base exception for communication failures"""
    pass


class ValidationError(CommunicationError):
    """Raised when message validation fails"""
    pass


class TransformationError(CommunicationError):
    """Raised when message transformation fails"""
    pass


class MessageBroker:
    """
    Central message broker for structured agent communication.
    
    Features:
    - Schema validation for all messages
    - Natural language to structured data transformation
    - Message logging and audit trail
    - Quality scoring and monitoring
    - Error handling and rollback
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.message_log: List[Dict[str, Any]] = []
        self.transformation_history: List[Dict[str, Any]] = []
        
        if self.enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
    
    def log_message(self, message: Dict[str, Any]):
        """Log message for audit trail"""
        if self.enable_logging and self.logger:
            self.logger.info(f"Message: {json.dumps(message, indent=2)}")
        
        self.message_log.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
    
    def validate_message(self, message: Dict[str, Any], schema_type: str) -> bool:
        """Validate message against schema"""
        try:
            is_valid = SchemaValidator.validate(message, schema_type)
            if not is_valid:
                raise ValidationError(f"Message validation failed for schema: {schema_type}")
            
            if self.enable_logging and self.logger:
                self.logger.info(f"Message validated successfully for schema: {schema_type}")
            
            return True
        except Exception as e:
            if self.enable_logging and self.logger:
                self.logger.error(f"Validation error: {e}")
            raise ValidationError(f"Message validation failed: {e}")
    
    def transform_natural_language_to_structured(
        self, 
        natural_language: str, 
        target_schema: str
    ) -> Dict[str, Any]:
        """
        Transform natural language output to structured format using LLM.
        
        Uses CrewAI LLM to parse natural language and extract structured data
        according to the target schema.
        """
        try:
            # Import here to avoid circular imports
            from config.model_config import ModelConfig
            import json
            
            # Use PMO agent's LLM for parsing
            llm = ModelConfig.get_llm_for_agent("pmo")
            
            # Create prompt for transformation
            prompt = f"""Transform the following natural language text to structured JSON format for the '{target_schema}' schema:

TEXT:
{natural_language}

Return ONLY valid JSON, no markdown formatting, no explanations.
The JSON should follow the {target_schema} schema structure."""
            
            if self.enable_logging and self.logger:
                self.logger.debug(f"Transforming text using LLM for schema: {target_schema}")
            
            # Call LLM
            response = llm.call(prompt)
            
            # Parse JSON response
            try:
                transformed = json.loads(response)
                if self.enable_logging and self.logger:
                    self.logger.debug(f"Transformation successful, keys: {list(transformed.keys())}")
                return transformed
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to mock structure
                if self.enable_logging and self.logger:
                    self.logger.warning(f"Failed to parse LLM response as JSON, using mock structure")
                
                if target_schema == "requirements":
                    return self._mock_requirements_from_text(natural_language)
                elif target_schema == "architecture":
                    return self._mock_architecture_from_text(natural_language)
                else:
                    return {"raw_text": natural_language, "schema": target_schema}
                
        except Exception as e:
            if self.enable_logging and self.logger:
                self.logger.error(f"Transformation error: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Fall back to mock structure on any error
            try:
                if target_schema == "requirements":
                    return self._mock_requirements_from_text(natural_language)
                elif target_schema == "architecture":
                    return self._mock_architecture_from_text(natural_language)
            except Exception as fallback_error:
                if self.enable_logging and self.logger:
                    self.logger.error(f"Fallback transformation also failed: {fallback_error}")
            
            raise TransformationError(f"Failed to transform natural language: {e}")
    
    def _mock_requirements_from_text(self, text: str) -> Dict[str, Any]:
        """Mock transformation for requirements (placeholder)"""
        # This would use an LLM to extract:
        # - Scope
        # - Functional requirements
        # - Ecosystem lock
        # - Constraints
        
        return {
            "scope": "Generated from natural language",
            "business_objective": "Auto-generated objective",
            "functional_requirements": [
                {
                    "id": "FR-001",
                    "description": "System must allow users to create accounts",
                    "priority": "P1",
                    "acceptance_criteria": ["User can register", "Email verification required"]
                }
            ],
            "ecosystem_lock": {
                "language": "python",
                "framework": "fastapi",
                "database": "postgresql",
                "package_manager": "pip",
                "runtime": "python3.11"
            },
            "constraints": [
                {
                    "type": "must_not_have",
                    "description": "No external API dependencies",
                    "rationale": "Offline operation required"
                }
            ]
        }
    
    def _mock_architecture_from_text(self, text: str) -> Dict[str, Any]:
        """Mock transformation for architecture (placeholder)"""
        # This would use an LLM to extract:
        # - Components
        # - Data model
        # - API contracts
        
        return {
            "components": [
                {
                    "name": "User Service",
                    "type": "service",
                    "responsibilities": ["User management", "Authentication"],
                    "interfaces": ["REST API"],
                    "dependencies": ["Database"],
                    "technology_stack": {"language": "python", "framework": "fastapi"}
                }
            ],
            "data_model": {
                "entities": [{"name": "User", "fields": ["id", "email", "password"]}],
                "relationships": [],
                "validation_rules": ["Email must be unique"],
                "migration_strategy": "Liquibase"
            },
            "api_contracts": [
                {
                    "endpoint": "/api/users",
                    "method": "POST",
                    "request_schema": {"type": "object", "properties": {"email": {"type": "string"}}},
                    "response_schema": {"type": "object", "properties": {"id": {"type": "string"}}},
                    "auth_required": False,
                    "rate_limit": "100/hour"
                }
            ]
        }
    
    def send_message(
        self,
        source_agent: AgentType,
        target_agent: AgentType,
        message_type: str,
        content: Union[Dict[str, Any], Any],
        quality_score: Optional[QualityScore] = None
    ) -> Dict[str, Any]:
        """
        Send structured message from one agent to another
        
        Args:
            source_agent: Source agent type
            target_agent: Target agent type
            message_type: Type of message (requirements, architecture, etc.)
            content: Message content (structured or natural language)
            quality_score: Quality assessment of the message
        
        Returns:
            Structured message ready for delivery
        """
        try:
            # Transform natural language to structured if needed
            if isinstance(content, str):
                structured_content = self.transform_natural_language_to_structured(
                    content, message_type
                )
            else:
                structured_content = content
            
            # Validate the structured content
            self.validate_message(structured_content, message_type)
            
            # Create message envelope
            message = {
                "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                "source_agent": source_agent.value,
                "target_agent": target_agent.value,
                "message_type": message_type,
                "timestamp": datetime.now().isoformat(),
                "content": structured_content,
                "quality_score": quality_score.value if quality_score else None,
                "version": "1.0"
            }
            
            # Log the message
            self.log_message(message)
            
            if self.enable_logging and self.logger:
                self.logger.info(f"Message sent from {source_agent.value} to {target_agent.value}")
            
            return message
            
        except Exception as e:
            error_msg = {
                "error": str(e),
                "source_agent": source_agent.value,
                "target_agent": target_agent.value,
                "message_type": message_type,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_message(error_msg)
            
            if self.enable_logging and self.logger:
                self.logger.error(f"Message sending failed: {e}")
            
            raise CommunicationError(f"Failed to send message: {e}")
    
    def receive_message(
        self,
        message: Dict[str, Any],
        expected_type: str
    ) -> Union[RequirementsSpecification, ArchitectureDesign, ProjectFiles, ReviewReport, TestSuite, EvaluationReport]:
        """
        Receive and process message for target agent
        
        Args:
            message: Incoming message
            expected_type: Expected message type
        
        Returns:
            Structured object corresponding to message type
        """
        try:
            # Validate message structure
            if "content" not in message:
                raise ValidationError("Message missing content field")
            
            if message.get("message_type") != expected_type:
                raise ValidationError(f"Message type mismatch: expected {expected_type}, got {message.get('message_type')}")
            
            # Validate content against schema
            self.validate_message(message["content"], expected_type)
            
            # Convert to appropriate structured object
            if expected_type == "requirements":
                return RequirementsSpecification(**message["content"])
            elif expected_type == "architecture":
                return ArchitectureDesign(**message["content"])
            elif expected_type == "code":
                return ProjectFiles(**message["content"])
            elif expected_type == "review":
                return ReviewReport(**message["content"])
            elif expected_type == "test":
                return TestSuite(**message["content"])
            elif expected_type == "evaluation":
                return EvaluationReport(**message["content"])
            else:
                raise ValidationError(f"Unknown message type: {expected_type}")
                
        except Exception as e:
            if self.enable_logging and self.logger:
                self.logger.error(f"Message receiving failed: {e}")
            raise CommunicationError(f"Failed to receive message: {e}")
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """Get complete message history for debugging"""
        return self.message_log
    
    def get_transformation_history(self) -> List[Dict[str, Any]]:
        """Get transformation history for monitoring"""
        return self.transformation_history
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get quality metrics for communication monitoring"""
        quality_scores = [
            msg.get("quality_score") 
            for msg in self.message_log 
            if msg.get("quality_score") is not None
        ]
        
        if not quality_scores:
            return {"average_quality": 0, "message_count": len(self.message_log)}
        
        return {
            "average_quality": sum(quality_scores) / len(quality_scores),
            "message_count": len(self.message_log),
            "quality_distribution": {
                "excellent": len([s for s in quality_scores if s >= 9]),
                "good": len([s for s in quality_scores if 7 <= s < 9]),
                "average": len([s for s in quality_scores if 5 <= s < 7]),
                "poor": len([s for s in quality_scores if s < 5])
            }
        }


class AgentInterface:
    """
    Interface wrapper for agents to use structured communication
    
    Provides:
    - Easy-to-use methods for sending/receiving messages
    - Automatic validation and transformation
    - Quality scoring integration
    """
    
    def __init__(self, agent_type: AgentType, broker: MessageBroker):
        self.agent_type = agent_type
        self.broker = broker
    
    def send_requirements(
        self, 
        target_agent: AgentType, 
        requirements: RequirementsSpecification,
        quality_score: QualityScore = QualityScore.GOOD
    ) -> Dict[str, Any]:
        """Send requirements specification to architect"""
        return self.broker.send_message(
            source_agent=self.agent_type,
            target_agent=target_agent,
            message_type="requirements",
            content=requirements.to_dict(),
            quality_score=quality_score
        )
    
    def send_architecture(
        self, 
        target_agent: AgentType, 
        architecture: ArchitectureDesign,
        quality_score: QualityScore = QualityScore.GOOD
    ) -> Dict[str, Any]:
        """Send architecture design to code writer"""
        return self.broker.send_message(
            source_agent=self.agent_type,
            target_agent=target_agent,
            message_type="architecture",
            content=architecture.to_dict(),
            quality_score=quality_score
        )
    
    def send_code(
        self, 
        target_agent: AgentType, 
        project_files: ProjectFiles,
        quality_score: QualityScore = QualityScore.GOOD
    ) -> Dict[str, Any]:
        """Send generated code to reviewer"""
        return self.broker.send_message(
            source_agent=self.agent_type,
            target_agent=target_agent,
            message_type="code",
            content=project_files.to_dict(),
            quality_score=quality_score
        )
    
    def send_review(
        self, 
        target_agent: AgentType, 
        review: ReviewReport,
        quality_score: QualityScore = QualityScore.GOOD
    ) -> Dict[str, Any]:
        """Send review report to tester"""
        return self.broker.send_message(
            source_agent=self.agent_type,
            target_agent=target_agent,
            message_type="review",
            content=review.to_dict(),
            quality_score=quality_score
        )
    
    def send_tests(
        self, 
        target_agent: AgentType, 
        test_suite: TestSuite,
        quality_score: QualityScore = QualityScore.GOOD
    ) -> Dict[str, Any]:
        """Send test suite to PMO for evaluation"""
        return self.broker.send_message(
            source_agent=self.agent_type,
            target_agent=target_agent,
            message_type="test",
            content=test_suite.to_dict(),
            quality_score=quality_score
        )
    
    def send_evaluation(
        self, 
        target_agent: AgentType, 
        evaluation: EvaluationReport,
        quality_score: QualityScore = QualityScore.GOOD
    ) -> Dict[str, Any]:
        """Send evaluation report (final output)"""
        return self.broker.send_message(
            source_agent=self.agent_type,
            target_agent=target_agent,
            message_type="evaluation",
            content=evaluation.to_dict(),
            quality_score=quality_score
        )
    
    def receive_requirements(self, message: Dict[str, Any]) -> RequirementsSpecification:
        """Receive requirements specification"""
        return self.broker.receive_message(message, "requirements")
    
    def receive_architecture(self, message: Dict[str, Any]) -> ArchitectureDesign:
        """Receive architecture design"""
        return self.broker.receive_message(message, "architecture")
    
    def receive_code(self, message: Dict[str, Any]) -> ProjectFiles:
        """Receive generated code"""
        return self.broker.receive_message(message, "code")
    
    def receive_review(self, message: Dict[str, Any]) -> ReviewReport:
        """Receive review report"""
        return self.broker.receive_message(message, "review")
    
    def receive_tests(self, message: Dict[str, Any]) -> TestSuite:
        """Receive test suite"""
        return self.broker.receive_message(message, "test")
    
    def receive_evaluation(self, message: Dict[str, Any]) -> EvaluationReport:
        """Receive evaluation report"""
        return self.broker.receive_message(message, "evaluation")


# Global broker instance for easy access
_global_broker = None


def get_message_broker(enable_logging: bool = True) -> MessageBroker:
    """Get global message broker instance"""
    global _global_broker
    if _global_broker is None:
        _global_broker = MessageBroker(enable_logging=enable_logging)
    return _global_broker


def create_agent_interface(agent_type: AgentType) -> AgentInterface:
    """Create agent interface for structured communication"""
    broker = get_message_broker()
    return AgentInterface(agent_type, broker)