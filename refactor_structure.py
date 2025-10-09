#!/usr/bin/env python3
"""
Refactoring Script for xwnode Structure Reorganization

This script moves files from strategies/ to common/ and updates imports.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 08-Oct-2025
"""

import os
import shutil
import re
from pathlib import Path


# Define file moves (source -> destination)
MOVES = {
    # Patterns
    'strategies/flyweight.py': 'common/patterns/flyweight.py',
    'strategies/registry.py': 'common/patterns/registry.py',
    'strategies/advisor.py': 'common/patterns/advisor.py',
    
    # Monitoring
    'strategies/metrics.py': 'common/monitoring/metrics.py',
    'strategies/performance_monitor.py': 'common/monitoring/performance_monitor.py',
    'strategies/pattern_detector.py': 'common/monitoring/pattern_detector.py',
    
    # Management
    'strategies/manager.py': 'common/management/manager.py',
    'strategies/migration.py': 'common/management/migration.py',
    
    # Utils
    'strategies/utils.py': 'common/utils/utils.py',
    'strategies/simple.py': 'common/utils/simple.py',
}


# Import replacements
IMPORT_REPLACEMENTS = [
    # Old strategies imports -> new common imports
    (r'from exonware\.xwnode\.strategies\.flyweight import', 'from exonware.xwnode.common.patterns.flyweight import'),
    (r'from exonware\.xwnode\.strategies\.registry import', 'from exonware.xwnode.common.patterns.registry import'),
    (r'from exonware\.xwnode\.strategies\.advisor import', 'from exonware.xwnode.common.patterns.advisor import'),
    (r'from exonware\.xwnode\.strategies\.metrics import', 'from exonware.xwnode.common.monitoring.metrics import'),
    (r'from exonware\.xwnode\.strategies\.performance_monitor import', 'from exonware.xwnode.common.monitoring.performance_monitor import'),
    (r'from exonware\.xwnode\.strategies\.pattern_detector import', 'from exonware.xwnode.common.monitoring.pattern_detector import'),
    (r'from exonware\.xwnode\.strategies\.manager import', 'from exonware.xwnode.common.management.manager import'),
    (r'from exonware\.xwnode\.strategies\.migration import', 'from exonware.xwnode.common.management.migration import'),
    (r'from exonware\.xwnode\.strategies\.utils import', 'from exonware.xwnode.common.utils.utils import'),
    (r'from exonware\.xwnode\.strategies\.simple import', 'from exonware.xwnode.common.utils.simple import'),
    
    # Relative imports in moved files
    (r'from \.\.strategies\.flyweight import', 'from ..common.patterns.flyweight import'),
    (r'from \.\.strategies\.registry import', 'from ..common.patterns.registry import'),
    (r'from \.\.strategies\.advisor import', 'from ..common.patterns.advisor import'),
    (r'from \.\.strategies\.metrics import', 'from ..common.monitoring.metrics import'),
    (r'from \.\.strategies\.manager import', 'from ..common.management.manager import'),
    (r'from \.\.strategies import', 'from ..common import'),
]


def update_file_header(content: str, old_path: str, new_path: str) -> str:
    """Update the file header comment with new path."""
    # Match the comment at the top like: #exonware/xwnode/src/exonware/xwnode/strategies/file.py
    pattern = r'#exonware/xwnode/src/exonware/xwnode/strategies/([^/]+\.py)'
    replacement = f'#exonware/xwnode/src/exonware/xwnode/common/{new_path.split("/", 1)[1]}'
    return re.sub(pattern, replacement, content, count=1)


def update_imports(content: str) -> str:
    """Update imports in file content."""
    for old_import, new_import in IMPORT_REPLACEMENTS:
        content = re.sub(old_import, new_import, content)
    return content


