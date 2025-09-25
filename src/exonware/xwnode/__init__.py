"""
xwnode: A lightweight library for representing and navigating hierarchical data.

The xwnode library provides a clean, immutable interface for working with
tree-structured data. It's designed to be the foundation for more complex
data handling libraries like xdata.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.4
Generation Date: 07-Sep-2025

Main Classes:
    XWNode: The primary interface for working with hierarchical data
    XWQuery: Query interface for searching and filtering nodes
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

from .facade import (
    XWNode, XWEdge, XWQuery, XWFactory,
    # A+ Usability Presets
    create_with_preset, list_available_presets,
    # Performance Modes
    fast, optimized, adaptive, dual_adaptive
)
from .errors import (
    XWNodeError, XWNodeTypeError, XWNodePathError, XWNodeValueError,
    XWNodeSecurityError, XWNodeLimitError, XWNodePathSecurityError
)
from .config import XWNodeConfig, get_config, set_config

# Version info
__version__ = '0.0.1'
__author__ = 'Eng. Muhammad AlShehri'
__email__ = 'connect@exonware.com'
__company__ = 'eXonware.com'

# Public API
__all__ = [
    # Main classes
    'XWNode',
    'XWEdge',
    'XWQuery',
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
    
    # Exceptions
    'XWNodeError',
    'XWNodeTypeError', 
    'XWNodePathError',
    'XWNodeValueError',
    'XWNodeSecurityError',
    'XWNodeLimitError',
    'XWNodePathSecurityError',
]

# Convenience functions for XWNode metrics
def get_metrics():
    """Get XWNode metrics instance."""
    try:
        from exonware.xwsystem.monitoring import get_metrics as get_xwsystem_metrics
        return get_xwsystem_metrics('xwnode')
    except ImportError:
        return {}

def reset_metrics():
    """Reset XWNode metrics."""
    try:
        from exonware.xwsystem.monitoring import reset_metrics
        reset_metrics('xwnode')
    except ImportError:
        pass