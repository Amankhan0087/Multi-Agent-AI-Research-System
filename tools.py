from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
import time
from dotenv import load_dotenv
from rich import print

load_dotenv()


def _get_key(name: str) -> str:
    val = os.getenv(name, "")
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get(name, "")
        except Exception:
            pass
    return val


tavily = TavilyClient(api_key=_get_key("TAVILY_API_KEY"))

# Realistic browser headers — avoids bot-detection connection resets
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets."""
    for attempt in range(3):
        try:
            results = tavily.search(query=query, max_results=5)
            out = []
            for r in results["results"]:
                out.append(
                    f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
                )
            return "\n----\n".join(out)
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            return f"Search failed after 3 attempts: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=12, headers=_HEADERS)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)[:3000]
            return text if text.strip() else "Page loaded but no readable text content found."
        except Exception as e:
            err = str(e)
            if attempt < 2:
                time.sleep(2)
                continue
            return f"Could not scrape URL after 3 attempts: {err}"
