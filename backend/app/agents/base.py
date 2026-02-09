"""Base Agent class and configuration for all agents."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import logging


class AgentType(Enum):
    """Types of agents in the system."""
    ORCHESTRATOR = "orchestrator"
    NLU = "nlu"
    RAG = "rag"
    SQL = "sql"
    DESIGN = "design"
    VOICE = "voice"
    TRANSLATION = "translation"
    FEEDBACK = "feedback"


@dataclass
class AgentConfig:
    """Base configuration for an agent."""
    name: str
    agent_type: AgentType
    description: str = ""
    model: str = "gpt-4o"
    temperature: float = 0.3
    max_tokens: int = 2000
    system_prompt: str = ""
    enabled: bool = True
    tools: list = field(default_factory=list)


class Agent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent with configuration."""
        self.config = config
        self._initialized = False
        self._logger = logging.getLogger(f"agent.{config.agent_type.value}")

    @property
    def name(self) -> str:
        """Get agent name."""
        return self.config.name

    @property
    def agent_type(self) -> AgentType:
        """Get agent type."""
        return self.config.agent_type

    @property
    def is_enabled(self) -> bool:
        """Check if agent is enabled."""
        return self.config.enabled

    @property
    def is_initialized(self) -> bool:
        """Check if agent is initialized."""
        return self._initialized

    async def initialize(self):
        """Initialize the agent (async). Override in subclasses."""
        self._initialized = True
        self._logger.info(f"Agent {self.name} initialized")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output. Override in subclasses."""
        return {
            "success": False,
            "error": "process() not implemented"
        }

    async def execute(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a task with the agent."""
        input_data = {
            "task": task,
            "context": context or {}
        }
        return await self.process(input_data)

    def log_info(self, message: str):
        """Log info message."""
        self._logger.info(message)

    def log_error(self, message: str):
        """Log error message."""
        self._logger.error(message)

    def log_warning(self, message: str):
        """Log warning message."""
        self._logger.warning(message)

    def log_debug(self, message: str):
        """Log debug message."""
        self._logger.debug(message)

    async def health_check(self) -> Dict[str, Any]:
        """Check agent health."""
        return {
            "status": "healthy" if self._initialized else "not_initialized",
            "agent_type": self.config.agent_type.value,
            "name": self.config.name
        }
