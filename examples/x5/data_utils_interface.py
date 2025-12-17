"""
Abstract interface for streaming JSON operations.

This module defines an abstract base class that captures the
capabilities provided by:
  - `json_utils` (V1 - streaming read / update)
  - `json_libs` (V3 - streaming with orjson + ijson)
  - `json_libs_v4` (V4 - streaming with all performance libraries)

All methods are abstract; concrete implementations are expected to
inherit from this class and implement the full contract.

The function signatures match exactly those from json_utils.py (V1).
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional, Union, TYPE_CHECKING
from abc import ABC, abstractmethod

# Avoid circular imports - define types locally
if TYPE_CHECKING:
    # Import types only for type checking
    from json_utils import (
        JsonValue,
        JsonPath,
        MatchFn,
        UpdateFn,
        JsonRecordNotFound,
        JsonStreamError,
    )
else:
    # Define types at runtime to avoid circular import
    JsonValue = Any
    JsonPath = Union[List[Union[str, int]], tuple]
    MatchFn = Callable[[Any], bool]
    UpdateFn = Callable[[Any], Any]
    
    class JsonRecordNotFound(Exception):
        pass
    
    class JsonStreamError(Exception):
        pass

__all__ = [
    "JsonValue",
    "JsonPath",
    "MatchFn",
    "UpdateFn",
    "JsonRecordNotFound",
    "JsonStreamError",
    "DataUtilsInterface",
    "data_utils_interface",
]


class DataUtilsInterface(ABC):
    """
    Abstract interface for streaming JSON operations.
    
    Implementations must match the exact function signatures from json_utils.py (V1).
    """

    @abstractmethod
    def stream_read(
        self,
        file_path: str,
        match: MatchFn,
        path: Optional[JsonPath] = None,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """
        Stream a huge NDJSON file and return the first record (or sub-path) matching `match`.
        Does NOT load the whole file into memory.
        """
        raise NotImplementedError

    @abstractmethod
    async def async_stream_read(
        self,
        file_path: str,
        match: MatchFn,
        path: Optional[JsonPath] = None,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """
        Async version of stream_read - allows concurrent reads from the same file.
        Stream a huge NDJSON file and return the first record (or sub-path) matching `match`.
        Does NOT load the whole file into memory.
        
        Multiple async reads can happen concurrently (no locking needed for reads).
        """
        raise NotImplementedError

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
        """
        Stream-copy a huge NDJSON file, applying `updater` to records where `match(obj)` is True.
        Only matching records are loaded into memory one-by-one.

        Returns the number of updated records.
        """
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
        """
        Async version of stream_update - uses write lock to prevent concurrent writes.
        Stream-copy a huge NDJSON file, applying `updater` to records where `match(obj)` is True.
        Only matching records are loaded into memory one-by-one.

        Returns the number of updated records.
        
        Note: Write operations are serialized (one at a time) to prevent corruption.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def match_by_id(field: str, value: Any) -> MatchFn:
        """Create a simple matcher: obj[field] == value."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def update_path(path: JsonPath, new_value: Any) -> UpdateFn:
        """Create an updater that sets obj[path] = new_value."""
        raise NotImplementedError


# Lowercase alias to match the requested name
data_utils_interface = DataUtilsInterface

