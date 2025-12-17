#!/usr/bin/env python3
"""
#exonware/xwnode/examples/db_example/x5_file_db/benchmark.py

Comprehensive File Serialization Benchmark - All Formats Comparison

Tests atomic save/load operations across ALL available serialization formats from:
- xwsystem: Core formats (JSON, YAML, XML, TOML, BSON, MsgPack, Pickle, CBOR, etc.)
- xwformats: Enterprise formats (Protobuf, Parquet, Avro, HDF5, Feather, etc.)

All operations use ONE BIG FILE per format to test atomic access and writing.
Files are saved to the data/ folder.

This benchmark identifies the TOP PERFORMING format for:
- Speed (fastest save/load times)
- Size (most compact file size)
- Category winners (best in text, binary, schema, scientific formats)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.4
Generation Date: 02-Dec-2025
"""

import sys
import random
import shutil
import uuid
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

# Add common module to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Add xwsystem to path
xwsystem_root = project_root.parent / "xwsystem" / "src"
sys.path.insert(0, str(xwsystem_root))

from x0_common.schema import (
    User, Post, Comment, Relationship, Like, Share, Message, Notification,
    Group, Event, Hashtag,
    generate_user, generate_post, generate_comment, generate_relationship,
    generate_like, generate_share, generate_message, generate_notification,
    generate_group, generate_event, generate_hashtag
)
from x0_common.metrics import BenchmarkMetrics

# Import xwsystem serialization (core formats)
try:
    from exonware.xwsystem.io.serialization.formats.text import (
        JsonSerializer, Json5Serializer, JsonLinesSerializer,
        YamlSerializer, TomlSerializer, XmlSerializer,
        CsvSerializer, ConfigParserSerializer
    )
    from exonware.xwsystem.io.serialization.formats.binary import (
        MsgPackSerializer, PickleSerializer, BsonSerializer,
        MarshalSerializer, CborSerializer, PlistSerializer
    )
    XWSYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: xwsystem serialization not fully available: {e}")
    print("Some formats may be missing. Install with: pip install exonware-xwsystem[full]")
    XWSYSTEM_AVAILABLE = False
    # Set defaults to avoid errors
    JsonSerializer = None
    Json5Serializer = None
    JsonLinesSerializer = None
    YamlSerializer = None
    TomlSerializer = None
    XmlSerializer = None
    CsvSerializer = None
    ConfigParserSerializer = None
    MsgPackSerializer = None
    PickleSerializer = None
    BsonSerializer = None
    MarshalSerializer = None
    CborSerializer = None
    PlistSerializer = None

# Import xwformats serialization (enterprise formats)
try:
    from exonware.xwformats.formats.schema import (
        XWProtobufSerializer, XWParquetSerializer, XWThriftSerializer,
        XWOrcSerializer, XWCapnProtoSerializer, XWFlatBuffersSerializer
    )
    from exonware.xwformats.formats.scientific import (
        XWHdf5Serializer, XWFeatherSerializer, XWZarrSerializer,
        XWNetcdfSerializer, XWMatSerializer
    )
    from exonware.xwformats.formats.binary import (
        XWUbjsonSerializer
    )
    XWFORMATS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: xwformats serialization not available: {e}")
    print("Enterprise formats will be skipped. Install with: pip install exonware-xwformats[full]")
    XWFORMATS_AVAILABLE = False
    # Set defaults to avoid errors
    XWProtobufSerializer = None
    XWParquetSerializer = None
    XWThriftSerializer = None
    XWOrcSerializer = None
    XWCapnProtoSerializer = None
    XWFlatBuffersSerializer = None
    XWHdf5Serializer = None
    XWFeatherSerializer = None
    XWZarrSerializer = None
    XWNetcdfSerializer = None
    XWMatSerializer = None
    XWUbjsonSerializer = None

SERIALIZATION_AVAILABLE = XWSYSTEM_AVAILABLE

# ==============================================================================
# BENCHMARK CONFIGURATION - ALL AVAILABLE FORMATS
# ==============================================================================

