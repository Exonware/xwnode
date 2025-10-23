#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x1_basic_db/benchmark.py

Basic Database Benchmark - Node-Only Testing (Refactored)

Tests ALL NodeModes with edge_mode=None (table-only storage).
Categorizes into Group A (Matrix/Array types) vs Group B (Others).

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

from exonware.xwnode.defs import NodeMode

from x0_common import (
    BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner,
    generate_user, generate_post, generate_comment,
    get_all_node_modes
)

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

# Model groups
GROUP_A_MODELS = []  # Matrix/Array-based types
GROUP_B_MODELS = []  # All other types

def generate_models():
    """Auto-discover and categorize all NodeModes"""
    global GROUP_A_MODELS, GROUP_B_MODELS
    
    all_node_modes = get_all_node_modes()
    
    # Group A: Matrix/Array-based types (optimized for table-like data)
    matrix_types = {
        NodeMode.SPARSE_MATRIX, NodeMode.ARRAY_LIST, NodeMode.BITMAP,
    }
    
    GROUP_A_MODELS = []
    GROUP_B_MODELS = []
    
    for node_mode in all_node_modes:
        model = {
            'name': node_mode.name,
            'node_mode': node_mode,
            'edge_mode': None
        }
        if node_mode in matrix_types:
            GROUP_A_MODELS.append(model)
        else:
            GROUP_B_MODELS.append(model)
    
    return GROUP_A_MODELS + GROUP_B_MODELS

# Auto-generate models
ALL_MODELS = generate_models()
print(f"Auto-generated {len(ALL_MODELS)} node-only models ({len(GROUP_A_MODELS)} matrix types, {len(GROUP_B_MODELS)} others)")


class DynamicDatabase(BaseDatabase):
    """Dynamically configured database from model configuration"""
    
    def __init__(self, model_config: dict):
        super().__init__(
            name=model_config['name'],
            node_mode=model_config['node_mode'],
            edge_mode=model_config.get('edge_mode')
        )


