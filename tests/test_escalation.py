"""
ADRION 369 — Escalation Module Tests v5.7
===========================================
Tests for Human-in-the-Loop escalation protocol.
"""

import json
import tempfile
import os
import pytest


class TestEscalationEvent:

    def test_event_creation(self):
        from core.escalation import EscalationEvent
        e = EscalationEvent(
            decision="HOLD_HUMAN_REVIEW",
            trinity_score=0.65,
            guardian_scores={"G8_Nonmaleficence": 0.94},
            reason="G8 near threshold",
        )
        assert e.decision == "HOLD_HUMAN_REVIEW"
        assert e.trinity_score == 0.65
        assert e.reason == "G8 near threshold"
        assert len(e.event_hash) == 64

    def test_event_immutable(self):
        from core.escalation import EscalationEvent
        e = EscalationEvent(
            decision="DENY", trinity_score=0.2,
            guardian_scores={"G1": 0.5},
        )
        with pytest.raises(AttributeError, match="immutable"):
            e.decision = "PROCEED"

    def test_event_to_dict(self):
        from core.escalation import EscalationEvent
        e = EscalationEvent(
            decision="HARD_VETO", trinity_score=0.1,
            guardian_scores={"G8": 0.3},
            violations=("G8_Nonmaleficence",),
            severity="CRITICAL",
        )
        d = e.to_dict()
        assert d["decision"] == "HARD_VETO"
        assert d["severity"] == "CRITICAL"
        assert d["timestamp"].endswith("Z")
        assert "G8_Nonmaleficence" in d["violations"]

    def test_event_repr(self):
        from core.escalation import EscalationEvent
        e = EscalationEvent(
            decision="DENY", trinity_score=0.3,
            guardian_scores={"G1": 0.5}, severity="HIGH",
        )
        r = repr(e)
        assert "EscalationEvent" in r
        assert "DENY" in r

    def test_different_events_different_hashes(self):
        from core.escalation import EscalationEvent
        import time
        e1 = EscalationEvent(decision="DENY", trinity_score=0.3, guardian_scores={"G1": 0.5})
        time.sleep(0.01)
        e2 = EscalationEvent(decision="DENY", trinity_score=0.3, guardian_scores={"G1": 0.5})
        assert e1.event_hash != e2.event_hash


class TestWebhookTarget:

    def test_webhook_creation(self):
        from core.escalation import WebhookTarget
        wh = WebhookTarget(url="https://hooks.example.com/test", name="test-hook")
        assert wh.name == "test-hook"
        assert wh.timeout == 5.0

    def test_webhook_invalid_url(self):
        from core.escalation import WebhookTarget
        with pytest.raises(ValueError, match="http"):
            WebhookTarget(url="ftp://invalid.com")

    def test_webhook_should_fire_matching_decision(self):
        from core.escalation import WebhookTarget
        wh = WebhookTarget(url="https://hooks.example.com/test")
        assert wh.should_fire("HOLD_HUMAN_REVIEW") is True
        assert wh.should_fire("DENY") is True

    def test_webhook_should_not_fire_proceed(self):
        from core.escalation import WebhookTarget
        wh = WebhookTarget(url="https://hooks.example.com/test")
        assert wh.should_fire("PROCEED") is False

    def test_webhook_custom_decisions_filter(self):
        from core.escalation import WebhookTarget
        wh = WebhookTarget(
            url="https://hooks.example.com/test",
            decisions=frozenset({"HARD_VETO"}),
        )
        assert wh.should_fire("HARD_VETO") is True
        assert wh.should_fire("DENY") is False

    def test_webhook_format_payload(self):
        from core.escalation import WebhookTarget, EscalationEvent
        wh = WebhookTarget(url="https://hooks.example.com/test")
        event = EscalationEvent(
            decision="DENY", trinity_score=0.3,
            guardian_scores={"G8": 0.3}, severity="HIGH",
        )
        payload = wh.format_payload(event)
        data = json.loads(payload)
        assert "text" in data
        assert "DENY" in data["text"]
        assert "[HIGH]" in data["text"]


class TestEscalationManager:

    def test_manager_creation(self):
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        assert mgr.webhook_count == 0
        assert len(mgr.history) == 0

    def test_escalate_without_webhooks(self):
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        event = mgr.escalate(
            decision="DENY", trinity_score=0.2,
            guardian_scores={"G8": 0.3},
            reason="test escalation",
        )
        assert event.decision == "DENY"
        assert len(mgr.history) == 1

    def test_escalate_with_callback(self):
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        received = []
        mgr.add_callback(lambda e: received.append(e))
        mgr.escalate(
            decision="HOLD_HUMAN_REVIEW",
            trinity_score=0.65,
            guardian_scores={"G1": 0.88},
        )
        assert len(received) == 1
        assert received[0].decision == "HOLD_HUMAN_REVIEW"

    def test_escalate_logs_to_file(self):
        from core.escalation import EscalationManager
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name
        try:
            mgr = EscalationManager(log_path=path)
            mgr.escalate(
                decision="DENY", trinity_score=0.2,
                guardian_scores={"G8": 0.3}, severity="HIGH",
            )
            with open(path, "r") as f:
                lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["decision"] == "DENY"
            assert data["severity"] == "HIGH"
        finally:
            os.unlink(path)

    def test_summary(self):
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        mgr.escalate(decision="DENY", trinity_score=0.2, guardian_scores={"G8": 0.3}, severity="HIGH")
        mgr.escalate(decision="DENY", trinity_score=0.1, guardian_scores={"G8": 0.2}, severity="CRITICAL")
        mgr.escalate(decision="HOLD_HUMAN_REVIEW", trinity_score=0.65, guardian_scores={"G1": 0.88}, severity="MEDIUM")
        s = mgr.summary()
        assert s["total_escalations"] == 3
        assert s["by_decision"]["DENY"] == 2
        assert s["by_decision"]["HOLD_HUMAN_REVIEW"] == 1
        assert s["by_severity"]["HIGH"] == 1

    def test_add_webhook(self):
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        mgr.add_webhook("https://hooks.example.com/test", name="test")
        assert mgr.webhook_count == 1

    def test_webhook_status(self):
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        mgr.add_webhook("https://hooks.example.com/slack", name="slack-ops")
        status = mgr.get_webhook_status()
        assert len(status) == 1
        assert status[0]["name"] == "slack-ops"
        assert status[0]["failures"] == 0

    def test_multiple_escalations(self):
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        for i in range(100):
            mgr.escalate(
                decision="DENY", trinity_score=0.1 + i * 0.001,
                guardian_scores={"G8": 0.3},
            )
        assert len(mgr.history) == 100

    def test_concurrent_escalations(self):
        import threading
        from core.escalation import EscalationManager
        mgr = EscalationManager()
        errors = []

        def worker(tid):
            try:
                for i in range(50):
                    mgr.escalate(
                        decision="DENY", trinity_score=0.2,
                        guardian_scores={"G8": 0.3},
                        reason=f"thread-{tid}-{i}",
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
        assert len(mgr.history) == 400
