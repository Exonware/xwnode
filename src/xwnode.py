"""
Convenience module for importing xwnode.
This allows users to import the library in two ways:
1. import exonware.xwnode
2. import xwnode  # This convenience import
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
Generation Date: 07-Sep-2025
"""
# Import everything from the main package

from exonware.xwnode import *  # noqa: F401, F403
# Re-export version from source of truth (version.py via exonware.xwnode)
__version__ = __version__  # noqa: F405
