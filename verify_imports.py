#!/usr/bin/env python3
"""
Verify Import Statements After Refactoring

This script verifies that all imports are correct after refactoring.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 08-Oct-2025
"""

import sys
import ast
from pathlib import Path
from typing import List, Dict, Tuple


class ImportVerifier:
    """Verifies imports in Python files."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.issues = []
        self.successes = []
    
    def verify_file(self, file_path: Path) -> List[Dict]:
        """Verify imports in a single file."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for old strategy imports
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        # Check for old patterns
                        if '.strategies.flyweight' in node.module and 'common.patterns' not in node.module:
                            issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'issue': f'Old import: {node.module}',
                                'type': 'old_path'
                            })
                        elif '.strategies.registry' in node.module and 'common.patterns' not in node.module:
                            issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'issue': f'Old import: {node.module}',
                                'type': 'old_path'
                            })
                        elif '.strategies.manager' in node.module and 'common.management' not in node.module:
                            issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'issue': f'Old import: {node.module}',
                                'type': 'old_path'
                            })
            
            if not issues:
                self.successes.append(file_path)
            
        except SyntaxError as e:
            issues.append({
                'file': file_path,
                'line': e.lineno or 0,
                'issue': f'Syntax error: {e.msg}',
                'type': 'syntax_error'
            })
        except Exception as e:
            issues.append({
                'file': file_path,
                'line': 0,
                'issue': f'Error parsing: {e}',
                'type': 'parse_error'
            })
        
        return issues
    
    def verify_directory(self, directory: Path, pattern: str = "*.py") -> None:
        """Verify all Python files in a directory."""
        for py_file in directory.rglob(pattern):
            if '__pycache__' in str(py_file):
                continue
            
            issues = self.verify_file(py_file)
            if issues:
                self.issues.extend(issues)
    
    def generate_report(self) -> str:
        """Generate verification report."""
        report = []
        report.append("="*70)
        report.append("Import Verification Report")
        report.append("="*70)
        report.append("")
        
        if not self.issues:
            report.append("SUCCESS! All imports are correct.")
            report.append(f"  Verified: {len(self.successes)} files")
        else:
            report.append(f"ISSUES FOUND: {len(self.issues)} import issues")
            report.append(f"  Files with issues: {len(set(i['file'] for i in self.issues))}")
            report.append(f"  Files verified OK: {len(self.successes)}")
            report.append("")
            report.append("Issues:")
            report.append("-"*70)
            
            for issue in self.issues[:50]:  # Limit to 50 for readability
                rel_path = issue['file'].relative_to(self.base_path.parent)
                report.append(f"  {rel_path}:{issue['line']}")
                report.append(f"    {issue['issue']}")
                report.append("")
            
            if len(self.issues) > 50:
                report.append(f"  ... and {len(self.issues) - 50} more issues")
        
        report.append("="*70)
        return "\n".join(report)


def test_imports():
    """Test that key imports work."""
    print("\nTesting key imports...")
    print("-"*70)
    
    tests = []
    
    # Test common imports
    tests.append(("common.patterns.flyweight", "from exonware.xwnode.common.patterns.flyweight import StrategyFlyweight"))
    tests.append(("common.patterns.registry", "from exonware.xwnode.common.patterns.registry import StrategyRegistry"))
    tests.append(("common.management.manager", "from exonware.xwnode.common.management.manager import StrategyManager"))
    tests.append(("common.utils.simple", "from exonware.xwnode.common.utils.simple import SimpleNodeStrategy"))
    
    # Test domain imports
    tests.append(("nodes.strategies", "from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy"))
    tests.append(("edges.strategies", "from exonware.xwnode.edges.strategies.adj_list import AdjacencyListStrategy"))
    tests.append(("queries.strategies", "from exonware.xwnode.queries.strategies.sql import SQLStrategy"))
    
    passed = 0
    failed = 0
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name} - {e}")
            failed += 1
    
    print("-"*70)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


def main():
    """Main verification function."""
    print("="*70)
    print("Import Verification After Refactoring")
    print("="*70)
    print("")
    
    base_path = Path(__file__).parent / 'src' / 'exonware' / 'xwnode'
    verifier = ImportVerifier(base_path)
    
    # Verify common/
    print("Verifying common/...")
    verifier.verify_directory(base_path / 'common')
    
    # Verify nodes/
    print("Verifying nodes/...")
    verifier.verify_directory(base_path / 'nodes')
    
    # Verify edges/
    print("Verifying edges/...")
    verifier.verify_directory(base_path / 'edges')
    
    # Verify queries/
    print("Verifying queries/...")
    verifier.verify_directory(base_path / 'queries')
    
    # Verify root files
    print("Verifying root files...")
    for file in ['facade.py', 'base.py', 'config.py']:
        file_path = base_path / file
        if file_path.exists():
            verifier.verify_file(file_path)
    
    # Generate report
    print("\n" + verifier.generate_report())
    
    # Test imports
    all_imports_work = test_imports()
    
    return len(verifier.issues) == 0 and all_imports_work


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
