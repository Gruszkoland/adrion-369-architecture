"""
ADRION 369 — Audit Trail Tests v5.7
=====================================
Tests for blockchain-ready hash-chained audit log.
"""

import json
import time
import tempfile
import os
import pytest


# ── AuditRecord Tests ───────────────────────────────────────────────────────

class TestAuditRecord:

    def _make_record(self, **overrides):
        from core.audit_trail import AuditRecord, GENESIS_PREV_HASH
        defaults = dict(
            seq=0,
            prev_hash=GENESIS_PREV_HASH,
            version="5.7.0",
            input_hash="a" * 64,
            trinity_score=0.85,
            decision="PROCEED",
            guardian_violations=(),
            guardian_scores={"G1_Unity": 0.90, "G8_Nonmaleficence": 0.96},
            pad_state=(0.1, 0.2, 0.3),
            severity="MEDIUM",
        )
        defaults.update(overrides)
        return AuditRecord(**defaults)

    def test_record_creation(self):
        r = self._make_record()
        assert r.seq == 0
        assert r.decision == "PROCEED"
        assert r.trinity_score == 0.85
        assert r.severity == "MEDIUM"

    def test_record_hash_is_sha256(self):
        r = self._make_record()
        assert len(r.record_hash) == 64
        assert all(c in "0123456789abcdef" for c in r.record_hash)

    def test_record_self_verify(self):
        r = self._make_record()
        assert r.verify() is True

    def test_record_immutable(self):
        r = self._make_record()
        with pytest.raises(AttributeError, match="immutable"):
            r.decision = "DENY"

    def test_record_prev_hash_genesis(self):
        from core.audit_trail import GENESIS_PREV_HASH
        r = self._make_record()
        assert r.prev_hash == GENESIS_PREV_HASH

    def test_record_to_dict(self):
        r = self._make_record()
        d = r.to_dict()
        assert d["seq"] == 0
        assert d["decision"] == "PROCEED"
        assert "timestamp" in d
        assert d["timestamp"].endswith("Z")
        assert isinstance(d["guardian_scores"], dict)
        assert isinstance(d["guardian_violations"], list)

    def test_record_timestamp_iso(self):
        r = self._make_record()
        iso = r.timestamp_iso
        assert iso.endswith("Z")
        assert "T" in iso

    def test_record_repr(self):
        r = self._make_record()
        s = repr(r)
        assert "AuditRecord" in s
        assert "seq=0" in s
        assert "PROCEED" in s

    def test_different_inputs_different_hashes(self):
        r1 = self._make_record(input_hash="a" * 64)
        r2 = self._make_record(input_hash="b" * 64)
        assert r1.record_hash != r2.record_hash

    def test_explicit_record_hash_accepted(self):
        from core.audit_trail import AuditRecord, GENESIS_PREV_HASH
        r = AuditRecord(
            seq=0, prev_hash=GENESIS_PREV_HASH, version="5.7.0",
            input_hash="a" * 64, trinity_score=0.5, decision="DENY",
            guardian_violations=("G8",), guardian_scores={"G8": 0.3},
            pad_state=(0.0, 0.0, 0.0), severity="HIGH",
            record_hash="custom_hash_value"
        )
        assert r.record_hash == "custom_hash_value"
        assert r.verify() is False  # Custom hash won't match computed

    def test_guardian_violations_tuple(self):
        r = self._make_record(guardian_violations=["G1_Unity", "G3_Rhythm"])
        assert r.guardian_violations == ("G1_Unity", "G3_Rhythm")

    def test_guardian_scores_immutable(self):
        r = self._make_record()
        with pytest.raises(TypeError):
            r.guardian_scores["new_key"] = 1.0


# ── AuditChain Tests ────────────────────────────────────────────────────────