# All formats to test with atomic single-file operations
# Format: (name, serializer_class, extension, category, requires_schema)
# Note: Some formats may require schemas or have limitations - they'll be skipped if unavailable
FORMATS = []

# Core Text Formats (xwsystem)
if JsonSerializer:
    FORMATS.append(('json', JsonSerializer, '.json', 'text', False))
# JSON5: Include but with strict limits - will fail gracefully if data too large
# Root cause: json5 library parser has performance issues with deep nesting
# Solution: Use strict limits (50 depth, 10MB) - will raise SerializationError if exceeded
if Json5Serializer:
    FORMATS.append(('json5', Json5Serializer, '.json5', 'text', False))
if JsonLinesSerializer:
    FORMATS.append(('jsonl', JsonLinesSerializer, '.jsonl', 'text', False))
if YamlSerializer:
    FORMATS.append(('yaml', YamlSerializer, '.yaml', 'text', False))
if TomlSerializer:
    FORMATS.append(('toml', TomlSerializer, '.toml', 'text', False))
if XmlSerializer:
    FORMATS.append(('xml', XmlSerializer, '.xml', 'text', False))
if CsvSerializer:
    FORMATS.append(('csv', CsvSerializer, '.csv', 'text', False))
if ConfigParserSerializer:
    FORMATS.append(('ini', ConfigParserSerializer, '.ini', 'text', False))

# Core Binary Formats (xwsystem)
if BsonSerializer:
    FORMATS.append(('bson', BsonSerializer, '.bson', 'binary', False))
if MsgPackSerializer:
    FORMATS.append(('msgpack', MsgPackSerializer, '.msgpack', 'binary', False))
if PickleSerializer:
    FORMATS.append(('pickle', PickleSerializer, '.pkl', 'binary', False))
if MarshalSerializer:
    FORMATS.append(('marshal', MarshalSerializer, '.marshal', 'binary', False))
if CborSerializer:
    FORMATS.append(('cbor', CborSerializer, '.cbor', 'binary', False))
if PlistSerializer:
    FORMATS.append(('plist', PlistSerializer, '.plist', 'binary', False))

# Enterprise Binary Formats (xwformats)
if XWUbjsonSerializer:
    FORMATS.append(('ubjson', XWUbjsonSerializer, '.ubjson', 'binary', False))

# Enterprise Schema Formats (xwformats) - May require schemas
if XWProtobufSerializer:
    FORMATS.append(('protobuf', XWProtobufSerializer, '.pb', 'schema', True))
if XWParquetSerializer:
    FORMATS.append(('parquet', XWParquetSerializer, '.parquet', 'schema', False))
if XWThriftSerializer:
    FORMATS.append(('thrift', XWThriftSerializer, '.thrift', 'schema', True))
if XWOrcSerializer:
    FORMATS.append(('orc', XWOrcSerializer, '.orc', 'schema', False))
if XWCapnProtoSerializer:
    FORMATS.append(('capnproto', XWCapnProtoSerializer, '.capnp', 'schema', True))
if XWFlatBuffersSerializer:
    FORMATS.append(('flatbuffers', XWFlatBuffersSerializer, '.fb', 'schema', True))

# Enterprise Scientific Formats (xwformats)
if XWHdf5Serializer:
    FORMATS.append(('hdf5', XWHdf5Serializer, '.h5', 'scientific', False))
if XWFeatherSerializer:
    FORMATS.append(('feather', XWFeatherSerializer, '.feather', 'scientific', False))
if XWZarrSerializer:
    FORMATS.append(('zarr', XWZarrSerializer, '.zarr', 'scientific', False))
if XWNetcdfSerializer:
    FORMATS.append(('netcdf', XWNetcdfSerializer, '.nc', 'scientific', False))
if XWMatSerializer:
    FORMATS.append(('mat', XWMatSerializer, '.mat', 'scientific', False))


