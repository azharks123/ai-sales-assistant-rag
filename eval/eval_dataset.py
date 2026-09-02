# eval_dataset.py

EVAL_CASES = [
    {
        "query": "cheap SUV under 10 lakhs",
        "expected_top_car": "Tata Nexon",
        "should_call_tool": False,
    },
    {
        "query": "I want a diesel family car with good mileage",
        "expected_top_car": "Hyundai Creta",
        "should_call_tool": False,
    },
    {
        "query": "budget-friendly first car",
        "expected_top_car": "Maruti Suzuki Swift",
        "should_call_tool": False,
    },
    {
        "query": "Is the 2020 Tata Nexon still available?",
        "expected_top_car": "Tata Nexon",
        "should_call_tool": True,
        "expected_tool": "check_availability",
    },
    {
        "query": "Can you confirm if the Honda City is in stock?",
        "expected_top_car": "Honda City",
        "should_call_tool": True,
        "expected_tool": "check_availability",
    },
]