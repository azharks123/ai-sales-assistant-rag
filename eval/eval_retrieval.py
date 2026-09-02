import sys
import asyncio
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from eval.eval_dataset import EVAL_CASES
except ImportError:
    from eval_dataset import EVAL_CASES

from app.tools.implementations.car_search import CarSearchTool

async def evaluate_retrieval():
    correct = 0
    total = 0

    car_search_tool = CarSearchTool()
    for case in EVAL_CASES:
        results = await car_search_tool.run(query=case["query"], top_k=1)
        if not results or "error" in results[0]:
            print(f"FAIL (no results/error): '{case['query']}'")
            continue

        top_result = results[0]
        top_car_name = top_result.get("car", "")

        total += 1
        expected = case["expected_top_car"]

        if expected.lower() in top_car_name.lower():
            correct += 1
            print(f"PASS: '{case['query']}' -> {top_car_name}")
        else:
            print(f"FAIL: '{case['query']}' -> got '{top_car_name}', expected '{expected}'")

    if total > 0:
        print(f"\nRetrieval accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    else:
        print("\nNo queries evaluated.")

if __name__ == "__main__":
    asyncio.run(evaluate_retrieval())