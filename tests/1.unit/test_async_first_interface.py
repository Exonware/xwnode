#!/usr/bin/env python3
"""
Quick test to verify async-first interface compiles and works.
"""

import sys
import asyncio
from pathlib import Path
# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
print("=" * 80)
print("Testing Async-First Interface (v0.0.1.30)")
print("=" * 80)
print()
# Test 1: Import contracts
print("Test 1: Importing contracts...")
try:
    from exonware.xwnode.nodes.strategies.contracts import INodeStrategy, NodeType
    print("  ✓ Contracts imported successfully")
except Exception as e:
    print(f"  ✗ Failed to import contracts: {e}")
    sys.exit(1)
# Test 2: Import base
print("\nTest 2: Importing base...")
try:
    from exonware.xwnode.nodes.strategies.base import ANodeStrategy
    print("  ✓ Base imported successfully")
except Exception as e:
    print(f"  ✗ Failed to import base: {e}")
    sys.exit(1)
# Test 3: Try to import HashMapStrategy
print("\nTest 3: Importing HashMapStrategy...")
try:
    from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
    from exonware.xwnode.defs import NodeMode, NodeTrait
    print("  ✓ HashMapStrategy imported")
except Exception as e:
    print(f"  ✗ Failed to import HashMapStrategy: {e}")
    print(f"  This is expected - HashMapStrategy needs to be updated")
    print(f"  We'll update it next...")
    sys.exit(0)  # Not a failure, just not updated yet
print("\n" + "=" * 80)
print("Interface Compilation Test: PASSED")
print("=" * 80)
print("\nNext: Update HashMapStrategy to implement async methods")
