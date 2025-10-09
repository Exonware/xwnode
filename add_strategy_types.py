#!/usr/bin/env python3
"""
Add STRATEGY_TYPE to All Node Strategies

This script automatically adds STRATEGY_TYPE declarations to all node strategy files
based on the inheritance audit.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 08-Oct-2025
"""

import re
from pathlib import Path
from typing import Dict

# Map strategy files to their NodeType
STRATEGY_TYPE_MAP = {
    # LINEAR
    'array_list.py': 'LINEAR',
    'linked_list.py': 'LINEAR',
    'stack.py': 'LINEAR',
    'queue.py': 'LINEAR',
    'deque.py': 'LINEAR',
    'priority_queue.py': 'LINEAR',
    'node_array_list.py': 'LINEAR',
    'node_linked_list.py': 'LINEAR',
    
    # TREE (already has hash_map.py done)
    'heap.py': 'TREE',
    'trie.py': 'TREE',
    'aho_corasick.py': 'TREE',
    'union_find.py': 'GRAPH',  # Actually graph
    'node_aho_corasick.py': 'TREE',
    'node_avl_tree.py': 'TREE',
    'node_b_plus_tree.py': 'TREE',
    'node_btree.py': 'TREE',
    'node_cow_tree.py': 'TREE',
    'node_fenwick_tree.py': 'TREE',
    'node_hash_map.py': 'TREE',
    'node_heap.py': 'TREE',
    'node_lsm_tree.py': 'TREE',
    'node_ordered_map.py': 'TREE',
    'node_ordered_map_balanced.py': 'TREE',
    'node_patricia.py': 'TREE',
    'node_persistent_tree.py': 'TREE',
    'node_radix_trie.py': 'TREE',
    'node_red_black_tree.py': 'TREE',
    'node_segment_tree.py': 'TREE',
    'node_skip_list.py': 'TREE',
    'node_splay_tree.py': 'TREE',
    'node_suffix_array.py': 'TREE',
    'node_treap.py': 'TREE',
    'node_trie.py': 'TREE',
    'node_union_find.py': 'GRAPH',
    
    # MATRIX
    'sparse_matrix.py': 'MATRIX',
    'node_bitmap.py': 'MATRIX',
    'node_bitset_dynamic.py': 'MATRIX',
    'node_roaring_bitmap.py': 'MATRIX',
    'node_bloom_filter.py': 'MATRIX',
    'node_count_min_sketch.py': 'MATRIX',
    'node_hyperloglog.py': 'MATRIX',
    'node_set_hash.py': 'MATRIX',
    'node_set_tree.py': 'TREE',  # Can be tree
    
    # HYBRID
    'node_tree_graph_hybrid.py': 'HYBRID',
    'node_xdata_optimized.py': 'HYBRID',
    
    # Special (probably edges, but in nodes folder)
    'adjacency_list.py': 'GRAPH',
}


def add_strategy_type_to_file(file_path: Path, node_type: str) -> bool:
    """Add STRATEGY_TYPE to a strategy file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if STRATEGY_TYPE already exists
        if 'STRATEGY_TYPE' in content:
            print(f"  ⏭️  Already has STRATEGY_TYPE: {file_path.name}")
            return False
        
        # Find class definition
        class_match = re.search(r'(class \w+Strategy\([^)]+\):\s*\n\s*"""[^"]*""")', content, re.MULTILINE)
        if not class_match:
            print(f"  ⚠️  Could not find class definition: {file_path.name}")
            return False
        
        # Add import if not present
        if 'from .contracts import NodeType' not in content:
            # Find where to add import (after other local imports)
            if 'from .base import' in content:
                content = content.replace(
                    'from .base import',
                    'from .base import'
                )
                # Add after base import
                import_pos = content.find('from .base import')
                line_end = content.find('\n', import_pos)
                content = content[:line_end+1] + 'from .contracts import NodeType\n' + content[line_end+1:]
        
        # Add STRATEGY_TYPE after class docstring
        class_end = class_match.end()
        
        # Add STRATEGY_TYPE declaration
        strategy_type_line = f'\n    \n    # Strategy type classification\n    STRATEGY_TYPE = NodeType.{node_type}\n'
        content = content[:class_end] + strategy_type_line + content[class_end:]
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Added STRATEGY_TYPE.{node_type}: {file_path.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path.name}: {e}")
        return False


def main():
    """Main function."""
    print("="*70)
    print("Adding STRATEGY_TYPE to All Node Strategies")
    print("="*70)
    
    base_path = Path(__file__).parent / 'src' / 'exonware' / 'xwnode' / 'nodes' / 'strategies'
    
    count_added = 0
    count_skipped = 0
    count_errors = 0
    
    for filename, node_type in STRATEGY_TYPE_MAP.items():
        file_path = base_path / filename
        
        if not file_path.exists():
            print(f"  ⚠️  File not found: {filename}")
            count_errors += 1
            continue
        
        result = add_strategy_type_to_file(file_path, node_type)
        if result:
            count_added += 1
        elif 'Already has' in str(result):
            count_skipped += 1
        else:
            count_errors += 1
    
    print("\n" + "="*70)
    print(f"Summary: {count_added} added, {count_skipped} skipped, {count_errors} errors")
    print("="*70)


if __name__ == '__main__':
    main()
