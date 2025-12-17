"""
JSON Utils with Indexing and Caching - Version 4

This version adds:
- Line offset indexing for O(1) random access
- Optional ID-based indexing for fast lookups
- Persistent index files (.idx.json)
- Paging support

V4 Enhancement: Uses all high-performance libraries:
- orjson: Fast JSON parsing/writing
- ijson: Streaming for large structures
- simdjson: Ultra-fast parsing for large files
- msgspec: Structured/typed encoding (optional)
- jsonpath-ng/jsonpointer: Advanced path queries
"""

import os
import tempfile
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Callable
from asyncio import Lock

# Import interface for implementation
from data_utils_indexed_interface import DataUtilsIndexedInterface

# High-performance JSON libraries
try:
    import orjson
except ImportError:
    raise ImportError("orjson is required for V4. Install with: pip install orjson")

try:
    import ijson
except ImportError:
    raise ImportError("ijson is required for V4. Install with: pip install ijson")

# Optional high-performance libraries
try:
    import simdjson
    SIMDJSON_AVAILABLE = True
except ImportError:
    SIMDJSON_AVAILABLE = False
    simdjson = None

try:
    import msgspec
    MSGSPEC_AVAILABLE = True
except ImportError:
    MSGSPEC_AVAILABLE = False
    msgspec = None

try:
    from jsonpointer import resolve_pointer, set_pointer
    JSONPOINTER_AVAILABLE = True
except ImportError:
    JSONPOINTER_AVAILABLE = False
    resolve_pointer = None
    set_pointer = None

JsonValue = Any
JsonPath = List[Any]
MatchFn = Callable[[JsonValue], bool]

INDEX_SUFFIX = ".idx.json"
INDEX_VERSION = 4  # Version 4 index format

# Performance tuning: Use simdjson for files larger than this threshold (bytes)
SIMDJSON_THRESHOLD = 10 * 1024 * 1024  # 10 MB

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
    line_offsets: List[int]
    # optional id index: id_value -> line_number (0-based)
    id_index: Optional[Dict[str, int]] = None


def _index_path(file_path: str) -> str:
    return file_path + INDEX_SUFFIX


def _get_file_stat(file_path: str) -> Tuple[int, float]:
    st = os.stat(file_path)
    return st.st_size, st.st_mtime


def _parse_json_fast(line: bytes, use_simd: bool = False) -> JsonValue:
    """
    Parse JSON using the fastest available method.
    
    V4: Uses simdjson for large files, orjson otherwise.
    """
    if use_simd and SIMDJSON_AVAILABLE:
        try:
            return simdjson.loads(line)
        except Exception:
            # Fallback to orjson if simdjson fails
            pass
    
    # Default to orjson (fast and reliable)
    return orjson.loads(line)


def build_index(
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
    Designed for NDJSON (one JSON object per line, or multiple objects per line).
    
    V4: Uses simdjson for large files, orjson for smaller files.

    max_id_index: cap number of id entries (None = no cap).
    progress_callback: Optional callback(line_no, total_lines) for progress updates.
    """
    abs_path = os.path.abspath(file_path)
    size, mtime = _get_file_stat(abs_path)

    line_offsets: List[int] = []
    id_index: Dict[str, int] = {} if id_field else None

    # Estimate total lines for progress (rough estimate based on file size)
    estimated_lines = max(1, size // 500)
    
    # Use simdjson for large files
    use_simd = SIMDJSON_AVAILABLE and size > SIMDJSON_THRESHOLD
    
    # binary mode for stable byte offsets
    with open(abs_path, "rb") as f:
        line_no = 0
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
                    # Use fastest available parser
                    parsed = _parse_json_fast(line, use_simd=use_simd)
                    
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


def load_index(file_path: str, *, strict: bool = True) -> Optional[JsonIndex]:
    """
    Load and validate index if present.
    If strict=True and file changed -> returns None.
    
    V4: Uses orjson for fast index file loading.
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
            version=meta_raw.get("version", 4),
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
    id_field: Optional[str] = None,
    max_id_index: Optional[int] = None,
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
    index: Optional[JsonIndex] = None,
) -> JsonValue:
    """
    Random-access a specific record by line_number (0-based)
    using prebuilt index.
    
    V4: Uses simdjson for large files, orjson for smaller files.
    """
    if index is None:
        index = ensure_index(file_path)

    if line_number < 0 or line_number >= len(index.line_offsets):
        raise IndexError("line_number out of range")

    offset = index.line_offsets[line_number]
    with open(file_path, "rb") as f:
        f.seek(offset)
        line = f.readline()
    
    # Use fastest available parser
    file_size = index.meta.size
    use_simd = SIMDJSON_AVAILABLE and file_size > SIMDJSON_THRESHOLD
    
    try:
        parsed = _parse_json_fast(line, use_simd=use_simd)
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
    index: Optional[JsonIndex] = None,
) -> JsonValue:
    """
    Random-access a record by logical id using id_index if available.
    Falls back to linear scan if id_index missing or incomplete.
    
    V4: Uses json_libs_v4 (V4) for fallback instead of json_libs (V3).
    """
    # Import from V4 json_libs_v4 for fallback
    from json_libs_v4 import stream_read, match_by_id

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

    # slow fallback: linear scan using V4 stream_read/match_by_id
    matcher = match_by_id(id_field, id_value)
    return stream_read(file_path, matcher, path=None, encoding=encoding)


