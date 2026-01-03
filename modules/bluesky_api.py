import os
import io
import requests
from PIL import Image
from atproto import Client, models, exceptions
from dotenv import load_dotenv
from modules.url_utils import extract_url_from_text, fetch_page_metadata

load_dotenv()
BSKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BSKY_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

def process_image_for_bluesky(image_url):
    """Downloads and resizes image for Bluesky (<1MB limit)."""
    if not image_url: return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; POSSE-CLI/1.0)'}
        resp = requests.get(image_url, headers=headers, timeout=10)
        if resp.status_code != 200: return None

        img = Image.open(io.BytesIO(resp.content))
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")

        # Resize to max 800px width
        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=80, optimize=True)
        img_byte_arr.seek(0)
        return img_byte_arr.read()
    except Exception:
        return None

def post_to_bluesky(text):
    print("\n--- 🦋 Posting to Bluesky... ---")
    if not all([BSKY_HANDLE, BSKY_PASSWORD]):
        print("❌ Bluesky credentials not found.")
        return False

    try:
        client = Client()
        client.login(BSKY_HANDLE, BSKY_PASSWORD)
        
        # 1. Analyze text for URLs
        match = extract_url_from_text(text)
        facets = []
        embed = None

        if match:
            url = match.group(1)
            start, end = match.span()
            
            # Create clickable link in text
            facets = [
                models.AppBskyRichtextFacet.Main(
                    features=[models.AppBskyRichtextFacet.Link(uri=url)],
                    index=models.AppBskyRichtextFacet.ByteSlice(byte_start=start, byte_end=end),
                )
            ]
            
            # Fetch metadata for the card
            print(f"   🔎 Fetching page data for {url}...")
            meta = fetch_page_metadata(url)
            
            # Upload Image Blob
            thumb_blob = None
            if meta["image_url"]:
                print(f"   🖼️  Processing image...")
                img_bytes = process_image_for_bluesky(meta["image_url"])
                if img_bytes:
                    upload = client.upload_blob(img_bytes)
                    thumb_blob = upload.blob

            # Create Card
            embed = models.AppBskyEmbedExternal.Main(
                external=models.AppBskyEmbedExternal.External(
                    title=meta["title"],
                    description=meta["description"] or "",
                    uri=url,
                    thumb=thumb_blob
                )
            )

        client.send_post(text=text, facets=facets, embed=embed)
        print(f"✅ Successfully posted to Bluesky!")
        return True

    except Exception as e:
        print(f"❌ Error posting to Bluesky: {e}")
        return False