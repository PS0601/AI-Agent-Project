# app.py
# the UI — streamlit web interface for the research agent

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI
from tools import TOOLS, run_tool

st.set_page_config(
    page_title="Research Agent",
    page_icon="🤖",
    layout="centered"
)

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

# ── Session state = memory ────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "search_log" not in st.session_state:
    st.session_state.search_log = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

# ── Agent function ────────────────────────────────────────────
def chat(user_message):
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    while True:
        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + st.session_state.messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        ai_message = response.choices[0].message
        stop_reason = response.choices[0].finish_reason

        if stop_reason == "tool_calls" and ai_message.tool_calls:
            st.session_state.messages.append({
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

                if tool_name == "web_search":
                    st.session_state.search_log.append(
                        f"🔍 Searched: {tool_input['query']}"
                    )

                tool_result = run_tool(tool_name, tool_input)
                st.session_state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
            continue

        else:
            final_reply = ai_message.content
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_reply
            })
            return final_reply


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Agent Stats")
    user_msgs = sum(
        1 for m in st.session_state.messages
        if m["role"] == "user"
    )
    st.metric("Questions asked", user_msgs)

    st.header("🔍 Search Log")
    if st.session_state.search_log:
        for search in st.session_state.search_log:
            st.caption(search)
    else:
        st.caption("No searches yet")

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.search_log = []
        st.session_state.display_messages = []
        st.rerun()

# ── Header ────────────────────────────────────────────────────
st.title("🤖 Research Agent")
st.caption("Ask me anything — I'll search the web when needed!")
st.divider()

# ── Display chat history ──────────────────────────────────────
for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input — always visible at bottom ────────────────────
prompt = st.chat_input("Ask me anything...")

if prompt:
    # Show user message
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.display_messages.append({
        "role": "user",
        "content": prompt
    })

    # Show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = chat(prompt)
                st.write(reply)
                st.session_state.display_messages.append({
                    "role": "assistant",
                    "content": reply
                })
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                if (st.session_state.messages and
                        st.session_state.messages[-1]["role"] == "user"):
                    st.session_state.messages.pop()