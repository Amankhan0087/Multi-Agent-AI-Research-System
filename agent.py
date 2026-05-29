"""
Multi-Agent AI Research System — Agent
=======================================
Uses a LangGraph ReAct agent backed by Google Gemini.
Tools available:
  - web_search   : Tavily search (titles, URLs, snippets)
  - scrape_webpage: BeautifulSoup full-page text extraction
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

from tools import web_search, scrape_webpage

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

# ── Tools ─────────────────────────────────────────────────────────────────────
tools = [web_search, scrape_webpage]

# ── Agent ─────────────────────────────────────────────────────────────────────
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=(
        "You are an expert AI research assistant. "
        "When given a research question:\n"
        "1. Use web_search to find relevant sources.\n"
        "2. Use scrape_webpage on the most promising URLs for deeper content.\n"
        "3. Synthesise a clear, well-structured answer with citations.\n"
        "Always cite your sources with their URLs."
    ),
)


def run_research(query: str) -> str:
    """Run the ReAct research agent on the given query and return the final answer."""
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    # The last message in the list is the agent's final answer
    return result["messages"][-1].content


if __name__ == "__main__":
    question = "What are the latest breakthroughs in multimodal AI models in 2025-2026?"
    print(f"\n[Research Query]: {question}\n")
    print("=" * 70)
    answer = run_research(question)
    print(answer)
