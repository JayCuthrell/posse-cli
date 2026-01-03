# posse-cli

POSSE CLI to send  1 to 300 characters sized messages to Bluesky, GoToSocial, and LinkedIn.

```bash
$ source ./setup
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

**posse-cli** is a command-line interface tool designed to implement the **POSSE** philosophy (Publish (on) Own Site, Syndicate Elsewhere). It allows you to broadcast short-form updates, links, and thoughts to multiple social networks simultaneously from your terminal.

It currently supports **Bluesky**, **GoToSocial** (ActivityPub/Mastodon), and **LinkedIn**.

#### **Key Features**

* **Unified Broadcasting:** Send a single message to all three networks with one command.
* **Smart Link Unfurling (Rich Cards):**
* **LinkedIn:** Automatically detects URLs, scrapes OpenGraph metadata (title, description, image), uploads the preview image as a native asset, and creates a rich "Article" share. This bypasses LinkedIn's often-flaky auto-scraper.
* **Bluesky:** Scrapes metadata locally, resizes and compresses the preview image to meet API limits, uploads it as a blob, and attaches it as a native "content card" (embed).
* **GoToSocial:** Posts clean text updates, relying on the ActivityPub server to handle link previews.

* **Interactive Mode:** If no message is provided, it opens a multi-line editor in your terminal, allowing you to compose longer thoughts and preview them before sending.
* **Selective Posting:** Use flags to target specific networks (e.g., `--only-bsky` or `--no-li`) for testing or platform-specific updates.
* **Safety Checks:** Warns you if your message exceeds the 300-character limit for Bluesky and includes a `--dry-run` mode to preview payloads without actually posting.

#### **Usage Examples**

**Interactive Mode (Multi-line input)**

```bash
python3 posse.py

```

**Quick Post (One-liner)**

```bash
python3 posse.py "Just published a new blog post! https://example.com"

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
python3 posse.py --dry-run "Checking my link preview logic https://example.com"

```
