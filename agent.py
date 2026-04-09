# agent.py
# the brain — the main agent loop lives here

from dotenv import load_dotenv
load_dotenv()

import os
import json
import time
from openai import OpenAI
from tools import TOOLS, run_tool

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

SYSTEM_PROMPT = """
You are a helpful research assistant with access to a web search tool.

When to search:
- Current events, news, recent data
- Prices, stats, anything that changes over time
- When you are not confident in your answer

When NOT to search:
- Simple general knowledge (what is Python, who is Einstein etc.)
- Math or logic questions
- Anything from your training data you are confident about

Always be clear, concise and cite your sources when you search.
"""

conversation_history = []

# ── Agent Loop ────────────────────────────────────────────────
def chat(user_message):
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    while True:
        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + conversation_history,
            tools=TOOLS,
            tool_choice="auto"
        )

        ai_message = response.choices[0].message
        stop_reason = response.choices[0].finish_reason

        if stop_reason == "tool_calls" and ai_message.tool_calls:
            conversation_history.append({
                "role": "assistant",
                "content": ai_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in ai_message.tool_calls
                ]
            })

            for tool_call in ai_message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                tool_result = run_tool(tool_name, tool_input)
                conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
            continue

        else:
            final_reply = ai_message.content
            conversation_history.append({
                "role": "assistant",
                "content": final_reply
            })
            return final_reply


# ── Chat Interface ────────────────────────────────────────────
def run_agent():
    print("\n" + "="*50)
    print("🤖  Research Agent")
    print("="*50)
    print("💡 Commands: 'quit' to exit | 'history' to see memory")
    print("="*50 + "\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle quit
            if user_input.lower() == "quit":
                print("\n👋 Goodbye! Your session had "
                      f"{len(conversation_history)} messages.\n")
                break

            # Handle history command — shows memory size
            if user_input.lower() == "history":
                print(f"\n📝 Memory: {len(conversation_history)} "
                      f"messages stored\n")
                for i, msg in enumerate(conversation_history):
                    role = msg["role"].upper()
                    # only show text content, skip tool calls
                    content = msg.get("content", "")
                    if content:
                        # trim long messages
                        preview = content[:80] + "..." \
                            if len(content) > 80 else content
                        print(f"  {i+1}. [{role}]: {preview}")
                print()
                continue

            # Show thinking indicator
            print("⏳ Thinking...\n")
            start_time = time.time()

            # Call the agent — wrapped in try/except ✅
            try:
                reply = chat(user_input)
                elapsed = round(time.time() - start_time, 1)
                print(f"🤖 Agent: {reply}")
                print(f"\n⚡ Responded in {elapsed}s | "
                      f"💾 {len(conversation_history)} messages in memory\n")

            # Handle API errors
            except Exception as api_error:
                print(f"⚠️  Agent error: {api_error}")
                print("Please try again or rephrase your question.\n")
                # Remove the failed user message from history
                # so memory stays clean
                if conversation_history and \
                        conversation_history[-1]["role"] == "user":
                    conversation_history.pop()

        # Handle Ctrl+C gracefully
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    run_agent()