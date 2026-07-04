"""
Nexus AI — Tool Executor
Secures and runs tool logic, handling logging and errors.
"""
from __future__ import annotations
from typing import Dict, Any, Type
from pydantic import BaseModel, ValidationError
from app.ai.tools.base import BaseTool, ToolParameterError
from app.ai.tools.registry import ToolRegistry
from app.ai.logging.ai_logger import AILogger
import time

class ToolExecutor:
    """Safely executes tools by enforcing validation, permissions, and logging."""
    
    def __init__(self, registry: ToolRegistry, logger: AILogger):
        self.registry = registry
        self.logger = logger
        
    async def execute(self, tool_name: str, raw_params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        start_time = time.time()
        tool = self.registry.get_tool(tool_name)
        
        # 1. Permission Check
        if not await tool.validate_permissions(context):
            self._log(tool, context, start_time, False, error="Permission denied.")
            raise PermissionError(f"Unauthorized to execute tool {tool_name}")
            
        # 2. Input Validation
        try:
            validated_input = tool.input_schema(**raw_params)
        except ValidationError as e:
            self._log(tool, context, start_time, False, error="Validation failed.")
            raise ToolParameterError(f"Invalid parameters for {tool_name}: {str(e)}")
            
        # 3. Execution
        try:
            result = await tool.execute(validated_input, context)
            self._log(tool, context, start_time, True)
            
            # Ensure it adheres to output schema
            if not isinstance(result, tool.output_schema):
                pass # Ideally serialize into the pydantic model
            return result
        except Exception as e:
            self._log(tool, context, start_time, False, error=str(e))
            raise
            
    def _log(self, tool: BaseTool, ctx: Dict[str, Any], start_time: float, success: bool, error: str = None) -> None:
        exec_time = (time.time() - start_time) * 1000
        self.logger.log_execution(
            agent_id=ctx.get("agent_id", "unknown"),
            task_name=f"Execute: {tool.metadata.name}",
            workflow_id=ctx.get("workflow_id", "unknown"),
            execution_time_ms=exec_time,
            confidence=1.0,
            decision="success" if success else "failed",
            reasoning="Tool execution wrapper",
            tool_usage=[tool.metadata.name],
            error=error
        )
