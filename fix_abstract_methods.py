"""Script to add missing abstract methods to all incomplete node strategies."""
import re
import sys
from pathlib import Path

STRATEGIES_DIR = Path("src/exonware/xwnode/nodes/strategies")

# Template for tree strategies (extends ANodeTreeStrategy -> ANodeGraphStrategy)
# These need: graph methods + traverse + get_min + get_max + conversion methods
TREE_GRAPH_METHODS = '''
    # --- Abstract method implementations (graph operations not supported) ---

    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def find_path(self, start: Any, end: Any) -> list[Any]:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph paths")

    def get_neighbors(self, node: Any) -> list[Any]:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph neighbors")

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")
'''

TREE_CONVERSION_METHODS = '''
    # --- Abstract method implementations (conversion views not supported) ---

    def as_union_find(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support union-find view")

    def as_neural_graph(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support neural graph view")

    def as_flow_network(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support flow network view")

    def as_trie(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support trie view")

    def as_heap(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support heap view")

    def as_skip_list(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support skip list view")
'''

TREE_TRAVERSE_METHODS = '''
    # --- Abstract method implementations (tree traversal) ---

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """Traverse - returns all key-value pairs."""
        return list(self.items())

    def get_min(self) -> Any:
        """Get minimum key."""
        keys = list(self.keys())
        if not keys:
            return None
        return min(keys)

    def get_max(self) -> Any:
        """Get maximum key."""
        keys = list(self.keys())
        if not keys:
            return None
        return max(keys)
'''

# For linear strategies (QueueStrategy)
LINEAR_METHODS = '''
    # --- Abstract method implementations (linear operations) ---

    def push_front(self, value: Any) -> None:
        """Add element to front of queue."""
        self._data.appendleft(value)

    def push_back(self, value: Any) -> None:
        """Add element to back of queue."""
        self._data.append(value)

    def pop_front(self) -> Any:
        """Remove and return element from front."""
        if not self._data:
            return None
        return self._data.popleft()

    def pop_back(self) -> Any:
        """Remove and return element from back."""
        if not self._data:
            return None
        return self._data.pop()

    def get_at_index(self, index: int) -> Any:
        """Get element at index."""
        if 0 <= index < len(self._data):
            return self._data[index]
        return None

    def set_at_index(self, index: int, value: Any) -> None:
        """Set element at index."""
        if 0 <= index < len(self._data):
            self._data[index] = value

    def as_linked_list(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError("QueueStrategy does not support linked list view")

    def as_stack(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError("QueueStrategy does not support stack view")

    def as_queue(self):
        """Return self as queue view."""
        return self

    def as_deque(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError("QueueStrategy does not support deque view")
'''


def has_method(content: str, method_name: str) -> bool:
    """Check if a method is defined in the class (not just inherited)."""
    return bool(re.search(rf'^\s+def {method_name}\s*\(', content, re.MULTILINE))


def ensure_import(content: str, import_name: str, from_module: str) -> str:
    """Ensure an import exists in the file."""
    if import_name in content:
        return content
    # Find a good place to add it - after existing imports from same module
    pattern = rf'(from {re.escape(from_module)} import [^\n]+)'
    match = re.search(pattern, content)
    if match:
        old = match.group(0)
        if import_name not in old:
            new = old.rstrip() + f', {import_name}' if not old.endswith(')') else old
            # Actually just add a new import line
            content = content.replace(old, old + f'\nfrom {from_module} import {import_name}', 1)
    return content


def find_class_end(content: str, class_name: str) -> int:
    """Find the end of a class definition (before the next class or end of file)."""
    # Find the class definition
    class_pattern = rf'^class {class_name}\b'
    class_match = re.search(class_pattern, content, re.MULTILINE)
    if not class_match:
        return -1

    start = class_match.start()
    # Find the next class definition or end of file
    next_class = re.search(r'^class \w+', content[start + 1:], re.MULTILINE)
    if next_class:
        return start + 1 + next_class.start()
    return len(content)


