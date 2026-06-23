import os, json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

messages = [
    {"role": "user", "content": "Should I bring an umbrella today in HotSprings?"}
]

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

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=300,
    temperature=1.0,
    tools=tools,
    messages=messages,
)




#The Real function. Claude can never run this
def get_weather(city):  
        fake_data = {
            "Hot Springs": "Cloudy, 68 degrees, chance of meat balls",
            "Dallas": "Sunny, 72 degrees, chance of rain",
            "New York": "Cloudy, 65 degrees, chance of snow",
            "Los Angeles": "Sunny, 70 degrees, chance of rain",
            "Chicago": "Cloudy, 60 degrees, chance of snow",
            "Houston": "Sunny, 75 degrees, chance of rain",
            "Miami": "Sunny, 80 degrees, chance of rain",
            "Seattle": "Cloudy, 55 degrees, chance of snow",
            "San Francisco": "Sunny, 60 degrees, chance of rain",
            "Washington DC": "Cloudy, 62 degrees, chance of snow",
            "Boston": "Sunny, 68 degrees, chance of rain",
        }
        return fake_data.get(city, f"I don't know the weather for {city}.")




print("stop_reason", response.stop_reason)
print("response", response.content)

tool_use = next(block for block in response.content if block.type == "tool_use")
print("Claude wants to call", tool_use.name, "with the following arguments:", tool_use.input) 

result = get_weather(tool_use.input["city"])
print("Tool returned", result)

messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [
        {"type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": result,
        }
        
    ]
})

followup = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=300,
    temperature=1.0,
    tools=tools,
    messages=messages,
)

print("\n Final answer:", followup.content[0].text)
print("\n Stop reason", followup.stop_reason)
