from app.tools.base import BaseTool
from app.tools.registry import ToolRegistry, tool_registry
from app.tools.implementations.car_search import CarSearchTool
from app.tools.implementations.car_availability import CheckAvailabilityTool

# Register default tools
tool_registry.register(CarSearchTool())
tool_registry.register(CheckAvailabilityTool())

__all__ = ["BaseTool", "ToolRegistry", "tool_registry"]