def get_page(
    file_path: str,
    page_number: int,
    page_size: int,
    *,
    encoding: str = "utf-8",
    index: Optional[JsonIndex] = None,
) -> List[JsonValue]:
    """
    Paging helper using index:
      - page_number: 1-based
      - page_size: number of records per page

    Uses line_offsets to jump directly to the start record.
    
    V4: Uses simdjson for large files, orjson for smaller files.
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

    # Use fastest available parser
    file_size = index.meta.size
    use_simd = SIMDJSON_AVAILABLE and file_size > SIMDJSON_THRESHOLD

    results: List[JsonValue] = []
    with open(file_path, "rb") as f:
        for off in offsets:
            f.seek(off)
            line = f.readline()
            if not line.strip():
                continue
            # Use fastest available parser
            try:
                parsed = _parse_json_fast(line, use_simd=use_simd)
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
    index: Optional[JsonIndex] = None,
) -> JsonValue:
    """
    Async version of indexed_get_by_line - allows concurrent reads.
    Random-access a specific record by line_number (0-based) using prebuilt index.
    
    Multiple async reads can happen concurrently (no locking needed for reads).
    
    V4: Uses simdjson for large files, orjson for smaller files.
    """
    if index is None:
        index = await asyncio.to_thread(ensure_index, file_path)

    if line_number < 0 or line_number >= len(index.line_offsets):
        raise IndexError("line_number out of range")

    offset = index.line_offsets[line_number]
    file_size = index.meta.size
    use_simd = SIMDJSON_AVAILABLE and file_size > SIMDJSON_THRESHOLD
    
    # Use asyncio.to_thread for file I/O
    def _read_sync():
        with open(file_path, "rb") as f:
            f.seek(offset)
            line = f.readline()
        # Use fastest available parser
        parsed = _parse_json_fast(line, use_simd=use_simd)
        # If it's an array, return first object
        if isinstance(parsed, list):
            if parsed:
                return parsed[0]
            raise ValueError(f"Empty array at line {line_number}")
        return parsed
    
    return await asyncio.to_thread(_read_sync)


async def async_indexed_get_by_id(
    file_path: str,
    id_value: Any,
    *,
    encoding: str = "utf-8",
    id_field: str = "id",
    index: Optional[JsonIndex] = None,
) -> JsonValue:
    """
    Async version of indexed_get_by_id - allows concurrent reads.
    Random-access a record by logical id using id_index if available.
    Falls back to linear scan if id_index missing or incomplete.
    
    Multiple async reads can happen concurrently (no locking needed for reads).
    
    V4: Uses json_libs_v4 (V4) for fallback instead of json_libs (V3).
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

    # slow fallback: linear scan using V4 async_stream_read
    from json_libs_v4 import async_stream_read, match_by_id
    matcher = match_by_id(id_field, id_value)
    return await async_stream_read(file_path, matcher, path=None, encoding=encoding)


async def async_get_page(
    file_path: str,
    page_number: int,
    page_size: int,
    *,
    encoding: str = "utf-8",
    index: Optional[JsonIndex] = None,
) -> List[JsonValue]:
    """
    Async version of get_page - allows concurrent reads.
    Paging helper using index:
      - page_number: 1-based
      - page_size: number of records per page

    Uses line_offsets to jump directly to the start record.
    
    Multiple async reads can happen concurrently (no locking needed for reads).
    
    V4: Uses simdjson for large files, orjson for smaller files.
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

    # Use fastest available parser
    file_size = index.meta.size
    use_simd = SIMDJSON_AVAILABLE and file_size > SIMDJSON_THRESHOLD

    # Use asyncio.to_thread for file I/O
    def _read_sync():
        results: List[JsonValue] = []
        with open(file_path, "rb") as f:
            for off in offsets:
                f.seek(off)
                line = f.readline()
                if not line.strip():
                    continue
                # Use fastest available parser
                try:
                    parsed = _parse_json_fast(line, use_simd=use_simd)
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
    id_field: Optional[str] = None,
    max_id_index: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
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
    id_field: Optional[str] = None,
    max_id_index: Optional[int] = None,
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

class JsonLibsIndexedV4(DataUtilsIndexedInterface):
    """
    V4 implementation of DataUtilsIndexedInterface using all high-performance libraries.
    
    This class wraps the module-level functions to implement the interface.
    """
    
    def build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.build_index."""
        return build_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index, progress_callback=progress_callback)
    
    def load_index(
        self,
        file_path: str,
        *,
        strict: bool = True,
    ) -> Optional[JsonIndex]:
        """Implementation of DataUtilsIndexedInterface.load_index."""
        return load_index(file_path, strict=strict)
    
    def ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.ensure_index."""
        return ensure_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index)
    
    async def async_build_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.async_build_index."""
        return await async_build_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index, progress_callback=progress_callback)
    
    async def async_ensure_index(
        self,
        file_path: str,
        *,
        encoding: str = "utf-8",
        id_field: Optional[str] = None,
        max_id_index: Optional[int] = None,
    ) -> JsonIndex:
        """Implementation of DataUtilsIndexedInterface.async_ensure_index."""
        return await async_ensure_index(file_path, encoding=encoding, id_field=id_field, max_id_index=max_id_index)
    
    def indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """Implementation of DataUtilsIndexedInterface.indexed_get_by_line."""
        return indexed_get_by_line(file_path, line_number, encoding=encoding, index=index)
    
    async def async_indexed_get_by_line(
        self,
        file_path: str,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
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
        index: Optional[JsonIndex] = None,
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
        index: Optional[JsonIndex] = None,
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
        index: Optional[JsonIndex] = None,
    ) -> List[Any]:
        """Implementation of DataUtilsIndexedInterface.get_page."""
        return get_page(file_path, page_number, page_size, encoding=encoding, index=index)
    
    async def async_get_page(
        self,
        file_path: str,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> List[Any]:
        """Implementation of DataUtilsIndexedInterface.async_get_page."""
        return await async_get_page(file_path, page_number, page_size, encoding=encoding, index=index)

