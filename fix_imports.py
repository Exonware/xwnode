#!/usr/bin/env python3
"""
Fix Import Statements After Refactoring

This script fixes all import statements after moving files from strategies/ to common/.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 08-Oct-2025
"""

import re
from pathlib import Path
from typing import List, Tuple


# Define import replacements
REPLACEMENTS = [
    # Fix common/ files - relative imports need to go up more levels
    (r'from \.nodes\.', 'from ...nodes.strategies.'),
    (r'from \.edges\.', 'from ...edges.strategies.'),
    (r'from \.queries\.', 'from ...queries.strategies.'),
    
    # Fix src/ files - update to common path
    (r'from \.strategies\.simple import', 'from .common.utils.simple import'),
    (r'from \.strategies\.flyweight import', 'from .common.patterns.flyweight import'),
    (r'from \.strategies\.registry import', 'from .common.patterns.registry import'),
    (r'from \.strategies\.manager import', 'from .common.management.manager import'),
    (r'from \.strategies\.advisor import', 'from .common.patterns.advisor import'),
    (r'from \.strategies\.metrics import', 'from .common.monitoring.metrics import'),
    (r'from \.strategies\.pattern_detector import', 'from .common.monitoring.pattern_detector import'),
    (r'from \.strategies\.performance_monitor import', 'from .common.monitoring.performance_monitor import'),
    (r'from \.strategies\.migration import', 'from .common.management.migration import'),
    (r'from \.strategies\.utils import', 'from .common.utils.utils import'),
]


def fix_imports_in_file(file_path: Path) -> Tuple[bool, int]:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        for old_pattern, new_pattern in REPLACEMENTS:
            new_content, count = re.subn(old_pattern, new_pattern, content)
            if count > 0:
                content = new_content
                changes_made += count
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        
        return False, 0
        
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False, 0


def fix_imports_in_directory(directory: Path, pattern: str = "*.py") -> Tuple[int, int]:
    """Fix imports in all Python files in a directory."""
    files_changed = 0
    total_changes = 0
    
    for py_file in directory.rglob(pattern):
        if '__pycache__' in str(py_file):
            continue
        
        changed, count = fix_imports_in_file(py_file)
        if changed:
            files_changed += 1
            total_changes += count
            rel_path = py_file.relative_to(directory.parent)
            print(f"  Fixed: {rel_path} ({count} changes)")
    
    return files_changed, total_changes


def main():
    """Main function to fix all imports."""
    print("="*70)
    print("Fixing Import Statements After Refactoring")
    print("="*70)
    
    base_path = Path(__file__).parent / 'src' / 'exonware' / 'xwnode'
    print(f"\nBase path: {base_path}\n")
    
    # Phase 1: Fix common/ files
    print("Phase 1: Fixing common/ imports")
    print("-"*70)
    common_path = base_path / 'common'
    files_changed, total_changes = fix_imports_in_directory(common_path)
    print(f"  Result: {files_changed} files changed, {total_changes} import statements fixed\n")
    
    # Phase 2: Fix root src/ files (facade.py, base.py)
    print("Phase 2: Fixing root src/ files")
    print("-"*70)
    root_files = [base_path / 'facade.py', base_path / 'base.py']
    root_changed = 0
    root_total = 0
    for file_path in root_files:
        if file_path.exists():
            changed, count = fix_imports_in_file(file_path)
            if changed:
                root_changed += 1
                root_total += count
                print(f"  Fixed: {file_path.name} ({count} changes)")
    print(f"  Result: {root_changed} files changed, {root_total} import statements fixed\n")
    
    # Phase 3: Check nodes/, edges/, queries/ (should be OK already)
    print("Phase 3: Checking nodes/, edges/, queries/")
    print("-"*70)
    for domain in ['nodes', 'edges', 'queries']:
        domain_path = base_path / domain
        if domain_path.exists():
            files_changed, total_changes = fix_imports_in_directory(domain_path)
            if files_changed > 0:
                print(f"  {domain}/: {files_changed} files changed, {total_changes} fixes")
            else:
                print(f"  {domain}/: No changes needed (already correct)")
    
    # Summary
    print("\n" + "="*70)
    print("Import Fixes Complete!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review changed files")
    print("  2. Run tests: python -m pytest tests/")
    print("  3. Check for any remaining import errors")
    print("")


if __name__ == '__main__':
    main()
