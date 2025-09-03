"""
xnode: A lightweight library for representing and navigating hierarchical data.

The xnode library provides a clean, immutable interface for working with
tree-structured data. It's designed to be the foundation for more complex
data handling libraries like xdata.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025

Main Classes:
    xNode: The primary interface for working with hierarchical data
    xNodeQuery: Query interface for searching and filtering nodes
    xNodeFactory: Factory for creating xNode instances
    
Exceptions:
    xNodeError: Base exception for all xnode errors
    xNodeTypeError: Raised for invalid node type operations
    xNodePathError: Raised for invalid path lookups
    xNodeValueError: Raised for value operation failures
    xNodeSecurityError: Raised for security violations
    xNodeLimitError: Raised for resource limit violations

Example:
    >>> from exonware.xnode import xNode
    >>> 
    >>> # Create from Python objects
    >>> data = xNode.from_native({
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

from .facade import xNode, xNodeQuery, xNodeFactory
from .errors import (
    xNodeError, xNodeTypeError, xNodePathError, xNodeValueError,
    xNodeSecurityError, xNodeLimitError, xNodePathSecurityError
)
from .config import xNodeConfig, get_config, set_config

# Version info
__version__ = '0.0.1'
__author__ = 'Eng. Muhammad AlShehri'
__email__ = 'connect@exonware.com'
__company__ = 'eXonware.com'

# Public API
__all__ = [
    # Main classes
    'xNode',
    'xNodeQuery',
    'xNodeFactory',
    
    # Configuration
    'xNodeConfig',
    'get_config',
    'set_config',
    
    # Exceptions
    'xNodeError',
    'xNodeTypeError', 
    'xNodePathError',
    'xNodeValueError',
    'xNodeSecurityError',
    'xNodeLimitError',
    'xNodePathSecurityError',
]

# Convenience functions for xNode metrics
def get_metrics():
    """Get xNode metrics instance."""
    try:
        from exonware.xsystem.monitoring import get_metrics as get_xsystem_metrics
        return get_xsystem_metrics('xnode')
    except ImportError:
        return {}

def reset_metrics():
    """Reset xNode metrics."""
    try:
        from exonware.xsystem.monitoring import reset_metrics
        reset_metrics('xnode')
    except ImportError:
        pass