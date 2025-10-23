#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x5_file_db/benchmark.py

File-Backed Database Benchmark - CRUD Operations on File Storage

Tests database operations that work directly with file storage across
different serialization formats. All operations (insert, read, update, delete)
actually read from and write to persistent files.

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
    SimpleFileStorage, FileBackedDatabase
)

# Import xwsystem serialization
try:
    from exonware.xwsystem.serialization import (
        JsonSerializer, YamlSerializer, MsgPackSerializer, PickleSerializer,
        CborSerializer, BsonSerializer, TomlSerializer, XmlSerializer
    )
    SERIALIZATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: xwsystem serialization not available: {e}")
    SERIALIZATION_AVAILABLE = False

# ==============================================================================
# BENCHMARK CONFIGURATION
# ==============================================================================

# Serialization formats to test
# All formats now support full database structures (including UUID keys)
# Root cause fix applied: XML now handles UUID keys and preserves types
FORMATS = [
    ('json', JsonSerializer, '.json'),
    ('yaml', YamlSerializer, '.yaml'),
    ('msgpack', MsgPackSerializer, '.msgpack'),
    ('pickle', PickleSerializer, '.pkl'),
    ('cbor', CborSerializer, '.cbor'),
    ('bson', BsonSerializer, '.bson'),
    ('toml', TomlSerializer, '.toml'),
    ('xml', XmlSerializer, '.xml'),  # Now supported with UUID key handling!
]


class FileBenchmark(BaseBenchmarkRunner):
    """Benchmark runner for file-backed database operations"""
    
    def __init__(self):
        super().__init__(
            benchmark_name="x5 File-Backed Database Benchmark",
            default_test_sizes=[100, 1000, 10000]
        )
        # Setup data directory
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def run_single_benchmark(self, total_entities: int) -> Dict[str, Any]:
        """Run benchmark for a single test size"""
        print(f"\n{'='*80}")
        print(f"x5 FILE-BACKED DATABASE BENCHMARK - {total_entities:,} ENTITIES")
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
        print(f"  Formats to test: {len(FORMATS)}")
        print(f"  Random execution: {'ENABLED' if self.random_enabled else 'DISABLED'}")
        print(f"  Data directory: {self.data_dir}")
        print("\nOperations tested (all on file storage):")
        print(f"  - INSERT: {num_users + num_posts + num_comments + num_relationships:,} operations")
        print(f"  - READ: {num_users * 2:,} operations (2x users)")
        print(f"  - UPDATE: {num_posts:,} operations (all posts)")
        print(f"  - DELETE: {num_comments // 2:,} operations (50% of comments)\n")
        
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
        
        for format_name, serializer_class, ext in formats_to_test:
            result_key = f"SPARSE_MATRIX+EDGE_PROPERTY_STORE+{format_name.upper()}"
            
            print(f"Testing: {result_key}")
            
            try:
                # Create file-backed database
                file_path = self.data_dir / f"db_{total_entities}_{format_name}{ext}"
                
                # Root cause: Pickle has security warnings for untrusted data
                # Solution: In benchmark context with self-generated trusted data,
                #           acknowledge security risk by setting allow_unsafe=True
                # Priority: Security #1 - Documented security decision
                serializer_kwargs = {'validate_paths': False}
                if format_name == 'pickle':
                    # Benchmark uses only self-generated trusted data
                    serializer_kwargs['allow_unsafe'] = True
                
                serializer = serializer_class(**serializer_kwargs)
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
                
                # Phase 1: INSERT operations (writes to file)
                with metrics.measure("insert"):
                    # Insert users
                    for i in range(num_users):
                        user_ids.append(db.insert_user(generate_user(i)))
                    
                    # Insert posts
                    for i in range(num_posts):
                        post_ids.append(db.insert_post(generate_post(i, random.choice(user_ids))))
                    
                    # Insert comments
                    for i in range(num_comments):
                        comment_ids.append(db.insert_comment(generate_comment(i, random.choice(post_ids), random.choice(user_ids))))
                    
                    # Insert relationships
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
                
                # Phase 3: UPDATE operations (reads and writes file)
                with metrics.measure("update"):
                    # Update all posts
                    for post_id in post_ids:
                        db.update_post(post_id, {'likes_count': random.randint(0, 100)})
                
                # Phase 4: DELETE operations (removes from file)
                with metrics.measure("delete"):
                    # Delete half of comments
                    comments_to_delete = comment_ids[:len(comment_ids)//2]
                    for comment_id in comments_to_delete:
                        db.delete_comment(comment_id)
                
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
                
                # Add x5_ prefix for unique naming across all benchmarks
                unique_name = f"x5_{result_key}"
                
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': NodeMode.SPARSE_MATRIX.name,
                    'edge_mode': EdgeMode.EDGE_PROPERTY_STORE.name,
                    'graph_manager': 'OFF',
                    'storage_format': format_name.upper(),
                    'storage_smart_format': 'ON',
                    'group': f'File-{format_name}',
                    'total_entities': total_entities,
                    'total_time_ms': metrics.get_total_time(),
                    'peak_memory_mb': metrics.get_peak_memory(),
                    'file_size_kb': file_size_kb,
                    'metrics': metrics.get_metrics(),
                    'stats': stats,
                    'success': success,
                    'file_path': str(file_path)
                }
                
                print(f"  [OK] {format_name}: {metrics.get_total_time():.2f}ms, {file_size_kb:.1f}KB, {stats['total_users']}U/{stats['total_posts']}P/{stats['total_comments']}C")
                
            except Exception as e:
                print(f"  [FAIL] {format_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                unique_name = f"x5_{result_key}"
                results[unique_name] = {
                    'database': unique_name,
                    'node_mode': NodeMode.SPARSE_MATRIX.name,
                    'edge_mode': EdgeMode.EDGE_PROPERTY_STORE.name,
                    'storage_format': format_name.upper(),
                    'success': False,
                    'error': str(e)
                }
        
        # Show rankings
        successful = {k: v for k, v in results.items() if v.get('success')}
        if successful:
            print(f"\n{'='*80}")
            print(f"TOP FORMATS BY SPEED - {total_entities:,} ENTITIES")
            print(f"{'='*80}")
            sorted_by_speed = sorted(successful.items(), key=lambda x: x[1]['total_time_ms'])
            for rank, (name, data) in enumerate(sorted_by_speed[:5], 1):
                insert_time = data['metrics']['insert']['total_time_ms']
                read_time = data['metrics']['read']['total_time_ms']
                update_time = data['metrics']['update']['total_time_ms']
                delete_time = data['metrics']['delete']['total_time_ms']
                print(f"  {rank}. {data['storage_format']}: {data['total_time_ms']:.2f}ms total")
                print(f"     INSERT:{insert_time:.1f}ms READ:{read_time:.1f}ms UPDATE:{update_time:.1f}ms DELETE:{delete_time:.1f}ms")
            
            print(f"\n{'='*80}")
            print(f"TOP FORMATS BY SIZE - {total_entities:,} ENTITIES")
            print(f"{'='*80}")
            sorted_by_size = sorted(successful.items(), key=lambda x: x[1]['file_size_kb'])
            for rank, (name, data) in enumerate(sorted_by_size[:5], 1):
                print(f"  {rank}. {data['storage_format']}: {data['file_size_kb']:.1f}KB, {data['total_time_ms']:.2f}ms")
        
        return results


def main():
    """Main entry point"""
    benchmark = FileBenchmark()
    benchmark.main()


if __name__ == "__main__":
    main()
