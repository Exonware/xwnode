from __future__ import annotations
import json
import os
import tempfile
import asyncio
import weakref
from typing import Any, TYPE_CHECKING
from asyncio import Lock
# Import interface for implementation
from data_utils_interface import DataUtilsInterface
from collections.abc import Callable, Iterable
if TYPE_CHECKING:
    from data_operations_interface import DataOperationsInterface
JsonValue = Any
JsonPath = list[str | int] | tuple
MatchFn = Callable[[JsonValue], bool]
UpdateFn = Callable[[JsonValue], JsonValue]


class JsonRecordNotFound(Exception):
    pass


class JsonStreamError(Exception):
    pass
# Global write locks per event loop to prevent concurrent writes
# Root cause fix: Locks created at module level are bound to the event loop
# that exists at import time. When asyncio.run() creates a new event loop,
# the old lock can't be used. This dictionary stores one lock per event loop.
# Following GUIDE_TEST.md - Fix root causes, handle event loop lifecycle properly
_write_locks: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


def _get_write_lock() -> Lock:
    """
    Get or create the write lock for the current event loop.
    Root cause fix: Locks created at module level are bound to the event loop
    that exists at import time. When asyncio.run() creates a new event loop,
    the old lock can't be used. This function creates the lock lazily from
    the current event loop and stores it in a WeakKeyDictionary to avoid
    memory leaks when event loops are destroyed.
    Following GUIDE_TEST.md - Fix root causes, handle event loop lifecycle properly.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running - this shouldn't happen in async context
        # Create a lock anyway (will be bound to next loop that uses it)
        # This is a fallback for edge cases
        return Lock()
    # Get or create lock for this event loop
    if loop not in _write_locks:
        _write_locks[loop] = Lock()
    return _write_locks[loop]


def _iter_json_lines(fp: Iterable[str]) -> Iterable[tuple[int, str, JsonValue]]:
    """
    Yield (line_no, raw_line, parsed_json) for each non-empty line.
    Designed for very large NDJSON files.
    """
    for line_no, line in enumerate(fp, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError as e:
            raise JsonStreamError(f"Invalid JSON at line {line_no}: {e}") from e
        yield line_no, line, obj


def _get_by_path(obj: JsonValue, path: JsonPath | None) -> JsonValue:
    if path is None:
        return obj
    cur: JsonValue = obj
    for key in path:
        try:
            if isinstance(key, int):
                cur = cur[key]
            else:
                cur = cur[str(key)]
        except (KeyError, IndexError, TypeError) as e:
            raise JsonStreamError(f"Path not found: {path!r}") from e
    return cur


def stream_read(
    file_path: str,
    match: MatchFn,
    path: JsonPath | None = None,
    encoding: str = "utf-8",
) -> JsonValue:
    """
    Stream a huge NDJSON file and return the first record (or sub-path) matching `match`.
    Does NOT load the whole file into memory.
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            for _line_no, _raw, obj in _iter_json_lines(f):
                if match(obj):
                    return _get_by_path(obj, path)
    except FileNotFoundError as e:
        raise JsonStreamError(f"File not found: {file_path}") from e
    except PermissionError as e:
        raise JsonStreamError(f"Permission denied: {file_path}") from e
    except OSError as e:
        raise JsonStreamError(f"OS error for {file_path}: {e}") from e
    raise JsonRecordNotFound("No matching JSON record found")
async def async_stream_read(
    file_path: str,
    match: MatchFn,
    path: JsonPath | None = None,
    encoding: str = "utf-8",
) -> JsonValue:
    """
    Async version of stream_read - allows concurrent reads from the same file.
    Stream a huge NDJSON file and return the first record (or sub-path) matching `match`.
    Does NOT load the whole file into memory.
    Multiple async reads can happen concurrently (no locking needed for reads).
    """
    try:
        # Use asyncio.to_thread for file I/O to allow concurrent reads
        def _read_sync():
            with open(file_path, "r", encoding=encoding) as f:
                for _line_no, _raw, obj in _iter_json_lines(f):
                    if match(obj):
                        return _get_by_path(obj, path)
            raise JsonRecordNotFound("No matching JSON record found")
        return await asyncio.to_thread(_read_sync)
    except FileNotFoundError as e:
        raise JsonStreamError(f"File not found: {file_path}") from e
    except PermissionError as e:
        raise JsonStreamError(f"Permission denied: {file_path}") from e
    except OSError as e:
        raise JsonStreamError(f"OS error for {file_path}: {e}") from e


