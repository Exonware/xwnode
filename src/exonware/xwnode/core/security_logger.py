#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/core/security_logger.py
Security Event Logging System for xwnode.
REUSES xwsystem security and monitoring features:
- xwsystem.security.SecurityMonitor for intrusion detection
- xwsystem.monitoring.GenericMetrics for event recording
- xwsystem logging infrastructure
Provides xwnode-specific security event logging for:
- Path traversal attempts
- Injection attempts
- Resource limit violations
- Suspicious activities
- Security policy violations
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.6
Generation Date: 26-Jan-2025
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
from typing import Any
from exonware.xwsystem import get_logger
from exonware.xwsystem.security.monitor import SecurityMonitor as XWSystemSecurityMonitor
from exonware.xwsystem.monitoring.metrics import GenericMetrics
from exonware.xwsystem.security.defs import SecurityLevel
logger = get_logger(__name__)


class SecurityEventType(Enum):
    """Types of security events."""
    PATH_TRAVERSAL = "path_traversal"
    INJECTION_ATTEMPT = "injection_attempt"
    RESOURCE_LIMIT = "resource_limit"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    POLICY_VIOLATION = "policy_violation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_INPUT = "invalid_input"
    MEMORY_SAFETY = "memory_safety"
@dataclass

class SecurityEvent:
    """A security event to be logged."""
    event_type: SecurityEventType
    message: str
    timestamp: float = field(default_factory=time.time)
    context: dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"  # low, medium, high, critical
    source: str | None = None
    user_id: str | None = None
    ip_address: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_type': self.event_type.value,
            'message': self.message,
            'timestamp': self.timestamp,
            'context': self.context,
            'severity': self.severity,
            'source': self.source,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
        }


