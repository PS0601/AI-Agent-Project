# AI-Agent-Project
AI Research Agent with web search, memory, and Streamlit UI — built with OpenRouter and Tavily

# AI Research Agent

A beginner-friendly AI agent that can search the web in real-time 
and remember your conversation.

## What it does
- Searches the web automatically when needed
- Answers directly from knowledge when it doesn't need to search
- Remembers the full conversation
- Built with ReAct pattern (Reason → Act → Observe)
- Clean web UI built with Streamlit

## Tech Stack
- **LLM** — OpenRouter (free tier)
- **Web Search** — Tavily API (free tier)
- **UI** — Streamlit
- **Language** — Python

## How to run
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your API keys in `.env`
4. Run terminal version: `python agent.py`
5. Run web UI: `streamlit run app.py`

## Project Structure
- `agent.py` — terminal version of the agent
- `app.py` — Streamlit web UI
- `tools.py` — web search tool definition
