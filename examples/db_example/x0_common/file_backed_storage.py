"""
File-Backed Storage Layer

Provides persistent storage backends for database operations using different
serialization formats. Supports both simple file operations and advanced
transactional operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 17, 2025
"""

import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

# Add xwsystem to path
project_root = Path(__file__).parent.parent.parent.parent
xwsystem_root = project_root.parent / "xwsystem" / "src"
sys.path.insert(0, str(xwsystem_root))


class FileBackedStorage(ABC):
    """Abstract base class for file-backed storage"""
    
    def __init__(self, file_path: Path, serializer):
        """
        Initialize file-backed storage.
        
        Args:
            file_path: Path to storage file
            serializer: Serializer instance for reading/writing
        """
        self.file_path = file_path
        self.serializer = serializer
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage file/directory exists"""
        if not self.file_path.exists():
            # Initialize empty storage
            self._write_data({
                'metadata': {},
                'data': {
                    'users': {},
                    'posts': {},
                    'comments': {},
                    'relationships': {}
                },
                'indexes': {
                    'users_by_username': {},
                    'posts_by_user': {},
                    'comments_by_post': {}
                }
            })
    
    @abstractmethod
    def _read_data(self) -> Dict[str, Any]:
        """Read entire database from storage"""
        pass
    
    @abstractmethod
    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write entire database to storage"""
        pass
    
    @abstractmethod
    def get_entity(self, collection: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get a single entity by ID"""
        pass
    
    @abstractmethod
    def set_entity(self, collection: str, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """Set/update a single entity"""
        pass
    
    @abstractmethod
    def delete_entity(self, collection: str, entity_id: str) -> bool:
        """Delete a single entity"""
        pass
    
    @abstractmethod
    def get_collection(self, collection: str) -> Dict[str, Dict[str, Any]]:
        """Get entire collection"""
        pass


class SimpleFileStorage(FileBackedStorage):
    """
    Simple file-backed storage - reads/writes entire file on each operation.
    Best for formats like JSON, YAML, MSGPACK, PICKLE, etc.
    """
    
    def _read_data(self) -> Dict[str, Any]:
        """Read entire database from file"""
        if not self.file_path.exists():
            return {
                'metadata': {},
                'data': {
                    'users': {},
                    'posts': {},
                    'comments': {},
                    'relationships': {}
                },
                'indexes': {
                    'users_by_username': {},
                    'posts_by_user': {},
                    'comments_by_post': {}
                }
            }
        
        try:
            return self.serializer.load_file(self.file_path)
        except Exception as e:
            print(f"Warning: Could not read {self.file_path}: {e}")
            return {
                'metadata': {},
                'data': {
                    'users': {},
                    'posts': {},
                    'comments': {},
                    'relationships': {}
                },
                'indexes': {
                    'users_by_username': {},
                    'posts_by_user': {},
                    'comments_by_post': {}
                }
            }
    
    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write entire database to file"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.serializer.save_file(data, self.file_path)
    
    def get_entity(self, collection: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get a single entity by ID"""
        data = self._read_data()
        return data.get('data', {}).get(collection, {}).get(entity_id)
    
    def set_entity(self, collection: str, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """Set/update a single entity"""
        data = self._read_data()
        if 'data' not in data:
            data['data'] = {}
        if collection not in data['data']:
            data['data'][collection] = {}
        data['data'][collection][entity_id] = entity_data
        self._write_data(data)
    
    def delete_entity(self, collection: str, entity_id: str) -> bool:
        """Delete a single entity"""
        data = self._read_data()
        if entity_id in data.get('data', {}).get(collection, {}):
            del data['data'][collection][entity_id]
            self._write_data(data)
            return True
        return False
    
    def get_collection(self, collection: str) -> Dict[str, Dict[str, Any]]:
        """Get entire collection"""
        data = self._read_data()
        return data.get('data', {}).get(collection, {})
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get entire database"""
        return self._read_data()
    
    def set_all_data(self, data: Dict[str, Any]) -> None:
        """Set entire database"""
        self._write_data(data)


class TransactionalFileStorage(FileBackedStorage):
    """
    Transactional file-backed storage with atomic operations.
    Supports formats like SQLITE3, LMDB that have native transaction support.
    """
    
    def __init__(self, file_path: Path, serializer):
        """Initialize transactional storage"""
        self._in_transaction = False
        self._transaction_data = None
        super().__init__(file_path, serializer)
    
    def _read_data(self) -> Dict[str, Any]:
        """Read data (from transaction buffer if in transaction)"""
        if self._in_transaction and self._transaction_data is not None:
            return self._transaction_data
        
        if not self.file_path.exists():
            return {
                'metadata': {},
                'data': {
                    'users': {},
                    'posts': {},
                    'comments': {},
                    'relationships': {}
                },
                'indexes': {
                    'users_by_username': {},
                    'posts_by_user': {},
                    'comments_by_post': {}
                }
            }
        
        try:
            return self.serializer.load_file(self.file_path)
        except Exception:
            return {
                'metadata': {},
                'data': {
                    'users': {},
                    'posts': {},
                    'comments': {},
                    'relationships': {}
                },
                'indexes': {
                    'users_by_username': {},
                    'posts_by_user': {},
                    'comments_by_post': {}
                }
            }
    
    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write data (to transaction buffer if in transaction)"""
        if self._in_transaction:
            self._transaction_data = data
        else:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.serializer.save_file(data, self.file_path)
    
    @contextmanager
    def transaction(self):
        """
        Transaction context manager for atomic operations.
        
        Usage:
            with storage.transaction():
                storage.set_entity('users', 'id1', {...})
                storage.set_entity('users', 'id2', {...})
                # All changes committed atomically
        """
        self._in_transaction = True
        self._transaction_data = self._read_data()
        
        try:
            yield self
            # Commit: write transaction buffer to file
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.serializer.save_file(self._transaction_data, self.file_path)
        except Exception as e:
            # Rollback: discard transaction buffer
            print(f"Transaction rolled back due to error: {e}")
            raise
        finally:
            self._in_transaction = False
            self._transaction_data = None
    
    def get_entity(self, collection: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get a single entity by ID (transaction-aware)"""
        data = self._read_data()
        return data.get('data', {}).get(collection, {}).get(entity_id)
    
    def set_entity(self, collection: str, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """Set/update a single entity (transaction-aware)"""
        data = self._read_data()
        if 'data' not in data:
            data['data'] = {}
        if collection not in data['data']:
            data['data'][collection] = {}
        data['data'][collection][entity_id] = entity_data
        self._write_data(data)
    
    def delete_entity(self, collection: str, entity_id: str) -> bool:
        """Delete a single entity (transaction-aware)"""
        data = self._read_data()
        if entity_id in data.get('data', {}).get(collection, {}):
            del data['data'][collection][entity_id]
            self._write_data(data)
            return True
        return False
    
    def get_collection(self, collection: str) -> Dict[str, Dict[str, Any]]:
        """Get entire collection (transaction-aware)"""
        data = self._read_data()
        return data.get('data', {}).get(collection, {})
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get entire database"""
        return self._read_data()
    
    def set_all_data(self, data: Dict[str, Any]) -> None:
        """Set entire database"""
        self._write_data(data)

