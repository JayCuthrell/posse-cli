# posse-cli

POSSE CLI to send 1 to 300 characters sized messages to Bluesky, GoToSocial, and LinkedIn. Now includes a mobile-friendly web interface!

```bash
$ source ./setup.sh
(my_env) $ python3 ./posse.py --help   
usage: posse.py [-h] [--dry-run] [--no-bsky] [--no-gts] [--no-li] [--only-bsky] [--only-gts]
                [--only-li]
                [message]

POSSE CLI: Post to Bluesky, GoToSocial, and LinkedIn.

positional arguments:
  message      The text content you want to post. Leave empty for interactive mode.

options:
  -h, --help   show this help message and exit
  --dry-run    Print what would be posted without sending.
  --no-bsky    Skip Bluesky
  --no-gts     Skip GoToSocial
  --no-li      Skip LinkedIn
  --only-bsky  Post ONLY to Bluesky
  --only-gts   Post ONLY to GoToSocial
  --only-li    Post ONLY to LinkedIn

```

### **What posse-cli tool does**

**posse-cli** is a tool designed to implement the **POSSE** philosophy (Publish (on) Own Site, Syndicate Elsewhere). It allows you to broadcast short-form updates, links, and thoughts to multiple social networks simultaneously from your terminal or a mobile web app.

It currently supports **Bluesky**, **GoToSocial** (ActivityPub/Mastodon), and **LinkedIn**.

#### **Key Features**

* **Unified Broadcasting:** Send a single message to all three networks with one command.
* **Smart Link Unfurling (Rich Cards):**
* **LinkedIn:** Automatically detects URLs, scrapes OpenGraph metadata (title, description, image), uploads the preview image as a native asset, and creates a rich "Article" share. This bypasses LinkedIn's often-flaky auto-scraper.
* **Bluesky:** Scrapes metadata locally, resizes and compresses the preview image to meet API limits, uploads it as a blob, and attaches it as a native "content card" (embed).
* **GoToSocial:** Posts clean text updates, relying on the ActivityPub server to handle link previews.


* **Interactive Mode:** If no message is provided, it opens a multi-line editor in your terminal, allowing you to compose longer thoughts and preview them before sending.
* **Web & Mobile UI:** A responsive web interface (`web_app.py`) allowing you to post from your iPhone or browser without using the terminal.
* **Safety Checks:** Warns you if your message exceeds the 300-character limit for Bluesky and includes a `--dry-run` mode to preview payloads without actually posting.

---

### **Usage Examples**

#### **1. Command Line Interface (CLI)**

**Interactive Mode (Multi-line input)**

```bash
python3 posse.py

```

**Quick Post (One-liner)**

```bash
python3 posse.py "Just published a new blog post! [https://example.com](https://example.com)"

```

**Post to specific networks only**

```bash
# Post only to Bluesky (useful for threads or testing)
python3 posse.py --only-bsky "Hello Bluesky!"

# Post to everyone EXCEPT LinkedIn
python3 posse.py --no-li "Good morning Fediverse and Bluesky!"

```

**Dry Run (Test without sending)**

```bash
python3 posse.py --dry-run "Checking my link preview logic [https://example.com](https://example.com)"

```

#### **2. Web / Mobile Interface**

You can run the tool as a web server to post from your phone.

**Run Locally:**

```bash
# 1. Install web dependencies
pip install fastapi uvicorn jinja2 python-multipart

# 2. Start the server
uvicorn web_app:app --reload

```

Open `http://127.0.0.1:8000` in your browser.

**Deploy for iPhone / Mobile Access:**

1. Deploy this repository to a cloud host (e.g., **Render**, **Railway**, or a VPS).
2. Set the Start Command to: `uvicorn web_app:app --host 0.0.0.0 --port $PORT`
3. Add your Environment Variables (from `.env`) in the host's dashboard settings.
4. **On iPhone:** Open the deployed URL in Safari, tap **Share**, and select **"Add to Home Screen"**. This installs it as a native-feeling PWA app.

---

### Configuration

1. **Environment Variables:**
Copy the sample configuration file to create your local `.env` file:
```bash
cp .env-sample .env

```


2. **Fill in your credentials:**
Open `.env` and populate the variables:
* **Bluesky:** Generate an App Password in **Settings > App Passwords**. Do not use your main login password.
* **GoToSocial:** Use your instance URL and generate an Access Token with `write:statuses` permissions.
* **LinkedIn:**
* Obtain an Access Token with `w_member_social` scope.
* Find your Author URN (e.g., `urn:li:person:12345`).
* *Tip:* You can use the helper scripts in `tools/` (if available) to fetch these.
