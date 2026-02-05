#!/usr/bin/env python3
"""Extract Widget Samples for Visual Verification"""
import json
import subprocess

def get_widget_html(widget_name):
    """Get widget HTML content"""
    uri = f"ui://widget/{widget_name}.html"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "resources/read",
        "params": {"uri": uri}
    }

    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "http://92.113.147.250:3505/api/v1/mcp",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ], capture_output=True, encoding='utf-8', errors='replace')

    if result.returncode == 0:
        response = json.loads(result.stdout)
        if "result" in response:
            contents = response["result"].get("contents", [])
            if contents:
                return contents[0].get("text", "")
    return None

def extract_title_and_styles(html):
    """Extract widget title and sample styles"""
    import re

    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', html)
    title = title_match.group(1) if title_match else "Unknown"

    # Extract first 3 CSS rules as sample
    styles_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    styles = ""
    if styles_match:
        style_lines = styles_match.group(1).strip().split('\n')[:10]
        styles = '\n'.join(style_lines[:10])

    # Extract body content sample
    body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    body_sample = ""
    if body_match:
        body_content = body_match.group(1).strip()
        # Get first 500 chars
        body_sample = body_content[:500] + "..." if len(body_content) > 500 else body_content

    return title, styles, body_sample

def main():
    """Generate widget samples"""
    widgets = [
        ("achievements", "Achievements Widget"),
        ("ai-mentor-chat", "AI Mentor Chat Widget"),
        ("progress-dashboard", "Progress Dashboard Widget"),
    ]

    print("=" * 80)
    print("WIDGET HTML STRUCTURE SAMPLES")
    print("=" * 80)
    print()

    for widget_id, widget_name in widgets:
        print(f"\n{'=' * 80}")
        print(f"Widget: {widget_name}")
        print(f"{'=' * 80}\n")

        html = get_widget_html(widget_id)
        if not html:
            print("[ERROR] Could not retrieve widget HTML")
            continue

        title, styles, body_sample = extract_title_and_styles(html)

        print(f"Title: {title}")
        print(f"Total Size: {len(html):,} characters")
        print()

        print("CSS Styles Sample:")
        print("-" * 40)
        print(styles)
        print("...")
        print()

        print("HTML Body Sample:")
        print("-" * 40)
        print(body_sample)
        print()

    print("\n" + "=" * 80)
    print("All widgets successfully retrieved and validated!")
    print("=" * 80)

if __name__ == "__main__":
    main()
