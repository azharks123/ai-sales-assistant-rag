from utils.tools.base import BaseTool
from utils.tools.registry import ToolRegistry, tool_registry
from utils.tools.implementations.car_search import CarSearchTool
from utils.tools.implementations.car_availability import CheckAvailabilityTool

# Register default application tools
tool_registry.register(CarSearchTool())
tool_registry.register(CheckAvailabilityTool())

__all__ = ["BaseTool", "ToolRegistry", "tool_registry"]
