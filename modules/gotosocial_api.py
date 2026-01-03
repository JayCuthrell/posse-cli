import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOTOSOCIAL_INSTANCE_URL = os.getenv("GOTOSOCIAL_INSTANCE_URL")
GOTOSOCIAL_ACCESS_TOKEN = os.getenv("GOTOSOCIAL_ACCESS_TOKEN")

def post_to_gotosocial(text):
    print("\n--- 🐘 Posting to GoToSocial... ---")
    if not all([GOTOSOCIAL_INSTANCE_URL, GOTOSOCIAL_ACCESS_TOKEN]):
        print("❌ GoToSocial credentials not found in .env.")
        return False

    headers = {
        "Authorization": f"Bearer {GOTOSOCIAL_ACCESS_TOKEN}", 
        "Content-Type": "application/json"
    }
    # Ensure URL doesn't have a trailing slash for cleanliness
    base_url = GOTOSOCIAL_INSTANCE_URL.rstrip('/')
    post_url = f"{base_url}/api/v1/statuses"
    
    post_data = {
        "status": text, 
        "visibility": "public"
    }

    try:
        response = requests.post(post_url, headers=headers, json=post_data)
        response.raise_for_status()
        print("✅ Successfully posted to GoToSocial!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error posting to GoToSocial: {e}")
        return False