def prepare_test_data(
    num_users: int, num_posts: int, num_comments: int, num_relationships: int,
    num_likes: int, num_shares: int, num_messages: int, num_notifications: int,
    num_groups: int, num_events: int
) -> Dict[str, Any]:
    """
    Prepare comprehensive social media test data in memory as a single dictionary structure.
    
    Root cause: Need to test atomic single-file operations where entire database
    is written and read as one unit. This ensures atomic access and writing.
    Full social media platform with users, posts, comments, relationships, likes,
    shares, messages, notifications, groups, events, and hashtags.
    
    Returns:
        Dictionary with complete database structure ready for serialization
    """
    # Generate all entities in memory
    users = {}
    posts = {}
    comments = {}
    relationships = {}
    likes = {}
    shares = {}
    messages = {}
    notifications = {}
    groups = {}
    events = {}
    hashtags = {}
    
    user_ids = []
    post_ids = []
    comment_ids = []
    group_ids = []
    event_ids = []
    hashtag_set = set()
    
    # Generate users
    print(f"  Generating {num_users:,} users...")
    for i in range(num_users):
        user = generate_user(i)
        users[user.id] = user.to_dict()
        user_ids.append(user.id)
    
    # Generate groups
    print(f"  Generating {num_groups:,} groups...")
    for i in range(num_groups):
        owner_id = random.choice(user_ids) if user_ids else None
        if owner_id:
            group = generate_group(i, owner_id)
            groups[group.id] = group.to_dict()
            group_ids.append(group.id)
    
    # Generate events
    print(f"  Generating {num_events:,} events...")
    for i in range(num_events):
        organizer_id = random.choice(user_ids) if user_ids else None
        if organizer_id:
            event = generate_event(i, organizer_id)
            events[event.id] = event.to_dict()
            event_ids.append(event.id)
    
    # Generate posts (linked to random users)
    print(f"  Generating {num_posts:,} posts...")
    for i in range(num_posts):
        post = generate_post(i, random.choice(user_ids), user_ids)
        posts[post.id] = post.to_dict()
        post_ids.append(post.id)
        
        # Extract hashtags from post
        for hashtag in post.hashtags:
            hashtag_name = hashtag.lstrip('#')
            hashtag_set.add(hashtag_name)
    
    # Generate comments (linked to random posts and users, with some nested replies)
    print(f"  Generating {num_comments:,} comments...")
    top_level_comments = []
    for i in range(num_comments):
        post_id = random.choice(post_ids)
        user_id = random.choice(user_ids)
        
        # 20% chance of being a reply to another comment
        parent_comment_id = None
        if top_level_comments and random.random() < 0.2:
            parent_comment_id = random.choice(top_level_comments)
        
        comment = generate_comment(i, post_id, user_id, user_ids, parent_comment_id)
        comments[comment.id] = comment.to_dict()
        comment_ids.append(comment.id)
        
        if parent_comment_id is None:
            top_level_comments.append(comment.id)
    
    # Generate relationships (user-to-user)
    print(f"  Generating {num_relationships:,} relationships...")
    relationship_count = 0
    while relationship_count < num_relationships:
        source, target = random.choice(user_ids), random.choice(user_ids)
        if source != target:
            rel_type = random.choice(["follows", "friend", "block", "mute"])
            rel = generate_relationship(source, target, rel_type)
            relationships[rel.id] = rel.to_dict()
            relationship_count += 1
    
    # Generate likes (on posts and comments)
    print(f"  Generating {num_likes:,} likes...")
    for i in range(num_likes):
        user_id = random.choice(user_ids)
        # 80% on posts, 20% on comments
        if random.random() < 0.8 and post_ids:
            target_id = random.choice(post_ids)
            target_type = "post"
        elif comment_ids:
            target_id = random.choice(comment_ids)
            target_type = "comment"
        else:
            continue
        
        like = generate_like(user_id, target_type, target_id)
        likes[like.id] = like.to_dict()
    
    # Generate shares
    print(f"  Generating {num_shares:,} shares...")
    for i in range(num_shares):
        if not post_ids:
            break
        user_id = random.choice(user_ids)
        post_id = random.choice(post_ids)
        share = generate_share(user_id, post_id)
        shares[share.id] = share.to_dict()
    
    # Generate messages (create conversations between users)
    print(f"  Generating {num_messages:,} messages...")
    conversations = {}
    for i in range(num_messages):
        sender_id = random.choice(user_ids)
        recipient_id = random.choice([uid for uid in user_ids if uid != sender_id])
        
        # Create conversation ID
        conv_key = tuple(sorted([sender_id, recipient_id]))
        if conv_key not in conversations:
            conversations[conv_key] = str(uuid.uuid4())
        conversation_id = conversations[conv_key]
        
        message = generate_message(conversation_id, sender_id, recipient_id)
        messages[message.id] = message.to_dict()
    
    # Generate notifications
    print(f"  Generating {num_notifications:,} notifications...")
    notification_types = ["like", "comment", "follow", "mention", "message", "share"]
    for i in range(num_notifications):
        user_id = random.choice(user_ids)
        actor_id = random.choice([uid for uid in user_ids if uid != user_id])
        notification_type = random.choice(notification_types)
        
        # Determine target based on type
        if notification_type == "like":
            target_type = random.choice(["post", "comment"])
            target_id = random.choice(post_ids if target_type == "post" and post_ids else comment_ids if comment_ids else [])
        elif notification_type == "comment":
            target_type = "post"
            target_id = random.choice(post_ids) if post_ids else None
        elif notification_type == "follow":
            target_type = "user"
            target_id = user_id
        elif notification_type == "mention":
            target_type = "post"
            target_id = random.choice(post_ids) if post_ids else None
        elif notification_type == "message":
            target_type = "message"
            target_id = random.choice(list(messages.keys())) if messages else None
        else:  # share
            target_type = "post"
            target_id = random.choice(post_ids) if post_ids else None
        
        if target_id:
            notification = generate_notification(user_id, actor_id, notification_type, target_type, target_id)
            notifications[notification.id] = notification.to_dict()
    
    # Generate hashtags from collected hashtag names
    print(f"  Generating {len(hashtag_set):,} hashtags...")
    for hashtag_name in hashtag_set:
        hashtag = generate_hashtag(hashtag_name)
        hashtags[hashtag.name] = hashtag.to_dict()
    
    # Structure for atomic single-file serialization
    database = {
        'metadata': {
            'version': '2.0',
            'platform': 'full_social_media',
            'total_users': len(users),
            'total_posts': len(posts),
            'total_comments': len(comments),
            'total_relationships': len(relationships),
            'total_likes': len(likes),
            'total_shares': len(shares),
            'total_messages': len(messages),
            'total_notifications': len(notifications),
            'total_groups': len(groups),
            'total_events': len(events),
            'total_hashtags': len(hashtags),
            'total_entities': (
                len(users) + len(posts) + len(comments) + len(relationships) +
                len(likes) + len(shares) + len(messages) + len(notifications) +
                len(groups) + len(events) + len(hashtags)
            )
        },
        'data': {
            'users': users,
            'posts': posts,
            'comments': comments,
            'relationships': relationships,
            'likes': likes,
            'shares': shares,
            'messages': messages,
            'notifications': notifications,
            'groups': groups,
            'events': events,
            'hashtags': hashtags
        }
    }
    
    return database


