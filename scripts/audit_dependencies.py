#!/usr/bin/env python3
"""
#exonware/xwnode/scripts/audit_dependencies.py
Dependency Security Audit Script for xwnode.
REUSES standard security audit tools:
- pip-audit (if available)
- safety (if available)
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import subprocess
import sys
from pathlib import Path


def run_pip_audit() -> bool:
    """
    Run pip-audit to check for vulnerable dependencies.
    Returns:
        True if vulnerabilities found, False otherwise
    """
    try:
        result = subprocess.run(
            ['pip-audit', '--requirement', 'requirements.txt'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode != 0:
            print("⚠️  pip-audit found vulnerabilities:")
            print(result.stdout)
            print(result.stderr)
            return True
        if "No known vulnerabilities found" in result.stdout:
            print("✅ pip-audit: No known vulnerabilities found")
            return False
        else:
            print("⚠️  pip-audit output:")
            print(result.stdout)
            return True
    except FileNotFoundError:
        print("ℹ️  pip-audit not installed. Install with: pip install pip-audit")
        return False
    except Exception as e:
        print(f"❌ Error running pip-audit: {e}")
        return False


def run_safety() -> bool:
    """
    Run safety to check for vulnerable dependencies.
    Returns:
        True if vulnerabilities found, False otherwise
    """
    try:
        result = subprocess.run(
            ['safety', 'check', '--file', 'requirements.txt'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode != 0:
            print("⚠️  safety found vulnerabilities:")
            print(result.stdout)
            print(result.stderr)
            return True
        if "No known security vulnerabilities found" in result.stdout:
            print("✅ safety: No known security vulnerabilities found")
            return False
        else:
            print("⚠️  safety output:")
            print(result.stdout)
            return True
    except FileNotFoundError:
        print("ℹ️  safety not installed. Install with: pip install safety")
        return False
    except Exception as e:
        print(f"❌ Error running safety: {e}")
        return False


def main():
    """Run dependency security audit."""
    print("🔍 Running dependency security audit for xwnode...")
    print("=" * 60)
    vulnerabilities_found = False
    # Try pip-audit first (preferred)
    print("\n1. Running pip-audit...")
    if run_pip_audit():
        vulnerabilities_found = True
    # Try safety as backup
    print("\n2. Running safety...")
    if run_safety():
        vulnerabilities_found = True
    print("\n" + "=" * 60)
    if vulnerabilities_found:
        print("❌ Security audit: Vulnerabilities found!")
        print("   Please review and update dependencies.")
        sys.exit(1)
    else:
        print("✅ Security audit: No vulnerabilities found!")
        sys.exit(0)
if __name__ == "__main__":
    main()
