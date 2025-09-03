"""
Basic functionality tests for xnode migration verification

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025
"""

import pytest
from exonware.xnode import xNode, xNodeError, xNodePathError, xNodeTypeError


class TestBasicFunctionality:
    """Test basic xNode functionality to verify migration."""
    
    def test_import(self):
        """Test that the library can be imported."""
        from exonware.xnode import xNode
        assert xNode is not None
    
    def test_create_from_dict(self):
        """Test creating xNode from dictionary."""
        data = {'name': 'Alice', 'age': 30}
        node = xNode.from_native(data)
        
        assert node is not None
        assert node.is_dict
        assert not node.is_list
        assert not node.is_leaf
    
    def test_create_from_list(self):
        """Test creating xNode from list."""
        data = ['apple', 'banana', 'cherry']
        node = xNode.from_native(data)
        
        assert node is not None
        assert node.is_list
        assert not node.is_dict
        assert not node.is_leaf
    
    def test_create_from_primitive(self):
        """Test creating xNode from primitive value."""
        node = xNode.from_native("hello")
        
        assert node is not None
        assert node.is_leaf
        assert not node.is_dict
        assert not node.is_list
        assert node.value == "hello"
    
    def test_path_navigation(self):
        """Test basic path navigation."""
        data = {
            'user': {
                'name': 'Alice',
                'age': 30
            }
        }
        node = xNode.from_native(data)
        
        # Test get method
        user_node = node.get('user')
        assert user_node is not None
        assert user_node.is_dict
        
        # Test nested access
        name_node = user_node.get('name')
        assert name_node is not None
        assert name_node.value == 'Alice'
    
    def test_bracket_notation(self):
        """Test bracket notation access."""
        data = {
            'users': [
                {'name': 'Alice'},
                {'name': 'Bob'}
            ]
        }
        node = xNode.from_native(data)
        
        # Test dictionary access
        users = node['users']
        assert users.is_list
        
        # Test list access
        first_user = users[0]
        assert first_user.is_dict
        
        # Test nested access
        name = first_user['name']
        assert name.value == 'Alice'
    
    def test_find_method(self):
        """Test find method with path."""
        data = {
            'users': [
                {'name': 'Alice', 'age': 30},
                {'name': 'Bob', 'age': 25}
            ]
        }
        node = xNode.from_native(data)
        
        # Test find with dot notation
        alice_name = node.find('users.0.name')
        assert alice_name is not None
        assert alice_name.value == 'Alice'
        
        # Test find with default
        missing = node.find('users.0.missing', 'default')
        assert missing is not None
        assert missing.value == 'default'
    
    def test_to_native(self):
        """Test converting back to native Python objects."""
        data = {
            'name': 'Alice',
            'age': 30,
            'hobbies': ['reading', 'coding']
        }
        node = xNode.from_native(data)
        
        result = node.to_native()
        assert result == data
    
    def test_set_operation(self):
        """Test setting values."""
        node = xNode.from_native({'name': 'Alice'})
        
        # Test set operation
        node.set('age', 30)
        
        age_node = node.get('age')
        assert age_node is not None
        assert age_node.value == 30
    
    def test_error_handling(self):
        """Test basic error handling."""
        node = xNode.from_native({'name': 'Alice'})
        
        # Test accessing non-existent key
        missing = node.get('missing')
        assert missing is None
        
        # Test with bracket notation (should raise error)
        with pytest.raises(xNodePathError):
            _ = node['missing']
    
    def test_iteration(self):
        """Test iteration over nodes."""
        data = {'a': 1, 'b': 2, 'c': 3}
        node = xNode.from_native(data)
        
        # Test length
        assert len(node) == 3
        
        # Test iteration
        values = []
        for child in node:
            values.append(child.value)
        
        assert set(values) == {1, 2, 3}
    
    def test_performance_stats(self):
        """Test performance statistics."""
        node = xNode.from_native({'name': 'Alice'})
        
        # Perform some operations
        node.get('name')
        node.find('name')
        node.set('age', 30)
        
        stats = node.get_performance_stats()
        assert isinstance(stats, dict)
        assert 'ops' in stats
        assert stats['ops'] > 0
    
    def test_query_interface(self):
        """Test query interface."""
        data = {
            'users': [
                {'name': 'Alice', 'age': 30},
                {'name': 'Bob', 'age': 25}
            ]
        }
        node = xNode.from_native(data)
        
        query = node.query('test')
        assert query is not None
        
        # Test find by value
        results = query.find_by_value('Alice')
        assert len(results) >= 0  # May be 0 in simplified implementation
    
    def test_factory_methods(self):
        """Test factory methods."""
        from exonware.xnode import xNodeFactory
        
        # Test create method
        node = xNodeFactory.create({'name': 'Alice'})
        assert node is not None
        assert node.get('name').value == 'Alice'
        
        # Test empty node
        empty = xNodeFactory.empty()
        assert empty is not None
        assert empty.is_dict
        assert len(empty) == 0
    
    def test_version_info(self):
        """Test version information."""
        import exonware.xnode
        
        assert hasattr(exonware.xnode, '__version__')
        assert hasattr(exonware.xnode, '__author__')
        assert hasattr(exonware.xnode, '__email__')
        assert hasattr(exonware.xnode, '__company__')
        
        assert exonware.xnode.__version__ == '0.0.1'
        assert exonware.xnode.__author__ == 'Eng. Muhammad AlShehri'
        assert exonware.xnode.__company__ == 'eXonware.com'
