from __future__ import annotations

"""
Abstract interface that unifies streaming and indexed JSON operations.

This module defines a single abstract base class that captures the
capabilities provided by:
  - `json_utils`  (streaming read / update)
  - `json_utils_indexed` (indexing, random access, paging)

All methods are abstract; concrete implementations are expected to
inherit from this class and implement the full contract.
"""

from typing import Any, List
from abc import ABC, abstractmethod

from json_utils import (
    JsonValue,
    JsonPath,
    MatchFn,
    UpdateFn,
    JsonRecordNotFound,
    JsonStreamError,
)

from json_utils_indexed import (
    JsonIndexMeta,
    JsonIndex,
)

__all__ = [
    "JsonValue",
    "JsonPath",
    "MatchFn",
    "UpdateFn",
    "JsonRecordNotFound",
    "JsonStreamError",
    "JsonIndexMeta",
    "JsonIndex",
    "DataOperationsInterface",
    "data_operations_interface",
]


class DataOperationsInterface(ABC):
    """
    Unified abstract interface for JSON data operations.

    Implementations may choose to use streaming, indexing, or a hybrid
    strategy internally, but must honour these method contracts.
    """

    # ------------------------------------------------------------------
    # Streaming read
    # ------------------------------------------------------------------

    @abstractmethod
    def stream_read(
        self,
        file_path: str,
        match: MatchFn,
        path: JsonPath | None = None,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Stream a huge NDJSON file and return the first record (or sub-path) matching `match`."""
        raise NotImplementedError

    @abstractmethod
    async def async_stream_read(
        self,
        file_path: str,
        match: MatchFn,
        path: JsonPath | None = None,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Async version of `stream_read`."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Streaming update
    # ------------------------------------------------------------------

    @abstractmethod
    def stream_update(
        self,
        file_path: str,
        match: MatchFn,
        updater: UpdateFn,
        *,
        encoding: str = "utf-8",
        newline: str = "\n",
        atomic: bool = True,
    ) -> int:
        """Stream-copy and update matching records. Returns number of updated records."""
        raise NotImplementedError

    @abstractmethod
    async def async_stream_update(
        self,
        file_path: str,
        match: MatchFn,
        updater: UpdateFn,
        *,
        encoding: str = "utf-8",
        newline: str = "\n",
        atomic: bool = True,
    ) -> int:
        """Async version of `stream_update`."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Index building / management
    # ------------------------------------------------------------------

    @abstractmethod
    def build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """One-time full scan to build an index."""
        raise NotImplementedError

    @abstractmethod
    def load_index(self, file_path: str, *, strict: bool = True) -> JsonIndex | None:
        """Load an existing index, or return None if not available / invalid."""
        raise NotImplementedError

    @abstractmethod
    def ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """Load existing index if valid; otherwise rebuild."""
        raise NotImplementedError

    @abstractmethod
    async def async_build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """Async version of `build_index`."""
        raise NotImplementedError

    @abstractmethod
    async def async_ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """Async version of `ensure_index`."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Random access by line / id
    # ------------------------------------------------------------------

    @abstractmethod
    def indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Random-access a specific record by line_number (0-based) using index."""
        raise NotImplementedError

    @abstractmethod
    async def async_indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Async version of `indexed_get_by_line`."""
        raise NotImplementedError

    @abstractmethod
    def indexed_get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
    ) -> JsonValue:
        """Random-access a record by logical id."""
        raise NotImplementedError

    @abstractmethod
    async def async_indexed_get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
    ) -> JsonValue:
        """Async version of `indexed_get_by_id`."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Paging
    # ------------------------------------------------------------------

    @abstractmethod
    def get_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
    ) -> List[JsonValue]:
        """Return a page of records using the index for fast access."""
        raise NotImplementedError

    @abstractmethod
    async def async_get_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
    ) -> List[JsonValue]:
        """Async version of `get_page`."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Unified convenience methods
    # ------------------------------------------------------------------

    @abstractmethod
    def get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
    ) -> JsonValue:
        """Convenience wrapper: fetch record by logical id (implementation may use index and/or streaming)."""
        raise NotImplementedError

    @abstractmethod
    async def async_get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
    ) -> JsonValue:
        """Async convenience wrapper for `get_by_id`."""
        raise NotImplementedError

    @abstractmethod
    def get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Convenience wrapper: fetch record by 0-based line number."""
        raise NotImplementedError

    @abstractmethod
    async def async_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Async convenience wrapper for `get_by_line`."""
        raise NotImplementedError

    @abstractmethod
    def get_records_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
    ) -> List[JsonValue]:
        """Convenience wrapper: fetch a page of records."""
        raise NotImplementedError

    @abstractmethod
    async def async_get_records_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
    ) -> List[JsonValue]:
        """Async convenience wrapper for `get_records_page`."""
        raise NotImplementedError


# Lowercase alias to match the requested name
data_operations_interface = DataOperationsInterface