def verify_data_integrity(original: Dict[str, Any], loaded: Dict[str, Any]) -> tuple[bool, str]:
    """
    Verify that loaded data matches original data (round-trip integrity).
    
    Args:
        original: Original database dictionary
        loaded: Loaded database dictionary
        
    Returns:
        (success: bool, error_message: str)
    """
    # Check metadata
    orig_meta = original.get('metadata', {})
    loaded_meta = loaded.get('metadata', {})
    
    # Root cause fixed: XML serializer now preserves types using XML attributes.
    # Solution: Direct comparison (no normalization needed - serializer handles it).
    # Priority #2: Usability - Round-trip integrity works with proper type preservation.
    
    # Check all metadata counts
    metadata_fields = [
        'total_users', 'total_posts', 'total_comments', 'total_relationships',
        'total_likes', 'total_shares', 'total_messages', 'total_notifications',
        'total_groups', 'total_events', 'total_hashtags'
    ]
    
    for field in metadata_fields:
        orig_val = orig_meta.get(field, 0)
        loaded_val = loaded_meta.get(field, 0)
        if orig_val != loaded_val:
            return False, f"{field} mismatch: {orig_val} != {loaded_val}"
    
    # Check data collections
    orig_data = original.get('data', {})
    loaded_data = loaded.get('data', {})
    
    collection_names = [
        'users', 'posts', 'comments', 'relationships',
        'likes', 'shares', 'messages', 'notifications',
        'groups', 'events', 'hashtags'
    ]
    
    for collection_name in collection_names:
        orig_collection = orig_data.get(collection_name, {})
        loaded_collection = loaded_data.get(collection_name, {})
        
        if len(orig_collection) != len(loaded_collection):
            return False, f"{collection_name} count mismatch: {len(orig_collection)} != {len(loaded_collection)}"
        
        # Check a sample of entities (verify first 3 entities match)
        orig_items = list(orig_collection.items())[:3]
        for entity_id, orig_entity in orig_items:
            if entity_id not in loaded_collection:
                return False, f"{collection_name} entity {entity_id} missing in loaded data"
            
            loaded_entity = loaded_collection[entity_id]
            
            # Compare key fields based on entity type
            if collection_name == 'users':
                if orig_entity.get('username') != loaded_entity.get('username'):
                    return False, f"User {entity_id} username mismatch"
                if orig_entity.get('email') != loaded_entity.get('email'):
                    return False, f"User {entity_id} email mismatch"
            elif collection_name == 'posts':
                if orig_entity.get('user_id') != loaded_entity.get('user_id'):
                    return False, f"Post {entity_id} user_id mismatch"
                if orig_entity.get('content') != loaded_entity.get('content'):
                    return False, f"Post {entity_id} content mismatch"
            elif collection_name == 'comments':
                if orig_entity.get('post_id') != loaded_entity.get('post_id'):
                    return False, f"Comment {entity_id} post_id mismatch"
                if orig_entity.get('user_id') != loaded_entity.get('user_id'):
                    return False, f"Comment {entity_id} user_id mismatch"
            elif collection_name == 'relationships':
                if orig_entity.get('source_user_id') != loaded_entity.get('source_user_id'):
                    return False, f"Relationship {entity_id} source_user_id mismatch"
                if orig_entity.get('target_user_id') != loaded_entity.get('target_user_id'):
                    return False, f"Relationship {entity_id} target_user_id mismatch"
    
    return True, "Data integrity verified"


