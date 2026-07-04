"""
Nexus AI — Tool Registry
Central point for tool discovery and instantiation.
"""
from __future__ import annotations
from typing import Dict, List, Type, Any
from app.ai.tools.base import BaseTool, TOOL_REGISTRY_MAP, ToolMetadata

class ToolRegistry:
    """Manages the available AI tools."""
    
    def __init__(self):
        # We instantiate the tools here or use factories
        self.available_tools: Dict[str, BaseTool] = {}
        self._load_registered_tools()
        
    def _load_registered_tools(self) -> None:
        """Loads all tools decorated with @register_tool."""
        for name, cls in TOOL_REGISTRY_MAP.items():
            self.available_tools[name] = cls()
            
    def get_tool(self, name: str) -> BaseTool:
        if name not in self.available_tools:
            raise KeyError(f"Tool {name} not found in registry.")
        return self.available_tools[name]
        
    def list_tools(self, category: str = None) -> List[ToolMetadata]:
        tools = self.available_tools.values()
        if category:
            tools = [t for t in tools if t.metadata.category == category]
        return [t.metadata for t in tools]
        
    def get_tool_schemas(self) -> Dict[str, Any]:
        """Generate JSON schemas for all available tools (for LLM context)."""
        schemas = {}
        for name, tool in self.available_tools.items():
            schemas[name] = {
                "description": tool.metadata.description,
                "inputSchema": tool.input_schema.model_json_schema()
            }
        return schemas
