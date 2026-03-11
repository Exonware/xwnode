#!/usr/bin/env python3
"""
#exonware/xwnode/scripts/add_file_headers.py
Add file headers to strategy files that are missing them.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
# File header template
HEADER_TEMPLATE = '''#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/{filename}
{description}
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: {date}
"""
'''


def get_strategy_description(filename: str) -> str:
    """Get description for strategy based on filename."""
    # Map common strategy names to descriptions
    descriptions = {
        'array_list': 'Array List Node Strategy Implementation',
        'stack': 'Stack Node Strategy Implementation',
        'queue': 'Queue Node Strategy Implementation',
        'deque': 'Deque Node Strategy Implementation',
        'linked_list': 'Linked List Node Strategy Implementation',
        'trie': 'Trie Node Strategy Implementation',
        'radix_trie': 'Radix Trie Node Strategy Implementation',
        'patricia': 'Patricia Trie Node Strategy Implementation',
        'heap': 'Heap Node Strategy Implementation',
        'set_hash': 'Set Hash Node Strategy Implementation',
        'set_tree': 'Set Tree Node Strategy Implementation',
        'bloom_filter': 'Bloom Filter Node Strategy Implementation',
        'bitmap': 'Bitmap Node Strategy Implementation',
        'bitset_dynamic': 'Dynamic Bitset Node Strategy Implementation',
        'roaring_bitmap': 'Roaring Bitmap Node Strategy Implementation',
        'sparse_matrix': 'Sparse Matrix Node Strategy Implementation',
        'b_tree': 'B-Tree Node Strategy Implementation',
        'b_plus_tree': 'B+ Tree Node Strategy Implementation',
        'lsm_tree': 'LSM Tree Node Strategy Implementation',
        'union_find': 'Union-Find Node Strategy Implementation',
        'segment_tree': 'Segment Tree Node Strategy Implementation',
        'fenwick_tree': 'Fenwick Tree Node Strategy Implementation',
        'skip_list': 'Skip List Node Strategy Implementation',
        'red_black_tree': 'Red-Black Tree Node Strategy Implementation',
        'avl_tree': 'AVL Tree Node Strategy Implementation',
        'treap': 'Treap Node Strategy Implementation',
        'splay_tree': 'Splay Tree Node Strategy Implementation',
        'art': 'Adaptive Radix Tree (ART) Node Strategy Implementation',
        'bw_tree': 'Bw-Tree Node Strategy Implementation',
        'hamt': 'Hash Array Mapped Trie (HAMT) Node Strategy Implementation',
        'masstree': 'Masstree Node Strategy Implementation',
        'extendible_hash': 'Extendible Hash Node Strategy Implementation',
        'linear_hash': 'Linear Hash Node Strategy Implementation',
        'cuckoo_hash': 'Cuckoo Hash Node Strategy Implementation',
        'hopscotch_hash': 'Hopscotch Hash Node Strategy Implementation',
        'ordered_map': 'Ordered Map Node Strategy Implementation',
        'ordered_map_balanced': 'Ordered Map Balanced Node Strategy Implementation',
        'lru_cache': 'LRU Cache Node Strategy Implementation',
        'circular_buffer': 'Circular Buffer Node Strategy Implementation',
    }
    base_name = filename.replace('.py', '').replace('_strategy', '')
    return descriptions.get(base_name, f'{base_name.replace("_", " ").title()} Node Strategy Implementation')


def has_header(file_path: Path) -> bool:
    """Check if file already has a proper header."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = ''.join(f.readlines()[:10])
            return '#exonware/xwnode' in first_lines or 'Company: eXonware.com' in first_lines
    except Exception:
        return False


def add_header_to_file(file_path: Path) -> Tuple[bool, str]:
    """Add header to file if missing."""
    if has_header(file_path):
        return False, "Already has header"
    try:
        # Read existing content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Generate header
        filename = file_path.name
        description = get_strategy_description(filename)
        header = HEADER_TEMPLATE.format(
            filename=filename,
            description=description,
            date=datetime.now().strftime('%d-%b-%Y')
        )
        # Add header
        new_content = header + content
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "Header added"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Add headers to all strategy files."""
    strategies_dir = Path(__file__).parent.parent / "src" / "exonware" / "xwnode" / "nodes" / "strategies"
    if not strategies_dir.exists():
        print(f"Error: Strategies directory not found: {strategies_dir}")
        return 1
    print("=" * 60)
    print("Adding File Headers to Strategy Files")
    print("=" * 60)
    strategy_files = sorted([f for f in strategies_dir.glob("*.py") if f.name != "__init__.py" and f.name != "base.py" and f.name != "contracts.py"])
    print(f"\nFound {len(strategy_files)} strategy files")
    added = 0
    skipped = 0
    errors = 0
    for strategy_file in strategy_files:
        success, message = add_header_to_file(strategy_file)
        if success:
            print(f"  [ADDED] {strategy_file.name}")
            added += 1
        elif "Already has header" in message:
            skipped += 1
        else:
            print(f"  [ERROR] {strategy_file.name}: {message}")
            errors += 1
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Added headers: {added}")
    print(f"  Already had headers: {skipped}")
    print(f"  Errors: {errors}")
    print("=" * 60)
    return 0 if errors == 0 else 1
if __name__ == "__main__":
    sys.exit(main())
