"""
Nexus AI — AI Exceptions
Core exception classes for the AI Kernel.
"""
from __future__ import annotations

class AIException(Exception):
    """Base exception for all AI platform errors."""
    pass

class ToolException(AIException):
    """Raised when a tool execution fails."""
    pass

class MemoryException(AIException):
    """Raised when a memory operation fails."""
    pass

class ContextException(AIException):
    """Raised when context loading or management fails."""
    pass

class WorkflowException(AIException):
    """Raised when the workflow runtime encounters an error."""
    pass

class PermissionException(AIException):
    """Raised when an AI agent or action lacks sufficient permissions."""
    pass

class RegistryException(AIException):
    """Raised when a registry lookup fails (e.g. agent or tool not found)."""
    pass
