#!/usr/bin/env python3
"""
Quick test: Generate a 100MB NDJSON file to test the system works.
"""

import sys
from pathlib import Path
# Import the main generator
from generate_1gb_file import generate_1gb_ndjson
if __name__ == "__main__":
    output_file = Path(__file__).parent / "data" / "database_100mb.jsonl"
    output_file.parent.mkdir(exist_ok=True)
    print("Generating 100MB test file...")
    generate_1gb_ndjson(str(output_file), target_size_gb=0.1)
