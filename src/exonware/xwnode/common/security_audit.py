#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/security_audit.py

Security Audit Utilities

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 15-Nov-2025
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from exonware.xwsystem import get_logger

logger = get_logger(__name__)


class SecurityLevel(Enum):
    """Security issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityIssue:
    """A security issue found during audit."""
    level: SecurityLevel
    category: str
    description: str
    recommendation: str
    location: Optional[str] = None


class SecurityAuditor:
    """Security audit utilities for node strategies."""
    
    @staticmethod
    def audit_strategy(strategy: Any) -> List[SecurityIssue]:
        """
        Audit a strategy for security issues.
        
        Args:
            strategy: Strategy instance to audit
            
        Returns:
            List of SecurityIssue objects
        """
        issues = []
        strategy_name = getattr(strategy, '__class__', {}).__name__ if hasattr(strategy, '__class__') else 'Unknown'
        
        # Check for input validation
        if not hasattr(strategy, 'validate_input'):
            issues.append(SecurityIssue(
                level=SecurityLevel.MEDIUM,
                category="Input Validation",
                description=f"Strategy {strategy_name} does not have explicit input validation",
                recommendation="Add validate_input method to check inputs before processing",
                location=f"{strategy_name}.validate_input"
            ))
        
        # Check for bounds checking
        if hasattr(strategy, 'get') and not hasattr(strategy, '_check_bounds'):
            issues.append(SecurityIssue(
                level=SecurityLevel.LOW,
                category="Bounds Checking",
                description=f"Strategy {strategy_name} may not check bounds on get operations",
                recommendation="Ensure all index/key access operations validate bounds",
                location=f"{strategy_name}.get"
            ))
        
        # Check for error handling
        methods = [m for m in dir(strategy) if not m.startswith('_') and callable(getattr(strategy, m))]
        error_handling_count = sum(1 for m in methods if 'error' in m.lower() or 'exception' in m.lower())
        if error_handling_count == 0:
            issues.append(SecurityIssue(
                level=SecurityLevel.MEDIUM,
                category="Error Handling",
                description=f"Strategy {strategy_name} may lack comprehensive error handling",
                recommendation="Add explicit error handling for edge cases and invalid inputs",
                location=f"{strategy_name}"
            ))
        
        # Check for data sanitization
        if hasattr(strategy, 'put') or hasattr(strategy, 'set'):
            issues.append(SecurityIssue(
                level=SecurityLevel.INFO,
                category="Data Sanitization",
                description=f"Strategy {strategy_name} should sanitize data before storage",
                recommendation="Consider adding data sanitization for user-provided inputs",
                location=f"{strategy_name}.put/set"
            ))
        
        return issues
    
    @staticmethod
    def audit_node(node: Any) -> List[SecurityIssue]:
        """
        Audit a node for security issues.
        
        Args:
            node: XWNode instance to audit
            
        Returns:
            List of SecurityIssue objects
        """
        issues = []
        
        # Check strategy
        if hasattr(node, '_strategy'):
            strategy_issues = SecurityAuditor.audit_strategy(node._strategy)
            issues.extend(strategy_issues)
        
        # Check for access control
        if not hasattr(node, '_access_control'):
            issues.append(SecurityIssue(
                level=SecurityLevel.INFO,
                category="Access Control",
                description="Node does not have explicit access control",
                recommendation="Consider adding access control for sensitive operations",
                location="XWNode._access_control"
            ))
        
        return issues
    
    @staticmethod
    def generate_report(issues: List[SecurityIssue]) -> Dict[str, Any]:
        """
        Generate a security audit report.
        
        Args:
            issues: List of security issues
            
        Returns:
            Dictionary with report data
        """
        by_level = {}
        by_category = {}
        
        for issue in issues:
            # Group by level
            level = issue.level.value
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(issue)
            
            # Group by category
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)
        
        return {
            'total_issues': len(issues),
            'by_level': {k: len(v) for k, v in by_level.items()},
            'by_category': {k: len(v) for k, v in by_category.items()},
            'issues': [
                {
                    'level': issue.level.value,
                    'category': issue.category,
                    'description': issue.description,
                    'recommendation': issue.recommendation,
                    'location': issue.location
                }
                for issue in issues
            ]
        }


def audit_node_security(node: Any) -> Dict[str, Any]:
    """
    Convenience function to audit a node's security.
    
    Args:
        node: XWNode instance
        
    Returns:
        Security audit report
    """
    issues = SecurityAuditor.audit_node(node)
    return SecurityAuditor.generate_report(issues)

