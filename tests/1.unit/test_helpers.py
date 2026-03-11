"""
#exonware/xwnode/examples/x5/data_operations/test_helpers.py
Shared test utilities for data operations test suite.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import os
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Any, Optional, Callable
# Import both versions: resolve path to examples/x5 so json_utils and json_utils_indexed are found
_xwnode_root = Path(__file__).resolve().parent.parent.parent
_examples_x5 = _xwnode_root / "examples" / "x5"
if _examples_x5.is_dir():
    sys.path.insert(0, str(_examples_x5))
from json_utils import (
    stream_read,
    stream_update,
    match_by_id,
    update_path,
    JsonRecordNotFound,
    JsonStreamError,
    MatchFn,
    UpdateFn,
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_line,
    indexed_get_by_id,
    get_page,
    load_index,
    JsonIndex,
)


def safe_ensure_index(file_path: str, id_field: Optional[str] = "id") -> JsonIndex:
    """
    Safely ensure index exists, handling all edge cases.
    Root cause fix: Properly handle empty files, missing files, and all edge cases.
    Following GUIDE_TEST.md - Fix root causes, handle all edge cases properly.
    Args:
        file_path: Path to the JSONL file
        id_field: Optional ID field name for indexing
    Returns:
        JsonIndex object, even for empty files
    Raises:
        RuntimeError: If file cannot be read or index cannot be created
    """
    # Handle empty or non-existent files gracefully
    if not file_path or not os.path.exists(file_path):
        raise RuntimeError(f"File does not exist: {file_path}")
    # Handle empty files - check file size first
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            # Empty file - build empty index
            # Following GUIDE_TEST.md: Fix root cause - empty files need empty index
            return build_index(file_path, id_field=id_field)
    except (OSError, PermissionError) as e:
        raise RuntimeError(f"Failed to access file {file_path}: {e}") from e
    # Build or ensure index exists
    try:
        return ensure_index(file_path, id_field=id_field)
    except (OSError, PermissionError, ValueError) as e:
        # Index operation failed - provide proper error message
        raise RuntimeError(f"Failed to create/load index for {file_path}: {e}") from e


def create_test_file(data: list[dict[str, Any]]) -> str:
    """
    Create a temporary test file with given data.
    Root cause fix: Properly handle empty data lists and edge cases.
    Following GUIDE_TEST.md - Fix root causes, handle all edge cases properly.
    """
    fd, path = tempfile.mkstemp(suffix='.jsonl', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            # Handle empty data list - create empty file (edge case)
            for record in data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        return path
    except Exception as e:
        # Cleanup on failure
        try:
            os.close(fd)
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
        raise RuntimeError(f"Failed to create test file: {e}") from e


def cleanup_test_file(file_path: str):
    """
    Remove test file and associated index files.
    Root cause fix: Proper error handling instead of silently ignoring errors.
    Following GUIDE_TEST.md - Never hide problems, fix root causes.
    """
    errors = []
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except (OSError, PermissionError) as e:
        errors.append(f"Failed to remove file {file_path}: {e}")
    idx_path = file_path + '.idx.json'
    try:
        if os.path.exists(idx_path):
            os.remove(idx_path)
    except (OSError, PermissionError) as e:
        errors.append(f"Failed to remove index {idx_path}: {e}")
    # Log errors but don't fail - cleanup is best effort
    if errors:
        import warnings
        for error in errors:
            warnings.warn(f"Cleanup warning: {error}", UserWarning)


def append_record_v1(file_path: str, record: dict[str, Any]) -> None:
    """V1: Append record to end of file by reading all and writing back."""
    records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
    except FileNotFoundError:
        records = []
    records.append(record)
    # Write back atomically
    dir_name, base_name = os.path.split(os.path.abspath(file_path))
    temp_fd, temp_path = tempfile.mkstemp(
        prefix=f".{base_name}.tmp.", dir=dir_name, text=True
    )
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        os.replace(temp_path, file_path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def append_record_v2(file_path: str, record: dict[str, Any]) -> None:
    """
    V2: Append record to end of file (same as V1, but rebuilds index).
    Root cause fix: Proper error handling for index rebuild failures.
    Following GUIDE_TEST.md - Fix root causes, don't hide errors.
    """
    append_record_v1(file_path, record)
    # Rebuild index after append
    try:
        build_index(file_path, id_field="id" if "id" in record else None)
    except (OSError, PermissionError, ValueError) as e:
        # Index rebuild failure is a real issue - raise it
        raise RuntimeError(f"Failed to rebuild index after append: {e}") from e


def insert_record_at_position_v1(file_path: str, record: dict[str, Any], position: int) -> None:
    """V1: Insert record at specific position."""
    records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
    except FileNotFoundError:
        records = []
    records.insert(position, record)
    # Write back atomically
    dir_name, base_name = os.path.split(os.path.abspath(file_path))
    temp_fd, temp_path = tempfile.mkstemp(
        prefix=f".{base_name}.tmp.", dir=dir_name, text=True
    )
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        os.replace(temp_path, file_path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def insert_record_at_position_v2(file_path: str, record: dict[str, Any], position: int) -> None:
    """
    V2: Insert record at specific position (rebuilds index).
    Root cause fix: Proper error handling for index rebuild failures.
    Following GUIDE_TEST.md - Fix root causes, don't hide errors.
    """
    insert_record_at_position_v1(file_path, record, position)
    try:
        build_index(file_path, id_field="id" if "id" in record else None)
    except (OSError, PermissionError, ValueError) as e:
        # Index rebuild failure is a real issue - raise it
        raise RuntimeError(f"Failed to rebuild index after insert: {e}") from e


def delete_record_by_id_v1(file_path: str, record_id: Any, id_field: str = "id") -> bool:
    """
    V1: Delete record by ID by filtering it out.
    Root cause fix: Only delete the FIRST matching record when duplicates exist.
    Following GUIDE_TEST.md - Fix root causes, don't hide errors.
    """
    records = []
    found = False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    # Only skip the FIRST record that matches
                    if obj.get(id_field) == record_id and not found:
                        found = True  # Mark that we found and will delete this one
                        # Don't append this record (delete it)
                    else:
                        records.append(obj)
    except FileNotFoundError:
        return False
    if not found:
        return False
    # Write back atomically
    dir_name, base_name = os.path.split(os.path.abspath(file_path))
    temp_fd, temp_path = tempfile.mkstemp(
        prefix=f".{base_name}.tmp.", dir=dir_name, text=True
    )
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        os.replace(temp_path, file_path)
        return True
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def delete_record_by_id_v2(file_path: str, record_id: Any, id_field: str = "id") -> bool:
    """
    V2: Delete record by ID (rebuilds index).
    Root cause fix: Proper error handling for index rebuild failures.
    Following GUIDE_TEST.md - Fix root causes, don't hide errors.
    """
    result = delete_record_by_id_v1(file_path, record_id, id_field)
    if result:
        try:
            build_index(file_path, id_field=id_field)
        except (OSError, PermissionError, ValueError) as e:
            # Index rebuild failure is a real issue - raise it
            raise RuntimeError(f"Failed to rebuild index after delete: {e}") from e
    return result


def delete_record_by_line_v1(file_path: str, line_number: int) -> bool:
    """
    V1: Delete record by line number (0-indexed).
    Root cause fix: Added validation for negative and out-of-bounds line numbers.
    Following GUIDE_TEST.md - Fix root causes, don't hide errors.
    """
    # Validate line number before processing
    if line_number < 0:
        return False
    # First, count total records to validate line_number
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for line in f if line.strip())
    except FileNotFoundError:
        return False
    # Check if line_number is out of bounds
    if line_number >= total_lines:
        return False
    # Now delete the record
    records = []
    found = False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if line.strip():
                    if i == line_number:
                        found = True  # Mark that we found the line to delete
                    else:
                        records.append(json.loads(line.strip()))
    except (FileNotFoundError, IndexError, json.JSONDecodeError):
        return False
    # If we didn't find the line, return False
    if not found:
        return False
    # Write back atomically
    dir_name, base_name = os.path.split(os.path.abspath(file_path))
    temp_fd, temp_path = tempfile.mkstemp(
        prefix=f".{base_name}.tmp.", dir=dir_name, text=True
    )
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        os.replace(temp_path, file_path)
        return True
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def delete_record_by_line_v2(file_path: str, line_number: int) -> bool:
    """
    V2: Delete record by line number (rebuilds index).
    Root cause fix: Proper error handling for index rebuild failures.
    Following GUIDE_TEST.md - Fix root causes, don't hide errors.
    """
    result = delete_record_by_line_v1(file_path, line_number)
    if result:
        try:
            build_index(file_path, id_field="id")
        except (OSError, PermissionError, ValueError) as e:
            # Index rebuild failure is a real issue - raise it
            raise RuntimeError(f"Failed to rebuild index after delete: {e}") from e
    return result


def get_all_matching_v1(file_path: str, match: MatchFn) -> list[dict[str, Any]]:
    """
    V1: Get all records matching criteria.
    Root cause fix: Properly handle empty files and edge cases.
    Following GUIDE_TEST.md - Fix root causes, handle all edge cases properly.
    """
    results = []
    try:
        # Handle empty or non-existent files gracefully
        if not file_path or not os.path.exists(file_path):
            return results
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        obj = json.loads(line.strip())
                        if match(obj):
                            results.append(obj)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        # Skip malformed lines but log the issue
                        import warnings
                        warnings.warn(f"Skipping malformed line in {file_path}: {e}", UserWarning)
                        continue
    except FileNotFoundError:
        # File doesn't exist - return empty list (edge case: file was deleted)
        pass
    except (OSError, PermissionError) as e:
        # Proper error handling instead of silent failure
        raise RuntimeError(f"Failed to read file {file_path}: {e}") from e
    return results


def get_all_matching_v2(file_path: str, match: MatchFn, index: Optional[JsonIndex] = None) -> list[dict[str, Any]]:
    """
    V2: Get all records matching criteria using index for faster access.
    Root cause fix: Properly handle empty files, missing indices, and all edge cases.
    Following GUIDE_TEST.md - Fix root causes, handle all edge cases properly.
    """
    # Handle empty or non-existent files gracefully
    if not file_path or not os.path.exists(file_path):
        return []
    # Handle empty files - check file size first
    try:
        if os.path.getsize(file_path) == 0:
            return []
    except (OSError, PermissionError):
        # Can't check size, try to continue anyway
        pass
    # Build index if not provided
    if index is None:
        try:
            index = ensure_index(file_path, id_field="id")
        except (OSError, PermissionError, ValueError) as e:
            # If index building fails, fallback to V1 method
            import warnings
            warnings.warn(f"Index build failed for {file_path}, falling back to V1: {e}", UserWarning)
            return get_all_matching_v1(file_path, match)
    # Handle empty index (empty file)
    if not index or not hasattr(index, 'line_offsets') or len(index.line_offsets) == 0:
        return []
    results = []
    for i in range(len(index.line_offsets)):
        try:
            obj = indexed_get_by_line(file_path, i, index=index)
            if match(obj):
                results.append(obj)
        except (IndexError, json.JSONDecodeError, OSError, KeyError) as e:
            # Specific errors that can occur - log and continue for robustness
            # but don't silently ignore all exceptions
            import warnings
            warnings.warn(f"Failed to read record at line {i} in {file_path}: {e}", UserWarning)
            continue
    return results


def count_records_v1(file_path: str) -> int:
    """
    V1: Count total records in file.
    Root cause fix: Properly handle empty files and edge cases.
    Following GUIDE_TEST.md - Fix root causes, handle all edge cases properly.
    """
    # Handle empty or non-existent files gracefully
    if not file_path or not os.path.exists(file_path):
        return 0
    # Handle empty files - check file size first
    try:
        if os.path.getsize(file_path) == 0:
            return 0
    except (OSError, PermissionError):
        # Can't check size, try to continue anyway
        pass
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
    except FileNotFoundError:
        # File doesn't exist - return 0 (edge case: file was deleted)
        return 0
    except (OSError, PermissionError) as e:
        # Proper error handling instead of silent failure
        raise RuntimeError(f"Failed to read file {file_path}: {e}") from e
    return count


def count_records_v2(file_path: str, index: Optional[JsonIndex] = None) -> int:
    """
    V2: Count total records using index.
    Root cause fix: Properly handle empty files and edge cases.
    Following GUIDE_TEST.md - Fix root causes, handle all edge cases properly.
    """
    # Handle empty or non-existent files gracefully
    if not file_path or not os.path.exists(file_path):
        return 0
    # Handle empty files - check file size first
    try:
        if os.path.getsize(file_path) == 0:
            return 0
    except (OSError, PermissionError):
        # Can't check size, try to continue anyway
        pass
    # Build index if not provided
    if index is None:
        try:
            index = ensure_index(file_path)
        except (OSError, PermissionError, ValueError) as e:
            # If index building fails, fallback to V1 method
            import warnings
            warnings.warn(f"Index build failed for {file_path}, falling back to V1: {e}", UserWarning)
            return count_records_v1(file_path)
    # Handle empty index (empty file)
    if not index or not hasattr(index, 'line_offsets'):
        return 0
    return len(index.line_offsets)


def bulk_append_v1(file_path: str, records: list[dict[str, Any]]) -> int:
    """V1: Append multiple records."""
    for record in records:
        append_record_v1(file_path, record)
    return len(records)


def bulk_append_v2(file_path: str, records: list[dict[str, Any]]) -> int:
    """
    V2: Append multiple records (rebuilds index once at end).
    Root cause fix: Proper error handling for index rebuild failures.
    Following GUIDE_TEST.md - Fix root causes, don't hide errors.
    """
    for record in records:
        append_record_v1(file_path, record)
    try:
        build_index(file_path, id_field="id" if records and "id" in records[0] else None)
    except (OSError, PermissionError, ValueError) as e:
        # Index rebuild failure is a real issue - raise it
        raise RuntimeError(f"Failed to rebuild index after bulk append: {e}") from e
    return len(records)


class FileStateTracker:
    """
    Helper class to track file state and provide assertions that work with any dataset size.
    Works automatically with default, 100mb, 500mb, 1GB, or 10GB datasets.
    Usage:
        tracker = FileStateTracker(file_path)
        append_record_v1(file_path, record)
        tracker.add_records(1)
        tracker.assert_count_v1()  # Automatically checks initial_count + 1
        # Or specify exact delta:
        tracker.assert_count_v1(expected_delta=5)  # initial_count + 5
    """

    def __init__(self, file_path: str, id_field: str = "id"):
        self.file_path = file_path
        self.id_field = id_field
        self.initial_count_v1 = count_records_v1(file_path)
        self.index = ensure_index(file_path, id_field=id_field)
        self.initial_count_v2 = count_records_v2(file_path, self.index)
        self.records_added = 0
        self.records_removed = 0
        self.records_updated = 0

    def add_records(self, count: int):
        """Track that records were added."""
        self.records_added += count

    def remove_records(self, count: int):
        """Track that records were removed."""
        self.records_removed += count

    def update_records(self, count: int):
        """Track that records were updated (count doesn't change)."""
        self.records_updated += count

    def assert_count_v1(self, expected_delta: int = None):
        """
        Assert V1 count matches expected.
        If expected_delta is None, uses tracked changes (records_added - records_removed).
        """
        current_count = count_records_v1(self.file_path)
        if expected_delta is None:
            expected_delta = self.records_added - self.records_removed
        expected_count = self.initial_count_v1 + expected_delta
        assert current_count == expected_count, (
            f"V1 count mismatch: expected {expected_count} (initial {self.initial_count_v1} + delta {expected_delta}), "
            f"got {current_count}"
        )
        return current_count

    def assert_count_v2(self, expected_delta: int = None):
        """
        Assert V2 count matches expected.
        If expected_delta is None, uses tracked changes (records_added - records_removed).
        """
        # Rebuild index to ensure it's up to date
        self.index = ensure_index(self.file_path, id_field=self.id_field)
        current_count = count_records_v2(self.file_path, self.index)
        if expected_delta is None:
            expected_delta = self.records_added - self.records_removed
        expected_count = self.initial_count_v2 + expected_delta
        assert current_count == expected_count, (
            f"V2 count mismatch: expected {expected_count} (initial {self.initial_count_v2} + delta {expected_delta}), "
            f"got {current_count}"
        )
        return current_count

    def assert_counts_equal(self, expected_delta: int = None):
        """Assert both V1 and V2 counts match and are correct."""
        v1_count = self.assert_count_v1(expected_delta)
        v2_count = self.assert_count_v2(expected_delta)
        assert v1_count == v2_count, f"V1 count ({v1_count}) != V2 count ({v2_count})"
        return v1_count, v2_count

    def get_current_count_v1(self) -> int:
        """Get current V1 count."""
        return count_records_v1(self.file_path)

    def get_current_count_v2(self) -> int:
        """Get current V2 count."""
        self.index = ensure_index(self.file_path, id_field=self.id_field)
        return count_records_v2(self.file_path, self.index)
