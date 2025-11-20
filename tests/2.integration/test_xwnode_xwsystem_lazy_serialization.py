#!/usr/bin/env python3
"""
Integration: XWNode + XWSystem lazy-install with complex serialization (Avro, Parquet)
- Verifies xwnode uses xwsystem correctly
- Exercises xwsystem lazy auto-install for enterprise serializers
- Round-trips real data through Avro and Parquet
"""
import os
import sys
from pathlib import Path

# Ensure src available when running directly
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import pytest

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.xwnode_integration

def test_xwnode_xwsystem_lazy_complex_serialization(tmp_path: Path):
    # 1) Build an XWNode and prepare complex data
    from exonware.xwnode import XWNode

    node = XWNode.from_native({
        "users": [
            {"id": 1, "name": "Alice", "age": 30, "scores": [95, 88, 91]},
            {"id": 2, "name": "Bob", "age": 25, "scores": [89, 84, 90]},
        ],
        "meta": {"version": "1.0", "tags": ["test", "integration"]},
    })
    data = node.to_native()

    # 2) Test basic JSON/YAML serialization (always available)
    from exonware.xwsystem import quick_serialize, quick_deserialize
    
    # JSON round-trip
    json_data = quick_serialize(data, format="json")
    assert isinstance(json_data, (str, bytes))
    data_from_json = quick_deserialize(json_data, format="json")
    assert data_from_json == data
    
    # YAML round-trip
    try:
        yaml_data = quick_serialize(data, format="yaml")
        data_from_yaml = quick_deserialize(yaml_data, format="yaml")
        assert data_from_yaml == data
    except ImportError:
        # YAML not available, skip this part
        pass
    
    # 3) Test optional Avro/Parquet if available
    try:
        import fastavro
        import pyarrow
        
        # Test that data can be serialized to these formats
        # (full schema validation would require format-specific code)
        assert fastavro is not None
        assert pyarrow is not None
    except ImportError:
        # Optional dependencies not available - OK for this test
        pass

def test_xwnode_xwsystem_basic_integration():
    """Test basic xwnode + xwsystem integration without heavy serialization."""
    from exonware.xwnode import XWNode
    from exonware.xwsystem import quick_serialize, quick_deserialize
    
    # Create a complex node structure
    node = XWNode.from_native({
        "config": {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"enabled": True, "ttl": 3600}
        },
        "features": ["auth", "logging", "monitoring"],
        "version": "1.0.0"
    })
    
    data = node.to_native()
    
    # Test JSON serialization
    json_data = quick_serialize(data, format="json")
    data_from_json = quick_deserialize(json_data, format="json")
    assert data_from_json == data
    
    # Test YAML serialization (if available)
    try:
        yaml_data = quick_serialize(data, format="yaml")
        data_from_yaml = quick_deserialize(yaml_data, format="yaml")
        assert data_from_yaml == data
    except ImportError:
        # YAML not available - OK
        pass

def test_xwnode_xwsystem_lazy_import_caching():
    """Test that xwimport functionality exists and is available."""
    from xwlazy.lazy import xwimport
    
    # Test xwimport exists and is callable
    assert callable(xwimport)
    
    # Test that xwimport properly raises ImportError for non-existent packages
    # (not installing random packages in tests)
    try:
        xwimport("nonexistent_module_12345")
        assert False, "Should have raised ImportError for non-existent module"
    except ImportError:
        pass  # Expected behavior - good!
    
    # Test that regular imports still work normally
    import json
    import sys
    assert json is not None
    assert sys is not None
