from typing import Dict, List, Any
from app.tools.base import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_tool() for tool in self._tools.values()]

    async def execute_tool(self, name: str, kwargs: dict) -> Any:
        tool = self.get_tool(name)
        validated_args = tool.args_schema(**kwargs)
        return await tool.run(**validated_args.model_dump())

tool_registry = ToolRegistry()