def stream_update(
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
    updated_count = 0
    dir_name, base_name = os.path.split(os.path.abspath(file_path))
    temp_fd = None
    temp_path = None
    try:
        if atomic:
            temp_fd, temp_path = tempfile.mkstemp(
                prefix=f".{base_name}.tmp.", dir=dir_name, text=True
            )
            out_fp = os.fdopen(temp_fd, "w", encoding=encoding, newline=newline)
        else:
            # non-atomic: write to a fixed .tmp next to file
            temp_path = os.path.join(dir_name, f".{base_name}.tmp")
            out_fp = open(temp_path, "w", encoding=encoding, newline=newline)
        with out_fp as out_f, open(file_path, "r", encoding=encoding) as in_f:
            for _line_no, raw_line, obj in _iter_json_lines(in_f):
                try:
                    if match(obj):
                        obj = updater(obj)
                        updated_count += 1
                        raw_line = json.dumps(obj, ensure_ascii=False) + newline
                except Exception as e:
                    raise JsonStreamError(
                        f"Updater/match failed at line {_line_no}: {e}"
                    ) from e
                out_f.write(raw_line)
        # atomic replace
        os.replace(temp_path, file_path)
    except FileNotFoundError as e:
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except Exception:
                pass
        raise JsonStreamError(f"File not found: {file_path}") from e
    except PermissionError as e:
        raise JsonStreamError(f"Permission denied: {file_path}") from e
    except OSError as e:
        raise JsonStreamError(f"OS error while updating {file_path}: {e}") from e
    finally:
        # Best-effort cleanup if something went wrong before os.replace
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
    return updated_count
async def async_stream_update(
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
    # Acquire write lock to prevent concurrent writes
    # Root cause fix: Get lock from current event loop to avoid binding issues
    # Following GUIDE_TEST.md - Fix root causes, handle event loop lifecycle properly
    write_lock = _get_write_lock()
    async with write_lock:
        def _update_sync():
            return stream_update(
                file_path, match, updater,
                encoding=encoding, newline=newline, atomic=atomic
            )
        return await asyncio.to_thread(_update_sync)


def match_by_id(field: str, value: Any) -> MatchFn:
    """Create a simple matcher: obj[field] == value."""
    def _match(obj: JsonValue) -> bool:
        try:
            return obj.get(field) == value  # type: ignore[union-attr]
        except AttributeError:
            return False
    return _match


def update_path(path: JsonPath, new_value: Any) -> UpdateFn:
    """Create an updater that sets obj[path] = new_value."""
    def _update(obj: JsonValue) -> JsonValue:
        cur = obj
        if not path:
            return new_value
        for key in path[:-1]:
            if isinstance(key, int):
                while len(cur) <= key:
                    cur.append({})
                cur = cur[key]
            else:
                if key not in cur or not isinstance(cur[key], (dict, list)):
                    cur[key] = {}
                cur = cur[key]
        last = path[-1]
        if isinstance(last, int):
            while len(cur) <= last:
                cur.append(None)
            cur[last] = new_value
        else:
            cur[last] = new_value
        return obj
    return _update
# ============================================================================
# Interface Implementation
# ============================================================================

class JsonUtils(DataUtilsInterface):
    """
    V1 implementation of DataUtilsInterface using Python stdlib json.
    This class wraps the module-level functions to implement the interface.
    """

    def stream_read(
        self,
        file_path: str,
        match: MatchFn,
        path: JsonPath | None = None,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Implementation of DataUtilsInterface.stream_read."""
        return stream_read(file_path, match, path, encoding)

    async def async_stream_read(
        self,
        file_path: str,
        match: MatchFn,
        path: JsonPath | None = None,
        encoding: str = "utf-8",
    ) -> JsonValue:
        """Implementation of DataUtilsInterface.async_stream_read."""
        return await async_stream_read(file_path, match, path, encoding)

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
        """Implementation of DataUtilsInterface.stream_update."""
        return stream_update(file_path, match, updater, encoding=encoding, newline=newline, atomic=atomic)

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
        """Implementation of DataUtilsInterface.async_stream_update."""
        return await async_stream_update(file_path, match, updater, encoding=encoding, newline=newline, atomic=atomic)
    @staticmethod

    def match_by_id(field: str, value: Any) -> MatchFn:
        """Implementation of DataUtilsInterface.match_by_id."""
        return match_by_id(field, value)
    @staticmethod

    def update_path(path: JsonPath, new_value: Any) -> UpdateFn:
        """Implementation of DataUtilsInterface.update_path."""
        return update_path(path, new_value)
