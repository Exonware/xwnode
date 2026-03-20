"""
Test scale configuration - reduces iterations for faster CI/local runs.
Set XWNODE_TEST_SCALE=1 for full stress tests.
Default 0.01: 100000->1000, 10000->100, 1000->10
"""
import os

_FACTOR = float(os.environ.get("XWNODE_TEST_SCALE", "0.01"))


def scaled(n: int) -> int:
    """Scale down large test sizes dynamically."""
    return max(10, int(n * _FACTOR))


# Precomputed common sizes
STRESS_SIZE = scaled(100000)
LARGE_SIZE = scaled(10000)
MEDIUM_SIZE = scaled(1000)
