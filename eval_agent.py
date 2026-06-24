from graph_agent import run_agent

# --- THE DATASET: inputs + ground-truth expectations ---
# Each case: the question, plus what a correct answer must (or must not) contain.
test_cases = [
    {"question": "Should I bring an umbrella in Austin?", "must_include": "umbrella", "city_is_rainy": True},
    {"question": "What's the weather in Denver?", "must_include": "sunny", "city_is_rainy": False},
    {"question": "Do I need an umbrella in Austin today?", "must_include": "umbrella", "city_is_rainy": True},
    {"question": "Is it nice out in Denver?", "must_include": "72", "city_is_rainy": False},
    {"question": "Should I bring an umbrella in Miami?", "must_include": "miami", "city_is_rainy": False},
]

# --- THE RUNNER + SCORER ---
passed = 0
for i, case in enumerate(test_cases, 1):
    answer = run_agent(case["question"]).lower()       # run the agent
    expected = case["must_include"].lower()

    # objective check: does the answer contain what it should?
    ok = expected in answer

    # second objective check: rainy cities should mention umbrella; sunny should not
    if case["city_is_rainy"]:
        ok = ok and ("umbrella" in answer)
    else:
        ok = ok and ("umbrella" not in answer or "no umbrella" in answer or "don't" in answer)

    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    print(f"[{status}] case {i}: {case['question']}")
    if not ok:
        print(f"        got: {answer[:120]}...")

print(f"\nSCORE: {passed}/{len(test_cases)} passed ({100*passed//len(test_cases)}%)")