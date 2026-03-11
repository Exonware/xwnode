"""
Abstract interface for indexed JSON operations.
This module defines an abstract base class that captures the
capabilities provided by:
  - `json_utils_indexed` (V2 - indexing with stdlib json)
  - `json_libs_indexed` (V3 - indexing with orjson + ijson)
  - `json_libs_indexed_v4` (V4 - indexing with all performance libraries)
All methods are abstract; concrete implementations are expected to
inherit from this class and implement the full contract.
The function signatures match exactly those from json_utils_indexed.py (V2).
"""

from __future__ import annotations
from typing import Any, Callable, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass
# Avoid circular imports - define types locally
if TYPE_CHECKING:
    # Import types only for type checking
    from json_utils_indexed import (
        JsonIndexMeta,
        JsonIndex,
    )
else:
    # Define types at runtime to avoid circular import
    @dataclass
    class JsonIndexMeta:
        path: str
        size: int
        mtime: float
        version: int = 1
    @dataclass
    class JsonIndex:
        meta: JsonIndexMeta
        line_offsets: list[int]
        id_index: Optional[dict[str, int]] = None
__all__ = [
    "JsonIndexMeta",
    "JsonIndex",
    "DataUtilsIndexedInterface",
    "data_utils_indexed_interface",
]


class DataUtilsIndexedInterface(ABC):
    """
    Abstract interface for indexed JSON operations.
    Implementations must match the exact function signatures from json_utils_indexed.py (V2).
    """
    @abstractmethod

    def build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> JsonIndex:
        """
        One-time full scan to build an index:
          - line_offsets: start byte of each JSON line
          - optional id_index: obj[id_field] -> line_number
        Designed for NDJSON (one JSON object per line).
        max_id_index: cap number of id entries (None = no cap).
        progress_callback: Optional callback(line_no, total_lines) for progress updates.
        """
        raise NotImplementedError
    @abstractmethod

    def load_index(
        self,
        file_path: str,
        *,
        strict: bool = True,
    ) -> Optional[JsonIndex]:
        """
        Load and validate index if present.
        If strict=True and file changed -> returns None.
        """
        raise NotImplementedError
    @abstractmethod

    def ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
    ) -> JsonIndex:
        """
        Load existing index if valid; otherwise rebuild.
        Intended for 2nd+ access.
        """
        raise NotImplementedError
    @abstractmethod

    async def async_build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> JsonIndex:
        """
        Async version of build_index - runs in thread pool to avoid blocking.
        One-time full scan to build an index.
        Note: Index building is CPU/IO intensive, so it runs in a thread pool.
        """
        raise NotImplementedError
    @abstractmethod

    async def async_ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
    ) -> JsonIndex:
        """
        Async version of ensure_index - runs in thread pool to avoid blocking.
        Load existing index if valid; otherwise rebuild.
        """
        raise NotImplementedError
    @abstractmethod

    def indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """
        Random-access a specific record by line_number (0-based)
        using prebuilt index.
        """
        raise NotImplementedError
    @abstractmethod

    async def async_indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """
        Async version of indexed_get_by_line - allows concurrent reads.
        Random-access a specific record by line_number (0-based) using prebuilt index.
        Multiple async reads can happen concurrently (no locking needed for reads).
        """
        raise NotImplementedError
    @abstractmethod

    def indexed_get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """
        Random-access a record by logical id using id_index if available.
        Falls back to linear scan if id_index missing or incomplete.
        """
        raise NotImplementedError
    @abstractmethod

    async def async_indexed_get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """
        Async version of indexed_get_by_id - allows concurrent reads.
        Random-access a record by logical id using id_index if available.
        Falls back to linear scan if id_index missing or incomplete.
        Multiple async reads can happen concurrently (no locking needed for reads).
        """
        raise NotImplementedError
    @abstractmethod

    def get_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> list[Any]:
        """
        Paging helper using index:
          - page_number: 1-based
          - page_size: number of records per page
        Uses line_offsets to jump directly to the start record.
        """
        raise NotImplementedError
    @abstractmethod

    async def async_get_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> list[Any]:
        """
        Async version of get_page - allows concurrent reads.
        Paging helper using index:
          - page_number: 1-based
          - page_size: number of records per page
        Uses line_offsets to jump directly to the start record.
        Multiple async reads can happen concurrently (no locking needed for reads).
        """
        raise NotImplementedError
# Lowercase alias to match the requested name
data_utils_indexed_interface = DataUtilsIndexedInterface
