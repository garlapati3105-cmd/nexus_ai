"""
Nexus AI — Tool Base Architecture
Base classes and interfaces for all AI executable tools.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional, Callable
from pydantic import BaseModel
import inspect

class ToolMetadata(BaseModel):
    name: str
    description: str
    category: str
    requires_approval: bool = False
    required_permissions: list[str] = []

class BaseTool(ABC):
    """
    Abstract base class for all AI tools.
    Forces definition of input/output schemas, permissions, and async execution.
    """
    
    # Needs to be overridden by subclasses
    metadata: ToolMetadata
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]

    @abstractmethod
    async def execute(self, params: BaseModel, context: Dict[str, Any]) -> BaseModel:
        """
        Core execution logic. Subclasses implement the business operations here.
        Params are already validated against input_schema.
        Returns a model matching output_schema.
        """
        pass
        
    async def validate_permissions(self, context: Dict[str, Any]) -> bool:
        """
        Hook for subclasses to execute specialized permission checks.
        Default checks against metadata.required_permissions.
        """
        user_perms = context.get("permissions", [])
        for req in self.metadata.required_permissions:
            if req not in user_perms:
                return False
        return True

# Decorator for automatic tool registration
TOOL_REGISTRY_MAP: Dict[str, Type[BaseTool]] = {}

def register_tool(cls: Type[BaseTool]) -> Type[BaseTool]:
    """Decorator to automatically register a tool class."""
    if not issubclass(cls, BaseTool):
        raise TypeError(f"{cls.__name__} must inherit from BaseTool")
    TOOL_REGISTRY_MAP[cls.metadata.name] = cls
    return cls

class ToolParameterError(Exception):
    pass