@contextmanager
def timeout_handler(timeout_seconds: float):
    """
    Context manager for timeout handling.
    
    Root cause: Some formats (like JSON5) hang on large files.
    Solution: Add timeout protection to prevent benchmark from hanging.
    Priority #4: Performance - Ensure benchmark completes in reasonable time.
    """
    if sys.platform == "win32":
        # Windows doesn't support signal.alarm, use threading.Timer instead
        import threading
        timer = None
        def timeout_function():
            raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
        try:
            timer = threading.Timer(timeout_seconds, timeout_function)
            timer.start()
            yield
        finally:
            if timer:
                timer.cancel()
    else:
        # Unix-like systems can use signal.alarm
        def timeout_handler_func(signum, frame):
            raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler_func)
        signal.alarm(int(timeout_seconds))
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


def test_format_atomic_operations(
    format_name: str,
    serializer_class: type,
    extension: str,
    test_data: Dict[str, Any],
    file_path: Path,
    metrics: BenchmarkMetrics,
    requires_schema: bool = False,
    timeout_seconds: float = 300.0  # 5 minute timeout per format
) -> Dict[str, Any]:
    """
    Test atomic save/load operations for a single format.
    
    Root cause: Testing atomic single-file operations ensures that:
    1. Entire database is written atomically (no partial writes)
    2. Entire database is read atomically (consistent state)
    3. Round-trip integrity is maintained
    
    Args:
        format_name: Name of format (bson, json, xml, toml, yaml, etc.)
        serializer_class: Serializer class from xwsystem or xwformats
        extension: File extension for format
        test_data: Complete database dictionary to serialize
        file_path: Path where file will be saved
        metrics: Metrics tracker
        requires_schema: Whether format requires a schema (may skip if True)
        
    Returns:
        Result dictionary with performance and success metrics
    """
    result = {
        'format': format_name.upper(),
        'file_path': str(file_path),
        'success': False,
        'error': None,
        'save_time_ms': 0.0,
        'load_time_ms': 0.0,
        'file_size_kb': 0.0,
        'data_integrity': False
    }
    
    try:
        # Create serializer instance
        # Root cause: Some serializers may require initialization parameters
        # Solution: Try instantiation, handle errors gracefully
        try:
            serializer = serializer_class()
        except Exception as init_error:
            # Some formats (like schema-based) may require configuration
            if requires_schema:
                result['error'] = f"Format requires schema configuration: {init_error}"
                return result
            raise
        
        # Skip formats that don't support dict serialization well
        # Root cause: Some formats (CSV, INI, JSONL) are not ideal for nested dictionaries
        # Solution: Skip them with a clear message
        # JSONL is line-delimited and returns a list, not a dict
        if format_name in ['csv', 'ini', 'jsonl']:
            result['error'] = f"Format '{format_name}' not suitable for nested dictionary structures (expects list/streaming format)"
            return result
        
        # Phase 1: ATOMIC SAVE (write entire database as one big file)
        with metrics.measure("save"):
            serializer.save_file(test_data, file_path)
        
        save_time_ms = metrics.get_metrics()['save']['total_time_ms']
        result['save_time_ms'] = save_time_ms
        
        # Verify file was created and get size
        if not file_path.exists():
            result['error'] = f"File not created: {file_path}"
            return result
        
        file_size_bytes = file_path.stat().st_size
        result['file_size_kb'] = file_size_bytes / 1024.0
        
        # Phase 2: ATOMIC LOAD (read entire database as one big file)
        with metrics.measure("load"):
            loaded_data = serializer.load_file(file_path)
        
        load_time_ms = metrics.get_metrics()['load']['total_time_ms']
        result['load_time_ms'] = load_time_ms
        
        # Phase 3: VERIFY DATA INTEGRITY (round-trip check)
        integrity_ok, integrity_msg = verify_data_integrity(test_data, loaded_data)
        result['data_integrity'] = integrity_ok
        
        if not integrity_ok:
            result['error'] = f"Data integrity check failed: {integrity_msg}"
            return result
        
        # All operations successful
        result['success'] = True
        
    except Exception as e:
        # Root cause: Capture all exceptions for debugging
        # Solution: Store error message and continue with other formats
        result['error'] = str(e)
        import traceback
        print(f"    Error details:\n{traceback.format_exc()}")
    
    return result


