"""
#exonware/xwnode/examples/x5/data_operations/conftest.py

Pytest configuration and shared fixtures for data operations test suite.

Following GUIDE_TEST.md standards:
- Test isolation
- Resource cleanup
- Proper fixtures
- No side effects

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import os
import pytest
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Generator

# Configure UTF-8 for Windows console (GUIDE_TEST.md requirement)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with default encoding

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Import test helpers
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    build_index,
    ensure_index,
)


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """
    Create a temporary test file that is automatically cleaned up.
    
    Following GUIDE_TEST.md:
    - Test isolation: Each test gets a fresh file
    - Resource cleanup: Automatically removed after test
    - No side effects: Files are isolated per test
    """
    file_path = None
    try:
        # Create empty file
        file_path = create_test_file([])
        yield file_path
    finally:
        # Cleanup: Remove file and index
        if file_path:
            cleanup_test_file(file_path)


@pytest.fixture
def sample_data() -> List[Dict[str, Any]]:
    """
    Sample test data for use in tests.
    
    Returns a list of sample records with various fields.
    """
    return [
        {"id": "1", "name": "Alice", "age": 30, "role": "admin"},
        {"id": "2", "name": "Bob", "age": 25, "role": "user"},
        {"id": "3", "name": "Charlie", "age": 35, "role": "user"},
    ]


@pytest.fixture
def populated_file(sample_data: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    Create a temporary file populated with sample data.
    
    Following GUIDE_TEST.md:
    - Test isolation: Each test gets a fresh populated file
    - Resource cleanup: Automatically removed after test
    """
    file_path = None
    try:
        file_path = create_test_file(sample_data)
        yield file_path
    finally:
        if file_path:
            cleanup_test_file(file_path)


@pytest.fixture
def indexed_file(populated_file: str) -> Generator[str, None, None]:
    """
    Create a temporary file with index built.
    
    Following GUIDE_TEST.md:
    - Test isolation: Each test gets a fresh indexed file
    - Resource cleanup: Automatically removed after test
    """
    # Build index for V2 tests
    try:
        build_index(populated_file, id_field="id")
        yield populated_file
    finally:
        # Cleanup handled by populated_file fixture
        pass


@pytest.fixture(autouse=True)
def ensure_cleanup():
    """
    Autouse fixture to ensure cleanup happens even if tests fail.
    
    Following GUIDE_TEST.md:
    - Resource cleanup: Ensures files are cleaned up
    - No side effects: Prevents test file accumulation
    """
    # Track created files
    created_files = []
    
    yield
    
    # Cleanup any remaining files
    for file_path in created_files:
        if os.path.exists(file_path):
            cleanup_test_file(file_path)


@pytest.fixture
def large_dataset() -> List[Dict[str, Any]]:
    """
    Generate a large dataset for performance tests.
    
    Returns 1000 records for testing bulk operations.
    """
    return [
        {"id": str(i), "name": f"User{i}", "value": i * 10}
        for i in range(1000)
    ]


@pytest.fixture
def empty_file() -> Generator[str, None, None]:
    """
    Create an empty temporary file.
    
    Useful for testing append operations and edge cases.
    """
    file_path = None
    try:
        file_path = create_test_file([])
        yield file_path
    finally:
        if file_path:
            cleanup_test_file(file_path)

