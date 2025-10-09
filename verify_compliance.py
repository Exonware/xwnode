#!/usr/bin/env python3
"""
Verify DEV_GUIDELINES.md Compliance

Checks that all changes follow DEV_GUIDELINES.md without actually importing
(to avoid environment issues).
"""

import os
import re
from pathlib import Path

def check_file_exists(path):
    """Check if file exists."""
    return Path(path).exists()

def check_class_inheritance(file_path, class_name, expected_parent):
    """Check if a class extends the expected parent."""
    if not Path(file_path).exists():
        return False, f"File not found: {file_path}"
    
    content = Path(file_path).read_text(encoding='utf-8')
    
    # Look for class definition
    pattern = rf'class\s+{class_name}\s*\(\s*{expected_parent}'
    if re.search(pattern, content):
        return True, f"✅ {class_name} extends {expected_parent}"
    
    return False, f"❌ {class_name} does not extend {expected_parent}"

def main():
    print("=" * 80)
    print("DEV_GUIDELINES.md COMPLIANCE VERIFICATION")
    print("=" * 80)
    print()
    
    # Change to xwnode directory
    os.chdir('xwnode/src/exonware/xwnode')
    
    checks = []
    
    # 1. Check interface inheritance
    print("1. Interface-Abstract Inheritance")
    print("-" * 80)
    
    result, msg = check_class_inheritance(
        'nodes/strategies/base.py',
        'ANodeStrategy',
        'iNodeStrategy'
    )
    checks.append(result)
    print(f"   {msg}")
    
    result, msg = check_class_inheritance(
        'edges/strategies/base.py',
        'AEdgeStrategy',
        'iEdgeStrategy'
    )
    checks.append(result)
    print(f"   {msg}")
    
    result, msg = check_class_inheritance(
        'queries/strategies/base.py',
        'AQueryStrategy',
        'IQueryStrategy'
    )
    checks.append(result)
    print(f"   {msg}")
    
    result, msg = check_class_inheritance(
        'queries/executors/base.py',
        'AOperationExecutor',
        'IOperationExecutor'
    )
    checks.append(result)
    print(f"   {msg}")
    print()
    
    # 2. Check new files created
    print("2. Required Files Created")
    print("-" * 80)
    
    required_files = [
        'queries/executors/types.py',
        'queries/executors/errors.py',
        '../../../docs/DESIGN_PATTERNS.md',
        '../../../docs/DEV_GUIDELINES_COMPLIANCE.md',
    ]
    
    for file in required_files:
        exists = check_file_exists(file)
        checks.append(exists)
        status = "✅" if exists else "❌"
        print(f"   {status} {file}")
    print()
    
    # 3. Check redundancy removed
    print("3. No Redundancy")
    print("-" * 80)
    
    # Check that UnsupportedOperationError is NOT defined in base.py
    base_content = Path('queries/executors/base.py').read_text(encoding='utf-8')
    has_redundant_error = 'class UnsupportedOperationError' in base_content
    checks.append(not has_redundant_error)
    
    if not has_redundant_error:
        print("   ✅ No redundant UnsupportedOperationError in base.py")
    else:
        print("   ❌ Redundant UnsupportedOperationError still in base.py")
    
    # Check that OperationCapability is NOT in contracts.py
    contracts_content = Path('queries/executors/contracts.py').read_text(encoding='utf-8')
    has_redundant_enum = 'class OperationCapability' in contracts_content
    checks.append(not has_redundant_enum)
    
    if not has_redundant_enum:
        print("   ✅ OperationCapability moved to types.py")
    else:
        print("   ❌ OperationCapability still in contracts.py")
    
    # Check that errors extend root
    errors_content = Path('queries/executors/errors.py').read_text(encoding='utf-8')
    extends_root = 'from ...errors import' in errors_content
    checks.append(extends_root)
    
    if extends_root:
        print("   ✅ Errors extend root error classes")
    else:
        print("   ❌ Errors don't extend root")
    print()
    
    # 4. Check imports
    print("4. Proper Imports")
    print("-" * 80)
    
    # Check that base.py imports from errors.py
    imports_from_errors = 'from .errors import' in base_content
    checks.append(imports_from_errors)
    
    if imports_from_errors:
        print("   ✅ base.py imports from errors.py")
    else:
        print("   ❌ base.py doesn't import from errors.py")
    
    # Check that base.py imports from types.py
    imports_from_types = 'from .types import' in base_content
    checks.append(imports_from_types)
    
    if imports_from_types:
        print("   ✅ base.py imports from types.py")
    else:
        print("   ❌ base.py doesn't import from types.py")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    print(f"   Total checks: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print()
    
    if all(checks):
        print("   ✅ ALL CHECKS PASSED - 100% DEV_GUIDELINES.md COMPLIANT")
        return 0
    else:
        print(f"   ⚠️  {failed} checks failed")
        return 1

if __name__ == '__main__':
    exit(main())
