"""
Compatibility shim for AsyncRWLock.

The canonical implementation now lives in `exonware.xwsystem.threading`.
"""

from exonware.xwsystem.threading.async_primitives import AsyncRWLock

__all__ = ["AsyncRWLock"]
