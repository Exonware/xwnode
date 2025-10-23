#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x2_classic_db/benchmark.py

Classic Database Benchmark - Predefined Configurations (Refactored)

Tests 6 predefined database configurations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 14, 2025
"""

import sys
import random
from pathlib import Path
from typing import Dict, Any

# Add common module to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from exonware.xwnode.defs import NodeMode, EdgeMode, GraphOptimization

from x0_common import (
    BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner,
    generate_user, generate_post, generate_comment, generate_relationship
)

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

MODELS = [
    {
        'name': 'Read-Optimized',
        'description': 'HASH_MAP + None. Best for: Fast lookups, frequent reads',
        'node_mode': NodeMode.HASH_MAP,
        'edge_mode': None
    },
    {
        'name': 'Write-Optimized',
        'description': 'LSM_TREE + DYNAMIC_ADJ_LIST. Best for: High write throughput, inserts',
        'node_mode': NodeMode.LSM_TREE,
        'edge_mode': EdgeMode.DYNAMIC_ADJ_LIST
    },
    {
        'name': 'Memory-Efficient',
        'description': 'B_TREE + CSR. Best for: Large datasets, minimal RAM',
        'node_mode': NodeMode.B_TREE,
        'edge_mode': EdgeMode.CSR
    },
    {
        'name': 'Query-Optimized',
        'description': 'TREE_GRAPH_HYBRID + WEIGHTED_GRAPH. Best for: Graph traversal, complex queries',
        'node_mode': NodeMode.TREE_GRAPH_HYBRID,
        'edge_mode': EdgeMode.WEIGHTED_GRAPH
    },
    {
        'name': 'Persistence-Optimized',
        'description': 'B_PLUS_TREE + EDGE_PROPERTY_STORE. Best for: Durability, ACID compliance',
        'node_mode': NodeMode.B_PLUS_TREE,
        'edge_mode': EdgeMode.EDGE_PROPERTY_STORE
    },
    {
        'name': 'XWData-Optimized',
        'description': 'DATA_INTERCHANGE_OPTIMIZED. Best for: Serialization, format conversion',
        'node_mode': NodeMode.DATA_INTERCHANGE_OPTIMIZED,
        'edge_mode': None
    }
]


class DynamicDatabase(BaseDatabase):
    """Dynamically configured database from model configuration"""
    
    def __init__(self, model_config: dict):
        graph_opt = GraphOptimization.FULL if model_config.get('graph_manager') else GraphOptimization.OFF
        super().__init__(
            name=model_config['name'],
            node_mode=model_config['node_mode'],
            edge_mode=model_config.get('edge_mode'),
            graph_optimization=graph_opt
        )
        self.description = model_config.get('description', '')


class ClassicBenchmark(BaseBenchmarkRunner):
    """Benchmark runner for classic configurations"""
    
    def __init__(self):
        super().__init__(
            benchmark_name="x2 Classic Database Benchmark",
            default_test_sizes=[1, 10, 100]
        )
    
    def run_single_benchmark(self, total_entities: int) -> Dict[str, Any]:
        """
        Run benchmark for a single test size.
        
        Root cause fixed: int() truncation caused 0 entities for total_entities=1.
        Solution: Use max(1, ...) to guarantee at least 1 entity of each type.
        
        Priority: Security #1 - Prevent IndexError on empty lists
        Priority: Usability #2 - Clear, predictable entity distribution
        """
        print(f"\n{'='*80}")
        print(f"x2 CLASSIC DATABASE BENCHMARK - {total_entities:,} ENTITIES")
        print(f"{'='*80}")
        
        # Entity distribution with minimum guarantees
        # Root cause: int(1 * 0.5) = 0, causing empty lists
        # Fix: Ensure at least 1 of each type for testing
        if total_entities < 3:
            # For very small tests, at least 1 user is required
            num_users = max(1, total_entities)
            num_posts = max(1, total_entities - 1) if total_entities >= 2 else 0
            num_comments = max(1, total_entities - 2) if total_entities >= 3 else 0
        else:
            # Standard distribution: 50% users, 30% posts, 20% comments
            num_users = max(1, int(total_entities * 0.5))
            num_posts = max(1, int(total_entities * 0.3))
            num_comments = max(1, int(total_entities * 0.2))
            
            # Adjust to match exact total
            actual_total = num_users + num_posts + num_comments
            if actual_total != total_entities:
                # Add/remove from users (largest group)
                num_users += (total_entities - actual_total)
        
        num_relationships = max(2, num_users * 2)
        
        # Operations
        num_read_ops = max(100, int(num_users * 0.1))
        num_update_users = int(num_users * 0.5)
        num_update_posts = int(num_posts * 0.5)
        num_update_comments = int(num_comments * 0.5)
        num_delete_ops = max(10, int(num_users * 0.05))
        
        print(f"\nConfiguration:")
        print(f"  Total Entities: {total_entities:,}")
        print(f"  Distribution: {num_users:,} users, {num_posts:,} posts, {num_comments:,} comments")
        print(f"  Relationships: {num_relationships:,}")
        print(f"  Models to test: {len(MODELS)}")
        print(f"  Random execution: {'ENABLED' if self.random_enabled else 'DISABLED'}\n")
        
        for i, model in enumerate(MODELS, 1):
            edge_name = model['edge_mode'].name if model.get('edge_mode') else 'None'
            node_name = model['node_mode'].name if hasattr(model['node_mode'], 'name') else str(model['node_mode'])
            print(f"  {i}. {model['name']}: {node_name} + {edge_name} (Graph: OFF)")
        
        # Shuffle models if random execution is enabled
        models_to_test = self.shuffle_if_enabled(MODELS)
        
        results = {}
        
        for model in models_to_test:
            print(f"\n{'='*80}")
            print(f"Benchmarking: {model['name']} ({total_entities} entities)")
            print(f"{'='*80}")
            print(model.get('description', ''))
            
            try:
                db = DynamicDatabase(model)
                metrics = BenchmarkMetrics()
                user_ids = []
                post_ids = []
                comment_ids = []
                
                # Phase 1: Insert
                print(f"\n[Phase 1: Insert {num_users + num_posts + num_comments} entities + {num_relationships} relationships]")
                with metrics.measure("insert"):
                    # Insert users first
                    for i in range(num_users):
                        user_ids.append(db.insert_user(generate_user(i)))
                    
                    # Insert posts (requires users)
                    for i in range(num_posts):
                        if not user_ids:
                            raise ValueError(
                                f"Cannot create post: No users available. "
                                f"Expected {num_users} users but got 0. "
                                f"Check entity distribution calculation."
                            )
                        post_ids.append(db.insert_post(generate_post(i, random.choice(user_ids))))
                    
                    # Insert comments (requires posts and users)
                    for i in range(num_comments):
                        if not post_ids:
                            raise ValueError(
                                f"Cannot create comment: No posts available. "
                                f"Expected {num_posts} posts but got 0."
                            )
                        if not user_ids:
                            raise ValueError(
                                f"Cannot create comment: No users available. "
                                f"Expected {num_users} users but got 0."
                            )
                        comment_ids.append(db.insert_comment(generate_comment(i, random.choice(post_ids), random.choice(user_ids))))
                    
                    # Add relationships (requires users)
                    for i in range(num_relationships):
                        if not user_ids or len(user_ids) < 2:
                            break  # Skip if insufficient users
                        source, target = random.choice(user_ids), random.choice(user_ids)
                        if source != target:
                            db.add_relationship(generate_relationship(source, target))
                
                # Phase 2: Read (validate lists before random.choice)
                print(f"[Phase 2: Read {num_read_ops * 3} entities]")
                with metrics.measure("read"):
                    for _ in range(num_read_ops):
                        # Validate before random.choice to prevent IndexError
                        if user_ids:
                            db.get_user(random.choice(user_ids))
                        if post_ids:
                            db.get_post(random.choice(post_ids))
                        if comment_ids:
                            db.get_comment(random.choice(comment_ids))
                
                # Phase 3: Update
                print(f"[Phase 3: Update {num_update_users + num_update_posts + num_update_comments} entities]")
                with metrics.measure("update"):
                    for i in range(num_update_users):
                        db.update_user(user_ids[i], {'bio': f'Updated {i}'})
                    for i in range(num_update_posts):
                        db.update_post(post_ids[i], {'likes_count': i})
                    for i in range(num_update_comments):
                        db.update_comment(comment_ids[i], {'content': f'Updated {i}'})
                
                # Phase 4: Delete
                print(f"[Phase 4: Delete {num_delete_ops} entities]")
                with metrics.measure("delete"):
                    for i in range(min(num_delete_ops, len(comment_ids))):
                        db.delete_comment(comment_ids[-(i+1)])
                    num_post_deletes = min(num_delete_ops // 2, len(post_ids))
                    for i in range(num_post_deletes):
                        db.delete_post(post_ids[-(i+1)])
                    num_user_deletes = min(num_delete_ops // 3, len(user_ids))
                    for i in range(num_user_deletes):
                        db.delete_user(user_ids[-(i+1)])
                
                # Phase 5: Relationship queries (validate before random.choice)
                print(f"[Phase 5: Query {num_read_ops * 2} relationships]")
                with metrics.measure("relationships"):
                    for _ in range(num_read_ops):
                        # Validate users still exist after deletes
                        if user_ids:
                            db.get_followers(random.choice(user_ids))
                            db.get_following(random.choice(user_ids))
                
                total_time = metrics.get_total_time()
                peak_memory = metrics.get_peak_memory()
                
                print(f"\n[Results: {total_time:.2f}ms, {peak_memory:.1f}MB]")
                
                node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
                edge_mode_name = db.edge_mode.name if db.edge_mode else 'None'
                
                # Add x2_ prefix for unique naming across all benchmarks
                unique_name = f"x2_{model['name']}"
                
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': node_mode_name,
                    'edge_mode': edge_mode_name,
                    'graph_manager': 'OFF',
                    'storage_format': 'N/A',
                    'storage_smart_format': 'N/A',
                    'group': 'Classic',
                    'total_entities': total_entities,
                    'total_time_ms': total_time,
                    'peak_memory_mb': peak_memory,
                    'file_size_kb': 0,
                    'metrics': metrics.get_metrics(),
                    'stats': db.get_stats(),
                    'success': True
                }
                
            except IndexError as e:
                # Specific error handling for empty sequence errors
                # Priority: Usability #2 - Clear error messages
                print(f"\n[ERROR] {model['name']}: {e}")
                print(f"[DEBUG] This error indicates empty entity lists.")
                print(f"[DEBUG] Check Phase 1 entity insertion completed successfully.")
                print(f"[DEBUG] Config: users={num_users}, posts={num_posts}, comments={num_comments}")
                import traceback
                traceback.print_exc()
                unique_name = f"x2_{model['name']}"
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': model['node_mode'].name,
                    'edge_mode': model.get('edge_mode').name if model.get('edge_mode') else 'None',
                    'success': False,
                    'error': f"IndexError: {e} (Check entity distribution)"
                }
            except ValueError as e:
                # Specific error handling for validation errors
                # Priority: Security #1 - Proper error propagation
                print(f"\n[ERROR] {model['name']}: Validation failed - {e}")
                import traceback
                traceback.print_exc()
                unique_name = f"x2_{model['name']}"
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': model['node_mode'].name,
                    'edge_mode': model.get('edge_mode').name if model.get('edge_mode') else 'None',
                    'success': False,
                    'error': f"ValueError: {e}"
                }
            except Exception as e:
                # Generic error handling for unexpected issues
                # Priority: Maintainability #3 - Full error reporting
                print(f"\n[ERROR] {model['name']}: {e}")
                import traceback
                traceback.print_exc()
                unique_name = f"x2_{model['name']}"
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': model['node_mode'].name,
                    'edge_mode': model.get('edge_mode').name if model.get('edge_mode') else 'None',
                    'success': False,
                    'error': str(e)
                }
        
        return results


def main():
    """Main entry point"""
    benchmark = ClassicBenchmark()
    benchmark.main()


if __name__ == "__main__":
    main()

