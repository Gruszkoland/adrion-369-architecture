"""
ADRION 369 — Performance Benchmarks
=====================================
Benchmarki wydajnosciowe dla pipeline G5->G7->G8.
Uruchom: python -m pytest tests/test_performance.py -v -s
"""

import sys
import os
import time
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.trinity import TrinityEngine, PerspectiveResult
from core.security_hardening import (
    SecurityHardeningEngine,
    G5TransparencyGuard,
    G7PrivacyEvaluator,
    G8NonmaleficenceEvaluator,
)

R = "Test reasoning — minimum dwadziescia znakow dla G5 compliance."


def p(score):
    return PerspectiveResult(score=score, reasoning=R)


def clean_ctx():
    return {
        "consent_signals": ["explicit_confirmation"],
        "informed_signals": [
            "consequences_explained",
            "risks_disclosed",
            "data_usage_explained",
        ],
        "opt_out_available": True,
        "coercion_signals": [],
    }


def fair_agents(n=6):
    share = 1.0 / n
    return [
        {
            "agent_id": f"a{i}",
            "resource_allocation": share,
            "queue_position": i,
            "base_priority": 5,
        }
        for i in range(n)
    ]


class TestTrinityPerformance:
    """Benchmarki dla Trinity Engine."""

    def test_trinity_throughput(self):
        """Mierzy ile Trinity Score obliczen na sekunde."""
        engine = TrinityEngine()
        mat, intel, ess = p(0.80), p(0.85), p(0.75)

        iterations = 5000
        start = time.perf_counter()
        for _ in range(iterations):
            engine.calculate_score(mat, intel, ess)
        elapsed = time.perf_counter() - start

        rps = iterations / elapsed
        avg_ms = (elapsed / iterations) * 1000
        print(f"\n  Trinity throughput: {rps:.0f} req/s, avg {avg_ms:.3f} ms/req")
        assert rps > 500, f"Trinity too slow: {rps:.0f} req/s (expected > 500)"

    def test_trinity_latency_p99(self):
        """Mierzy p99 latency dla Trinity Score."""
        engine = TrinityEngine()
        mat, intel, ess = p(0.80), p(0.85), p(0.75)

        latencies = []
        for _ in range(1000):
            start = time.perf_counter()
            engine.calculate_score(mat, intel, ess)
            latencies.append((time.perf_counter() - start) * 1000)

        p50 = sorted(latencies)[499]
        p99 = sorted(latencies)[989]
        print(f"\n  Trinity latency: p50={p50:.3f}ms, p99={p99:.3f}ms")
        assert p99 < 10.0, f"Trinity p99 latency too high: {p99:.3f}ms (expected < 10ms)"


