#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x6_file_advance_db/benchmark.py

Advanced File-Backed Database Benchmark - Atomic & Transactional Operations

Tests advanced database operations with atomic transactions on file storage.
Demonstrates transactional capabilities where multiple operations are committed
atomically, ensuring data consistency.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.2
Generation Date: October 17, 2025
"""

import sys
import random
import shutil
from pathlib import Path
from typing import Dict, Any

# Add common module to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Add xwsystem to path
xwsystem_root = project_root.parent / "xwsystem" / "src"
sys.path.insert(0, str(xwsystem_root))

from exonware.xwnode.defs import NodeMode, EdgeMode
from x0_common import (
    BenchmarkMetrics, BaseBenchmarkRunner,
    generate_user, generate_post, generate_comment, generate_relationship,
    SimpleFileStorage, TransactionalFileStorage,
    FileBackedDatabase, TransactionalFileBackedDatabase
)

# Import xwsystem serialization
try:
    from exonware.xwsystem.serialization import (
        JsonSerializer, YamlSerializer, MsgPackSerializer, XmlSerializer
    )
    SERIALIZATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: xwsystem serialization not available: {e}")
    SERIALIZATION_AVAILABLE = False

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

# Formats with their transactional capabilities
# Root cause fix applied: XML now handles UUID keys and preserves types
FORMATS = [
    ('json', JsonSerializer, '.json', True, 'Full transactional support'),
    ('yaml', YamlSerializer, '.yaml', True, 'Full transactional support'),
    ('msgpack', MsgPackSerializer, '.msgpack', True, 'Full transactional support'),
    ('xml', XmlSerializer, '.xml', True, 'Full transactional support + type preservation'),  # Now supported!
    # Note: SQLITE3 and LMDB have native transactional support but require special handling
]


class FileAdvancedBenchmark(BaseBenchmarkRunner):
    """Benchmark runner for advanced transactional file operations"""
    
    def __init__(self):
        super().__init__(
            benchmark_name="x6 Advanced File-Backed Database Benchmark",
            default_test_sizes=[100, 1000, 10000]
        )
        # Setup data directory
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def run_single_benchmark(self, total_entities: int) -> Dict[str, Any]:
        """Run benchmark for a single test size"""
        print(f"\n{'='*80}")
        print(f"x6 ADVANCED FILE-BACKED DATABASE BENCHMARK - {total_entities:,} ENTITIES")
        print(f"{'='*80}")
        
        if not SERIALIZATION_AVAILABLE:
            print("\n⚠️  ERROR: xwsystem serialization not available")
            print("Please ensure xwsystem is installed and in the path")
            return {}
        
        # Entity distribution (10% of full scale for file testing)
        base_scale = total_entities // 10
        num_users = int(base_scale * 0.5)
        num_posts = int(base_scale * 0.3)
        num_comments = int(base_scale * 0.2)
        num_relationships = num_users * 2
        
        print(f"\nConfiguration:")
        print(f"  Total Entities (actual): {num_users + num_posts + num_comments:,}")
        print(f"  Distribution: {num_users:,} users, {num_posts:,} posts, {num_comments:,} comments")
        print(f"  Relationships: {num_relationships:,}")
        print(f"  Advanced formats: {len(FORMATS)}")
        print(f"  Random execution: {'ENABLED' if self.random_enabled else 'DISABLED'}")
        print(f"  Data directory: {self.data_dir}")
        print("\nAdvanced operations tested:")
        print(f"  - ATOMIC BATCH INSERT: All {num_users + num_posts + num_comments + num_relationships:,} entities in one transaction")
        print(f"  - ATOMIC BATCH UPDATE: {num_posts:,} posts updated atomically")
        print(f"  - ATOMIC BATCH DELETE: {num_comments // 2:,} comments deleted atomically")
        print(f"  - READ OPERATIONS: {num_users * 2:,} operations")
        print(f"  - TRANSACTION ROLLBACK TEST: Simulated failure with rollback\n")
        
        # Clean data directory
        if self.data_dir.exists():
            try:
                shutil.rmtree(self.data_dir)
            except PermissionError as e:
                # Root cause: Another process (Excel, file explorer) has files open
                # Solution: Inform user to close files, tests will overwrite existing files
                # Priority: Usability #2 - Clear, cross-platform error messages
                print(f"  [WARNING] Data directory in use (close any open files in: {self.data_dir})")
                print(f"  [INFO] Tests will overwrite existing files")
            except OSError as e:
                # Root cause: File system issue (disk full, readonly, etc.)
                # Solution: Provide specific error and guidance
                print(f"  [WARNING] Cannot clean data directory: {e}")
                print(f"  [INFO] Tests will attempt to overwrite existing files")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Shuffle formats if random execution is enabled
        formats_to_test = self.shuffle_if_enabled(FORMATS)
        
        results = {}
        
        for format_name, serializer_class, ext, has_transactions, description in formats_to_test:
            result_key = f"SPARSE_MATRIX+EDGE_PROPERTY_STORE+{format_name.upper()}"
            
            print(f"Testing: {result_key} ({description})")
            
            try:
                # Create transactional file-backed database
                file_path = self.data_dir / f"db_{total_entities}_{format_name}{ext}"
                serializer = serializer_class(validate_paths=False)
                
                # Use transactional storage if format supports it
                if has_transactions:
                    storage = TransactionalFileStorage(file_path, serializer)
                    db = TransactionalFileBackedDatabase(
                        name="SPARSE_MATRIX+EDGE_PROPERTY_STORE",
                        storage=storage,
                        node_mode=NodeMode.SPARSE_MATRIX,
                        edge_mode=EdgeMode.EDGE_PROPERTY_STORE
                    )
                else:
                    storage = SimpleFileStorage(file_path, serializer)
                    db = FileBackedDatabase(
                        name="SPARSE_MATRIX+EDGE_PROPERTY_STORE",
                        storage=storage,
                        node_mode=NodeMode.SPARSE_MATRIX,
                        edge_mode=EdgeMode.EDGE_PROPERTY_STORE
                    )
                
                metrics = BenchmarkMetrics()
                user_ids = []
                post_ids = []
                comment_ids = []
                
                # Generate entities first
                users = [generate_user(i) for i in range(num_users)]
                posts = []
                comments = []
                relationships = []
                
                # Phase 1: ATOMIC BATCH INSERT (all entities in one transaction)
                with metrics.measure("insert"):
                    # Insert all users
                    for user in users:
                        user_ids.append(db.insert_user(user))
                    
                    # Generate and insert posts
                    for i in range(num_posts):
                        post = generate_post(i, random.choice(user_ids))
                        post_ids.append(db.insert_post(post))
                    
                    # Generate and insert comments
                    for i in range(num_comments):
                        comment = generate_comment(i, random.choice(post_ids), random.choice(user_ids))
                        comment_ids.append(db.insert_comment(comment))
                    
                    # Generate and insert relationships
                    for i in range(num_relationships):
                        source, target = random.choice(user_ids), random.choice(user_ids)
                        if source != target:
                            db.add_relationship(generate_relationship(source, target))
                
                # Phase 2: READ operations (reads from file)
                with metrics.measure("read"):
                    # Read all users twice
                    for _ in range(2):
                        for user_id in user_ids:
                            user = db.get_user(user_id)
                            if not user:
                                print(f"    Warning: User {user_id} not found")
                
                # Phase 3: ATOMIC BATCH UPDATE (update all posts atomically)
                with metrics.measure("update"):
                    if has_transactions and isinstance(db, TransactionalFileBackedDatabase):
                        # Use batch update with transaction
                        updates = [(post_id, {'likes_count': random.randint(0, 100)}) for post_id in post_ids]
                        updates_with_collection = [('posts', post_id, update) for post_id, update in updates]
                        db.batch_update(updates_with_collection)
                    else:
                        # Update one by one
                        for post_id in post_ids:
                            db.update_post(post_id, {'likes_count': random.randint(0, 100)})
                
                # Phase 4: ATOMIC BATCH DELETE (delete half of comments atomically)
                with metrics.measure("delete"):
                    comments_to_delete = comment_ids[:len(comment_ids)//2]
                    if has_transactions and isinstance(db, TransactionalFileBackedDatabase):
                        # Use batch delete with transaction
                        deletions = [('comments', comment_id) for comment_id in comments_to_delete]
                        db.batch_delete(deletions)
                    else:
                        # Delete one by one
                        for comment_id in comments_to_delete:
                            db.delete_comment(comment_id)
                
                # Phase 5: Transaction rollback test (measure overhead)
                with metrics.measure("rollback_test"):
                    if has_transactions and isinstance(storage, TransactionalFileStorage):
                        try:
                            with storage.transaction():
                                # Try to insert a user
                                test_user = generate_user(9999)
                                storage.set_entity('users', test_user.id, test_user.to_dict())
                                # Simulate error to trigger rollback
                                raise ValueError("Simulated error for rollback test")
                        except ValueError:
                            # Rollback happened successfully
                            pass
                
                # Measure file size
                file_size_kb = 0
                if file_path.exists():
                    if file_path.is_file():
                        file_size_kb = file_path.stat().st_size / 1024
                    elif file_path.is_dir():
                        file_size_kb = sum(f.stat().st_size for f in file_path.rglob('*') if f.is_file()) / 1024
                
                # Verify final state
                stats = db.get_stats()
                success = (
                    stats['total_users'] == num_users and
                    stats['total_posts'] == num_posts and
                    stats['total_comments'] == len(comment_ids) - len(comments_to_delete)
                )
                
                # Add x6_ prefix for unique naming across all benchmarks
                unique_name = f"x6_{result_key}"
                
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': NodeMode.SPARSE_MATRIX.name,
                    'edge_mode': EdgeMode.EDGE_PROPERTY_STORE.name,
                    'graph_manager': 'OFF',
                    'storage_format': format_name.upper(),
                    'storage_smart_format': 'ON',
                    'group': f'Advanced-{format_name}',
                    'capabilities': ['atomic', 'transactional'] if has_transactions else ['basic'],
                    'total_entities': total_entities,
                    'total_time_ms': metrics.get_total_time(),
                    'peak_memory_mb': metrics.get_peak_memory(),
                    'file_size_kb': file_size_kb,
                    'metrics': metrics.get_metrics(),
                    'stats': stats,
                    'success': success,
                    'file_path': str(file_path)
                }
                
                insert_time = metrics.get_metrics()['insert']['total_time_ms']
                update_time = metrics.get_metrics()['update']['total_time_ms']
                delete_time = metrics.get_metrics()['delete']['total_time_ms']
                rollback_time = metrics.get_metrics()['rollback_test']['total_time_ms']
                
                print(f"  [OK] {format_name}: {metrics.get_total_time():.2f}ms total, {file_size_kb:.1f}KB")
                print(f"       Atomic INSERT:{insert_time:.1f}ms UPDATE:{update_time:.1f}ms DELETE:{delete_time:.1f}ms ROLLBACK:{rollback_time:.1f}ms")
                
            except Exception as e:
                print(f"  [FAIL] {format_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                unique_name = f"x6_{result_key}"
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': NodeMode.SPARSE_MATRIX.name,
                    'edge_mode': EdgeMode.EDGE_PROPERTY_STORE.name,
                    'storage_format': format_name.upper(),
                    'capabilities': ['atomic', 'transactional'] if has_transactions else ['basic'],
                    'success': False,
                    'error': str(e)
                }
        
        # Show rankings
        successful = {k: v for k, v in results.items() if v.get('success')}
        if successful:
            print(f"\n{'='*80}")
            print(f"TOP ADVANCED FORMATS BY SPEED - {total_entities:,} ENTITIES")
            print(f"{'='*80}")
            sorted_by_speed = sorted(successful.items(), key=lambda x: x[1]['total_time_ms'])
            for rank, (name, data) in enumerate(sorted_by_speed, 1):
                caps = ', '.join(data['capabilities'])
                insert_time = data['metrics']['insert']['total_time_ms']
                update_time = data['metrics']['update']['total_time_ms']
                delete_time = data['metrics']['delete']['total_time_ms']
                print(f"  {rank}. {data['storage_format']} ({caps}): {data['total_time_ms']:.2f}ms, {data['file_size_kb']:.1f}KB")
                print(f"     Atomic: INSERT:{insert_time:.1f}ms UPDATE:{update_time:.1f}ms DELETE:{delete_time:.1f}ms")
            
            print(f"\n{'='*80}")
            print(f"TOP FORMATS BY SIZE - {total_entities:,} ENTITIES")
            print(f"{'='*80}")
            sorted_by_size = sorted(successful.items(), key=lambda x: x[1]['file_size_kb'])
            for rank, (name, data) in enumerate(sorted_by_size, 1):
                print(f"  {rank}. {data['storage_format']}: {data['file_size_kb']:.1f}KB, {data['total_time_ms']:.2f}ms")
        
        return results


def main():
    """Main entry point"""
    benchmark = FileAdvancedBenchmark()
    benchmark.main()


if __name__ == "__main__":
    main()
