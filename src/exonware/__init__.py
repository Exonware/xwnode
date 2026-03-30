"""
exonware package - Enterprise-grade Python framework ecosystem
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.16
Generation Date: 2025-01-03
This is a namespace package allowing multiple exonware subpackages
to coexist (xwsystem, xwnode, xwdata, etc.)
"""
# Make this a namespace package - DO NOT set __path__
# This allows both exonware.xwsystem and exonware.xwnode to coexist

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
try:
    from exonware.xwnode.version import __version__
except ImportError:
    __version__ = '0.0.0'  # fallback when package version not loaded
__author__ = 'eXonware Backend Team'
__email__ = 'connect@exonware.com'
__company__ = 'eXonware.com'
