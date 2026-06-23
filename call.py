import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

messages = [
    {"role": "user", "content": "Should I bring an umbrella today in HotSprings?"}
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=300,
    temperature=1.0,
    tools=tools,
    messages=messages,
)

tools = [
{
    "name": "get_weather",
    "description": "Get the weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "The city to get the weather for"},
        },
        "required": ["city"],
    }
    }    
]

print("stop_reason", response.stop_reason)
print("response", response.content)

#print(response)