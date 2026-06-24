Claude agent set up to learn basic flow structures and tooling.
Agent passes a predefined user message to claude about weather in a city, claude checks the weather for various cities and reponds to the user. Since this is educational, the weather lookup uses faked data, not connected to an actual weather API.
Repo explores how claude responds when we remove access to the tooling to witness refusal or hallucination. Most of the time it would say it can't find weather and then give a generic answer about weather in a specific city (obviously unreliable)

Claude is stateless so we have to pass the full message history back to it with each subsequent user message.

On the tool side - Claude doesn't actually "check the weather" - it references its list of available tools, one of which is a function to check the weather, and it relies on that function to get answers, and then go about it's own process.

We included a safety loop to ensure we don't iterate more than 10 times to prevent budget overflow. The loop engine continues to run if the `stop_reason` is driven by a `tool_use`, or ends if it finds `end_turn` as a top reason

Project also contains an eval agent so we can test how the agent is performing. The short fall is that we're using mockdata so the outputs are fairly predictable. Also because if we ask for weather data in a city that's not in our dataset, it defaults to stating it's mild and clear, so the "do i need an umbrella" question will always resort to false. Ideally the system would report it doesn't have sufficient data to properly test a given case.