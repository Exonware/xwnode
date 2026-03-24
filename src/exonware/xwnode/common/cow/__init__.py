#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/cow/__init__.py
Copy-on-Write (COW) Module for XWNode
Provides high-performance immutable data structures with structural sharing
using HAMT (Hash Array Mapped Trie) for O(log₃₂ n) ≈ O(1) operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.15
Generation Date: 26-Oct-2025
"""

from .contracts import ICOWNode, ICOWStrategy
from .base import ACOWNode, ACOWStrategy
from .persistent_node import PersistentNode
from .hamt_engine import HAMTEngine, HAMTNode
__all__ = [
    # Interfaces
    'ICOWNode',
    'ICOWStrategy',
    # Abstract Classes
    'ACOWNode',
    'ACOWStrategy',
    # Concrete Implementations
    'PersistentNode',
    'HAMTEngine',
    'HAMTNode',
]
