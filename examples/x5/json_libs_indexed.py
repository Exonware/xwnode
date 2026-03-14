"""
JSON Utils with Indexing and Caching - Version 3
This version adds:
- Line offset indexing for O(1) random access
- Optional ID-based indexing for fast lookups
- Persistent index files (.idx.json)
- Paging support
V3 Enhancement: Uses orjson + ijson for high-performance JSON parsing.
"""

import os
import tempfile
import asyncio
from dataclasses import dataclass
from typing import Any
from asyncio import Lock
# Import interface for implementation
from data_utils_indexed_interface import DataUtilsIndexedInterface
# High-performance JSON libraries
from collections.abc import Callable
try:
    import orjson
except ImportError:
    raise ImportError("orjson is required for V3. Install with: pip install orjson")
try:
    import ijson
except ImportError:
    raise ImportError("ijson is required for V3. Install with: pip install ijson")
JsonValue = Any
JsonPath = list[Any]
MatchFn = Callable[[JsonValue], bool]
INDEX_SUFFIX = ".idx.json"
INDEX_VERSION = 3  # Version 3 index format
# Global write lock to prevent concurrent writes
_write_lock = Lock()
@dataclass


class JsonIndexMeta:
    path: str
    size: int
    mtime: float
    version: int = INDEX_VERSION
@dataclass


class JsonIndex:
    meta: JsonIndexMeta
    # byte offsets for each line (record) start
    line_offsets: list[int]
    # optional id index: id_value -> line_number (0-based)
    id_index: dict[str, int] | None = None


def _index_path(file_path: str) -> str:
    return file_path + INDEX_SUFFIX


def _get_file_stat(file_path: str) -> tuple[int, float]:
    st = os.stat(file_path)
    return st.st_size, st.st_mtime


