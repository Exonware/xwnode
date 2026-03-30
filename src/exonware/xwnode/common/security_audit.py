#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/security_audit.py
Security Audit Utilities for xwnode.
REUSES xwsystem.security.audit for generic security auditing.
Provides xwnode-specific convenience functions.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.19
Generation Date: 15-Nov-2025
"""

from typing import Any
# REUSE xwsystem security audit utilities
from exonware.xwsystem.security.audit import (
    SecurityAuditor as XWSystemSecurityAuditor,
    SecurityLevel,
    SecurityIssue,
    audit_security
)


class SecurityAuditor:
    """
    Security audit utilities for xwnode strategies.
    REUSES xwsystem.security.audit.SecurityAuditor.
    """
    @staticmethod

    def audit_strategy(strategy: Any) -> list[SecurityIssue]:
        """
        Audit a strategy for security issues.
        REUSES xwsystem.security.audit.SecurityAuditor.audit_object.
        Args:
            strategy: Strategy instance to audit
        Returns:
            List of SecurityIssue objects
        """
        # REUSE xwsystem SecurityAuditor
        return XWSystemSecurityAuditor.audit_object(strategy, object_type="strategy")
    @staticmethod

    def audit_node(node: Any) -> list[SecurityIssue]:
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

    def generate_report(issues: list[SecurityIssue]) -> dict[str, Any]:
        """
        Generate a security audit report.
        REUSES xwsystem.security.audit.SecurityAuditor.generate_report.
        Args:
            issues: List of security issues
        Returns:
            Dictionary with report data
        """
        # REUSE xwsystem SecurityAuditor
        return XWSystemSecurityAuditor.generate_report(issues)


def audit_node_security(node: Any) -> dict[str, Any]:
    """
    Convenience function to audit a node's security.
    Args:
        node: XWNode instance
    Returns:
        Security audit report
    """
    issues = SecurityAuditor.audit_node(node)
    return SecurityAuditor.generate_report(issues)