def move_file(base_path: Path, source: str, dest: str):
    """Move a file and update its imports."""
    source_path = base_path / source
    dest_path = base_path / dest
    
    if not source_path.exists():
        print(f"  ⚠️  Source not found: {source}")
        return False
    
    print(f"  📄 Moving: {source} -> {dest}")
    
    # Read content
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update file header
    content = update_file_header(content, source, dest)
    
    # Update imports
    content = update_imports(content)
    
    # Create destination directory if needed
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to new location
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Created: {dest}")
    return True


def update_imports_in_directory(base_path: Path, directory: str):
    """Update imports in all Python files in a directory."""
    dir_path = base_path / directory
    
    if not dir_path.exists():
        return
    
    print(f"\n📂 Updating imports in: {directory}")
    
    count = 0
    for py_file in dir_path.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = update_imports(content)
            
            if new_content != content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                print(f"  ✅ Updated: {py_file.relative_to(base_path)}")
        except Exception as e:
            print(f"  ❌ Error updating {py_file}: {e}")
    
    print(f"  📊 Updated {count} files")


def create_init_files(base_path: Path):
    """Create __init__.py files for new structure."""
    init_files = [
        'common/__init__.py',
        'common/patterns/__init__.py',
        'common/monitoring/__init__.py',
        'common/management/__init__.py',
        'common/utils/__init__.py',
    ]
    
    print("\n📝 Creating __init__.py files...")
    
    for init_file in init_files:
        init_path = base_path / init_file
        
        if not init_path.exists():
            # Create appropriate __init__.py content
            if init_file == 'common/__init__.py':
                content = '''"""
#exonware/xwnode/src/exonware/xwnode/common/__init__.py

Common utilities and patterns shared across xwnode.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
"""

# Export common patterns
from .patterns import *
from .monitoring import *
from .management import *
from .utils import *

__all__ = [
    # Re-export from submodules
]
'''
            else:
                # Basic __init__.py for submodules
                module_name = init_file.split('/')[1]
                content = f'''"""
#exonware/xwnode/src/exonware/xwnode/common/{module_name}/__init__.py

{module_name.title()} module for xwnode.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
"""

# Import and export main components
from pathlib import Path
import importlib

# Auto-discover and import all modules
_current_dir = Path(__file__).parent
for _file in _current_dir.glob('*.py'):
    if _file.name != '__init__.py' and not _file.name.startswith('_'):
        _module_name = _file.stem
        try:
            globals()[_module_name] = importlib.import_module(f'.{{_module_name}}', package=__name__)
        except ImportError:
            pass

__all__ = []
'''
            
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Created: {init_file}")


def main():
    """Main refactoring function."""
    print("="*70)
    print("xwnode Structure Refactoring")
    print("="*70)
    
    # Get base path
    script_dir = Path(__file__).parent
    base_path = script_dir / 'src' / 'exonware' / 'xwnode'
    
    print(f"\n📍 Base path: {base_path}")
    
    # Phase 1: Move files
    print("\n📦 Phase 1: Moving files to common/")
    print("-"*70)
    
    moved_count = 0
    for source, dest in MOVES.items():
        if move_file(base_path, source, dest):
            moved_count += 1
    
    print(f"\n  📊 Moved {moved_count}/{len(MOVES)} files")
    
    # Phase 2: Create __init__.py files
    print("\n📦 Phase 2: Creating __init__.py files")
    print("-"*70)
    create_init_files(base_path)
    
    # Phase 3: Update imports in all directories
    print("\n📦 Phase 3: Updating imports in all directories")
    print("-"*70)
    
    directories = ['nodes', 'edges', 'queries', 'common', '.']
    for directory in directories:
        update_imports_in_directory(base_path, directory)
    
    # Phase 4: Summary
    print("\n"+"="*70)
    print("✅ Refactoring Complete!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("  1. Review moved files")
    print("  2. Run tests: python -m pytest tests/")
    print("  3. Check for any remaining import issues")
    print("  4. Delete old strategies/ folder if empty")
    print("")


if __name__ == '__main__':
    main()
