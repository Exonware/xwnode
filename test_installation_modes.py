#!/usr/bin/env python3
"""
Test script to verify xwnode installation modes work correctly.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
# Add xwsystem src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "xwsystem" / "src"))

def test_default_installation():
    """Test default (lite) installation."""
    print("Testing default (lite) installation...")
    
    try:
        from exonware.xwnode import XWNode, XWQuery, XWFactory
        print("✅ Core xwnode classes imported successfully")
        
        # Test basic functionality
        node = XWNode.from_native({"test": "data"})
        data = node.to_native()
        assert data == {"test": "data"}
        print("✅ Basic XWNode functionality works")
        
        return True
    except Exception as e:
        print(f"❌ Default installation failed: {e}")
        return False

def test_xwsystem_integration():
    """Test xwsystem integration."""
    print("\nTesting xwsystem integration...")
    
    try:
        from exonware.xwsystem import JSONSerializer, YAMLSerializer
        print("✅ xwsystem serializers imported successfully")
        
        # Test serialization
        data = {"test": "data", "number": 42}
        json_serializer = JSONSerializer()
        json_data = json_serializer.dumps(data)
        data_from_json = json_serializer.loads(json_data)
        assert data_from_json == data
        print("✅ JSON serialization works")
        
        return True
    except Exception as e:
        print(f"❌ xwsystem integration failed: {e}")
        return False

def test_lazy_import():
    """Test lazy import functionality."""
    print("\nTesting lazy import functionality...")
    
    try:
        from exonware.xwsystem import xwimport
        print("✅ xwimport imported successfully")
        
        # Test importing a standard library module
        json_module = xwimport("json")
        assert json_module is not None
        print("✅ xwimport works with standard library")
        
        return True
    except Exception as e:
        print(f"❌ Lazy import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing xwnode installation modes...\n")
    
    tests = [
        test_default_installation,
        test_xwsystem_integration,
        test_lazy_import,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! xwnode installation modes work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
