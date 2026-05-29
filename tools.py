from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a given topic. Return title, URL and snippet."""
    results = tavily.search(query=query, max_results=5)
    out = []

    for r in results.get("results", []):
        out.append(
            f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nSnippet: {r.get('content', '')[:300]}\n"
        )

    return "\n----\n".join(out)

@tool
def scrape_webpage(url: str) -> str:
    """Scrape and extract the main text content from a given webpage URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Remove script/style noise
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Return first 2000 chars to keep context manageable
        return text[:2000] if text else "No readable content found."
    except Exception as e:
        return f"Error scraping {url}: {e}"


if __name__ == "__main__":
    print(web_search.invoke("What is the current state of AI research?"))

