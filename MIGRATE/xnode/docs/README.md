# xNode Library v0.1.0

A lightweight, high-performance library for representing and navigating hierarchical data.

## 🚀 Features

- **Immutable Interface**: Clean, immutable-style facade for safe data manipulation
- **Performance Modes**: Multiple optimization strategies (FAST, OPTIMIZED, ADAPTIVE, DUAL_ADAPTIVE)
- **Thread Safety**: Configurable thread-safe operations with locking
- **Memory Efficient**: Object pooling, caching, and weak references
- **Security**: Path traversal protection and resource limits
- **Monitoring**: Built-in performance metrics and cache statistics

## 📦 Installation

```bash
pip install xnode
```

## 🎯 Quick Start

```python
from xnode import xNode

# Create from Python objects with performance modes
data = xNode.dual_adaptive({
    'users': [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25}
    ]
})

# Navigate using paths
alice_name = data.find('users.0.name').value  # 'Alice'

# Use bracket notation
bob_age = data['users'][1]['age'].value  # 25
```

## 🔧 Performance Modes

### Fast Mode
Optimized for speed with larger caches and eager loading:
```python
data = xNode.fast({'large': 'dataset'})
```

### Optimized Mode
Memory-efficient with smaller caches and lazy loading:
```python
data = xNode.optimized({'large': 'dataset'})
```

### Adaptive Mode
Runtime adaptation based on performance monitoring:
```python
data = xNode.adaptive({'large': 'dataset'})
```

### Dual Adaptive Mode
Smart dual-phase optimization:
```python
data = xNode.dual_adaptive({'large': 'dataset'})
```

## ⚙️ Configuration

### Environment Variables
```bash
export XNODE_PERFORMANCE_MODE=fast
export XNODE_PATH_CACHE_SIZE=2048
export XNODE_ENABLE_THREAD_SAFETY=false
```

### Programmatic Configuration
```python
from xnode import set_performance_mode, PerformanceMode

# Set performance mode
set_performance_mode(PerformanceMode.FAST)

# Get current configuration
from xnode import get_config
config = get_config()
print(config.get_active_profile())
```

## 📚 API Reference

### Core Classes

#### xNode
The primary interface for working with hierarchical data.

**Methods:**
- `find(path: str) -> xNode`: Navigate to a node by path
- `get(path: str, default: Any = None) -> Any`: Get value with default
- `set(path: str, value: Any) -> xNode`: Set value at path
- `delete(path: str) -> xNode`: Delete node at path
- `to_native() -> Any`: Convert to native Python object
- `to_json() -> str`: Convert to JSON string

#### xNodeQuery
Advanced querying capabilities for complex data operations.

#### xNodeFactory
Factory for creating xNode instances with specific configurations.

### Performance Monitoring

```python
from xnode import get_metrics, get_pool_stats

# Get performance metrics
metrics = get_metrics()
print(f"Cache hit rate: {metrics.cache_hit_rate}")

# Get object pool statistics
pool_stats = get_pool_stats()
print(f"Pool efficiency: {pool_stats.efficiency}")
```

## 🛡️ Security Features

- **Path Traversal Protection**: Prevents `..` attacks
- **Resource Limits**: Configurable depth, node count, and path length limits
- **Untrusted Data Validation**: Integration with validation systems
- **Thread Safety**: Configurable locking mechanisms

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest src/xlib/xnode/tests/

# Run performance tests
python src/xlib/xnode/tests/test_runner.py

# Run specific test categories
python src/xlib/xnode/tests/test_runner.py --category=basics
```

## ⚡ Performance Tuning Guide

### For Small Datasets (< 1MB)
```python
# Use fast mode for maximum speed
data = xNode.fast(your_data)
```

### For Large Datasets (> 10MB)
```python
# Use optimized mode for memory efficiency
data = xNode.optimized(your_data)
```

### For Dynamic Workloads
```python
# Use adaptive mode for automatic optimization
data = xNode.adaptive(your_data)
```

### Custom Configuration
```python
from xnode import xNodeConfig, PerformanceMode

config = xNodeConfig(
    performance_mode=PerformanceMode.MANUAL,
    path_cache_size=4096,
    enable_thread_safety=False,
    lazy_threshold_dict=10
)
```

## 🔧 Advanced Usage

### Custom Node Types
```python
from xnode.abc import iNodeCustom

class CustomNode(iNodeCustom):
    def _to_native(self) -> Any:
        return self._custom_conversion()
```

### Performance Monitoring
```python
from xnode import measure_operation

@measure_operation
def expensive_operation(data):
    # Your expensive operation here
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Memory Usage High**
   - Use `xNode.optimized()` mode
   - Reduce cache sizes in configuration
   - Enable weak references

2. **Performance Slow**
   - Use `xNode.fast()` mode
   - Increase cache sizes
   - Disable thread safety for single-threaded applications

3. **Path Not Found**
   - Check path syntax (dot notation vs bracket notation)
   - Verify node exists in data structure
   - Use `get()` method with default value

## 📄 License

Copyright 2025 eXonware.com. All rights reserved.

## 👥 Credits

- **Software Architect**: Eng. Muhammad AlShehri
- **Developer**: Eng. Muhammad AlShehri  
- **Tester**: Eng. Muhammad AlShehri
- **Company**: eXonware.com

## 🔗 Related Libraries

- **xData**: Advanced data processing built on xNode
- **xSchema**: Schema validation and transformation
- **xSystem**: Core system utilities and patterns
