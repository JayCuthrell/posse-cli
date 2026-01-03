import re
import requests
from bs4 import BeautifulSoup

def extract_url_from_text(text):
    """Finds the first http/https URL in the text."""
    url_pattern = re.compile(r'(https?://\S+)')
    match = url_pattern.search(text)
    return match

def fetch_page_metadata(url):
    """
    Scrapes a URL for OpenGraph title, description, and image.
    Returns a dict with 'title', 'description', 'image_url'.
    """
    data = {
        "title": None,
        "description": None,
        "image_url": None
    }
    
    try:
        # Use a real-looking User-Agent to avoid blocks
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; POSSE-CLI/1.0)'}
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            # FORCE UTF-8 encoding to fix emoji rendering issues
            r.encoding = 'utf-8'
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # --- Title ---
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                data["title"] = og_title["content"]
            elif soup.title:
                data["title"] = soup.title.string

            # --- Description ---
            og_desc = soup.find("meta", property="og:description")
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if og_desc and og_desc.get("content"):
                data["description"] = og_desc["content"]
            elif meta_desc and meta_desc.get("content"):
                data["description"] = meta_desc["content"]

            # --- Image ---
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                data["image_url"] = og_image["content"]
                
    except Exception as e:
        print(f"   ⚠️  Metadata fetch warning: {e}")

    # Fallbacks if scraping failed but we have a URL
    if not data["title"]:
        data["title"] = url
        
    return data