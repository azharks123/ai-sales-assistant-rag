from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel

class BaseTool(ABC):
    name: str
    description: str
    args_schema: Type[BaseModel]

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        """Execute the tool logic asynchronously."""
        pass

    def to_openai_tool(self) -> Dict[str, Any]:
        """Convert the tool into OpenAI function calling schema format."""
        schema = self.args_schema.model_json_schema()
        # Clean up Pydantic schema title to keep schema clean for LLMs
        schema.pop("title", None)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema
            }
        }
