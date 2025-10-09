#!/usr/bin/env python3
"""
Generator script to create remaining XWQuery operation executors.

This script generates executor files following DEV_GUIDELINES.md patterns.
"""

import os
from pathlib import Path
from datetime import datetime

# Executor configurations
EXECUTORS = {
    'aggregation': [
        ('sum', 'SUM', 'AGGREGATION', [], 'Computes sum of numeric values'),
        ('avg', 'AVG', 'AGGREGATION', [], 'Computes average of numeric values'),
        ('min', 'MIN', 'AGGREGATION', [], 'Finds minimum value'),
        ('max', 'MAX', 'AGGREGATION', [], 'Finds maximum value'),
        ('distinct', 'DISTINCT', 'AGGREGATION', [], 'Returns distinct/unique values'),
        ('group', 'GROUP', 'AGGREGATION', [], 'Groups data by specified fields'),
        ('having', 'HAVING', 'AGGREGATION', [], 'Filters grouped data'),
        ('summarize', 'SUMMARIZE', 'AGGREGATION', [], 'Summarizes data with aggregations'),
    ],
    'ordering': [
        ('order', 'ORDER', 'ORDERING', ['TREE', 'LINEAR'], 'Orders/sorts data'),
        ('by', 'BY', 'ORDERING', [], 'Modifier for ORDER/GROUP BY'),
    ],
    'graph': [
        ('match', 'MATCH', 'GRAPH', ['GRAPH', 'TREE', 'HYBRID'], 'Graph pattern matching'),
        ('path', 'PATH', 'GRAPH', ['GRAPH', 'TREE', 'HYBRID'], 'Path operations in graphs'),
        ('out', 'OUT', 'GRAPH', ['GRAPH', 'TREE', 'HYBRID'], 'Outbound graph traversal'),
        ('in_traverse', 'IN_TRAVERSE', 'GRAPH', ['GRAPH', 'TREE', 'HYBRID'], 'Inbound graph traversal'),
        ('return', 'RETURN', 'GRAPH', ['GRAPH', 'TREE', 'HYBRID'], 'Returns graph query results'),
    ],
    'projection': [
        ('project', 'PROJECT', 'PROJECTION', [], 'Projects/selects specific fields'),
        ('extend', 'EXTEND', 'PROJECTION', [], 'Extends data with computed fields'),
    ],
    'array': [
        ('slicing', 'SLICING', 'ARRAY', ['LINEAR', 'MATRIX'], 'Array slicing operations'),
        ('indexing', 'INDEXING', 'ARRAY', ['LINEAR', 'MATRIX', 'TREE'], 'Array indexing operations'),
    ],
    'data': [
        ('load', 'LOAD', 'DATA_OPS', [], 'Loads data from external sources'),
        ('store', 'STORE', 'DATA_OPS', [], 'Stores data to external destinations'),
        ('merge', 'MERGE', 'DATA_OPS', [], 'Merges/upserts data'),
        ('alter', 'ALTER', 'DATA_OPS', [], 'Alters structure/schema'),
    ],
    'advanced': [
        ('join', 'JOIN', 'JOINING', [], 'Joins data from multiple sources'),
        ('union', 'UNION', 'JOINING', [], 'Unions data from multiple sources'),
        ('with_cte', 'WITH', 'CONTROL_FLOW', [], 'Common Table Expressions'),
        ('aggregate', 'AGGREGATE', 'AGGREGATION', [], 'Window aggregation operations'),
        ('foreach', 'FOREACH', 'CONTROL_FLOW', [], 'Iterates over collections'),
        ('let', 'LET', 'CONTROL_FLOW', [], 'Variable binding/assignment'),
        ('for_loop', 'FOR', 'CONTROL_FLOW', [], 'For loop construct'),
        ('window', 'WINDOW', 'WINDOW', ['LINEAR', 'TREE'], 'Window functions for time-series'),
        ('describe', 'DESCRIBE', 'ADVANCED', [], 'Describes structure/schema'),
        ('construct', 'CONSTRUCT', 'ADVANCED', [], 'Constructs new data structures'),
        ('ask', 'ASK', 'ADVANCED', [], 'Boolean query (yes/no result)'),
        ('subscribe', 'SUBSCRIBE', 'ADVANCED', [], 'Subscribes to data changes'),
        ('subscription', 'SUBSCRIPTION', 'ADVANCED', [], 'Manages subscriptions'),
        ('mutation', 'MUTATION', 'ADVANCED', [], 'Transactional mutations'),
        ('pipe', 'PIPE', 'ADVANCED', [], 'Pipeline operations'),
        ('options', 'OPTIONS', 'ADVANCED', [], 'Query options/metadata'),
    ],
}

