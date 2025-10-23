#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x4_db_graph_on_off/benchmark.py

Graph Manager ON/OFF Benchmark - All Combinations (Refactored)

Tests ALL NodeMode × EdgeMode combinations with Graph Manager ON and OFF.
Measures the performance impact of XWGraphManager indexing and caching.

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
    generate_user, generate_post, generate_comment, generate_relationship,
    generate_all_combinations
)

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

def generate_models():
    """Generate all possible strategy combinations with Graph Manager ON/OFF"""
    combinations = generate_all_combinations()
    models = []
    
    for combo in combinations:
        edge_name = combo.edge_mode.name if combo.edge_mode else 'None'
        
        # Only test with edge modes (Graph Manager requires edges)
        if combo.edge_mode is not None:
            # Graph OFF variant
            models.append({
                'name': f"{combo.node_mode.name}+{edge_name}+GraphOFF",
                'description': f"{combo.node_mode.name} + {edge_name} (Graph: OFF)",
                'node_mode': combo.node_mode,
                'edge_mode': combo.edge_mode,
                'graph_manager': False
            })
            
            # Graph ON variant
            models.append({
                'name': f"{combo.node_mode.name}+{edge_name}+GraphON",
                'description': f"{combo.node_mode.name} + {edge_name} (Graph: ON)",
                'node_mode': combo.node_mode,
                'edge_mode': combo.edge_mode,
                'graph_manager': True
            })
    
    return models

# Auto-generate models
ALL_MODELS = generate_models()
print(f"Auto-generated {len(ALL_MODELS)} graph on/off configurations ({len(ALL_MODELS)//2} combinations × 2 modes)")


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
        self.graph_enabled = model_config.get('graph_manager', False)


class GraphOnOffBenchmark(BaseBenchmarkRunner):
    """Benchmark runner for Graph Manager ON/OFF comparison"""
    
    def __init__(self):
        super().__init__(
            benchmark_name="x4 Graph Manager ON/OFF Benchmark",
            default_test_sizes=[1000, 10000, 100000]
        )
    
    def run_single_benchmark(self, total_entities: int) -> Dict[str, Any]:
        """Run benchmark for a single test size"""
        print(f"\n{'='*80}")
        print(f"x4 GRAPH MANAGER ON/OFF BENCHMARK - {total_entities:,} ENTITIES")
        print(f"{'='*80}")
        
        # Entity distribution (lighter for exhaustive tests - 10% of full scale)
        base_scale = max(1, total_entities // 10)  # Ensure at least 1
        num_users = max(1, int(base_scale * 0.5))
        num_posts = max(1, int(base_scale * 0.3))
        num_comments = max(1, int(base_scale * 0.2))
        num_relationships = num_users * 2
        
        # Operations (lighter for exhaustive tests, ensure we don't exceed available entities)
        num_read_ops = max(1, min(10, int(num_users * 0.1)))
        num_update_ops = max(1, min(num_users, int(num_users * 0.5)))
        num_delete_ops = max(1, min(num_users // 3, int(num_users * 0.05)))
        
        print(f"\nConfiguration:")
        print(f"  Total Entities (actual): {num_users + num_posts + num_comments:,}")
        print(f"  Distribution: {num_users:,} users, {num_posts:,} posts, {num_comments:,} comments")
        print(f"  Relationships: {num_relationships:,}")
        print(f"  Total Models: {len(ALL_MODELS)} ({len(ALL_MODELS)//2} × 2 modes)")
        print(f"  Random execution: {'ENABLED' if self.random_enabled else 'DISABLED'}\n")
        
        # Shuffle models if random execution is enabled
        models_to_test = self.shuffle_if_enabled(ALL_MODELS)
        
        results = {}
        successful = 0
        failed = 0
        
        for i, model in enumerate(models_to_test):
            if (i + 1) % 100 == 0 or i == 0 or (i + 1) == len(ALL_MODELS):
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
                    
                    # Add relationships
                    for j in range(num_relationships):
                        source, target = random.choice(user_ids), random.choice(user_ids)
                        if source != target:
                            db.add_relationship(generate_relationship(source, target))
                
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
                
                # Phase 5: Graph queries (to test Graph Manager impact)
                with metrics.measure("graph_queries"):
                    for _ in range(num_read_ops):
                        db.get_followers(random.choice(user_ids))
                        db.get_following(random.choice(user_ids))
                
                node_mode_name = db.node_mode if isinstance(db.node_mode, str) else db.node_mode.name
                edge_mode_name = db.edge_mode.name if db.edge_mode else 'None'
                graph_status = 'ON' if db.graph_enabled else 'OFF'
                
                # Add x4_ prefix for unique naming across all benchmarks
                unique_name = f"x4_{model['name']}"
                
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': node_mode_name,
                    'edge_mode': edge_mode_name,
                    'graph_manager': graph_status,
                    'storage_format': 'N/A',
                    'storage_smart_format': 'N/A',
                    'group': f'Graph {graph_status}',
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
                unique_name = f"x4_{model['name']}"
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': model['node_mode'].name,
                    'edge_mode': model.get('edge_mode').name if model.get('edge_mode') else 'None',
                    'graph_manager': 'ON' if model.get('graph_manager') else 'OFF',
                    'success': False,
                    'error': str(e)
                }
        
        print(f"\nCompleted: {successful} successful, {failed} failed")
        
        # Show top 10 winners for each mode
        successful_results = {k: v for k, v in results.items() if v.get('success', True)}
        if successful_results:
            graph_on = {k: v for k, v in successful_results.items() if v.get('graph_manager') == 'ON'}
            graph_off = {k: v for k, v in successful_results.items() if v.get('graph_manager') == 'OFF'}
            
            if graph_on:
                sorted_on = sorted(graph_on.items(), key=lambda x: x[1].get('total_time_ms', float('inf')))
                print(f"\n{'='*80}")
                print(f"TOP 5 WINNERS - GRAPH MANAGER ON - {total_entities:,} ENTITIES")
                print(f"{'='*80}")
                for rank, (name, data) in enumerate(sorted_on[:5], 1):
                    time_ms = data.get('total_time_ms', 0)
                    memory = data.get('peak_memory_mb', 0)
                    print(f"  {rank}. {name}: {time_ms:.2f}ms, {memory:.1f}MB")
            
            if graph_off:
                sorted_off = sorted(graph_off.items(), key=lambda x: x[1].get('total_time_ms', float('inf')))
                print(f"\n{'='*80}")
                print(f"TOP 5 WINNERS - GRAPH MANAGER OFF - {total_entities:,} ENTITIES")
                print(f"{'='*80}")
                for rank, (name, data) in enumerate(sorted_off[:5], 1):
                    time_ms = data.get('total_time_ms', 0)
                    memory = data.get('peak_memory_mb', 0)
                    print(f"  {rank}. {name}: {time_ms:.2f}ms, {memory:.1f}MB")
        
        return results


def main():
    """Main entry point"""
    benchmark = GraphOnOffBenchmark()
    benchmark.main()


if __name__ == "__main__":
    main()

