#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/operations/node_diff.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.3
Generation Date: October 27, 2025
Node-aware diff operations using xwsystem.operations.
"""

from typing import Any
from exonware.xwsystem.operations import generate_diff, DiffMode, DiffResult


class NodeDiffer:
    """Node-aware differ with XWNode support."""

    def diff(
        self,
        original: Any,
        modified: Any,
        mode: DiffMode = DiffMode.FULL
    ) -> DiffResult:
        """Generate diff between two node structures."""
        # Convert to native if XWNode
        try:
            orig_native = original.to_native() if hasattr(original, 'to_native') else original
            mod_native = modified.to_native() if hasattr(modified, 'to_native') else modified
        except:
            orig_native = original
            mod_native = modified
        return generate_diff(orig_native, mod_native, mode=mode)


def diff_nodes(original: Any, modified: Any, mode: DiffMode = DiffMode.FULL) -> DiffResult:
    """Convenience function for diffing nodes."""
    differ = NodeDiffer()
    return differ.diff(original, modified, mode=mode)
__all__ = ["NodeDiffer", "diff_nodes"]
