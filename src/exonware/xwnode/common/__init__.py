"""
#exonware/xwnode/src/exonware/xwnode/common/__init__.py

Common utilities and patterns shared across xwnode.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.1.0.1
"""

# Explicit imports - no wildcards (per GUIDELINES_DEV.md)
from . import patterns
from . import monitoring
from . import management
from . import utils
from .cow import (
    ICOWNode, ICOWStrategy,
    ACOWNode, ACOWStrategy,
    PersistentNode, HAMTEngine, HAMTNode
)

__all__ = [
    # Submodules
    'patterns',
    'monitoring', 
    'management',
    'utils',
    # COW exports
    'ICOWNode',
    'ICOWStrategy',
    'ACOWNode',
    'ACOWStrategy',
    'PersistentNode',
    'HAMTEngine',
    'HAMTNode',
]
