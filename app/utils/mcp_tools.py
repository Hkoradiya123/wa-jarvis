import asyncio
from duckduckgo_search import DDGS
import trafilatura
from app.utils.logger import get_logger

logger = get_logger("mcp_tools")

async def web_search(query: str, max_results: int = 5):
    """
    Performs a web search using DuckDuckGo.
    """
    logger.info(f"Performing web search for: {query}")
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []

async def fetch_page(url: str):
    """
    Fetches and extracts content from a URL.
    """
    logger.info(f"Fetching page: {url}")
    try:
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract(downloaded)
        return content if content else "Could not extract content."
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return f"Error fetching page: {e}"

import time

SEARCH_CACHE = {}
CACHE_TTL_SECONDS = 900 # 15 minutes

async def search_and_summarize(query: str):
    """
    Combines search and content fetching for a comprehensive answer.
    """
    normalized_query = query.strip().lower()
    now = time.time()
    
    if normalized_query in SEARCH_CACHE:
        val, expiry = SEARCH_CACHE[normalized_query]
        if now < expiry:
            logger.info(f"Cache HIT for query: '{normalized_query}'")
            return val
        else:
            logger.info(f"Cache EXPIRED for query: '{normalized_query}'")
            del SEARCH_CACHE[normalized_query]
            
    logger.info(f"Cache MISS for query: '{normalized_query}'")
    results = await web_search(query)
    if not results:
        return "No search results found."
    
    summary = "SEARCH RESULTS:\n\n"
    for i, res in enumerate(results):
        summary += f"{i+1}. {res['title']}\nURL: {res['href']}\nSnippet: {res['body']}\n\n"
    
    SEARCH_CACHE[normalized_query] = (summary, now + CACHE_TTL_SECONDS)
    return summary

