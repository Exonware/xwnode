#!/usr/bin/env python3
"""
Generate a 1GB NDJSON file using x5 schema (social media platform data).
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for schema imports
# x5 is at: xwnode/examples/x5
# schema is at: xwnode/examples/db_example/x0_common
examples_dir = Path(__file__).parent.parent  # xwnode/examples
db_example_dir = examples_dir / "db_example"
sys.path.insert(0, str(db_example_dir))

from x0_common.schema import (
    User, Post, Comment, generate_user, generate_post, generate_comment
)


def generate_1gb_ndjson(output_path: str, target_size_gb: float = 1.0):
    """
    Generate a 1GB NDJSON file using x5 schema.
    
    Args:
        output_path: Path to output file
        target_size_gb: Target file size in GB (default: 1.0)
    """
    target_size_bytes = int(target_size_gb * 1024 * 1024 * 1024)
    current_size = 0
    record_count = 0
    
    # Track user IDs for relationships
    user_ids = []
    
    print(f"Generating {target_size_gb}GB NDJSON file...")
    print(f"Target size: {target_size_bytes / (1024**3):.2f} GB")
    print("-" * 60)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Generate users first (10% of data)
        print("Generating users...")
        user_count = 0
        while current_size < target_size_bytes * 0.1:
            user = generate_user(user_count)
            user_dict = user.to_dict()
            line = json.dumps(user_dict, ensure_ascii=False) + '\n'
            f.write(line)
            current_size += len(line.encode('utf-8'))
            user_ids.append(user.id)
            user_count += 1
            record_count += 1
            
            if user_count % 1000 == 0:
                print(f"  Users: {user_count}, Size: {current_size / (1024**2):.2f} MB")
        
        print(f"✓ Generated {user_count} users ({current_size / (1024**2):.2f} MB)")
        
        # Generate posts (60% of data)
        print("Generating posts...")
        post_count = 0
        while current_size < target_size_bytes * 0.7:
            user_id = user_ids[post_count % len(user_ids)] if user_ids else str(post_count)
            post = generate_post(post_count, user_id, user_ids)
            post_dict = post.to_dict()
            line = json.dumps(post_dict, ensure_ascii=False) + '\n'
            f.write(line)
            current_size += len(line.encode('utf-8'))
            post_count += 1
            record_count += 1
            
            if post_count % 1000 == 0:
                print(f"  Posts: {post_count}, Size: {current_size / (1024**2):.2f} MB")
        
        print(f"✓ Generated {post_count} posts ({current_size / (1024**2):.2f} MB)")
        
        # Generate comments (30% of data to reach target)
        print("Generating comments...")
        comment_count = 0
        post_ids = [f"post_{i}" for i in range(post_count)]
        
        while current_size < target_size_bytes:
            post_id = post_ids[comment_count % len(post_ids)] if post_ids else f"post_{comment_count}"
            user_id = user_ids[comment_count % len(user_ids)] if user_ids else str(comment_count)
            comment = generate_comment(comment_count, post_id, user_id, user_ids)
            comment_dict = comment.to_dict()
            line = json.dumps(comment_dict, ensure_ascii=False) + '\n'
            f.write(line)
            current_size += len(line.encode('utf-8'))
            comment_count += 1
            record_count += 1
            
            if comment_count % 1000 == 0:
                print(f"  Comments: {comment_count}, Size: {current_size / (1024**2):.2f} MB")
    
    final_size = Path(output_path).stat().st_size
    print("-" * 60)
    print(f"✓ Generation complete!")
    print(f"  Total records: {record_count:,}")
    print(f"  Final size: {final_size / (1024**3):.2f} GB ({final_size:,} bytes)")
    print(f"  File: {output_path}")
    
    return record_count, final_size


if __name__ == "__main__":
    output_file = Path(__file__).parent / "data" / "database_1gb.jsonl"
    output_file.parent.mkdir(exist_ok=True)
    
    generate_1gb_ndjson(str(output_file), target_size_gb=1.0)

