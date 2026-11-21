from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    try:
        results = tavily.search(query=query, max_results=5)
        out = []
        for r in results.get("results", []):
            out.append(
                f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
            )
        return "\n----\n".join(out) if out else "No search results found."
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given web page URL for deeper reading."""
    try:
        if url.lower().endswith(".pdf"):
            return "Skipped PDF URL. Pick a standard HTML article URL."
        resp = requests.get(url, timeout=(3, 5), headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        ctype = resp.headers.get("Content-Type", "").lower()
        if "text/html" not in ctype and "text/plain" not in ctype:
            return f"Skipped non-HTML URL ({ctype})."
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:1500] if text else "Page returned empty text."
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

#print(scrape_url.invoke("https://en.mehrnews.com/news/243679/Recent-war-symbol-of-misuse-of-tech-against-humanity"))
#Write a test script to test the tools
"""
if __name__ == "__main__":

    print("\nTesting Web Search...\n")

    result = web_search.invoke({
        "query": "Latest AI developments"
    })

    print(result)

    print("\nTesting URL Scraping...\n")

    result = scrape_url.invoke({
        "url": "https://www.python.org"
    })

    print(result)"""