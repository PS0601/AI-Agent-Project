# the hands — all tools the agent can use go here

# tools.py
# the hands — all tools the agent can use live here

import os
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()
# Create the Tavily search client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ── Tool Definition ───────────────────────────────────────────
# This is the "menu" we show the AI so it knows what tools exist
# The AI reads the name + description to decide WHEN to use it
# Think of it like a job posting — AI reads it and knows what the tool does

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",           # tool name — AI calls it by this name
            "description": """Search the web for current, real-time information.
            Use this tool when the user asks about:
            - Recent news or current events
            - Latest prices, stats, or data
            - Anything that may have changed recently
            - Information you are not confident about
            Do NOT use this for general knowledge you already know.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    }
                },
                "required": ["query"]   # query is mandatory
            }
        }
    }
]

# ── Tool Execution ────────────────────────────────────────────
# This function actually RUNS the search when the AI asks for it
# Think of it as the AI's hands — it decides to search, we execute it

def run_tool(tool_name, tool_input):
    """
    When the AI decides to use a tool:
    1. We check which tool it wants
    2. We run that tool with the AI's input
    3. We return the result back to the AI
    """
    if tool_name == "web_search":
        query = tool_input["query"]
        print(f"\n🔍 Agent is searching for: '{query}'")  # so you can see it working

        # Call Tavily search API
        result = tavily_client.search(
            query=query,
            max_results=3   # get top 3 results
        )

        # Format results into clean text the AI can read
        formatted = ""
        for i, item in enumerate(result["results"], 1):
            formatted += f"\nResult {i}:\n"
            formatted += f"Title: {item['title']}\n"
            formatted += f"Content: {item['content']}\n"
            formatted += f"URL: {item['url']}\n"

        return formatted

    return "Tool not found"