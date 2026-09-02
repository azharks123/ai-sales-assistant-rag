import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.tools.registry import ToolRegistry, tool_registry

class LLMService:
    def __init__(self, registry: ToolRegistry = tool_registry):
        self.client = AsyncOpenAI()
        self.registry = registry
        self.system_prompt = {
            "role": "system",
            "content": (
                "You are a Sales Manager from a second-sale car showroom (True value cars). "
                "You are connecting with customers to help them find cars from inventory or check availability.\n\n"
                "Tool Usage Guidelines:\n"
                "- Do NOT call any tools for general car recommendations, budget queries, or preference searches "
                "(e.g., 'cheap SUV under 10 lakhs', 'diesel family car', 'budget-friendly first car'). Answer directly using conversational context.\n"
                "- ONLY call tools when the user explicitly asks to check the stock, status, or availability of a specific car (using check_availability)."
            )
        }

    async def process_chat(self, history_messages: list, user_message: str) -> str:
        messages = [self.system_prompt]
        messages.extend(history_messages)
        new_user_msg = {"role": "user", "content": user_message}
        messages.append(new_user_msg)

        tools_schema = self.registry.get_openai_schemas()

        response = await self.client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=messages,
            tools=tools_schema if tools_schema else None,
            tool_choice="auto" if tools_schema else None,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKEN,
        )

        response_message = response.choices[0].message

        print(f'response_message: {response_message}')

        if response_message.tool_calls:
            messages.append(response_message.model_dump())

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                tool_output = await self.registry.execute_tool(function_name, function_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_output)
                })

            second_response = await self.client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKEN,
            )
            return second_response.choices[0].message.content
        
        return response_message.content

llm_service = LLMService()
