import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.environ["SERPER_API_KEY"]

def web_search(query: str):

    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "q": query
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    
    
    data = response.json()

    results = []

    for item in data.get("organic", [])[:5]:

        results.append(
            {
                "title": item["title"],
                "url": item["link"],
                "snippet": item["snippet"]
            }
        )

    return results

def web_fetch(url):
    try:
        

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return {
            "url": url,
            "content": response.text[:5000]
        }

    except Exception as e:

        return {
            "error": str(e)
        }
