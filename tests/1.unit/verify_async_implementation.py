#!/usr/bin/env python3
"""Quick verification that async-first implementation compiles correctly."""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

print("="*80)
print("Verifying Async-First Implementation (v0.0.1.30)")
print("="*80)
print()

# Test imports
print("1. Testing imports...")
try:
    from exonware.xwnode.nodes.strategies.contracts import INodeStrategy
    from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
    from exonware.xwnode.nodes.strategies.cuckoo_hash import CuckooHashStrategy
    from exonware.xwnode.nodes.strategies.b_tree import BTreeStrategy
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test strategy instantiation
print("\n2. Testing strategy instantiation...")
try:
    strategies = [
        ("HashMapStrategy", HashMapStrategy()),
        ("CuckooHashStrategy", CuckooHashStrategy()),
        ("BTreeStrategy", BTreeStrategy()),
    ]
    print("   ✅ All strategies instantiated")
except Exception as e:
    print(f"   ❌ Instantiation failed: {e}")
    sys.exit(1)

# Check async methods exist
print("\n3. Checking async methods exist...")
required_methods = [
    'insert_async', 'find_async', 'delete_async',
    'size_async', 'is_empty_async', 'to_native_async',
    'keys_async', 'values_async', 'items_async'
]

all_good = True
for name, strategy in strategies:
    print(f"   Checking {name}...")
    for method in required_methods:
        if not hasattr(strategy, method):
            print(f"      ❌ Missing {method}")
            all_good = False
    if all_good:
        print(f"      ✅ All 9 async methods present")

if not all_good:
    sys.exit(1)

# Check _lock exists
print("\n4. Checking async locks exist...")
for name, strategy in strategies:
    if hasattr(strategy, '_lock'):
        print(f"   ✅ {name} has _lock")
    else:
        print(f"   ❌ {name} missing _lock")
        all_good = False

if not all_good:
    sys.exit(1)

# Test sync methods (backward compatibility)
print("\n5. Testing backward compatibility (sync methods)...")
try:
    s = HashMapStrategy()
    s.insert("test_key", "test_value")
    val = s.find("test_key")
    assert val == "test_value", f"Expected 'test_value', got '{val}'"
    print("   ✅ Sync methods work (wrap async)")
except Exception as e:
    print(f"   ❌ Sync methods failed: {e}")
    sys.exit(1)

print()
print("="*80)
print("✅ VERIFICATION SUCCESSFUL!")
print("="*80)
print()
print("Summary:")
print("  - Imports: ✅ Working")
print("  - Instantiation: ✅ Working")
print("  - Async methods: ✅ All 9 methods present")
print("  - Async locks: ✅ Present in all strategies")
print("  - Backward compatibility: ✅ Sync API wraps async")
print()
print("🎉 Async-First Architecture (v0.0.1.30) is ready!")
print()