def fix_tree_strategy(filepath: Path, missing_methods: list[str]) -> bool:
    """Add missing abstract methods to a tree strategy."""
    content = filepath.read_text(encoding='utf-8')
    original = content

    # Ensure XWNodeUnsupportedCapabilityError is imported
    if 'XWNodeUnsupportedCapabilityError' not in content:
        # Find the imports section
        # Look for existing error imports
        if 'from ...errors import' in content:
            match = re.search(r'from \.\.\.errors import ([^\n]+)', content)
            if match and 'XWNodeUnsupportedCapabilityError' not in match.group(1):
                old = match.group(0)
                new = old.rstrip() + ', XWNodeUnsupportedCapabilityError'
                content = content.replace(old, new, 1)
        else:
            # Add after the last import
            last_import = None
            for m in re.finditer(r'^(?:from|import) .+$', content, re.MULTILINE):
                last_import = m
            if last_import:
                content = content[:last_import.end()] + '\nfrom ...errors import XWNodeUnsupportedCapabilityError' + content[last_import.end():]

    # Ensure 'Any' is imported from typing
    if 'Any' not in content:
        if 'from typing import' in content:
            match = re.search(r'from typing import ([^\n]+)', content)
            if match:
                old = match.group(0)
                content = content.replace(old, old + ', Any', 1)
        else:
            last_import = None
            for m in re.finditer(r'^(?:from|import) .+$', content, re.MULTILINE):
                last_import = m
            if last_import:
                content = content[:last_import.end()] + '\nfrom typing import Any' + content[last_import.end():]

    # Build the methods to add
    methods_to_add = ""

    # Check which groups of methods are missing
    graph_methods = {'add_edge', 'remove_edge', 'has_edge', 'find_path', 'get_neighbors', 'get_edge_weight'}
    conversion_methods = {'as_union_find', 'as_neural_graph', 'as_flow_network', 'as_trie', 'as_heap', 'as_skip_list'}
    tree_methods = {'traverse', 'get_min', 'get_max'}

    missing_set = set(missing_methods)

    if missing_set & graph_methods:
        # Only add the ones actually missing
        for method in ['add_edge', 'remove_edge', 'has_edge', 'find_path', 'get_neighbors', 'get_edge_weight']:
            if method in missing_set and not has_method(content, method):
                # Extract individual method from template
                pattern = rf'    def {method}\(.*?\n(?:        .*\n)*'
                match = re.search(pattern, TREE_GRAPH_METHODS)
                if match:
                    methods_to_add += match.group(0) + '\n'

    if missing_set & tree_methods:
        for method in ['traverse', 'get_min', 'get_max']:
            if method in missing_set and not has_method(content, method):
                pattern = rf'    def {method}\(.*?\n(?:        .*\n)*'
                match = re.search(pattern, TREE_TRAVERSE_METHODS)
                if match:
                    methods_to_add += match.group(0) + '\n'

    if missing_set & conversion_methods:
        for method in ['as_union_find', 'as_neural_graph', 'as_flow_network', 'as_trie', 'as_heap', 'as_skip_list']:
            if method in missing_set and not has_method(content, method):
                pattern = rf'    def {method}\(.*?\n(?:        .*\n)*'
                match = re.search(pattern, TREE_CONVERSION_METHODS)
                if match:
                    methods_to_add += match.group(0) + '\n'

    if not methods_to_add:
        return False

    # Find the end of file (before any trailing whitespace)
    content = content.rstrip() + '\n\n' + methods_to_add.rstrip() + '\n'

    filepath.write_text(content, encoding='utf-8')
    return content != original


# Strategy configs: (filename, missing_methods, strategy_type)
STRATEGIES = {
    # Tree strategies (extend ANodeTreeStrategy)
    'bloomier_filter': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'crdt_map': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'dawg': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'hopscotch_hash': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'interval_tree': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'kd_tree': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'radix_trie': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'red_black_tree': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'rope': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'segment_tree': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'set_tree': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'skip_list': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'splay_tree': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'suffix_array': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_max', 'get_min', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'treap': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
    'trie': ['add_edge', 'as_flow_network', 'as_neural_graph', 'as_union_find', 'find_path', 'get_edge_weight', 'get_neighbors', 'has_edge', 'remove_edge'],
    'veb_tree': ['add_edge', 'as_flow_network', 'as_heap', 'as_neural_graph', 'as_skip_list', 'as_trie', 'as_union_find', 'find_path', 'get_edge_weight', 'get_neighbors', 'has_edge', 'remove_edge', 'traverse'],
}


def main():
    fixed = []
    errors = []

    for strategy_file, missing in STRATEGIES.items():
        filepath = STRATEGIES_DIR / f"{strategy_file}.py"
        if not filepath.exists():
            errors.append(f"  NOT FOUND: {filepath}")
            continue
        try:
            if fix_tree_strategy(filepath, missing):
                fixed.append(strategy_file)
                print(f"  FIXED: {strategy_file} ({len(missing)} methods)")
            else:
                print(f"  SKIP: {strategy_file} (already has methods)")
        except Exception as e:
            errors.append(f"  ERROR: {strategy_file}: {e}")

    print(f"\nFixed {len(fixed)} strategies")
    if errors:
        print("Errors:")
        for e in errors:
            print(e)


if __name__ == "__main__":
    main()
