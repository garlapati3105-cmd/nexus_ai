"""
Nexus AI — Prompt Manager
Controls agent personas, system instructions, and task templates.
"""
from __future__ import annotations
from typing import Any, Dict

class PromptTemplate:
    def __init__(self, name: str, version: str, content: str):
        self.name = name
        self.version = version
        self.content = content
        
    def format(self, variables: Dict[str, Any]) -> str:
        # Super simple format for architectural demonstration
        return self.content.format(**variables)

class PromptManager:
    def __init__(self):
        self._prompts: Dict[str, PromptTemplate] = {}
        
    def register_prompt(self, template: PromptTemplate):
        self._prompts[template.name] = template
        
    def get_prompt(self, name: str) -> PromptTemplate:
        if name not in self._prompts:
            raise KeyError(f"Prompt {name} not found.")
        return self._prompts[name]
        
    def render(self, name: str, variables: Dict[str, Any]) -> str:
        prompt = self.get_prompt(name)
        return prompt.format(variables)
