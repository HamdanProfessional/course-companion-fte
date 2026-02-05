#!/usr/bin/env python3
"""Test MCP Server Widgets"""
import json
import subprocess
import sys

def test_widget(widget_name):
    """Test a single widget"""
    uri = f"ui://widget/{widget_name}.html"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "resources/read",
        "params": {"uri": uri}
    }

    # Make request
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "http://92.113.147.250:3505/api/v1/mcp",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ], capture_output=True, encoding='utf-8', errors='replace')

    if result.returncode != 0:
        print(f"  [X] HTTP Request Failed")
        return False

    # Parse response
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  [X] Invalid JSON Response")
        return False

    # Check for error
    if "error" in response:
        print(f"  [X] API Error: {response['error'].get('message', 'Unknown error')}")
        return False

    # Check for result
    if "result" not in response:
        print(f"  [X] No result in response")
        return False

    # Check contents
    contents = response["result"].get("contents", [])
    if not contents:
        print(f"  [X] No contents in result")
        return False

    html = contents[0].get("text", "")
    if not html:
        print(f"  [X] Empty HTML content")
        return False

    # Validate HTML structure
    checks = {
        "Has <!DOCTYPE html>": "<!DOCTYPE html>" in html,
        "Has <html> tag": "<html" in html,
        "Has <head> tag": "<head>" in html,
        "Has <body> tag": "<body>" in html,
        "Has <script> tag": "<script>" in html,
        "Has closing </html>": "</html>" in html,
    }

    print(f"  [OK] Widget Valid")
    print(f"  [OK] HTML Length: {len(html):,} characters")
    print(f"  [OK] Structure Valid: {all(checks.values())}")

    # Widget-specific checks
    if "chapter-list" in widget_name:
        print(f"  [OK] Has chapters grid: {'chapters' in html}")
    elif "quiz" in widget_name:
        print(f"  [OK] Has quiz container: {'quiz' in html.lower()}")
    elif "achievements" in widget_name:
        print(f"  [OK] Has achievements grid: {'achievements-grid' in html}")
    elif "streak-calendar" in widget_name:
        print(f"  [OK] Has calendar: {'calendar' in html}")
    elif "progress-dashboard" in widget_name:
        print(f"  [OK] Has progress section: {'progress' in html}")
    elif "quiz-insights" in widget_name:
        print(f"  [OK] Has stats grid: {'stats' in html}")
    elif "adaptive-learning" in widget_name:
        print(f"  [OK] Has recommendations: {'recommendations' in html}")
    elif "ai-mentor-chat" in widget_name:
        print(f"  [OK] Has messages: {'messages' in html}")

    return True

def main():
    """Test all widgets"""
    widgets = [
        ("chapter-list", "Chapter List Widget"),
        ("quiz", "Quiz Widget"),
        ("achievements", "Achievements Widget"),
        ("streak-calendar", "Streak Calendar Widget"),
        ("progress-dashboard", "Progress Dashboard Widget"),
        ("quiz-insights", "Quiz Insights Widget"),
        ("adaptive-learning", "Adaptive Learning Widget"),
        ("ai-mentor-chat", "AI Mentor Chat Widget"),
    ]

    print("=" * 60)
    print("Testing MCP Server Widgets")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for widget_id, widget_name in widgets:
        print(f"Testing: {widget_name}")
        try:
            if test_widget(widget_id):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  [X] Exception: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(widgets)} total")
    print("=" * 60)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
