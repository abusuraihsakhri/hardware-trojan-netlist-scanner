"""Security regression tests for the signed in-memory audit chain."""
import pytest

from agents.base import AuditTrail
from agents.models import SystemTaskPayload


def test_hmac_tampering_is_detected():
    trail = AuditTrail(secret_key="test-secret")
    trail.log("tester", "operator", "FIRST", {"count": 1})
    trail.log("tester", "operator", "SECOND", {"count": 2})
    assert trail.verify_integrity()

    trail.logs[0]["event_type"] = "MODIFIED"
    assert not trail.verify_integrity()


def test_chained_hmac_tampering_is_detected():
    trail = AuditTrail(secret_key="test-secret")
    trail.log("tester", "operator", "FIRST", {"count": 1})
    trail.log("tester", "operator", "SECOND", {"count": 2})
    trail.logs[1]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_audit_snapshot_is_not_mutable():
    trail = AuditTrail(secret_key="test-secret")
    trail.log("tester", "operator", "FIRST", {"count": 1})
    snapshot = trail.get_trail()
    snapshot[0]["event_type"] = "MODIFIED"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["event_type"] == "FIRST"


@pytest.mark.parametrize("value", ["nonsense", None, "", True, "nan", "inf"])
def test_metric_validation_yields_value_error(value):
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T", target_identifier="N", primary_metric=value)


def test_numeric_strings_are_accepted():
    payload = SystemTaskPayload(task_id="T", target_identifier="N", primary_metric="12.5")
    assert payload.primary_metric == 12.5
