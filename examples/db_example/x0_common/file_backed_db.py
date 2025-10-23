"""
File-Backed Database Classes

Database implementations that use file storage as the primary data store.
All operations work directly with persistent file storage.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 17, 2025
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from exonware.xwnode.defs import NodeMode, EdgeMode

from .schema import User, Post, Comment, Relationship
from .file_backed_storage import SimpleFileStorage, TransactionalFileStorage


class FileBackedDatabase:
    """
    File-backed database implementation.
    All operations read/write directly to file storage.
    """
    
    def __init__(self, name: str, storage, node_mode, edge_mode: Optional[EdgeMode] = None):
        """
        Initialize file-backed database.
        
        Args:
            name: Database name
            storage: FileBackedStorage instance
            node_mode: NodeMode (for metadata only in file-backed version)
            edge_mode: EdgeMode (for metadata only in file-backed version)
        """
        self.name = name
        self.storage = storage
        self.node_mode = node_mode
        self.edge_mode = edge_mode
        
        # Initialize metadata
        data = self.storage.get_all_data()
        if 'metadata' not in data or not data['metadata']:
            data['metadata'] = {
                'name': name,
                'node_mode': node_mode.name if hasattr(node_mode, 'name') else str(node_mode),
                'edge_mode': edge_mode.name if edge_mode and hasattr(edge_mode, 'name') else str(edge_mode),
            }
            self.storage.set_all_data(data)
    
    # ============================================================================
    # USER OPERATIONS
    # ============================================================================
    
    def insert_user(self, user: User) -> str:
        """Insert a new user (writes to file)"""
        user_dict = user.to_dict()
        user_id = user_dict['id']
        
        # Write user to storage
        self.storage.set_entity('users', user_id, user_dict)
        
        # Update index
        data = self.storage.get_all_data()
        if 'indexes' not in data:
            data['indexes'] = {}
        if 'users_by_username' not in data['indexes']:
            data['indexes']['users_by_username'] = {}
        data['indexes']['users_by_username'][user_dict['username']] = user_id
        self.storage.set_all_data(data)
        
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID (reads from file)"""
        return self.storage.get_entity('users', user_id)
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user fields (reads and writes to file)"""
        user = self.storage.get_entity('users', user_id)
        if not user:
            return False
        
        user.update(updates)
        self.storage.set_entity('users', user_id, user)
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Hard delete user (removes from file)"""
        user = self.storage.get_entity('users', user_id)
        if not user:
            return False
        
        # Remove from storage
        self.storage.delete_entity('users', user_id)
        
        # Update index
        data = self.storage.get_all_data()
        if 'indexes' in data and 'users_by_username' in data['indexes']:
            username = user['username']
            if username in data['indexes']['users_by_username']:
                del data['indexes']['users_by_username'][username]
                self.storage.set_all_data(data)
        
        return True
    
    def list_all_users(self) -> List[Dict[str, Any]]:
        """List all users (reads from file)"""
        return list(self.storage.get_collection('users').values())
    
    # ============================================================================
    # POST OPERATIONS
    # ============================================================================
    
    def insert_post(self, post: Post) -> str:
        """Insert a new post (writes to file)"""
        post_dict = post.to_dict()
        post_id = post_dict['id']
        
        # Write post to storage
        self.storage.set_entity('posts', post_id, post_dict)
        
        # Update index
        data = self.storage.get_all_data()
        if 'indexes' not in data:
            data['indexes'] = {}
        if 'posts_by_user' not in data['indexes']:
            data['indexes']['posts_by_user'] = {}
        
        user_id = post_dict['user_id']
        if user_id not in data['indexes']['posts_by_user']:
            data['indexes']['posts_by_user'][user_id] = []
        if post_id not in data['indexes']['posts_by_user'][user_id]:
            data['indexes']['posts_by_user'][user_id].append(post_id)
        self.storage.set_all_data(data)
        
        return post_id
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get post by ID (reads from file)"""
        return self.storage.get_entity('posts', post_id)
    
    def update_post(self, post_id: str, updates: Dict[str, Any]) -> bool:
        """Update post fields (reads and writes to file)"""
        post = self.storage.get_entity('posts', post_id)
        if not post:
            return False
        
        post.update(updates)
        self.storage.set_entity('posts', post_id, post)
        return True
    
    def delete_post(self, post_id: str) -> bool:
        """Hard delete post (removes from file)"""
        post = self.storage.get_entity('posts', post_id)
        if not post:
            return False
        
        # Remove from storage
        self.storage.delete_entity('posts', post_id)
        
        # Update index
        data = self.storage.get_all_data()
        if 'indexes' in data and 'posts_by_user' in data['indexes']:
            user_id = post['user_id']
            if user_id in data['indexes']['posts_by_user']:
                if post_id in data['indexes']['posts_by_user'][user_id]:
                    data['indexes']['posts_by_user'][user_id].remove(post_id)
                self.storage.set_all_data(data)
        
        return True
    
    def list_posts_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """List all posts by a specific user (reads from file)"""
        data = self.storage.get_all_data()
        post_ids = data.get('indexes', {}).get('posts_by_user', {}).get(user_id, [])
        return [self.storage.get_entity('posts', pid) for pid in post_ids if self.storage.get_entity('posts', pid)]
    
    # ============================================================================
    # COMMENT OPERATIONS
    # ============================================================================
    
    def insert_comment(self, comment: Comment) -> str:
        """Insert a new comment (writes to file)"""
        comment_dict = comment.to_dict()
        comment_id = comment_dict['id']
        
        # Write comment to storage
        self.storage.set_entity('comments', comment_id, comment_dict)
        
        # Update index
        data = self.storage.get_all_data()
        if 'indexes' not in data:
            data['indexes'] = {}
        if 'comments_by_post' not in data['indexes']:
            data['indexes']['comments_by_post'] = {}
        
        post_id = comment_dict['post_id']
        if post_id not in data['indexes']['comments_by_post']:
            data['indexes']['comments_by_post'][post_id] = []
        if comment_id not in data['indexes']['comments_by_post'][post_id]:
            data['indexes']['comments_by_post'][post_id].append(comment_id)
        self.storage.set_all_data(data)
        
        return comment_id
    
    def get_comment(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """Get comment by ID (reads from file)"""
        return self.storage.get_entity('comments', comment_id)
    
    def update_comment(self, comment_id: str, updates: Dict[str, Any]) -> bool:
        """Update comment fields (reads and writes to file)"""
        comment = self.storage.get_entity('comments', comment_id)
        if not comment:
            return False
        
        comment.update(updates)
        self.storage.set_entity('comments', comment_id, comment)
        return True
    
    def delete_comment(self, comment_id: str) -> bool:
        """Hard delete comment (removes from file)"""
        comment = self.storage.get_entity('comments', comment_id)
        if not comment:
            return False
        
        # Remove from storage
        self.storage.delete_entity('comments', comment_id)
        
        # Update index
        data = self.storage.get_all_data()
        if 'indexes' in data and 'comments_by_post' in data['indexes']:
            post_id = comment['post_id']
            if post_id in data['indexes']['comments_by_post']:
                if comment_id in data['indexes']['comments_by_post'][post_id]:
                    data['indexes']['comments_by_post'][post_id].remove(comment_id)
                self.storage.set_all_data(data)
        
        return True
    
    def list_comments_by_post(self, post_id: str) -> List[Dict[str, Any]]:
        """List all comments for a specific post (reads from file)"""
        data = self.storage.get_all_data()
        comment_ids = data.get('indexes', {}).get('comments_by_post', {}).get(post_id, [])
        return [self.storage.get_entity('comments', cid) for cid in comment_ids if self.storage.get_entity('comments', cid)]
    
    # ============================================================================
    # RELATIONSHIP OPERATIONS
    # ============================================================================
    
    def add_relationship(self, relationship: Relationship) -> str:
        """Add a relationship (writes to file)"""
        rel_dict = relationship.to_dict()
        rel_id = rel_dict['id']
        
        # Write relationship to storage
        self.storage.set_entity('relationships', rel_id, rel_dict)
        
        return rel_id
    
    def get_followers(self, user_id: str) -> List[str]:
        """Get all users who follow this user (reads from file)"""
        relationships = self.storage.get_collection('relationships')
        return [
            r['source_user_id'] for r in relationships.values()
            if r['target_user_id'] == user_id and r['relationship_type'] == 'follows'
        ]
    
    def get_following(self, user_id: str) -> List[str]:
        """Get all users that this user follows (reads from file)"""
        relationships = self.storage.get_collection('relationships')
        return [
            r['target_user_id'] for r in relationships.values()
            if r['source_user_id'] == user_id and r['relationship_type'] == 'follows'
        ]
    
    # ============================================================================
    # STATISTICS
    # ============================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics (reads from file)"""
        users = self.storage.get_collection('users')
        posts = self.storage.get_collection('posts')
        comments = self.storage.get_collection('comments')
        relationships = self.storage.get_collection('relationships')
        
        return {
            'name': self.name,
            'node_mode': self.node_mode.name if hasattr(self.node_mode, 'name') else str(self.node_mode),
            'edge_mode': self.edge_mode.name if self.edge_mode and hasattr(self.edge_mode, 'name') else str(self.edge_mode),
            'total_users': len(users),
            'total_posts': len(posts),
            'total_comments': len(comments),
            'total_relationships': len(relationships)
        }