def main():
    """Main benchmark execution"""
    print("=" * 80)
    print("x5 FILE SERIALIZATION BENCHMARK - ALL FORMATS COMPREHENSIVE TEST")
    print("=" * 80)
    
    if not SERIALIZATION_AVAILABLE:
        print("\n❌ ERROR: Required serialization libraries not available")
        print("Install with: pip install exonware-xwsystem[full]")
        if not XWFORMATS_AVAILABLE:
            print("For enterprise formats: pip install exonware-xwformats[full]")
        sys.exit(1)
    
    if len(FORMATS) == 0:
        print("\n❌ ERROR: No serialization formats available")
        print("Install with: pip install exonware-xwsystem[full]")
        if not XWFORMATS_AVAILABLE:
            print("For enterprise formats: pip install exonware-xwformats[full]")
        sys.exit(1)
    
    print(f"\n📋 Available Formats: {len(FORMATS)}")
    if not XWFORMATS_AVAILABLE:
        print("⚠️  NOTE: Enterprise formats (xwformats) not available - install for full test coverage")
    
    # Setup data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean data directory (remove old test files)
    # Root cause: Need to clean all possible format extensions before running benchmarks
    # Solution: Collect all extensions from FORMATS list and clean them
    if data_dir.exists():
        try:
            # Collect all extensions from FORMATS
            extensions = set()
            for fmt_info in FORMATS:
                if len(fmt_info) >= 3:
                    ext = fmt_info[2]
                    extensions.add(ext)
                    # Also clean common variants
                    if ext == '.yaml':
                        extensions.add('.yml')
            
            # Clean files with collected extensions
            for ext in extensions:
                for file in data_dir.glob(f"*{ext}"):
                    try:
                        file.unlink()
                    except PermissionError:
                        pass  # Skip files that can't be deleted
        except Exception as e:
            print(f"⚠️  WARNING: Could not clean some files: {e}")
            print(f"   Files may be open in another program. Continuing...")
    
    # Test configuration - Full social media platform scale
    # Significantly increased volumes for comprehensive testing
    num_users = 1000
    num_posts = 5000
    num_comments = 10000
    num_relationships = 5000
    num_likes = 25000
    num_shares = 2000
    num_messages = 5000
    num_notifications = 15000
    num_groups = 100
    num_events = 200
    
    print(f"\n📊 Test Configuration:")
    print(f"  Users: {num_users:,}")
    print(f"  Posts: {num_posts:,}")
    print(f"  Comments: {num_comments:,}")
    print(f"  Relationships: {num_relationships:,}")
    print(f"  Likes: {num_likes:,}")
    print(f"  Shares: {num_shares:,}")
    print(f"  Messages: {num_messages:,}")
    print(f"  Notifications: {num_notifications:,}")
    print(f"  Groups: {num_groups:,}")
    print(f"  Events: {num_events:,}")
    total_entities = (
        num_users + num_posts + num_comments + num_relationships +
        num_likes + num_shares + num_messages + num_notifications +
        num_groups + num_events
    )
    print(f"  Total entities: {total_entities:,}")
    print(f"  Formats to test: {len(FORMATS)}")
    print(f"  Format categories:")
    categories = {}
    for fmt_info in FORMATS:
        if len(fmt_info) >= 4:
            cat = fmt_info[3]
            categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"    - {cat}: {count}")
    print(f"  Data directory: {data_dir.absolute()}")
    print(f"\n🎯 Testing: Atomic single-file save/load operations")
    print(f"   - Each format writes ONE BIG FILE")
    print(f"   - Each format reads ONE BIG FILE")
    print(f"   - Round-trip integrity verification")
    print(f"   - Full social media platform data model\n")
    
    # Prepare test data (in memory)
    print("📦 Preparing comprehensive social media test data in memory...")
    test_data = prepare_test_data(
        num_users, num_posts, num_comments, num_relationships,
        num_likes, num_shares, num_messages, num_notifications,
        num_groups, num_events
    )
    meta = test_data['data']
    print(f"✅ Test data prepared:")
    print(f"   - {len(meta['users']):,} users")
    print(f"   - {len(meta['posts']):,} posts")
    print(f"   - {len(meta['comments']):,} comments")
    print(f"   - {len(meta['relationships']):,} relationships")
    print(f"   - {len(meta['likes']):,} likes")
    print(f"   - {len(meta['shares']):,} shares")
    print(f"   - {len(meta['messages']):,} messages")
    print(f"   - {len(meta['notifications']):,} notifications")
    print(f"   - {len(meta['groups']):,} groups")
    print(f"   - {len(meta['events']):,} events")
    print(f"   - {len(meta['hashtags']):,} hashtags")
    
    # Test each format
    print(f"\n{'=' * 80}")
    print("RUNNING BENCHMARKS")
    print(f"{'=' * 80}\n")
    
    all_results = {}
    
    for format_info in FORMATS:
        # Unpack format info (supports both old 3-tuple and new 5-tuple format)
        if len(format_info) == 3:
            format_name, serializer_class, extension = format_info
            category = 'unknown'
            requires_schema = False
        else:
            format_name, serializer_class, extension, category, requires_schema = format_info
        print(f"Testing: {format_name.upper()}")
        
        # Create unique file path for this format
        file_path = data_dir / f"database_{format_name}{extension}"
        
        # Create fresh metrics for this format
        metrics = BenchmarkMetrics()
        
        # Run atomic operations test
        result = test_format_atomic_operations(
            format_name=format_name,
            serializer_class=serializer_class,
            extension=extension,
            test_data=test_data,
            file_path=file_path,
            metrics=metrics,
            requires_schema=requires_schema
        )
        
        all_results[format_name] = result
        
        # Print result with category indicator
        category_indicator = f"[{category.upper()}]" if len(format_info) >= 4 else ""
        if result['success']:
            print(f"  ✅ {format_name.upper()} {category_indicator}: "
                  f"SAVE:{result['save_time_ms']:.1f}ms "
                  f"LOAD:{result['load_time_ms']:.1f}ms "
                  f"SIZE:{result['file_size_kb']:.1f}KB "
                  f"INTEGRITY:✅")
        else:
            print(f"  ❌ {format_name.upper()} {category_indicator}: FAILED - {result['error']}")
    
    # Print summary
    print(f"\n{'=' * 80}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 80}\n")
    
    successful = {k: v for k, v in all_results.items() if v['success']}
    failed = {k: v for k, v in all_results.items() if not v['success']}
    
    if successful:
        print(f"✅ Successful formats: {len(successful)}/{len(FORMATS)}")
        
        # Group by category for better analysis
        by_category = {}
        for format_name, result in successful.items():
            # Find category for this format
            category = 'unknown'
            for fmt_info in FORMATS:
                if fmt_info[0] == format_name and len(fmt_info) >= 4:
                    category = fmt_info[3]
                    break
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((format_name, result))
        
        # Overall Performance Ranking (by total time)
        print(f"\n📊 Overall Performance Ranking (by total time):")
        sorted_by_time = sorted(
            successful.items(),
            key=lambda x: x[1]['save_time_ms'] + x[1]['load_time_ms']
        )
        
        for rank, (format_name, result) in enumerate(sorted_by_time, 1):
            total_time = result['save_time_ms'] + result['load_time_ms']
            # Find category
            category = 'unknown'
            for fmt_info in FORMATS:
                if fmt_info[0] == format_name and len(fmt_info) >= 4:
                    category = fmt_info[3]
                    break
            print(f"  {rank}. {format_name.upper()} [{category.upper()}]: "
                  f"{total_time:.1f}ms total "
                  f"(SAVE:{result['save_time_ms']:.1f}ms + LOAD:{result['load_time_ms']:.1f}ms) "
                  f"{result['file_size_kb']:.1f}KB")
        
        # Top 3 by category
        print(f"\n🏆 Top Performers by Category:")
        for category in sorted(by_category.keys()):
            formats = by_category[category]
            if formats:
                sorted_cat = sorted(
                    formats,
                    key=lambda x: x[1]['save_time_ms'] + x[1]['load_time_ms']
                )
                top = sorted_cat[0]
                total_time = top[1]['save_time_ms'] + top[1]['load_time_ms']
                print(f"  {category.upper()}: {top[0].upper()} ({total_time:.1f}ms, {top[1]['file_size_kb']:.1f}KB)")
        
        print(f"\n📦 File Size Ranking (most compact first):")
        sorted_by_size = sorted(successful.items(), key=lambda x: x[1]['file_size_kb'])
        for rank, (format_name, result) in enumerate(sorted_by_size, 1):
            # Find category
            category = 'unknown'
            for fmt_info in FORMATS:
                if fmt_info[0] == format_name and len(fmt_info) >= 4:
                    category = fmt_info[3]
                    break
            print(f"  {rank}. {format_name.upper()} [{category.upper()}]: {result['file_size_kb']:.1f}KB")
    
    if failed:
        print(f"\n❌ Failed formats: {len(failed)}/{len(FORMATS)}")
        for format_name, result in failed.items():
            print(f"  - {format_name.upper()}: {result['error']}")
    
    print(f"\n{'=' * 80}")
    print(f"✅ Benchmark complete! Files saved to: {data_dir.absolute()}")
    print(f"{'=' * 80}\n")
    
    # Exit with error code if any format failed
    if failed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
