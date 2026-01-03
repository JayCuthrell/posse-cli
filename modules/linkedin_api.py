import os
import requests
from dotenv import load_dotenv
from modules.url_utils import extract_url_from_text, fetch_page_metadata

load_dotenv()
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR = os.getenv("LINKEDIN_AUTHOR")

def register_upload(author_urn):
    """Register an image upload with LinkedIn."""
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"   ⚠️  LinkedIn upload registration failed: {resp.text}")
            return None, None
        
        data = resp.json()
        upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_urn = data['value']['asset']
        return upload_url, asset_urn
    except Exception as e:
        print(f"   ⚠️  Registration exception: {e}")
        return None, None

def upload_image(upload_url, image_url):
    """Download image from source and upload to LinkedIn."""
    try:
        # Download with a browser-like UA to avoid 403s
        img_resp = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if img_resp.status_code != 200:
            return False
        
        # Upload to LinkedIn
        headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
        put_resp = requests.put(upload_url, headers=headers, data=img_resp.content)
        return put_resp.status_code in [200, 201]
    except Exception as e:
        print(f"   ⚠️  Image upload exception: {e}")
        return False

def _send_post_request(post_data):
    """Helper to send the final POST request."""
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "x-li-format": "json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    return requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_data)

def post_to_linkedin(text):
    print("\n--- 🔗 Posting to LinkedIn... ---")
    if not all([LINKEDIN_ACCESS_TOKEN, LINKEDIN_AUTHOR]):
        print("❌ LinkedIn credentials not found.")
        return False

    # 1. Analyze text for URL
    match = extract_url_from_text(text)
    
    strategies = []
    
    if match:
        url = match.group(1)
        print(f"   🔎 Fetching page data for {url}...")
        meta = fetch_page_metadata(url)
        
        # Prepare Asset for Strategy A (Custom Image)
        asset_urn = None
        if meta["image_url"]:
            print(f"   🖼️  Uploading thumbnail to LinkedIn...")
            upload_url, registered_urn = register_upload(LINKEDIN_AUTHOR)
            if upload_url and upload_image(upload_url, meta["image_url"]):
                asset_urn = registered_urn

        # Strategy A: Article + Custom Image (Preferred)
        if asset_urn:
            strategies.append({
                "type": "ARTICLE_WITH_IMAGE",
                "content": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": url,
                        # FIX: Use 'thumbnails' array instead of direct 'media' field
                        "thumbnails": [{"media": asset_urn}], 
                        "title": {"text": (meta["title"] or url)[:200]},
                        "description": {"text": (meta["description"] or "Shared via POSSE CLI")[:250]}
                    }]
                }
            })

        # Strategy B: Article (URL Only - Let LinkedIn scrape)
        strategies.append({
            "type": "ARTICLE_URL_ONLY",
            "content": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "ARTICLE",
                "media": [{
                    "status": "READY",
                    "originalUrl": url,
                    "title": {"text": (meta["title"] or url)[:200]},
                    "description": {"text": (meta["description"] or "Shared via POSSE CLI")[:250]}
                }]
            }
        })

    # Strategy C: Text Only (Fallback)
    strategies.append({
        "type": "TEXT_ONLY",
        "content": {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "NONE"
        }
    })

    # 2. Execute Strategies
    for strategy in strategies:
        print(f"   🚀 Attempting strategy: {strategy['type']}...")
        post_data = {
            "author": f"{LINKEDIN_AUTHOR}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {"com.linkedin.ugc.ShareContent": strategy['content']},
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        try:
            response = _send_post_request(post_data)
            response.raise_for_status()
            print("✅ Successfully posted to LinkedIn!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"      ❌ Failed: {e}")
            if e.response is not None:
                # This prints the specific reason LinkedIn rejected it
                print(f"      🔍 LinkedIn Error Detail: {e.response.text}")
            
            if strategy == strategies[-1]:
                print("❌ All posting strategies failed.")
                return False
            else:
                print("      🔄 Falling back to next strategy...")

    return False