"""
Nexus AI — Inventory Tools
"""
from __future__ import annotations
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool, ToolMetadata, register_tool

# --- SCHEMAS ---
class SearchMedicineInput(BaseModel):
    query: str = Field(..., description="Medicine name or SKU to search for")
    limit: int = Field(10, description="Max results")

class MedicineInfo(BaseModel):
    id: str
    name: str
    sku: str

class SearchMedicineOutput(BaseModel):
    results: List[MedicineInfo]

# --- TOOL CLASSIFICATION ---
@register_tool
class SearchMedicineTool(BaseTool):
    metadata = ToolMetadata(
        name="search_medicine",
        description="Search the central medicine catalog.",
        category="inventory",
        required_permissions=["inventory.read"]
    )
    input_schema = SearchMedicineInput
    output_schema = SearchMedicineOutput
    
    async def execute(self, params: SearchMedicineInput, context: Dict[str, Any]) -> SearchMedicineOutput:
        # Stub implementation mapping to business logic
        return SearchMedicineOutput(results=[
            MedicineInfo(id="m-1", name=f"{params.query} Forte", sku="SKU-100")
        ])