class TransactionalFileBackedDatabase(FileBackedDatabase):
    """
    Transactional file-backed database with atomic operations.
    Supports batch operations within transactions.
    """
    
    def __init__(self, name: str, storage: TransactionalFileStorage, node_mode, edge_mode: Optional[EdgeMode] = None):
        """Initialize transactional file-backed database"""
        super().__init__(name, storage, node_mode, edge_mode)
    
    def batch_insert(self, users: List[User] = None, posts: List[Post] = None, 
                    comments: List[Comment] = None, relationships: List[Relationship] = None):
        """
        Batch insert multiple entities atomically using transaction.
        
        Args:
            users: List of users to insert
            posts: List of posts to insert
            comments: List of comments to insert
            relationships: List of relationships to add
        """
        with self.storage.transaction():
            if users:
                for user in users:
                    self.insert_user(user)
            if posts:
                for post in posts:
                    self.insert_post(post)
            if comments:
                for comment in comments:
                    self.insert_comment(comment)
            if relationships:
                for rel in relationships:
                    self.add_relationship(rel)
    
    def batch_update(self, updates: List[tuple]):
        """
        Batch update multiple entities atomically using transaction.
        
        Args:
            updates: List of (collection, entity_id, updates_dict) tuples
        """
        with self.storage.transaction():
            for collection, entity_id, update_dict in updates:
                if collection == 'users':
                    self.update_user(entity_id, update_dict)
                elif collection == 'posts':
                    self.update_post(entity_id, update_dict)
                elif collection == 'comments':
                    self.update_comment(entity_id, update_dict)
    
    def batch_delete(self, deletions: List[tuple]):
        """
        Batch delete multiple entities atomically using transaction.
        
        Args:
            deletions: List of (collection, entity_id) tuples
        """
        with self.storage.transaction():
            for collection, entity_id in deletions:
                if collection == 'users':
                    self.delete_user(entity_id)
                elif collection == 'posts':
                    self.delete_post(entity_id)
                elif collection == 'comments':
                    self.delete_comment(entity_id)

