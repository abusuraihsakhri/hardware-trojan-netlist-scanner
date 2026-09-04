"""
Security and input validation tests for hardware-trojan-netlist-scanner.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import math
import os
import pytest
from agents.base import AuditTrail, PHIGuard, SecurityException
from agents.models import SystemTaskPayload


class TestPHIGuard:
    """Tests for the PHI outbound guard."""

    def test_mrn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_ssn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phone_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_email_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact user@example.com")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("TARGET-01 primary metric 28.5")

    def test_redaction(self):
        redacted = PHIGuard.redact_phi("Contact user@example.com for MRN-12345")
        assert "[REDACTED_IDENTIFIER]" in redacted
        assert "user@example.com" not in redacted
        assert "MRN-12345" not in redacted


class TestAuditTrailSecurity:
    """Tests for HMAC audit trail security properties."""

    def test_no_hardcoded_default_key(self):
        """AuditTrail should generate a random key when none provided."""
        # Ensure env var is not set
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            trail = AuditTrail()
            # Key should be 64 hex chars (32 bytes)
            assert len(trail.secret_key) == 64
        finally:
            if original is not None:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_env_var_key_precedence(self):
        """AUDIT_SECRET_KEY env var should be used when set."""
        os.environ["AUDIT_SECRET_KEY"] = "test-key-from-env"
        try:
            trail = AuditTrail()
            assert trail.secret_key == b"test-key-from-env"
        finally:
            os.environ.pop("AUDIT_SECRET_KEY", None)

    def test_explicit_key_precedence(self):
        """Explicit key parameter should take highest precedence."""
        os.environ["AUDIT_SECRET_KEY"] = "env-key"
        try:
            trail = AuditTrail(secret_key="explicit-key")
            assert trail.secret_key == b"explicit-key"
        finally:
            os.environ.pop("AUDIT_SECRET_KEY", None)

    def test_integrity_verification(self):
        """Audit trail integrity should be verifiable."""
        trail = AuditTrail(secret_key="test-key")
        trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value"})
        trail.log("test-actor", "test-tier", "TEST_EVENT_2", {"data": "value2"})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 2


class TestInputValidation:
    """Tests for numeric input validation."""

    def test_nan_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("nan"),
            )

    def test_positive_infinity_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("inf"),
            )

    def test_negative_infinity_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("-inf"),
            )

    def test_nan_secondary_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=10.0,
                secondary_metric=float("nan"),
            )

    def test_valid_finite_values_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=28.5,
            secondary_metric=14.2,
        )
        assert payload.primary_metric == 28.5
        assert payload.secondary_metric == 14.2

    def test_zero_values_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=0.0,
            secondary_metric=0.0,
        )
        assert payload.primary_metric == 0.0

    def test_negative_values_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=-5.0,
            secondary_metric=-2.0,
        )
        assert payload.primary_metric == -5.0
