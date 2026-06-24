import os, json
from dotenv import load_dotenv
from anthropic import Anthropic

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_anthropic import ChatAnthropic



load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


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

llm = ChatAnthropic(model="claude-sonnet-4-6", max_tokens=500)
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# --- your tool (the real function) ---


available_tools = {"get_weather": get_weather}

# --- NODE 1: call the model ---
def call_model(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}



# --- NODE 2: run the tools ---

from langchain_core.messages import ToolMessage

def run_tools(state: AgentState):
    last = state["messages"][-1]
    tool_results = []
    for call in last.tool_calls:
        fn = available_tools[call["name"]]
        result = fn(**call["args"])
        print(f"  ran {call['name']}({call['args']}) -> {result}")
        tool_results.append(
            ToolMessage(content=result, tool_call_id=call["id"])
        )
    return {"messages": tool_results}

    # --- the conditional edge: your Week 1 "if stop_reason" branch ---
def should_continue(state: AgentState):
    last = state["messages"][-1]
    if last.tool_calls:          # AIMessage has a .tool_calls attribute
        return "run_tools"
    return END                  # no tools -> we're done

# --- build the graph ---
graph = StateGraph(AgentState)
graph.add_node("call_model", call_model)
graph.add_node("run_tools", run_tools)

graph.add_edge(START, "call_model")          # entry point
graph.add_conditional_edges("call_model", should_continue)  # the branch
graph.add_edge("run_tools", "call_model")    # loop tools back to the model

app = graph.compile()


#now run it

def run_agent(question: str) -> str:
    result = app.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit":10}
    )
    # the final answer is the last message's text
    final = result["messages"][-1].content
    return final



if __name__ == "__main__":
    print(run_agent("Should I bring an umbrella in Austin, and what about Denver?"))
    print(app.get_graph().draw_ascii())