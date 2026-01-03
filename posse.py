import argparse
import sys
from dotenv import load_dotenv

# Load env before importing modules so they can grab the keys
load_dotenv()

try:
    from modules.linkedin_api import post_to_linkedin
    from modules.gotosocial_api import post_to_gotosocial
    from modules.bluesky_api import post_to_bluesky
except ImportError as e:
    print(f"❌ Implementation Error: {e}")
    print("Ensure you have created the 'modules/__init__.py' file.")
    sys.exit(1)

def get_multiline_input():
    """Captures multi-line input from the user."""
    print("\n📝 Enter your message below.")
    print("   - Type your text (press Return for a new line).")
    print("   - Press Return on an EMPTY line to finish and preview.")
    print("-" * 40)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                # If line is empty, stop reading
                break
            lines.append(line)
        except EOFError:
            break
            
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="POSSE CLI: Post to Bluesky, GoToSocial, and LinkedIn.")
    
    parser.add_argument("message", type=str, nargs='?', help="The text content you want to post. Leave empty for interactive mode.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be posted without sending.")
    
    # Exclude flags
    parser.add_argument("--no-bsky", action="store_true", help="Skip Bluesky")
    parser.add_argument("--no-gts", action="store_true", help="Skip GoToSocial")
    parser.add_argument("--no-li", action="store_true", help="Skip LinkedIn")

    # Exclusive flags (New)
    parser.add_argument("--only-bsky", action="store_true", help="Post ONLY to Bluesky")
    parser.add_argument("--only-gts", action="store_true", help="Post ONLY to GoToSocial")
    parser.add_argument("--only-li", action="store_true", help="Post ONLY to LinkedIn")
    
    args = parser.parse_args()
    
    # 1. Determine Message Source
    message = args.message
    interactive_mode = False

    if not message:
        interactive_mode = True
        message = get_multiline_input()
        if not message.strip():
            print("❌ No message entered. Exiting.")
            sys.exit(0)

    # 2. Determine Targets
    # Default: Enable all unless skipped
    do_bsky = not args.no_bsky
    do_gts = not args.no_gts
    do_li = not args.no_li

    # Override: If ANY --only flag is set, switch to exclusive mode
    # This disables everything except what is explicitly requested
    if args.only_bsky or args.only_gts or args.only_li:
        do_bsky = args.only_bsky
        do_gts = args.only_gts
        do_li = args.only_li

    # 3. Pre-validation
    length = len(message)
    if length > 300 and do_bsky:
        print(f"\n⚠️  NOTE: Your message is {length} chars. Bluesky may fail or truncate.")

    # 4. Preview and Confirmation
    if interactive_mode or args.dry_run:
        print("\n" + "="*20 + " PREVIEW " + "="*20)
        print(message)
        print("="*49 + "\n")
        
        # Show target status
        print("Targets:")
        print(f"  [ {'x' if do_bsky else ' '} ] Bluesky")
        print(f"  [ {'x' if do_gts else ' '} ] GoToSocial")
        print(f"  [ {'x' if do_li else ' '} ] LinkedIn")
        print("-" * 20)

    if args.dry_run:
        print("[DRY RUN] Exiting without posting.")
        return

    if interactive_mode:
        confirm = input(f"🚀 Ready to post? (y/N): ").lower()
        if confirm != 'y':
            print("❌ Operation cancelled.")
            sys.exit(0)

    # 5. Execute
    print("\n--- Sending ---")
    
    if do_bsky:
        post_to_bluesky(message)
    else:
        print("zzz Skipped Bluesky")
    
    if do_gts:
        post_to_gotosocial(message)
    else:
        print("zzz Skipped GoToSocial")
        
    if do_li:
        post_to_linkedin(message)
    else:
        print("zzz Skipped LinkedIn")

    print("\n✨ Operations complete.")

if __name__ == "__main__":
    main()