import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from huggingface_hub import InferenceClient

router = APIRouter(prefix="/news", tags=["News"])

# In-memory cache to avoid rate limiting
NEWS_CACHE = {
    "finance": {"data": [], "timestamp": 0},
    "growth": {"data": [], "timestamp": 0}
}
CACHE_DURATION = 900  # 15 minutes

HF_TOKEN = os.getenv("HF_TOKEN") # Add this to Railway variables
# Initialize client (uses public API if no token, subject to lower limits)
hf_client = InferenceClient(token=HF_TOKEN)

def analyze_relevance(text: str) -> bool:
    """
    Uses AI to determine if text is 'educating/inspiring' vs 'generic/noise'.
    Returns True if relevant.
    """
    try:
        if not text: return False
        
        # Zero-Shot Classification: "Is this helpful personal development advice?"
        # Using a small, fast model for sentiment as proxy for now to save latency
        # Model: distilbert-base-uncased-finetuned-sst-2-english
        # >0.5 Positive = Keep.
        
        response = hf_client.text_classification(
            text, 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        # Response format: [{'label': 'POSITIVE', 'score': 0.9}, ...]
        if isinstance(response, list):
             top = response[0]
             # Keep if Positive and confident, or if it's purely informational
             if top['label'] == 'POSITIVE' and top['score'] > 0.7:
                 return True
        return False
    except Exception as e:
        print(f"AI Filter Error: {e}")
        return True # Fallback: keep it

def fetch_rss_feed(topic_query: str, use_ai_filter: bool = False):
    try:
        url = f"https://news.google.com/rss/search?q={topic_query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        items = []
        
        # Fetch Top 15, then Filter down to 5-10
        candidates = root.findall(".//item")[:15]
        
        for item in candidates:
            title = item.find("title").text if item.find("title") is not None else "No Title"
            link = item.find("link").text if item.find("link") is not None else "#"
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            
            # Clean description
            raw_desc = item.find("description").text if item.find("description") is not None else ""
            summary = ""
            if raw_desc:
                soup = BeautifulSoup(raw_desc, "html.parser")
                summary = soup.get_text()
            
            # AI FILTERING
            if use_ai_filter:
                # Combine title + summary for context
                context = f"{title}. {summary}"
                if not analyze_relevance(context):
                    continue # Skip this item
            
            items.append({
                "title": title,
                "link": link,
                "summary": summary,
                "date": pub_date
            })
            
            if len(items) >= 8: break # Cap at 8 items
            
        return items
    except Exception as e:
        print(f"Error fetching news for {topic_query}: {e}")
        return []

@router.get("/", response_model=Dict[str, List[Dict]])
def get_live_news():
    current_time = time.time()
    
    # Update Finance Cache (No AI filter, market news is often negative but important)
    if current_time - NEWS_CACHE["finance"]["timestamp"] > CACHE_DURATION:
        NEWS_CACHE["finance"]["data"] = fetch_rss_feed("finance+investing+stock+market", use_ai_filter=False)
        NEWS_CACHE["finance"]["timestamp"] = current_time
        
    # Update Growth Cache (Use AI to filter for Positive/Helpful content)
    if current_time - NEWS_CACHE["growth"]["timestamp"] > CACHE_DURATION:
        NEWS_CACHE["growth"]["data"] = fetch_rss_feed("personal+development+productivity+mindset+life+hacks", use_ai_filter=True)
        NEWS_CACHE["growth"]["timestamp"] = current_time
        
    return {
        "finance": NEWS_CACHE["finance"]["data"],
        "growth": NEWS_CACHE["growth"]["data"]
    }
