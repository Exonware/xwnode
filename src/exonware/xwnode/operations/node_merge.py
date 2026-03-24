#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/operations/node_merge.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.15
Generation Date: October 27, 2025
Node-aware merge operations using xwsystem.operations.
Provides XWNode-specific merge functionality with strategy preservation.
"""

from typing import Any
from exonware.xwsystem.operations import deep_merge, MergeStrategy


class NodeMerger:
    """
    Node-aware merger that preserves XWNode strategies.
    Integrates xwsystem.operations with XWNode-specific concerns like
    strategy preservation, edge handling, and metadata.
    Priority Alignment:
    1. Security - Safe merging with validation
    2. Usability - Simple API for node merging
    3. Maintainability - Delegates to xwsystem.operations
    4. Performance - Efficient merge with strategy optimization
    5. Extensibility - Multiple strategies supported
    """

    def __init__(self, preserve_strategy: bool = True):
        """
        Initialize node merger.
        Args:
            preserve_strategy: Whether to preserve XWNode strategy
        """
        self.preserve_strategy = preserve_strategy

    def merge(
        self,
        target: Any,
        source: Any,
        strategy: MergeStrategy = MergeStrategy.DEEP
    ) -> Any:
        """
        Merge two node structures.
        Args:
            target: Target node
            source: Source node to merge
            strategy: Merge strategy
        Returns:
            Merged node
        """
        # Convert inputs to native format if they have to_native method
        # Direct import - no defensive try/except (per GUIDELINES_DEV.md)
        target_native = target.to_native() if hasattr(target, 'to_native') else target
        source_native = source.to_native() if hasattr(source, 'to_native') else source
        # Use xwsystem.operations for the merge
        result = deep_merge(target_native, source_native, strategy=strategy)
        # If target was XWNode, return XWNode to preserve type
        if hasattr(target, '__class__') and target.__class__.__name__ == 'XWNode':
            from ..facade import XWNode
            return XWNode.from_native(result)
        return result


def merge_nodes(
    target: Any,
    source: Any,
    strategy: MergeStrategy = MergeStrategy.DEEP
) -> Any:
    """
    Convenience function for merging nodes.
    Args:
        target: Target node
        source: Source node to merge
        strategy: Merge strategy
    Returns:
        Merged node
    """
    merger = NodeMerger()
    return merger.merge(target, source, strategy=strategy)
__all__ = ["NodeMerger", "merge_nodes"]
