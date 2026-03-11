"""
#exonware/xwnode/src/exonware/xwnode/__init__.py
xwnode: A lightweight library for representing and navigating hierarchical data.
The xwnode library provides a clean, immutable interface for working with
tree-structured data. It's designed to be the foundation for more complex
data handling libraries like xdata.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.1
Generation Date: 07-Sep-2025
Main Classes:
    XWNode: The primary interface for working with hierarchical data
    XWFactory: Factory for creating XWNode instances
Exceptions:
    XWNodeError: Base exception for all xwnode errors
    XWNodeTypeError: Raised for invalid node type operations
    XWNodePathError: Raised for invalid path lookups
    XWNodeValueError: Raised for value operation failures
    XWNodeSecurityError: Raised for security violations
    XWNodeLimitError: Raised for resource limit violations
Example:
    >>> from exonware.xwnode import XWNode
    >>> 
    >>> # Create from Python objects
    >>> data = XWNode.from_native({
    ...     'users': [
    ...         {'name': 'Alice', 'age': 30},
    ...         {'name': 'Bob', 'age': 25}
    ...     ]
    ... })
    >>> 
    >>> # Navigate using paths
    >>> data.find('users.0.name').value
    'Alice'
    >>> 
    >>> # Use bracket notation
    >>> data['users'][1]['age'].value
    25
"""
# =============================================================================
# XWLAZY INTEGRATION - Auto-install missing dependencies silently (EARLY)
# =============================================================================
# Activate xwlazy BEFORE other imports to enable auto-installation of missing dependencies
# This enables silent auto-installation of missing libraries when they are imported

try:
    from exonware.xwlazy import auto_enable_lazy
    auto_enable_lazy(__package__ or "exonware.xwnode", mode="smart")
except ImportError:
    # xwlazy not installed - lazy mode simply stays disabled (normal behavior)
    pass
# =============================================================================
# IMPORTS - Standard Python Imports (No Defensive Code!)
# =============================================================================
from .facade import (
    XWNode, XWEdge, XWFactory,
    # A+ Usability Presets
    create_with_preset, list_available_presets,
    # Performance Modes
    fast, optimized, adaptive, dual_adaptive
)
from .errors import (
    XWNodeError, 
    XWNodeTypeError, 
    XWNodePathError, 
    XWNodeValueError,
    XWNodeSecurityError, 
    XWNodeLimitError, 
    XWNodePathSecurityError
)
from .config import XWNodeConfig, get_config, set_config
from .defs import NodeMode, EdgeMode, NodeTrait, EdgeTrait, GraphOptimization
# Note: QueryMode and QueryTrait are in xwquery.defs module
from .common.graph import XWGraphManager
from exonware.xwsystem.monitoring import get_metrics as get_xwsystem_metrics, reset_metrics as reset_xwsystem_metrics
# Operations (xwsystem integration)
from .operations import (
    MergeStrategy, DiffMode, PatchOperation, DiffResult, PatchResult,
    NodeMerger, NodeDiffer, NodePatcher,
    merge_nodes, diff_nodes, patch_nodes
)
# Version info (source of truth: version.py)
from .version import __version__
__author__ = 'eXonware Backend Team'
__email__ = 'connect@exonware.com'
__company__ = 'eXonware.com'
# Public API
__all__ = [
    # Main classes
    'XWNode',
    'XWEdge',
    'XWFactory',
    # A+ Usability Presets
    'create_with_preset',
    'list_available_presets',
    # Performance Modes
    'fast',
    'optimized',
    'adaptive', 
    'dual_adaptive',
    # Configuration
    'XWNodeConfig',
    'get_config',
    'set_config',
    # Enums and Types
    'NodeMode',
    'EdgeMode',
    'NodeTrait',
    'EdgeTrait',
    'GraphOptimization',
    # Note: QueryMode and QueryTrait are in xwquery.defs - import from there if needed
    # Graph Optimization
    'XWGraphManager',
    # Operations (xwsystem integration)
    'MergeStrategy', 'DiffMode', 'PatchOperation', 'DiffResult', 'PatchResult',
    'NodeMerger', 'NodeDiffer', 'NodePatcher',
    'merge_nodes', 'diff_nodes', 'patch_nodes',
    # Exceptions
    'XWNodeError',
    'XWNodeTypeError', 
    'XWNodePathError',
    'XWNodeValueError',
    'XWNodeSecurityError',
    'XWNodeLimitError',
    'XWNodePathSecurityError',
]
# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_metrics():
    """Get XWNode metrics instance."""
    return get_xwsystem_metrics('xwnode')

def reset_metrics():
    """Reset XWNode metrics."""
    reset_xwsystem_metrics('xwnode')
