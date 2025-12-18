from fastapi import APIRouter
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import List, Dict
import time

router = APIRouter(prefix="/news", tags=["News"])

# In-memory cache to avoid rate limiting
NEWS_CACHE = {
    "finance": {"data": [], "timestamp": 0},
    "growth": {"data": [], "timestamp": 0}
}
CACHE_DURATION = 900  # 15 minutes

def fetch_rss_feed(topic_query: str):
    try:
        url = f"https://news.google.com/rss/search?q={topic_query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        items = []
        
        for item in root.findall(".//item")[:10]: # Limit to 10 items
            title = item.find("title").text if item.find("title") is not None else "No Title"
            link = item.find("link").text if item.find("link") is not None else "#"
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            
            # Clean description
            raw_desc = item.find("description").text if item.find("description") is not None else ""
            summary = ""
            if raw_desc:
                soup = BeautifulSoup(raw_desc, "html.parser")
                summary = soup.get_text()
            
            items.append({
                "title": title,
                "link": link,
                "summary": summary,
                "date": pub_date
            })
            
        return items
    except Exception as e:
        print(f"Error fetching news for {topic_query}: {e}")
        return []

@router.get("/", response_model=Dict[str, List[Dict]])
def get_live_news():
    current_time = time.time()
    
    # Update Finance Cache
    if current_time - NEWS_CACHE["finance"]["timestamp"] > CACHE_DURATION:
        NEWS_CACHE["finance"]["data"] = fetch_rss_feed("finance+investing+personal+finance")
        NEWS_CACHE["finance"]["timestamp"] = current_time
        
    # Update Growth Cache
    if current_time - NEWS_CACHE["growth"]["timestamp"] > CACHE_DURATION:
        NEWS_CACHE["growth"]["data"] = fetch_rss_feed("personal+development+productivity+mindset")
        NEWS_CACHE["growth"]["timestamp"] = current_time
        
    return {
        "finance": NEWS_CACHE["finance"]["data"],
        "growth": NEWS_CACHE["growth"]["data"]
    }
