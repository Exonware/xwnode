#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/operations/__init__.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.17
Generation Date: October 27, 2025
Node operations module integrating xwsystem.operations.
This module provides node-specific operations built on top of xwsystem's
universal operations library, adding XWNode-aware functionality.
"""
# Import xwsystem operations infrastructure

from exonware.xwsystem.operations import (
    MergeStrategy,
    DiffMode,
    PatchOperation,
    DiffResult,
    PatchResult,
    OperationError,
    MergeError,
    DiffError,
    PatchError,
    deep_merge as sys_deep_merge,
    generate_diff as sys_generate_diff,
    apply_patch as sys_apply_patch
)
from .node_merge import NodeMerger, merge_nodes
from .node_diff import NodeDiffer, diff_nodes
from .node_patch import NodePatcher, patch_nodes
__all__ = [
    # xwsystem operations (re-exported)
    "MergeStrategy",
    "DiffMode",
    "PatchOperation",
    "DiffResult",
    "PatchResult",
    "OperationError",
    "MergeError",
    "DiffError",
    "PatchError",
    # XWNode-specific operations
    "NodeMerger",
    "NodeDiffer",
    "NodePatcher",
    # Convenience functions
    "merge_nodes",
    "diff_nodes",
    "patch_nodes",
]
