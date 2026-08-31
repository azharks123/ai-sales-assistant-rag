from fastapi import APIRouter, Depends
from app.tools.registry import tool_registry, ToolRegistry

router = APIRouter(prefix="/tools", tags=["Tools"])

def get_tool_registry() -> ToolRegistry:
    return tool_registry

@router.get("", summary="List available LLM tool schemas")
def list_tools(registry: ToolRegistry = Depends(get_tool_registry)):
    """Returns OpenAI compatible JSON tool schemas."""
    return registry.get_openai_schemas()