def build_index(
    file_path: str,
    *,
    encoding: str = "utf-8",
    id_field: str | None = None,
    max_id_index: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> JsonIndex:
    """
    One-time full scan to build an index:
      - line_offsets: start byte of each JSON line
      - optional id_index: obj[id_field] -> line_number
    Designed for NDJSON (one JSON object per line, or multiple objects per line).
    V3: Uses orjson for fast JSON parsing and ijson for multi-object lines.
    max_id_index: cap number of id entries (None = no cap).
    progress_callback: Optional callback(line_no, total_lines) for progress updates.
    """
    abs_path = os.path.abspath(file_path)
    size, mtime = _get_file_stat(abs_path)
    line_offsets: list[int] = []
    id_index: dict[str, int] = {} if id_field else None
    # Estimate total lines for progress (rough estimate based on file size)
    # Average line is ~500 bytes, so estimate total lines
    estimated_lines = max(1, size // 500)
    # binary mode for stable byte offsets
    with open(abs_path, "rb") as f:
        line_no = 0
        last_progress = 0
        while True:
            offset = f.tell()
            line = f.readline()
            if not line:
                break
            if not line.strip():
                continue  # skip empty
            line_offsets.append(offset)
            if id_field and (max_id_index is None or len(id_index) < max_id_index):
                try:
                    # Use orjson for fast parsing (handles both objects and arrays)
                    parsed = orjson.loads(line)
                    # Handle arrays: use first object's ID
                    if isinstance(parsed, list):
                        if parsed:
                            obj = parsed[0]
                            key = obj.get(id_field)
                            if isinstance(key, (str, int)):
                                id_index[str(key)] = line_no
                    else:
                        # Single object
                        key = parsed.get(id_field)
                        if isinstance(key, (str, int)):
                            id_index[str(key)] = line_no
                except Exception:
                    # ignore malformed line for id index, still keep offset
                    pass
            line_no += 1
            # Progress update every 10,000 lines or 1% progress
            if progress_callback and (line_no % 10000 == 0 or 
                (estimated_lines > 0 and line_no % max(1, estimated_lines // 100) == 0)):
                progress_callback(line_no, estimated_lines)
    meta = JsonIndexMeta(path=abs_path, size=size, mtime=mtime)
    index = JsonIndex(meta=meta, line_offsets=line_offsets, id_index=id_index)
    # persist index using orjson for fast serialization
    idx_data = {
        "meta": {
            "path": meta.path,
            "size": meta.size,
            "mtime": meta.mtime,
            "version": meta.version,
        },
        "line_offsets": line_offsets,
        "id_index": id_index,
    }
    tmp_path = _index_path(abs_path) + ".tmp"
    # Use orjson for fast index file writing
    with open(tmp_path, "wb") as tmp:
        tmp.write(orjson.dumps(idx_data, option=orjson.OPT_INDENT_2))
    os.replace(tmp_path, _index_path(abs_path))
    return index


def load_index(file_path: str, *, strict: bool = True) -> JsonIndex | None:
    """
    Load and validate index if present.
    If strict=True and file changed -> returns None.
    V3: Uses orjson for fast index file loading.
    """
    abs_path = os.path.abspath(file_path)
    idx_path = _index_path(abs_path)
    if not os.path.exists(idx_path):
        return None
    try:
        with open(idx_path, "rb") as f:
            raw = orjson.loads(f.read())
    except Exception:
        # corrupted index
        return None
    try:
        meta_raw = raw["meta"]
        line_offsets = raw["line_offsets"]
        id_index = raw.get("id_index")
        meta = JsonIndexMeta(
            path=meta_raw["path"],
            size=meta_raw["size"],
            mtime=meta_raw["mtime"],
            version=meta_raw.get("version", 3),
        )
    except Exception:
        return None
    # validate file
    try:
        size, mtime = _get_file_stat(abs_path)
    except OSError:
        return None
    if strict and (size != meta.size or mtime != meta.mtime):
        # file changed -> ignore old index
        return None
    return JsonIndex(
        meta=JsonIndexMeta(
            path=abs_path,
            size=size,
            mtime=mtime,
            version=meta.version,
        ),
        line_offsets=line_offsets,
        id_index=id_index,
    )


def ensure_index(
    file_path: str,
    *,
    encoding: str = "utf-8",
    id_field: str | None = None,
    max_id_index: int | None = None,
) -> JsonIndex:
    """
    Load existing index if valid; otherwise rebuild.
    Intended for 2nd+ access.
    """
    idx = load_index(file_path, strict=True)
    if idx is not None:
        return idx
    return build_index(
        file_path,
        encoding=encoding,
        id_field=id_field,
        max_id_index=max_id_index,
    )


def indexed_get_by_line(
    file_path: str,
    line_number: int,
    *,
    encoding: str = "utf-8",
    index: JsonIndex | None = None,
) -> JsonValue:
    """
    Random-access a specific record by line_number (0-based)
    using prebuilt index.
    V3: Uses orjson for fast JSON parsing.
    """
    if index is None:
        index = ensure_index(file_path)
    if line_number < 0 or line_number >= len(index.line_offsets):
        raise IndexError("line_number out of range")
    offset = index.line_offsets[line_number]
    with open(file_path, "rb") as f:
        f.seek(offset)
        line = f.readline()
    # Use orjson for fast parsing (handles both objects and arrays)
    try:
        parsed = orjson.loads(line)
        # If it's an array, return first object
        if isinstance(parsed, list):
            if parsed:
                return parsed[0]
            raise ValueError(f"Empty array at line {line_number}")
        return parsed
    except (orjson.JSONDecodeError, ValueError, TypeError) as e:
        raise ValueError(f"Could not parse JSON at line {line_number}: {e}") from e


def indexed_get_by_id(
    file_path: str,
    id_value: Any,
    *,
    encoding: str = "utf-8",
    id_field: str = "id",
    index: JsonIndex | None = None,
) -> JsonValue:
    """
    Random-access a record by logical id using id_index if available.
    Falls back to linear scan if id_index missing or incomplete.
    V3: Uses json_libs (V3) for fallback instead of json_utils (V1).
    """
    # Import from V3 json_libs for fallback
    from json_libs import stream_read, match_by_id
    if index is None:
        index = ensure_index(file_path, encoding=encoding, id_field=id_field)
    # fast path via id_index
    if index.id_index is not None:
        key = str(id_value)
        if key in index.id_index:
            line_number = index.id_index[key]
            return indexed_get_by_line(
                file_path, line_number, encoding=encoding, index=index
            )
    # slow fallback: linear scan using V3 stream_read/match_by_id
    matcher = match_by_id(id_field, id_value)
    return stream_read(file_path, matcher, path=None, encoding=encoding)


def get_page(
    file_path: str,
    page_number: int,
    page_size: int,
    *,
    encoding: str = "utf-8",
    index: JsonIndex | None = None,
) -> list[JsonValue]:
    """
    Paging helper using index:
      - page_number: 1-based
      - page_size: number of records per page
    Uses line_offsets to jump directly to the start record.
    V3: Uses orjson for fast JSON parsing.
    """
    if page_number < 1:
        raise ValueError("page_number must be >= 1")
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if index is None:
        index = ensure_index(file_path)
    total_records = len(index.line_offsets)
    start_idx = (page_number - 1) * page_size
    if start_idx >= total_records:
        return []  # empty page
    end_idx = min(start_idx + page_size, total_records)
    offsets = index.line_offsets[start_idx:end_idx]
    results: list[JsonValue] = []
    with open(file_path, "rb") as f:
        for off in offsets:
            f.seek(off)
            line = f.readline()
            if not line.strip():
                continue
            # Use orjson for fast parsing (handles both objects and arrays)
            try:
                parsed = orjson.loads(line)
                # If it's an array, add all objects
                if isinstance(parsed, list):
                    results.extend(parsed)
                else:
                    results.append(parsed)
            except (orjson.JSONDecodeError, ValueError, TypeError):
                # Skip malformed lines
                continue
    return results
# ============================================================================
# ASYNC VERSIONS - Allow concurrent reads, serialize writes
# ============================================================================
async def async_indexed_get_by_line(
    file_path: str,
    line_number: int,
    *,
    encoding: str = "utf-8",
    index: JsonIndex | None = None,
) -> JsonValue:
    """
    Async version of indexed_get_by_line - allows concurrent reads.
    Random-access a specific record by line_number (0-based) using prebuilt index.
    Multiple async reads can happen concurrently (no locking needed for reads).
    V3: Uses orjson for fast JSON parsing.
    """
    if index is None:
        # Load index in thread pool to avoid blocking
        index = await asyncio.to_thread(ensure_index, file_path)
    if line_number < 0 or line_number >= len(index.line_offsets):
        raise IndexError("line_number out of range")
    offset = index.line_offsets[line_number]
    # Use asyncio.to_thread for file I/O
    def _read_sync():
        with open(file_path, "rb") as f:
            f.seek(offset)
            line = f.readline()
        # Use orjson for fast parsing (handles both objects and arrays)
        try:
            parsed = orjson.loads(line)
            # If it's an array, return first object
            if isinstance(parsed, list):
                if parsed:
                    return parsed[0]
                raise ValueError(f"Empty array at line {line_number}")
            return parsed
        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            raise ValueError(f"Could not parse JSON at line {line_number}: {e}") from e
    return await asyncio.to_thread(_read_sync)
async def async_indexed_get_by_id(
    file_path: str,
    id_value: Any,
    *,
    encoding: str = "utf-8",
    id_field: str = "id",
    index: JsonIndex | None = None,
) -> JsonValue:
    """
    Async version of indexed_get_by_id - allows concurrent reads.
    Random-access a record by logical id using id_index if available.
    Falls back to linear scan if id_index missing or incomplete.
    Multiple async reads can happen concurrently (no locking needed for reads).
    V3: Uses json_libs (V3) for fallback instead of json_utils (V1).
    """
    if index is None:
        index = await asyncio.to_thread(
            ensure_index, file_path, encoding=encoding, id_field=id_field
        )
    # fast path via id_index
    if index.id_index is not None:
        key = str(id_value)
        if key in index.id_index:
            line_number = index.id_index[key]
            return await async_indexed_get_by_line(
                file_path, line_number, encoding=encoding, index=index
            )
    # slow fallback: linear scan using V3 async_stream_read
    from json_libs import async_stream_read, match_by_id
    matcher = match_by_id(id_field, id_value)
    return await async_stream_read(file_path, matcher, path=None, encoding=encoding)
async def async_get_page(
    file_path: str,
    page_number: int,
    page_size: int,
    *,
    encoding: str = "utf-8",
    index: JsonIndex | None = None,
) -> list[JsonValue]:
    """
    Async version of get_page - allows concurrent reads.
    Paging helper using index:
      - page_number: 1-based
      - page_size: number of records per page
    Uses line_offsets to jump directly to the start record.
    Multiple async reads can happen concurrently (no locking needed for reads).
    V3: Uses orjson for fast JSON parsing.
    """
    if page_number < 1:
        raise ValueError("page_number must be >= 1")
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if index is None:
        index = await asyncio.to_thread(ensure_index, file_path)
    total_records = len(index.line_offsets)
    start_idx = (page_number - 1) * page_size
    if start_idx >= total_records:
        return []  # empty page
    end_idx = min(start_idx + page_size, total_records)
    offsets = index.line_offsets[start_idx:end_idx]
    # Use asyncio.to_thread for file I/O
    def _read_sync():
        results: list[JsonValue] = []
        with open(file_path, "rb") as f:
            for off in offsets:
                f.seek(off)
                line = f.readline()
                if not line.strip():
                    continue
                # Use orjson for fast parsing (handles both objects and arrays)
                try:
                    parsed = orjson.loads(line)
                    # If it's an array, add all objects
                    if isinstance(parsed, list):
                        results.extend(parsed)
                    else:
                        results.append(parsed)
                except (orjson.JSONDecodeError, ValueError, TypeError):
                    # Skip malformed lines
                    continue
        return results
    return await asyncio.to_thread(_read_sync)
async def async_build_index(
    file_path: str,
    *,
    encoding: str = "utf-8",
    id_field: str | None = None,
    max_id_index: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> JsonIndex:
    """
    Async version of build_index - runs in thread pool to avoid blocking.
    One-time full scan to build an index.
    Note: Index building is CPU/IO intensive, so it runs in a thread pool.
    """
    return await asyncio.to_thread(
        build_index,
        file_path,
        encoding=encoding,
        id_field=id_field,
        max_id_index=max_id_index,
        progress_callback=progress_callback,
    )
async def async_ensure_index(
    file_path: str,
    *,
    encoding: str = "utf-8",
    id_field: str | None = None,
    max_id_index: int | None = None,
) -> JsonIndex:
    """
    Async version of ensure_index - runs in thread pool to avoid blocking.
    Load existing index if valid; otherwise rebuild.
    """
    return await asyncio.to_thread(
        ensure_index,
        file_path,
        encoding=encoding,
        id_field=id_field,
        max_id_index=max_id_index,
    )
# ============================================================================
# Interface Implementation
# ============================================================================

class JsonLibsIndexed(DataUtilsIndexedInterface):
    """
    V3 implementation of DataUtilsIndexedInterface using orjson + ijson.
    This class wraps the module-level functions to implement the interface.
    """

    def build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.build_index."""
        return build_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index, progress_callback=progress_callback)

    def load_index(
        self,
        file_path: str,
        *,
        strict: bool = True,
    ) -> JsonIndex | None:
        """Implementation of DataUtilsIndexedInterface.load_index."""
        return load_index(file_path, strict=strict)

    def ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.ensure_index."""
        return ensure_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index)

    async def async_build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.async_build_index."""
        return await async_build_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index, progress_callback=progress_callback)

    async def async_ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.async_ensure_index."""
        return await async_ensure_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index)

    def indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: JsonIndex | None = None,
    ) -> Any:
        """Implementation of DataUtilsIndexedInterface.indexed_get_by_line."""
        return indexed_get_by_line(file_path, line_number, encoding=encoding, index=index)

    async def async_indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: JsonIndex | None = None,
    ) -> Any:
        """Implementation of DataUtilsIndexedInterface.async_indexed_get_by_line."""
        return await async_indexed_get_by_line(file_path, line_number, encoding=encoding, index=index)

    def indexed_get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
        index: JsonIndex | None = None,
    ) -> Any:
        """Implementation of DataUtilsIndexedInterface.indexed_get_by_id."""
        return indexed_get_by_id(file_path, id_value, encoding=encoding, id_field=id_field, index=index)

    async def async_indexed_get_by_id(
        self,
        file_path: str,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
        index: JsonIndex | None = None,
    ) -> Any:
        """Implementation of DataUtilsIndexedInterface.async_indexed_get_by_id."""
        return await async_indexed_get_by_id(file_path, id_value, encoding=encoding, id_field=id_field, index=index)

    def get_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
        index: JsonIndex | None = None,
    ) -> list[Any]:
        """Implementation of DataUtilsIndexedInterface.get_page."""
        return get_page(file_path, page_number, page_size, encoding=encoding, index=index)

    async def async_get_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
        index: JsonIndex | None = None,
    ) -> list[Any]:
        """Implementation of DataUtilsIndexedInterface.async_get_page."""
        return await async_get_page(file_path, page_number, page_size, encoding=encoding, index=index)
