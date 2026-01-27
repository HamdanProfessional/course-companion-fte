"""
Zero-LLM Compliance Test
Verify that the backend contains NO LLM API calls.
"""

import os
import subprocess
from pathlib import Path


def test_no_llm_imports():
    """
    Test that no LLM libraries are imported in the backend code.
    This is a CRITICAL test for hackathon Phase 1 compliance.
    """
    backend_dir = Path(__file__).parent.parent / "src"

    # Forbidden patterns that indicate LLM usage
    forbidden_patterns = [
        "openai",
        "anthropic",
        "claude",
        "chatgpt",
        "gpt",
        "llm",
        "langchain",
        "langchain_core",
        "langchain_openai",
    ]

    # Search all Python files
    python_files = list(backend_dir.rglob("*.py"))
    violations = []

    for py_file in python_files:
        content = py_file.read_text().lower()

        for pattern in forbidden_patterns:
            # Check for import statements
            if f"import {pattern}" in content or f"from {pattern}" in content:
                violations.append({
                    "file": str(py_file.relative_to(backend_dir)),
                    "pattern": pattern,
                })

    if violations:
        print("[FAIL] ZERO-LLM COMPLIANCE FAILED!")
        print("\nFound LLM-related imports:")
        for v in violations:
            print(f"  - {v['file']}: {v['pattern']}")
        raise AssertionError("Zero-LLM compliance violation: LLM libraries detected")
    else:
        print("[OK] Zero-LLM compliance verified: No LLM imports found")


def test_no_llm_api_calls():
    """
    Test that no LLM API endpoints are called in the backend code.
    """
    backend_dir = Path(__file__).parent.parent / "src"

    # Forbidden API endpoints
    forbidden_endpoints = [
        "api.openai.com",
        "api.anthropic.com",
        "openaibase",
        "anthropicbase",
    ]

    python_files = list(backend_dir.rglob("*.py"))
    violations = []

    for py_file in python_files:
        content = py_file.read_text().lower()

        for endpoint in forbidden_endpoints:
            if endpoint in content:
                violations.append({
                    "file": str(py_file.relative_to(backend_dir)),
                    "endpoint": endpoint,
                })

    if violations:
        print("[FAIL] ZERO-LLM COMPLIANCE FAILED!")
        print("\nFound LLM API calls:")
        for v in violations:
            print(f"  - {v['file']}: {v['endpoint']}")
        raise AssertionError("Zero-LLM compliance violation: LLM API calls detected")
    else:
        print("[OK] Zero-LLM compliance verified: No LLM API calls found")


def test_grep_compliance():
    """
    Use grep to search for LLM-related patterns.
    This mimics the command-line audit that judges will run.

    Note: We exclude "Zero-LLM" in comments/docstrings as those are just documentation,
    not actual LLM usage.
    """
    backend_dir = Path(__file__).parent.parent / "src"

    if not backend_dir.exists():
        print(f"[WARN] Backend directory not found: {backend_dir}")
        return

    try:
        # Run grep command, excluding "Zero-LLM" comments
        result = subprocess.run(
            ['grep', '-ri', 'openai\\|anthropic\\|claude', str(backend_dir)],
            capture_output=True,
            text=True,
        )

        # Filter out "Zero-LLM" documentation (false positives)
        lines = result.stdout.split('\n') if result.stdout else []
        violations = [
            line for line in lines
            if line and 'zero-llm' not in line.lower() and 'zero-backend-llm' not in line.lower()
        ]

        if violations:
            print("[FAIL] ZERO-LLM COMPLIANCE FAILED!")
            print("\nGrep found LLM-related content:")
            for v in violations:
                if v:
                    print(f"  {v}")
            raise AssertionError("Zero-LLM compliance violation: grep found LLM patterns")
        else:
            print("[OK] Zero-LLM compliance verified: Grep found no LLM patterns")

    except FileNotFoundError:
        # grep not available on this system, skip
        print("[WARN] Grep not available, skipping grep test")


if __name__ == "__main__":
    print("Running Zero-LLM Compliance Tests...\n")

    test_no_llm_imports()
    test_no_llm_api_calls()
    test_grep_compliance()

    print("\n" + "=" * 50)
    print("[OK] ALL ZERO-LLM COMPLIANCE TESTS PASSED!")
    print("=" * 50)
    print("\nThe backend is Phase 1 compliant:")
    print("  - No LLM library imports")
    print("  - No LLM API calls")
    print("  - All AI intelligence happens in ChatGPT")