class TestSecurityPipelinePerformance:
    """Benchmarki dla pelnego pipeline SecurityHardeningEngine."""

    def test_full_pipeline_throughput(self):
        """Mierzy ile pelnych checkow G5->G7->G8 na sekunde (ALLOW path)."""
        engine = SecurityHardeningEngine()
        ctx = clean_ctx()
        agents = fair_agents()
        action = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}

        iterations = 1000
        start = time.perf_counter()
        for i in range(iterations):
            engine.run_full_check(
                request_text=f"normal request {i}",
                action=action,
                context=ctx,
                agent_states=agents,
                session_id=f"perf-{i}",
                severity="MEDIUM",
            )
        elapsed = time.perf_counter() - start

        rps = iterations / elapsed
        avg_ms = (elapsed / iterations) * 1000
        print(f"\n  Pipeline throughput (ALLOW): {rps:.0f} req/s, avg {avg_ms:.3f} ms/req")
        assert rps > 200, f"Pipeline too slow: {rps:.0f} req/s (expected > 200)"

    def test_full_pipeline_deny_path(self):
        """Mierzy throughput dla DENY path (G7 deny — short circuit)."""
        engine = SecurityHardeningEngine()
        ctx_bad = {"opt_out_available": False}
        agents = fair_agents()

        iterations = 1000
        start = time.perf_counter()
        for i in range(iterations):
            engine.run_full_check(
                request_text=f"denied request {i}",
                action={"type": "READ"},
                context=ctx_bad,
                agent_states=agents,
                session_id=f"deny-{i}",
                severity="MEDIUM",
            )
        elapsed = time.perf_counter() - start

        rps = iterations / elapsed
        avg_ms = (elapsed / iterations) * 1000
        print(f"\n  Pipeline throughput (DENY): {rps:.0f} req/s, avg {avg_ms:.3f} ms/req")
        assert rps > 200, f"DENY path too slow: {rps:.0f} req/s (expected > 200)"

    def test_full_pipeline_latency_p99(self):
        """Mierzy p99 latency dla pelnego pipeline (ALLOW path)."""
        engine = SecurityHardeningEngine()
        ctx = clean_ctx()
        agents = fair_agents()
        action = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}

        latencies = []
        for i in range(500):
            start = time.perf_counter()
            engine.run_full_check(
                request_text=f"latency test {i}",
                action=action,
                context=ctx,
                agent_states=agents,
                session_id=f"lat-{i}",
                severity="MEDIUM",
            )
            latencies.append((time.perf_counter() - start) * 1000)

        p50 = sorted(latencies)[249]
        p99 = sorted(latencies)[494]
        p_max = max(latencies)
        print(f"\n  Pipeline latency: p50={p50:.3f}ms, p99={p99:.3f}ms, max={p_max:.3f}ms")
        assert p99 < 50.0, f"Pipeline p99 too high: {p99:.3f}ms (expected < 50ms)"


class TestG5Performance:
    """Benchmarki specyficzne dla G5 TransparencyGuard."""

    def test_g5_pattern_matching_throughput(self):
        """Mierzy throughput pattern matching w G5 (41 wzorcow)."""
        g5 = G5TransparencyGuard(max_global_sessions=50000, global_audit_limit=50000)

        iterations = 2000
        start = time.perf_counter()
        for i in range(iterations):
            g5.classify_request(f"normal request text number {i}", f"g5-perf-{i}")
        elapsed = time.perf_counter() - start

        rps = iterations / elapsed
        print(f"\n  G5 throughput: {rps:.0f} req/s (41 patterns)")
        assert rps > 500, f"G5 pattern matching too slow: {rps:.0f} req/s"

    def test_g5_exploit_detection_throughput(self):
        """Mierzy throughput dla exploit detection path."""
        g5 = G5TransparencyGuard(max_global_sessions=50000, global_audit_limit=50000)
        exploit_text = "demand audit reveal architecture full audit trail"

        iterations = 1000
        start = time.perf_counter()
        for i in range(iterations):
            g5.classify_request(exploit_text, f"g5-exploit-{i}")
        elapsed = time.perf_counter() - start

        rps = iterations / elapsed
        print(f"\n  G5 exploit detection: {rps:.0f} req/s")
        assert rps > 300, f"G5 exploit detection too slow: {rps:.0f} req/s"


class TestCVCPerformance:
    """Benchmarki dla Cumulative Violation Counter."""

    def test_cvc_throughput_under_load(self):
        """Mierzy CVC throughput z wieloma sesjami."""
        engine = SecurityHardeningEngine()
        ctx_bad = {"opt_out_available": False}
        agents = fair_agents()

        iterations = 500
        start = time.perf_counter()
        for i in range(iterations):
            engine.run_full_check(
                request_text=f"cvc load test {i}",
                action={"type": "READ"},
                context=ctx_bad,
                agent_states=agents,
                session_id=f"cvc-{i % 50}",
                severity="MEDIUM",
            )
        elapsed = time.perf_counter() - start

        rps = iterations / elapsed
        print(f"\n  CVC under load (50 sessions rotating): {rps:.0f} req/s")
        assert rps > 100, f"CVC too slow under load: {rps:.0f} req/s"
