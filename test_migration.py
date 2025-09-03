#!/usr/bin/env python3
"""
Test script to verify the xNode migration is working.
"""

import sys
import os

# Ensure we use the local version by inserting at the beginning
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Remove any existing exonware modules to avoid conflicts
modules_to_remove = [key for key in sys.modules.keys() if key.startswith('exonware')]
for module in modules_to_remove:
    del sys.modules[module]

try:
    print("Testing xNode migration...")
    
    # Test basic import
    from exonware.xnode import xNode, xNodeFactory
    print("✓ Import successful")
    
    # Test creating node from dict
    data = {'name': 'Alice', 'age': 30, 'active': True}
    node = xNode.from_native(data)
    print("✓ Node created from dict")
    
    # Test type checking
    assert node.is_dict
    assert not node.is_list
    assert not node.is_leaf
    print("✓ Type checking works")
    
    # Test value access
    name_node = node.get('name')
    assert name_node.value == 'Alice'
    print("✓ Value access works")
    
    # Test bracket notation
    age_value = node['age'].value
    assert age_value == 30
    print("✓ Bracket notation works")
    
    # Test to_native
    native = node.to_native()
    assert native == data
    print("✓ to_native works")
    
    # Test factory
    empty = xNodeFactory.empty()
    assert len(empty) == 0
    print("✓ Factory methods work")
    
    print("\n🎉 All tests passed! Migration successful!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