class TestAuditChain:

    def _make_chain(self):
        from core.audit_trail import AuditChain
        return AuditChain(version="5.7.0-test")

    def _append_record(self, chain, **overrides):
        defaults = dict(
            input_data="test input",
            trinity_score=0.85,
            decision="PROCEED",
            guardian_scores={"G1_Unity": 0.90, "G8_Nonmaleficence": 0.96},
        )
        defaults.update(overrides)
        return chain.append(**defaults)

    def test_empty_chain_valid(self):
        chain = self._make_chain()
        assert chain.verify() is True
        assert chain.length == 0

    def test_single_record_chain(self):
        chain = self._make_chain()
        r = self._append_record(chain)
        assert chain.length == 1
        assert r.seq == 0
        assert chain.verify() is True

    def test_multi_record_chain_linkage(self):
        chain = self._make_chain()
        r0 = self._append_record(chain, input_data="first")
        r1 = self._append_record(chain, input_data="second")
        r2 = self._append_record(chain, input_data="third")
        assert r1.prev_hash == r0.record_hash
        assert r2.prev_hash == r1.record_hash
        assert chain.length == 3
        assert chain.verify() is True

    def test_genesis_prev_hash(self):
        from core.audit_trail import GENESIS_PREV_HASH
        chain = self._make_chain()
        r = self._append_record(chain)
        assert r.prev_hash == GENESIS_PREV_HASH

    def test_last_hash_updates(self):
        from core.audit_trail import GENESIS_PREV_HASH
        chain = self._make_chain()
        assert chain.last_hash == GENESIS_PREV_HASH
        r = self._append_record(chain)
        assert chain.last_hash == r.record_hash

    def test_get_record_by_seq(self):
        chain = self._make_chain()
        self._append_record(chain, input_data="zero")
        self._append_record(chain, input_data="one")
        r = chain.get_record(1)
        assert r is not None
        assert r.seq == 1

    def test_get_record_out_of_range(self):
        chain = self._make_chain()
        assert chain.get_record(0) is None
        assert chain.get_record(-1) is None

    def test_get_records_by_decision(self):
        chain = self._make_chain()
        self._append_record(chain, decision="PROCEED")
        self._append_record(chain, decision="DENY")
        self._append_record(chain, decision="PROCEED")
        proceeds = chain.get_records_by_decision("PROCEED")
        assert len(proceeds) == 2
        denies = chain.get_records_by_decision("DENY")
        assert len(denies) == 1

    def test_get_violation_history(self):
        chain = self._make_chain()
        self._append_record(chain, guardian_scores={"G1": 0.9})
        chain.append(
            input_data="violation",
            trinity_score=0.4,
            decision="DENY",
            guardian_scores={"G8": 0.3},
            guardian_violations=("G8_Nonmaleficence",),
            severity="CRITICAL",
        )
        violations = chain.get_violation_history()
        assert len(violations) == 1
        assert "G8_Nonmaleficence" in violations[0].guardian_violations

    def test_export_json(self):
        chain = self._make_chain()
        self._append_record(chain, input_data="export-test")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.export_json(path)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["version"] == "5.7.0-test"
            assert data["chain_length"] == 1
            assert data["chain_valid"] is True
            assert len(data["records"]) == 1
            assert data["records"][0]["decision"] == "PROCEED"
        finally:
            os.unlink(path)

    def test_export_records(self):
        chain = self._make_chain()
        self._append_record(chain)
        records = chain.export_records()
        assert len(records) == 1
        assert isinstance(records[0], dict)

    def test_summary(self):
        chain = self._make_chain()
        self._append_record(chain, decision="PROCEED")
        self._append_record(chain, decision="DENY")
        s = chain.summary()
        assert s["chain_length"] == 2
        assert s["chain_valid"] is True
        assert s["decisions"]["PROCEED"] == 1
        assert s["decisions"]["DENY"] == 1
        assert "..." in s["last_hash"]

    def test_input_data_hashed_not_stored(self):
        """Verify raw input is SHA-256 hashed — not stored in plaintext."""
        chain = self._make_chain()
        r = self._append_record(chain, input_data="secret sensitive data")
        d = r.to_dict()
        assert "secret sensitive data" not in json.dumps(d)
        assert len(r.input_hash) == 64

    def test_severity_levels(self):
        chain = self._make_chain()
        for sev in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            chain.append(
                input_data=f"test-{sev}",
                trinity_score=0.5,
                decision="HOLD_SENTINEL_REVIEW",
                guardian_scores={"G1": 0.88},
                severity=sev,
            )
        assert chain.length == 4
        assert chain.get_record(3).severity == "CRITICAL"


# ── Tamper Detection Tests ──────────────────────────────────────────────────

class TestTamperDetection:

    def test_tampered_record_hash_detected(self):
        """Manually crafted record with wrong hash fails verification."""
        from core.audit_trail import AuditRecord, GENESIS_PREV_HASH
        r = AuditRecord(
            seq=0, prev_hash=GENESIS_PREV_HASH, version="5.7.0",
            input_hash="a" * 64, trinity_score=0.85, decision="PROCEED",
            guardian_violations=(), guardian_scores={"G1": 0.90},
            pad_state=(0.0, 0.0, 0.0), severity="MEDIUM",
            record_hash="0000000000000000000000000000000000000000000000000000000000000000",
        )
        assert r.verify() is False

    def test_chain_detects_broken_linkage(self):
        """Insert a record with wrong prev_hash — chain verification fails."""
        from core.audit_trail import AuditChain, AuditRecord
        chain = AuditChain()
        chain.append(
            input_data="first", trinity_score=0.9,
            decision="PROCEED", guardian_scores={"G1": 0.95},
        )
        # Manually inject a record with wrong prev_hash
        bad_record = AuditRecord(
            seq=1, prev_hash="f" * 64, version="5.7.0",
            input_hash="b" * 64, trinity_score=0.5, decision="DENY",
            guardian_violations=(), guardian_scores={"G1": 0.5},
            pad_state=(0.0, 0.0, 0.0), severity="HIGH",
        )
        chain._chain.append(bad_record)
        assert chain.verify() is False

    def test_chain_detects_modified_genesis(self):
        """If first record's prev_hash isn't genesis, verification fails."""
        from core.audit_trail import AuditChain, AuditRecord
        chain = AuditChain()
        bad_genesis = AuditRecord(
            seq=0, prev_hash="1" * 64, version="5.7.0",
            input_hash="a" * 64, trinity_score=0.9, decision="PROCEED",
            guardian_violations=(), guardian_scores={"G1": 0.95},
            pad_state=(0.0, 0.0, 0.0), severity="LOW",
        )
        chain._chain.append(bad_genesis)
        assert chain.verify() is False


# ── Thread Safety Tests ─────────────────────────────────────────────────────

class TestAuditChainThreadSafety:

    def test_concurrent_appends(self):
        """Multiple threads appending simultaneously should produce valid chain."""
        import threading
        from core.audit_trail import AuditChain

        chain = AuditChain()
        errors = []

        def worker(thread_id):
            try:
                for i in range(50):
                    chain.append(
                        input_data=f"thread-{thread_id}-{i}",
                        trinity_score=0.85,
                        decision="PROCEED",
                        guardian_scores={"G1": 0.90},
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert chain.length == 400  # 8 threads x 50
        assert chain.verify() is True