TEMPLATE = '''#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/{category}/{filename}_executor.py

{OPERATION} Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: {date}
"""

from typing import Any, Dict, List
from ..base import {base_class}
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType{node_type_import}

class {class_name}Executor({base_class}):
    """
    {OPERATION} operation executor.
    
    {description}
    
    Capability: {capability}
    Operation Type: {op_type}
    """
    
    OPERATION_NAME = "{OPERATION}"
    OPERATION_TYPE = OperationType.{op_type}
    SUPPORTED_NODE_TYPES = {supported_types}
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute {OPERATION} operation."""
        params = action.params
        node = context.node
        
        result_data = self._execute_{operation_lower}(node, params, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={{'operation': self.OPERATION_NAME}}
        )
    
    def _execute_{operation_lower}(self, node: Any, params: Dict, context: ExecutionContext) -> Dict:
        """Execute {operation_lower} logic."""
        # Implementation here
        return {{'result': '{OPERATION} executed', 'params': params}}
'''

def generate_executor(category, filename, operation, op_type, supported, description):
    """Generate an executor file."""
    
    # Determine base class
    if supported:
        base_class = "AOperationExecutor"
        node_type_import = "\nfrom ...nodes.strategies.contracts import NodeType"
        supported_types = f"[{', '.join(['NodeType.' + t for t in supported])}]"
        capability = f"{', '.join(supported)} only"
    else:
        base_class = "AUniversalOperationExecutor"
        node_type_import = ""
        supported_types = "[]  # Universal"
        capability = "Universal"
    
    class_name = ''.join(word.capitalize() for word in filename.split('_'))
    
    content = TEMPLATE.format(
        category=category,
        filename=filename,
        OPERATION=operation,
        date=datetime.now().strftime('%d-%b-%Y'),
        base_class=base_class,
        node_type_import=node_type_import,
        class_name=class_name,
        description=description,
        capability=capability,
        op_type=op_type,
        supported_types=supported_types,
        operation_lower=filename,
    )
    
    return content

def main():
    """Generate all executors."""
    base_path = Path(__file__).parent / 'src' / 'exonware' / 'xwnode' / 'queries' / 'executors'
    
    for category, executors in EXECUTORS.items():
        # Create category directory
        category_path = base_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Generate __init__.py
        init_imports = []
        init_exports = []
        
        for filename, operation, op_type, supported, description in executors:
            # Generate executor
            content = generate_executor(category, filename, operation, op_type, supported, description)
            
            # Write file
            file_path = category_path / f"{filename}_executor.py"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[OK] Generated {category}/{filename}_executor.py")
            
            # Track for __init__.py
            class_name = ''.join(word.capitalize() for word in filename.split('_'))
            init_imports.append(f"from .{filename}_executor import {class_name}Executor")
            init_exports.append(f"    '{class_name}Executor',")
        
        # Generate __init__.py
        init_content = f'''"""{category.capitalize()} operation executors."""

{chr(10).join(init_imports)}

__all__ = [
{chr(10).join(init_exports)}
]
'''
        init_path = category_path / '__init__.py'
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(init_content)
        
        print(f"[OK] Generated {category}/__init__.py")
        print()

if __name__ == '__main__':
    main()
    print("[SUCCESS] All executors generated successfully!")