class SecurityLogger:
    """
    Security event logger for xwnode.
    REUSES xwsystem security and monitoring:
    - xwsystem.security.SecurityMonitor for intrusion detection
    - xwsystem.monitoring.GenericMetrics for event metrics
    - xwsystem logging for file-based logging
    Provides xwnode-specific security event logging with integration.
    """

    def __init__(
        self,
        max_events: int = 1000,
        enable_file_logging: bool = True,
        enable_monitoring: bool = True,
        alert_threshold: int = 10  # Alert after N events in time window
    ):
        """
        Initialize security logger using xwsystem infrastructure.
        Args:
            max_events: Maximum number of events to keep in memory
            enable_file_logging: Enable file-based logging
            enable_monitoring: Enable xwsystem monitoring integration
            alert_threshold: Number of events to trigger alert
        """
        self._max_events = max_events
        self._enable_file_logging = enable_file_logging
        self._enable_monitoring = enable_monitoring
        self._alert_threshold = alert_threshold
        # REUSE xwsystem SecurityMonitor for intrusion detection
        self._xwsystem_security_monitor = XWSystemSecurityMonitor(security_level=SecurityLevel.HIGH)
        # REUSE xwsystem GenericMetrics for event metrics
        self._xwsystem_metrics = GenericMetrics(component_name="xwnode.security")
        # Event storage (circular buffer) - xwnode-specific events
        self._events: deque = deque(maxlen=max_events)
        # Event counters by type
        self._event_counts: dict[SecurityEventType, int] = {}
        logger.info("SecurityLogger initialized (using xwsystem SecurityMonitor and Metrics)")

    def log_event(
        self,
        event_type: SecurityEventType,
        message: str,
        severity: str = "medium",
        context: dict[str, Any] | None = None,
        source: str | None = None,
        user_id: str | None = None,
        ip_address: str | None = None
    ) -> None:
        """
        Log a security event.
        Args:
            event_type: Type of security event
            message: Event message
            severity: Event severity (low, medium, high, critical)
            context: Additional context
            source: Source of the event (e.g., strategy name)
            user_id: User ID (if applicable)
            ip_address: IP address (if applicable)
        """
        event = SecurityEvent(
            event_type=event_type,
            message=message,
            severity=severity,
            context=context or {},
            source=source,
            user_id=user_id,
            ip_address=ip_address
        )
        # Store event (xwnode-specific)
        self._events.append(event)
        # Update counters
        self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1
        # REUSE xwsystem SecurityMonitor for intrusion detection
        event_data = {
            "type": event_type.value,
            "message": event.message,
            "timestamp": event.timestamp,
            "severity": event.severity,
            "source": event.source or "xwnode",
            "user": event.user_id,
            "resource": event.context.get("path") or event.context.get("operation", ""),
            **event.context
        }
        # Check for intrusion patterns using xwsystem
        if self._xwsystem_security_monitor.detect_intrusion(event_data):
            # Intrusion detected - xwsystem will handle alerting
            pass
        # REUSE xwsystem metrics for event recording
        if self._enable_monitoring:
            self._xwsystem_metrics.increment_counter(f"security_event.{event_type.value}")
            if event.severity in ('high', 'critical'):
                self._xwsystem_metrics.increment_counter("security_event.critical")
        # Log to file (xwsystem logger)
        if self._enable_file_logging:
            self._log_to_file(event)
        # Check for alerts
        self._check_alerts(event)

    def log_path_traversal(
        self,
        path: str,
        source: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        """Log path traversal attempt."""
        self.log_event(
            event_type=SecurityEventType.PATH_TRAVERSAL,
            message=f"Path traversal attempt detected: {path}",
            severity="high",
            context={**(context or {}), 'path': path},
            source=source
        )

    def log_injection_attempt(
        self,
        input_data: str,
        injection_type: str = "unknown",
        source: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        """Log injection attempt."""
        self.log_event(
            event_type=SecurityEventType.INJECTION_ATTEMPT,
            message=f"Injection attempt detected: {injection_type}",
            severity="critical",
            context={**(context or {}), 'input': input_data[:100], 'type': injection_type},
            source=source
        )

    def log_resource_limit(
        self,
        resource_type: str,
        limit: int,
        actual: int,
        source: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        """Log resource limit violation."""
        self.log_event(
            event_type=SecurityEventType.RESOURCE_LIMIT,
            message=f"Resource limit exceeded: {resource_type} (limit: {limit}, actual: {actual})",
            severity="high",
            context={**(context or {}), 'resource': resource_type, 'limit': limit, 'actual': actual},
            source=source
        )

    def log_suspicious_activity(
        self,
        activity: str,
        source: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        """Log suspicious activity."""
        self.log_event(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            message=f"Suspicious activity detected: {activity}",
            severity="medium",
            context={**(context or {}), 'activity': activity},
            source=source
        )

    def log_policy_violation(
        self,
        policy: str,
        violation: str,
        source: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        """Log security policy violation."""
        self.log_event(
            event_type=SecurityEventType.POLICY_VIOLATION,
            message=f"Security policy violation: {policy} - {violation}",
            severity="high",
            context={**(context or {}), 'policy': policy, 'violation': violation},
            source=source
        )

    def log_rate_limit_exceeded(
        self,
        operation: str,
        limit: int,
        source: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        """Log rate limit exceeded."""
        self.log_event(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            message=f"Rate limit exceeded for operation: {operation} (limit: {limit})",
            severity="medium",
            context={**(context or {}), 'operation': operation, 'limit': limit},
            source=source
        )

    def _log_to_file(self, event: SecurityEvent) -> None:
        """Log event to file via xwsystem logger."""
        log_level = {
            'low': 'debug',
            'medium': 'info',
            'high': 'warning',
            'critical': 'error'
        }.get(event.severity, 'info')
        log_message = (
            f"[SECURITY] {event.event_type.value.upper()}: {event.message} | "
            f"Source: {event.source or 'unknown'} | "
            f"Context: {event.context}"
        )
        getattr(logger, log_level)(log_message)

    def get_security_metrics(self) -> dict[str, Any]:
        """
        Get security metrics from xwsystem.
        Returns:
            Dictionary with security metrics
        """
        # REUSE xwsystem SecurityMonitor metrics
        xwsystem_metrics = self._xwsystem_security_monitor.get_security_metrics()
        # Add xwnode-specific metrics
        return {
            **xwsystem_metrics,
            'xwnode_events': {
                'total': len(self._events),
                'by_type': self.get_event_counts(),
                'recent_60s': len(self.get_recent_events(60))
            }
        }

    def _check_alerts(self, event: SecurityEvent) -> None:
        """Check if alert threshold is reached."""
        if event.severity in ('high', 'critical'):
            # Count recent high/critical events
            recent_events = [
                e for e in self._events
                if e.severity in ('high', 'critical')
                and (time.time() - e.timestamp) < 60  # Last minute
            ]
            if len(recent_events) >= self._alert_threshold:
                logger.warning(
                    f"SECURITY ALERT: {len(recent_events)} high/critical events "
                    f"in the last minute. Event type: {event.event_type.value}"
                )

    def get_events(
        self,
        event_type: SecurityEventType | None = None,
        severity: str | None = None,
        limit: int | None = None,
    ) -> list[SecurityEvent]:
        """
        Get logged events with optional filtering.
        Args:
            event_type: Filter by event type
            severity: Filter by severity
            limit: Maximum number of events to return
        Returns:
            List of security events
        """
        events = list(self._events)
        # Filter by type
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        # Filter by severity
        if severity:
            events = [e for e in events if e.severity == severity]
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        # Apply limit
        if limit:
            events = events[:limit]
        return events

    def get_event_counts(self) -> dict[str, int]:
        """Get event counts by type."""
        return {k.value: v for k, v in self._event_counts.items()}

    def get_recent_events(self, seconds: int = 60) -> list[SecurityEvent]:
        """Get events from the last N seconds."""
        cutoff = time.time() - seconds
        return [e for e in self._events if e.timestamp >= cutoff]

    def clear_events(self) -> None:
        """Clear all logged events."""
        self._events.clear()
        self._event_counts.clear()
        logger.info("Security events cleared")
# Global security logger instance
_security_logger: SecurityLogger | None = None


def get_security_logger() -> SecurityLogger:
    """Get global security logger instance."""
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityLogger()
    return _security_logger


def set_security_logger(logger_instance: SecurityLogger) -> None:
    """Set global security logger instance."""
    global _security_logger
    _security_logger = logger_instance
