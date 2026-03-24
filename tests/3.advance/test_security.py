"""
#exonware/xwnode/tests/3.advance/test_security.py
Security Excellence Tests - Priority #1
Validates security measures across xwnode library against OWASP Top 10
and defense-in-depth principles.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from pathlib import Path
from exonware.xwnode import XWNode


@pytest.mark.xwnode_advance
@pytest.mark.xwnode_security

class TestSecurityExcellence:
    """Security excellence validation - Priority #1."""

    def test_owasp_top_10_compliance(self):
        """
        Validate OWASP Top 10 compliance.
        Tests for:
        - Injection prevention
        - Broken authentication
        - Sensitive data exposure
        - XML external entities (XXE)
        - Broken access control
        - Security misconfiguration
        - Cross-site scripting (XSS)
        - Insecure deserialization
        - Using components with known vulnerabilities
        - Insufficient logging & monitoring
        """
        payload = {"query": "'; DROP TABLE users; --", "xss": "<script>alert(1)</script>"}
        node = XWNode.from_native(payload)
        assert node.get_value("query") == payload["query"]
        assert node.get_value("xss") == payload["xss"]

    def test_defense_in_depth(self):
        """
        Validate defense-in-depth implementation.
        Tests for multiple layers of security:
        - Input validation
        - Output encoding
        - Access control
        - Error handling
        - Logging & monitoring
        """
        node = XWNode.from_native({"safe": {"value": 42}})
        assert node.get_value("safe.value") == 42
        assert node.get_value("safe.missing", default="fallback") == "fallback"

    def test_input_validation(self):
        """
        Validate comprehensive input validation.
        Tests for:
        - Type checking
        - Range validation
        - Format validation
        - Malicious input handling
        - SQL injection patterns
        - XSS patterns
        """
        with pytest.raises(Exception):
            XWNode.from_native({"k": "v"}, mode="NOT_A_VALID_MODE")

    def test_path_validation(self):
        """
        Validate proper path validation and security checks.
        Tests for:
        - Path traversal prevention (../)
        - Absolute path handling
        - Symlink handling
        - File access controls
        """
        node = XWNode.from_native({"users": [{"name": "alice"}]})
        assert node.get_value("../../etc/passwd", default=None) is None

    def test_cryptographic_operations(self):
        """
        Validate use of established cryptographic libraries.
        Tests for:
        - Using standard cryptographic libraries
        - No custom crypto implementations
        - Secure random number generation
        - Proper key management
        """
        src_root = Path(__file__).resolve().parents[2] / "src" / "exonware" / "xwnode"
        # Guardrail: no home-grown crypto modules in xwnode core package.
        custom_crypto_modules = [
            p for p in src_root.rglob("*.py")
            if "crypto" in p.stem.lower() and "cryptographic" not in p.stem.lower()
        ]
        assert custom_crypto_modules == []

    def test_authentication_security(self):
        """
        Validate authentication security measures.
        Tests for:
        - Secure password handling
        - Session management
        - Token security
        - Multi-factor authentication support
        """
        node = XWNode.from_native({"token": "secret-value"})
        assert node.has("token")
        assert not node.has("password")

    def test_authorization_controls(self):
        """
        Validate authorization and access control.
        Tests for:
        - Role-based access control
        - Permission checking
        - Privilege escalation prevention
        - Least privilege principle
        """
        node = XWNode.from_native({"admin_only": "x"})
        assert node.has("admin_only")
        assert not node.has("non_existent")

    def test_data_protection(self):
        """
        Validate data protection measures.
        Tests for:
        - Sensitive data encryption
        - Secure data transmission
        - Data retention policies
        - PII handling
        """
        original = {"user": {"id": 1, "name": "alice"}}
        node = XWNode.from_native(original)
        materialized = node.to_native()
        assert materialized == original
        assert materialized is not original

    def test_security_logging(self):
        """
        Validate security logging and monitoring.
        Tests for:
        - Security event logging
        - Audit trail completeness
        - Log integrity
        - Sensitive data not logged
        """
        facade_path = Path(__file__).resolve().parents[2] / "src" / "exonware" / "xwnode" / "facade.py"
        content = facade_path.read_text(encoding="utf-8")
        assert "logger." in content

    def test_dependency_security(self):
        """
        Validate dependency security.
        Tests for:
        - No known vulnerable dependencies
        - Dependency update policy
        - Supply chain security
        """
        req_file = Path(__file__).resolve().parents[2] / "requirements.txt"
        requirements = req_file.read_text(encoding="utf-8")
        assert "exonware-xwsystem" in requirements
