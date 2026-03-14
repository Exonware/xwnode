#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/operations/node_patch.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: October 27, 2025
Node-aware patch operations using xwsystem.operations.
"""

from typing import Any
from exonware.xwsystem.operations import apply_patch, PatchResult


class NodePatcher:
    """Node-aware patcher with XWNode support."""

    def patch(
        self,
        data: Any,
        operations: list[dict[str, Any]]
    ) -> PatchResult:
        """Apply patch operations to node."""
        # Convert to native if XWNode
        try:
            native_data = data.to_native() if hasattr(data, 'to_native') else data
        except:
            native_data = data
        result = apply_patch(native_data, operations)
        # Convert back to XWNode if original was XWNode
        try:
            if hasattr(data, '__class__') and data.__class__.__name__ == 'XWNode' and result.success:
                from ..facade import XWNode
                result.result = XWNode.from_native(result.result)
        except:
            pass
        return result


def patch_nodes(data: Any, operations: list[dict[str, Any]]) -> PatchResult:
    """Convenience function for patching nodes."""
    patcher = NodePatcher()
    return patcher.patch(data, operations)
__all__ = ["NodePatcher", "patch_nodes"]
