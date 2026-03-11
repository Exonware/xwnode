"""
Linear data structure facades.
Provides small convenience wrappers around `XWNode` for common linear structures:
- Queue
- Stack
- Deque
These classes primarily select a suitable `NodeMode` by default.
"""

from typing import Optional, TypeVar
from ..facade import XWNode
from ..defs import NodeMode
T = TypeVar("T")


class XWQueue[T](XWNode[list[T]]):
    """Queue facade (FIFO) backed by XWNode with `NodeMode.QUEUE`."""

    def __init__(self, data: Optional[list[T]] = None, immutable: bool = False, **options):
        super().__init__(data=data or [], mode=NodeMode.QUEUE, immutable=immutable, **options)


class XWStack[T](XWNode[list[T]]):
    """Stack facade (LIFO) backed by XWNode with `NodeMode.STACK`."""

    def __init__(self, data: Optional[list[T]] = None, immutable: bool = False, **options):
        super().__init__(data=data or [], mode=NodeMode.STACK, immutable=immutable, **options)


class XWDeque[T](XWNode[list[T]]):
    """Deque facade backed by XWNode with `NodeMode.DEQUE`."""

    def __init__(self, data: Optional[list[T]] = None, immutable: bool = False, **options):
        super().__init__(data=data or [], mode=NodeMode.DEQUE, immutable=immutable, **options)
__all__ = ["XWQueue", "XWStack", "XWDeque"]
