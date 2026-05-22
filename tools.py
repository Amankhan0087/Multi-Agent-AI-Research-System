from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
import dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a given topic.Return title, URL and snippet."""
    results = tavily.search(query=query, max_results=5)
    
    return results

web_search.invoke("What are the recent news of war?")