"""
Multi-Agent AI Research System — Main Entry Point
===================================================
Interactive CLI for running AI-powered research queries.

Usage:
    python main.py                  # interactive loop
    python main.py "your question"  # single query via CLI arg
"""

import sys
from agent import run_research


BANNER = """
==============================================================
Multi-Agent AI Research System
Powered by: Gemini 2.0 Flash + LangGraph ReAct
Tools: Tavily Web Search + BeautifulSoup Scraper
==============================================================
Type your research question and press Enter.
Type 'exit' or 'quit' to stop.
"""


def main():
    print(BANNER)

    # Single-shot mode: python main.py "question"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"[Query]: {query}\n{'-'*60}")
        print(run_research(query))
        return

    # Interactive loop mode
    while True:
        try:
            query = input("\n[Your Question]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        print(f"\n{'-'*60}")
        print("Researching... (this may take a few seconds)\n")
        try:
            answer = run_research(query)
            print(f"[Answer]\n\n{answer}")
        except Exception as e:
            print(f"[Error]: {e}")
        print(f"{'-'*60}")


if __name__ == "__main__":
    main()
