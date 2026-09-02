import sys
import asyncio
import json
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from eval.eval_dataset import EVAL_CASES
except ImportError:
    from eval_dataset import EVAL_CASES

from app.core.config import settings
from app.services.llm_service import llm_service

async def run_chat_and_check_tool_call(user_message: str) -> bool:
    messages = [
        llm_service.system_prompt,
        {"role": "user", "content": user_message}
    ]
    tools_schema = llm_service.registry.get_openai_schemas()
    response = await llm_service.client.chat.completions.create(
        model=settings.DEFAULT_MODEL,
        messages=messages,
        tools=tools_schema if tools_schema else None,
        tool_choice="auto" if tools_schema else None,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKEN,
    )
    return bool(response.choices[0].message.tool_calls)

async def evaluate_tool_calling():
    correct = 0
    total = 0

    for case in EVAL_CASES:
        if "should_call_tool" not in case:
            continue

        total += 1
        tool_was_called = await run_chat_and_check_tool_call(case["query"])

        if tool_was_called == case["should_call_tool"]:
            correct += 1
            print(f"PASS: '{case['query']}' (tool_called={tool_was_called})")
        else:
            print(f"FAIL: '{case['query']}' expected tool_called={case['should_call_tool']}, got {tool_was_called}")

    if total > 0:
        print(f"\nTool-calling accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    else:
        print("\nNo tool-calling queries evaluated.")

if __name__ == "__main__":
    asyncio.run(evaluate_tool_calling())