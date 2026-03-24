#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/core/security_integration.py
Security Integration Helper for xwnode Strategies.
REUSES xwsystem security features:
- xwsystem.security.SecurityValidator for input validation
- xwsystem.security.PathValidator for path validation
- xwnode.core.security_logger for event logging
Provides easy-to-use security helpers for strategies.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.15
Generation Date: 26-Jan-2025
"""

from typing import Any
from exonware.xwsystem.security.validator import SecurityValidator as XWSystemSecurityValidator
from exonware.xwsystem.security.path_validator import PathValidator as XWSystemPathValidator, PathSecurityError
from .security_logger import get_security_logger, SecurityEventType


def validate_and_log_input(
    input_data: Any,
    strategy_name: str,
    operation: str = "operation"
) -> None:
    """
    Validate input and log security events using xwsystem.
    REUSES xwsystem SecurityValidator for validation.
    Args:
        input_data: Input data to validate
        strategy_name: Name of strategy performing operation
        operation: Operation name (for logging)
    """
    if not isinstance(input_data, str):
        return  # Only validate strings
    security_validator = XWSystemSecurityValidator()
    security_logger = get_security_logger()
    # REUSE xwsystem SQL injection detection
    if security_validator.detect_sql_injection(input_data):
        security_logger.log_injection_attempt(
            input_data=input_data,
            injection_type="sql",
            source=strategy_name,
            context={'operation': operation}
        )
        raise ValueError(f"SQL injection detected in {operation}")
    # REUSE xwsystem XSS detection
    if security_validator.detect_xss(input_data):
        security_logger.log_injection_attempt(
            input_data=input_data,
            injection_type="xss",
            source=strategy_name,
            context={'operation': operation}
        )
        raise ValueError(f"XSS attack detected in {operation}")


def validate_and_log_path(
    path: str,
    strategy_name: str,
    operation: str = "path_access"
) -> None:
    """
    Validate path and log security events using xwsystem.
    REUSES xwsystem PathValidator for validation.
    Args:
        path: Path to validate
        strategy_name: Name of strategy performing operation
        operation: Operation name (for logging)
    """
    path_validator = XWSystemPathValidator(allow_absolute=False)
    security_logger = get_security_logger()
    try:
        # REUSE xwsystem path validation
        path_validator.validate_path(path, for_writing=False)
    except PathSecurityError as e:
        # Log path traversal attempt
        security_logger.log_path_traversal(
            path=path,
            source=strategy_name,
            context={'operation': operation, 'error': str(e)}
        )
        raise


def log_resource_limit(
    resource_type: str,
    limit: int,
    actual: int,
    strategy_name: str
) -> None:
    """
    Log resource limit violation.
    Args:
        resource_type: Type of resource (memory, size, etc.)
        limit: Resource limit
        actual: Actual resource usage
        strategy_name: Name of strategy
    """
    security_logger = get_security_logger()
    security_logger.log_resource_limit(
        resource_type=resource_type,
        limit=limit,
        actual=actual,
        source=strategy_name
    )


def log_suspicious_activity(
    activity: str,
    strategy_name: str,
    context: dict | None = None
) -> None:
    """
    Log suspicious activity.
    Args:
        activity: Description of suspicious activity
        strategy_name: Name of strategy
        context: Additional context
    """
    security_logger = get_security_logger()
    security_logger.log_suspicious_activity(
        activity=activity,
        source=strategy_name,
        context=context or {}
    )