class BasicBenchmark(BaseBenchmarkRunner):
    """Benchmark runner for node-only configurations"""
    
    def __init__(self):
        super().__init__(
            benchmark_name="x1 Basic Database Benchmark (Node-Only)",
            default_test_sizes=[1, 10, 100]
        )
    
    def run_single_benchmark(self, total_entities: int) -> Dict[str, Any]:
        """Run benchmark for a single test size"""
        print(f"\n{'='*80}")
        print(f"x1 BASIC DATABASE BENCHMARK (NODE-ONLY) - {total_entities:,} ENTITIES")
        print(f"{'='*80}")
        
        # Calculate entity distribution (lighter for exhaustive tests - 10% of full scale)
        base_scale = max(1, total_entities // 10)  # Ensure at least 1
        num_users = max(1, int(base_scale * 0.5))
        num_posts = max(1, int(base_scale * 0.3))
        num_comments = max(1, int(base_scale * 0.2))
        
        # Operations (ensure we don't exceed available entities)
        num_read_ops = max(1, min(10, int(num_users * 0.1)))
        num_update_ops = max(1, min(num_users, int(num_users * 0.5)))
        num_delete_ops = max(1, min(num_users // 3, int(num_users * 0.05)))
        
        print(f"\nConfiguration:")
        print(f"  Total Entities (actual): {num_users + num_posts + num_comments:,}")
        print(f"  Distribution: {num_users:,} users, {num_posts:,} posts, {num_comments:,} comments")
        print(f"  Total Models: {len(ALL_MODELS)}")
        print(f"    Group A (Matrix/Array): {len(GROUP_A_MODELS)}")
        print(f"    Group B (Others): {len(GROUP_B_MODELS)}")
        print(f"  Random execution: {'ENABLED' if self.random_enabled else 'DISABLED'}\n")
        
        # Shuffle models if random execution is enabled
        models_to_test = self.shuffle_if_enabled(ALL_MODELS)
        
        results = {}
        successful = 0
        failed = 0
        
        for i, model in enumerate(models_to_test):
            if (i + 1) % 50 == 0 or i == 0 or (i + 1) == len(ALL_MODELS):
                progress = (i + 1) / len(ALL_MODELS) * 100
                print(f"Progress: {i+1}/{len(ALL_MODELS)} ({progress:.1f}%) - Success: {successful}, Failed: {failed}")
            
            try:
                db = DynamicDatabase(model)
                metrics = BenchmarkMetrics()
                user_ids = []
                post_ids = []
                comment_ids = []
                
                # Phase 1: Insert
                with metrics.measure("insert"):
                    for j in range(num_users):
                        user_ids.append(db.insert_user(generate_user(j)))
                    for j in range(num_posts):
                        post_ids.append(db.insert_post(generate_post(j, random.choice(user_ids))))
                    for j in range(num_comments):
                        comment_ids.append(db.insert_comment(generate_comment(j, random.choice(post_ids), random.choice(user_ids))))
                
                # Phase 2: Read
                with metrics.measure("read"):
                    for _ in range(num_read_ops):
                        db.get_user(random.choice(user_ids))
                        db.get_post(random.choice(post_ids))
                        db.get_comment(random.choice(comment_ids))
                
                # Phase 3: Update
                with metrics.measure("update"):
                    for j in range(min(num_update_ops, len(user_ids))):
                        db.update_user(user_ids[j], {'bio': f'Updated {j}'})
                    for j in range(min(num_update_ops, len(post_ids))):
                        db.update_post(post_ids[j], {'likes_count': j})
                    for j in range(min(num_update_ops, len(comment_ids))):
                        db.update_comment(comment_ids[j], {'content': f'Updated {j}'})
                
                # Phase 4: Delete
                with metrics.measure("delete"):
                    for j in range(min(num_delete_ops, len(comment_ids))):
                        db.delete_comment(comment_ids[-(j+1)])
                    num_post_deletes = min(num_delete_ops // 2, len(post_ids))
                    for j in range(num_post_deletes):
                        db.delete_post(post_ids[-(j+1)])
                    num_user_deletes = min(num_delete_ops // 3, len(user_ids))
                    for j in range(num_user_deletes):
                        db.delete_user(user_ids[-(j+1)])
                
                # Determine group
                is_group_a = any(m['name'] == model['name'] for m in GROUP_A_MODELS)
                group = "Group A (Matrix)" if is_group_a else "Group B (Others)"
                
                node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
                
                # Add x1_ prefix for unique naming across all benchmarks
                unique_name = f"x1_{model['name']}"
                
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': node_mode_name,
                    'edge_mode': 'None',
                    'graph_manager': 'OFF',
                    'storage_format': 'N/A',
                    'storage_smart_format': 'N/A',
                    'group': group,
                    'total_entities': total_entities,
                    'total_time_ms': metrics.get_total_time(),
                    'peak_memory_mb': metrics.get_peak_memory(),
                    'file_size_kb': 0,
                    'metrics': metrics.get_metrics(),
                    'stats': db.get_stats(),
                    'success': True
                }
                successful += 1
                
            except Exception as e:
                failed += 1
                print(f"[ERROR] {model['name']}: {str(e)}")
                unique_name = f"x1_{model['name']}"
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': model['node_mode'].name,
                    'edge_mode': 'None',
                    'success': False,
                    'error': str(e)
                }
        
        print(f"\nCompleted: {successful} successful, {failed} failed")
        
        # Show top 10 winners
        successful_results = {k: v for k, v in results.items() if v.get('success', True)}
        if successful_results:
            sorted_results = sorted(successful_results.items(), 
                                   key=lambda x: x[1].get('total_time_ms', float('inf')))
            
            print(f"\n{'='*80}")
            print(f"TOP 10 WINNERS (ALL GROUPS) - {total_entities:,} ENTITIES")
            print(f"{'='*80}")
            for rank, (name, data) in enumerate(sorted_results[:10], 1):
                time_ms = data.get('total_time_ms', 0)
                memory = data.get('peak_memory_mb', 0)
                is_group_a = any(m['name'] == name for m in GROUP_A_MODELS)
                group = "Group A" if is_group_a else "Group B"
                print(f"  {rank:2}. {name} ({group}): {time_ms:.2f}ms, {memory:.1f}MB")
        
        return results


def main():
    """Main entry point"""
    benchmark = BasicBenchmark()
    benchmark.main()


if __name__ == "__main__":
    main()

