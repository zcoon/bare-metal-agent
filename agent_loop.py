import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# --- your tool (the real function) ---
def get_weather(city):
    fake_data = {
        "Austin": "Rainy, 64°F, 80% chance of showers",
        "Denver": "Sunny, 72°F, clear skies",
    }
    return fake_data.get(city, f"No data for {city}, assume mild and clear.")

# --- the menu Claude reads ---
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Austin'"}
            },
            "required": ["city"],
        },
    }
]

# --- a lookup so the loop can find the real function by name ---
available_tools = {"get_weather": get_weather}

# --- the conversation starts with the user's question ---
messages = [
    {"role": "user", "content": "Should I bring an umbrella in Chicago, and what about Honolulu?"}
]

# --- THE LOOP ---
max_iterations = 10
i = 0
while i < max_iterations:
    i += 1
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        tools=tools,
        messages=messages,
    )

    print(f"\n--- iteration {i}, stop_reason: {response.stop_reason} ---")

    if response.stop_reason == "end_turn":
        final_text = next(b.text for b in response.content if b.type == "text")
        print("\nFINAL ANSWER:", final_text)
        break

    if response.stop_reason == "tool_use":
        # record Claude's request turn
        messages.append({"role": "assistant", "content": response.content})

        # run EVERY tool the turn asked for, collect all results
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                fn = available_tools[block.name]
                result = fn(**block.input)
                print(f"  ran {block.name}({block.input}) -> {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # hand all results back as one user turn
        messages.append({"role": "user", "content": tool_results})
else:
    print("\nStopped: hit max iterations safety cap.")