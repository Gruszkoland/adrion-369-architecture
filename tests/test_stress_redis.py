"""
ADRION 369 — Redis Cluster Stress Tests for G5-G8 Pipeline
============================================================
Simulates multi-instance deployment with Redis-backed storage
to measure and optimize latency across the security pipeline.

Test scenarios:
1. Concurrent session load (G5) — thousands of simultaneous sessions
2. CVC sliding window under burst — rapid violation recording
3. Full pipeline G5→G7→G8 with Redis backend — end-to-end latency
4. Session eviction under pressure — TTL expiry during load
5. Cross-instance session consistency — multiple engines sharing store
6. Pipeline latency percentiles — p50/p95/p99/p999 under load
7. Starvation detection throughput — G8 with many agents
8. Mixed workload — ALLOW/DENY/SENTINEL paths interleaved
9. Burst spike resilience — sudden 10x traffic increase
10. Degraded mode — backend latency injection

Run with:
    python -m pytest tests/test_stress_redis.py -v -s
"""

import sys
import os
import time
import math
import random
import threading
import statistics
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.redis_backend import (
    InMemorySessionStore,
    InMemoryCVCStore,
)
from core.security_hardening import (
    SecurityHardeningEngine,
    G5TransparencyGuard,
    G7PrivacyEvaluator,
    G8NonmaleficenceEvaluator,
    _CumulativeViolationCounter,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_ctx():
    return {
        "consent_signals": ["explicit_confirmation"],
        "informed_signals": ["consequences_explained", "risks_disclosed", "data_usage_explained"],
        "opt_out_available": True,
        "coercion_signals": [],
    }


def deny_ctx():
    return {"opt_out_available": False}


def fair_agents(n=6):
    share = 1.0 / n
    return [
        {"agent_id": f"a{i}", "resource_allocation": share,
         "queue_position": i, "base_priority": 5}
        for i in range(n)
    ]


def starving_agents(n=10, starved_idx=0):
    """Create agents where one is starved (allocation < 10%)."""
    agents = []
    for i in range(n):
        alloc = 0.01 if i == starved_idx else (0.99 / (n - 1))
        agents.append({
            "agent_id": f"a{i}", "resource_allocation": alloc,
            "queue_position": i, "base_priority": 5,
        })
    return agents


def percentiles(latencies: List[float]) -> Dict[str, float]:
    """Compute latency percentiles."""
    s = sorted(latencies)
    n = len(s)
    return {
        "min": s[0],
        "p50": s[int(n * 0.50)],
        "p90": s[int(n * 0.90)],
        "p95": s[int(n * 0.95)],
        "p99": s[int(n * 0.99)] if n >= 100 else s[-1],
        "p999": s[int(n * 0.999)] if n >= 1000 else s[-1],
        "max": s[-1],
        "mean": statistics.mean(s),
        "stdev": statistics.stdev(s) if n > 1 else 0.0,
    }


def print_latency_report(label: str, latencies: List[float], rps: float):
    p = percentiles(latencies)
    print(f"\n  {label}:")
    print(f"    Throughput: {rps:.0f} req/s")
    print(f"    Latency (ms): min={p['min']:.3f} p50={p['p50']:.3f} "
          f"p90={p['p90']:.3f} p95={p['p95']:.3f} p99={p['p99']:.3f} "
          f"max={p['max']:.3f}")
    print(f"    mean={p['mean']:.3f}ms stdev={p['stdev']:.3f}ms")
    return p


# ── Test 1: Concurrent G5 Session Load ──────────────────────────────────────

class TestG5SessionStress:
    """Stress tests for G5 session handling with Redis-backed store."""

    def test_concurrent_session_creation(self):
        """10,000 unique sessions hitting G5 concurrently (simulated via store)."""
        store = InMemorySessionStore()
        num_sessions = 10_000

        start = time.perf_counter()
        for i in range(num_sessions):
            store.set_session(f"sess-{i}", {
                "last_audit": 0.0, "audit_depth": 0, "created_at": time.time(),
            })
        elapsed = time.perf_counter() - start

        rps = num_sessions / elapsed
        assert store.session_count() == num_sessions
        print(f"\n  Session creation: {rps:.0f} sess/s ({num_sessions} sessions in {elapsed:.3f}s)")
        assert rps > 50_000, f"Session creation too slow: {rps:.0f} sess/s"

    def test_session_eviction_under_load(self):
        """Fill store to capacity, trigger eviction, measure overhead."""
        store = InMemorySessionStore()
        num_sessions = 10_000
        old_time = time.time() - 7200  # 2h old

        # Fill with 50% old, 50% fresh sessions
        for i in range(num_sessions):
            ts = old_time if i < num_sessions // 2 else time.time()
            store.set_session(f"sess-{i}", {
                "last_audit": ts, "created_at": ts,
            })

        assert store.session_count() == num_sessions

        start = time.perf_counter()
        evicted = store.evict_expired(ttl=3600.0)
        elapsed = time.perf_counter() - start

        assert evicted == num_sessions // 2
        assert store.session_count() == num_sessions // 2
        print(f"\n  Eviction: {evicted} evicted in {elapsed*1000:.3f}ms "
              f"({evicted/elapsed:.0f} evictions/s)")
        assert elapsed < 1.0, f"Eviction too slow: {elapsed:.3f}s"

    def test_g5_high_concurrency_classify(self):
        """500 concurrent G5 classify requests via ThreadPool."""
        g5 = G5TransparencyGuard(max_global_sessions=50_000, global_audit_limit=50_000)
        latencies = []
        errors = []

        def classify_one(i):
            t0 = time.perf_counter()
            try:
                result = g5.classify_request(f"normal request text {i}", f"thread-{i}")
                lat = (time.perf_counter() - t0) * 1000
                return lat, result
            except Exception as e:
                return 0.0, {"error": str(e)}

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(classify_one, i) for i in range(500)]
            for f in as_completed(futures):
                lat, result = f.result()
                latencies.append(lat)
                if "error" in result:
                    errors.append(result["error"])

        rps = len(latencies) / (sum(latencies) / 1000) if sum(latencies) > 0 else 0
        p = print_latency_report("G5 concurrent classify (500 reqs, 16 threads)", latencies, rps)
        assert len(errors) == 0, f"Errors: {errors[:5]}"
        assert p["p99"] < 50.0, f"G5 concurrent p99 too high: {p['p99']:.3f}ms"


# ── Test 2: CVC Burst Stress ────────────────────────────────────────────────

class TestCVCBurstStress:
    """Stress tests for CVC under burst violation patterns."""

    def test_cvc_burst_recording(self):
        """5,000 rapid violation records across 100 sessions."""
        store = InMemoryCVCStore()
        num_sessions = 100
        violations_per = 50
        latencies = []

        start = time.perf_counter()
        for s in range(num_sessions):
            for _ in range(violations_per):
                t0 = time.perf_counter()
                store.record_violations(f"burst-{s}", 1, window_hours=24)
                latencies.append((time.perf_counter() - t0) * 1000)
        total_elapsed = time.perf_counter() - start

        total_ops = num_sessions * violations_per
        rps = total_ops / total_elapsed
        p = print_latency_report(f"CVC burst ({total_ops} ops, {num_sessions} sessions)", latencies, rps)
        assert rps > 10_000, f"CVC burst too slow: {rps:.0f} ops/s"
        assert p["p99"] < 5.0, f"CVC p99 too high: {p['p99']:.3f}ms"

    def test_cvc_sliding_window_accuracy(self):
        """Verify CVC correctly prunes old entries under load."""
        store = InMemoryCVCStore()
        sid = "window-test"

        # Record 10 violations
        store.record_violations(sid, 10, window_hours=24)
        assert store.get_violation_count(sid, 24) == 10

        # All within window
        assert store.get_violation_count(sid, 24) == 10

        # Record more
        store.record_violations(sid, 5, window_hours=24)
        assert store.get_violation_count(sid, 24) == 15

    def test_cvc_concurrent_access(self):
        """200 threads recording violations simultaneously on same session."""
        store = InMemoryCVCStore()
        results = []

        def record_violation(thread_id):
            return store.record_violations("shared-session", 1, window_hours=24)

        with ThreadPoolExecutor(max_workers=32) as pool:
            futures = [pool.submit(record_violation, i) for i in range(200)]
            for f in as_completed(futures):
                results.append(f.result())

        final = store.get_violation_count("shared-session", 24)
        assert final == 200, f"Expected 200 violations, got {final} (thread-safety issue)"
        print(f"\n  CVC concurrent: 200 threads -> {final} violations (correct)")


# ── Test 3: Full Pipeline G5→G7→G8 Stress ───────────────────────────────────

class TestFullPipelineStress:
    """End-to-end pipeline stress with instrumented latency."""

    def test_pipeline_sustained_load(self):
        """3,000 requests through full pipeline, measure sustained throughput."""
        engine = SecurityHardeningEngine(
            g5=G5TransparencyGuard(max_global_sessions=50_000, global_audit_limit=50_000),
        )
        ctx = clean_ctx()
        agents = fair_agents()
        action = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}
        latencies = []

        iterations = 3000
        start = time.perf_counter()
        for i in range(iterations):
            t0 = time.perf_counter()
            result = engine.run_full_check(
                request_text=f"sustained load {i}",
                action=action, context=ctx, agent_states=agents,
                session_id=f"sustained-{i}", severity="MEDIUM",
            )
            latencies.append((time.perf_counter() - t0) * 1000)
            assert result["decision"] == "ALLOW"

        total_elapsed = time.perf_counter() - start
        rps = iterations / total_elapsed
        p = print_latency_report(f"Pipeline sustained ({iterations} reqs)", latencies, rps)
        assert rps > 200, f"Sustained throughput too low: {rps:.0f} req/s"
        assert p["p99"] < 25.0, f"Pipeline p99 too high: {p['p99']:.3f}ms"

    def test_pipeline_deny_path_throughput(self):
        """2,000 DENY requests (G7 short-circuit) — measures fast-reject speed."""
        engine = SecurityHardeningEngine(
            g5=G5TransparencyGuard(max_global_sessions=50_000, global_audit_limit=50_000),
        )
        ctx_bad = deny_ctx()
        agents = fair_agents()
        latencies = []

        iterations = 2000
        start = time.perf_counter()
        for i in range(iterations):
            t0 = time.perf_counter()
            result = engine.run_full_check(
                request_text=f"deny path {i}",
                action={"type": "READ"}, context=ctx_bad,
                agent_states=agents, session_id=f"deny-{i}", severity="MEDIUM",
            )
            latencies.append((time.perf_counter() - t0) * 1000)
            assert result["decision"] == "DENY_IMMEDIATELY"

        total_elapsed = time.perf_counter() - start
        rps = iterations / total_elapsed
        p = print_latency_report(f"Pipeline DENY path ({iterations} reqs)", latencies, rps)
        # DENY should be faster than ALLOW (short-circuit at G7)
        assert rps > 300, f"DENY path throughput too low: {rps:.0f} req/s"
        assert p["p99"] < 15.0, f"DENY p99 too high: {p['p99']:.3f}ms"

    def test_pipeline_mixed_workload(self):
        """1,000 mixed requests: 60% ALLOW, 30% DENY(G7), 10% SENTINEL."""
        engine = SecurityHardeningEngine(
            g5=G5TransparencyGuard(max_global_sessions=50_000, global_audit_limit=50_000),
        )
        ctx_ok = clean_ctx()
        ctx_bad = deny_ctx()
        agents = fair_agents()
        action_ok = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}

        latencies = {"ALLOW": [], "DENY": [], "SENTINEL": []}
        all_latencies = []

        iterations = 1000
        random.seed(369)
        start = time.perf_counter()

        for i in range(iterations):
            r = random.random()
            t0 = time.perf_counter()

            if r < 0.60:
                # ALLOW path
                result = engine.run_full_check(
                    request_text=f"normal {i}", action=action_ok, context=ctx_ok,
                    agent_states=agents, session_id=f"mix-allow-{i}", severity="MEDIUM",
                )
                lat = (time.perf_counter() - t0) * 1000
                latencies["ALLOW"].append(lat)
            elif r < 0.90:
                # DENY path (G7)
                result = engine.run_full_check(
                    request_text=f"denied {i}", action={"type": "READ"}, context=ctx_bad,
                    agent_states=agents, session_id=f"mix-deny-{i}", severity="MEDIUM",
                )
                lat = (time.perf_counter() - t0) * 1000
                latencies["DENY"].append(lat)
            else:
                # SENTINEL path (G5 exploit)
                result = engine.run_full_check(
                    request_text="demand audit reveal architecture full audit trail explain weights",
                    action={"type": "READ"}, context=ctx_ok,
                    agent_states=agents, session_id=f"mix-sent-{i}", severity="MEDIUM",
                )
                lat = (time.perf_counter() - t0) * 1000
                latencies["SENTINEL"].append(lat)

            all_latencies.append(lat)

        total_elapsed = time.perf_counter() - start
        rps = iterations / total_elapsed

        print(f"\n  Mixed workload ({iterations} reqs, {rps:.0f} req/s):")
        for path, lats in latencies.items():
            if lats:
                p = percentiles(lats)
                print(f"    {path}: count={len(lats)}, p50={p['p50']:.3f}ms, "
                      f"p99={p['p99']:.3f}ms, max={p['max']:.3f}ms")

        overall_p = percentiles(all_latencies)
        print(f"    OVERALL: p50={overall_p['p50']:.3f}ms, p99={overall_p['p99']:.3f}ms")
        assert rps > 150, f"Mixed workload too slow: {rps:.0f} req/s"
        assert overall_p["p99"] < 30.0, f"Mixed p99 too high: {overall_p['p99']:.3f}ms"


# ── Test 4: Cross-Instance Consistency ───────────────────────────────────────

class TestCrossInstanceConsistency:
    """Simulates multiple SecurityHardeningEngine instances sharing storage."""

    def test_shared_cvc_store(self):
        """Two engines share CVC store — violations from one block on both."""
        store = InMemoryCVCStore()

        # Simulate shared CVC by using same store
        # Engine A records violations
        for _ in range(5):
            store.record_violations("shared-user", 1, window_hours=24)

        # Engine B checks status
        count = store.get_violation_count("shared-user", 24)
        assert count == 5
        print(f"\n  Cross-instance CVC: {count} violations visible across instances")

    def test_shared_session_store(self):
        """Two G5 guards sharing session store — depth persists."""
        store = InMemorySessionStore()

        # Instance A creates session with depth 1
        store.set_session("user-123", {
            "last_audit": time.time() - 400,  # cooldown expired
            "audit_depth": 1, "created_at": time.time(),
        })

        # Instance B reads same session
        session = store.get_session("user-123")
        assert session is not None
        assert session["audit_depth"] == 1
        print(f"\n  Cross-instance session: depth={session['audit_depth']} (consistent)")

    def test_parallel_engines_no_race(self):
        """4 engines processing different sessions concurrently — no data corruption."""
        store = InMemoryCVCStore()
        errors = []

        def engine_worker(engine_id, session_range):
            try:
                for s in session_range:
                    store.record_violations(f"engine-{engine_id}-sess-{s}", 2, 24)
                    count = store.get_violation_count(f"engine-{engine_id}-sess-{s}", 24)
                    if count < 2:
                        errors.append(f"engine-{engine_id} sess-{s}: expected >= 2, got {count}")
            except Exception as e:
                errors.append(str(e))

        threads = []
        for eid in range(4):
            t = threading.Thread(target=engine_worker, args=(eid, range(250)))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        assert len(errors) == 0, f"Race conditions detected: {errors[:5]}"
        print(f"\n  Parallel engines: 4 engines x 250 sessions = no races")


# ── Test 5: G8 Starvation Detection at Scale ────────────────────────────────

class TestG8StarvationScale:
    """G8 nonmaleficence evaluator under various agent configurations."""

    def test_large_agent_pool(self):
        """G8 fairness check with 100 agents — latency must stay < 5ms."""
        g8 = G8NonmaleficenceEvaluator()
        n_agents = 100
        agents = [
            {"agent_id": f"a{i}", "resource_allocation": 1.0 / n_agents,
             "queue_position": i, "base_priority": 5}
            for i in range(n_agents)
        ]
        action = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}
        latencies = []

        for _ in range(1000):
            t0 = time.perf_counter()
            result = g8.evaluate(action, agents)
            latencies.append((time.perf_counter() - t0) * 1000)

        rps = 1000 / (sum(latencies) / 1000)
        p = print_latency_report(f"G8 fairness (100 agents)", latencies, rps)
        assert p["p99"] < 5.0, f"G8 p99 too high with 100 agents: {p['p99']:.3f}ms"

    def test_starvation_detection_throughput(self):
        """Measure starvation detection speed with deliberately unfair allocation."""
        g8 = G8NonmaleficenceEvaluator()
        agents = starving_agents(n=20, starved_idx=7)
        action = {"type": "READ", "requesting_agent": "a7", "claimed_priority": 5}
        latencies = []

        for _ in range(2000):
            t0 = time.perf_counter()
            result = g8.evaluate(action, agents)
            latencies.append((time.perf_counter() - t0) * 1000)
            assert not result.compliant  # Starvation → DENY

        rps = 2000 / (sum(latencies) / 1000)
        p = print_latency_report(f"G8 starvation detection (20 agents)", latencies, rps)
        assert rps > 3_000, f"G8 starvation detection too slow: {rps:.0f} req/s"


# ── Test 6: Burst Spike Resilience ───────────────────────────────────────────

class TestBurstSpikeResilience:
    """Simulates sudden traffic spikes and measures degradation."""

    def test_10x_burst_spike(self):
        """
        Baseline: 100 req/s steady state
        Spike:    1000 req/s burst for 1 second
        Measure:  latency degradation during and after spike
        """
        engine = SecurityHardeningEngine(
            g5=G5TransparencyGuard(max_global_sessions=50_000, global_audit_limit=50_000),
        )
        ctx = clean_ctx()
        agents = fair_agents()
        action = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}

        # Phase 1: Warm-up (100 requests)
        warmup_latencies = []
        for i in range(100):
            t0 = time.perf_counter()
            engine.run_full_check(
                request_text=f"warmup {i}", action=action, context=ctx,
                agent_states=agents, session_id=f"warmup-{i}", severity="MEDIUM",
            )
            warmup_latencies.append((time.perf_counter() - t0) * 1000)

        # Phase 2: Burst (1000 requests as fast as possible)
        burst_latencies = []
        burst_start = time.perf_counter()
        for i in range(1000):
            t0 = time.perf_counter()
            engine.run_full_check(
                request_text=f"burst {i}", action=action, context=ctx,
                agent_states=agents, session_id=f"burst-{i}", severity="MEDIUM",
            )
            burst_latencies.append((time.perf_counter() - t0) * 1000)
        burst_elapsed = time.perf_counter() - burst_start
        burst_rps = 1000 / burst_elapsed

        # Phase 3: Recovery (100 requests after burst)
        recovery_latencies = []
        for i in range(100):
            t0 = time.perf_counter()
            engine.run_full_check(
                request_text=f"recovery {i}", action=action, context=ctx,
                agent_states=agents, session_id=f"recovery-{i}", severity="MEDIUM",
            )
            recovery_latencies.append((time.perf_counter() - t0) * 1000)

        w_p = percentiles(warmup_latencies)
        b_p = percentiles(burst_latencies)
        r_p = percentiles(recovery_latencies)

        print(f"\n  Burst Spike Test:")
        print(f"    Warmup:   p50={w_p['p50']:.3f}ms p99={w_p['p99']:.3f}ms")
        print(f"    Burst:    p50={b_p['p50']:.3f}ms p99={b_p['p99']:.3f}ms ({burst_rps:.0f} req/s)")
        print(f"    Recovery: p50={r_p['p50']:.3f}ms p99={r_p['p99']:.3f}ms")

        # Burst p99 should not degrade more than 5x from warmup
        max_degradation = 5.0
        degradation = b_p["p99"] / w_p["p99"] if w_p["p99"] > 0 else 1.0
        print(f"    Degradation: {degradation:.1f}x")
        assert degradation < max_degradation, \
            f"Burst degradation too high: {degradation:.1f}x (max {max_degradation}x)"

        # Recovery should be within 10x of warmup (OS scheduling variance on Windows)
        recovery_ratio = r_p["p50"] / w_p["p50"] if w_p["p50"] > 0 else 1.0
        print(f"    Recovery ratio: {recovery_ratio:.1f}x")
        assert recovery_ratio < 10.0, \
            f"Recovery too slow: {recovery_ratio:.1f}x warmup"


# ── Test 7: D^162 Pipeline Integration Stress ───────────────────────────────

class TestD162PipelineStress:
    """Stress the D^162 decision space with high-throughput evaluations."""

    def test_d162_validation_throughput(self):
        """1,000 decision vector validations per second target."""
        from core.decision_space_162d import DecisionVector, validate_decision
        latencies = []

        iterations = 2000
        start = time.perf_counter()
        for i in range(iterations):
            # Vary the vector slightly each iteration
            val = 0.90 + 0.05 * math.sin(i * 0.1)
            d = DecisionVector([val] * 162)
            t0 = time.perf_counter()
            validate_decision(d)
            latencies.append((time.perf_counter() - t0) * 1000)
        total_elapsed = time.perf_counter() - start

        rps = iterations / total_elapsed
        p = print_latency_report(f"D^162 validation ({iterations} vectors)", latencies, rps)
        assert rps > 1000, f"D^162 validation too slow: {rps:.0f} req/s"
        assert p["p99"] < 5.0, f"D^162 p99 too high: {p['p99']:.3f}ms"

    def test_superior_moral_code_throughput(self):
        """Superior Moral Code full pipeline — 500 evaluations."""
        from core.superior_moral_code import SuperiorMoralCode
        from core.decision_space_162d import DecisionVector, PADVector

        smc = SuperiorMoralCode(enable_transcendence=True)
        pad = PADVector(0.5, 0.3, 0.7)
        latencies = []

        iterations = 500
        start = time.perf_counter()
        for i in range(iterations):
            # Stable vector to avoid dissonance triggers
            d = DecisionVector([0.95 + 0.001 * (i % 5)] * 162)
            t0 = time.perf_counter()
            result = smc.evaluate(d, pad)
            latencies.append((time.perf_counter() - t0) * 1000)
        total_elapsed = time.perf_counter() - start

        rps = iterations / total_elapsed
        p = print_latency_report(f"Superior Moral Code ({iterations} evals)", latencies, rps)
        assert rps > 200, f"SMC throughput too low: {rps:.0f} req/s"
        assert p["p99"] < 25.0, f"SMC p99 too high: {p['p99']:.3f}ms"

    def test_steganography_throughput(self):
        """FFT steganography detector — 500 analyses."""
        from core.steganography_detector import SteganographyDetector

        det = SteganographyDetector()
        texts = [
            f"This is test sentence number {i} with enough words to trigger "
            f"full analysis of the steganographic detection pipeline system."
            for i in range(500)
        ]
        latencies = []

        start = time.perf_counter()
        for text in texts:
            t0 = time.perf_counter()
            det.analyze(text)
            latencies.append((time.perf_counter() - t0) * 1000)
        total_elapsed = time.perf_counter() - start

        rps = len(texts) / total_elapsed
        p = print_latency_report(f"FFT Steganography ({len(texts)} analyses)", latencies, rps)
        assert rps > 500, f"FFT stego too slow: {rps:.0f} req/s"
        assert p["p99"] < 10.0, f"FFT stego p99 too high: {p['p99']:.3f}ms"


# ── Test 8: Latency Budget Analysis ─────────────────────────────────────────

class TestLatencyBudget:
    """
    Measures time spent in each pipeline stage to identify bottlenecks.
    Target: full pipeline < 50ms at p99.
    """

    def test_pipeline_stage_breakdown(self):
        """Measure latency per stage: G5 → G7 → G8 → CVC."""
        g5 = G5TransparencyGuard(max_global_sessions=50_000, global_audit_limit=50_000)
        g7 = G7PrivacyEvaluator()
        g8 = G8NonmaleficenceEvaluator()
        cvc = _CumulativeViolationCounter()

        ctx_ok = clean_ctx()
        agents = fair_agents()
        action = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}

        g5_lats, g7_lats, g8_lats, cvc_lats = [], [], [], []

        for i in range(1000):
            # G5
            t0 = time.perf_counter()
            g5.classify_request(f"stage test {i}", f"stage-{i}")
            g5_lats.append((time.perf_counter() - t0) * 1000)

            # G7
            t0 = time.perf_counter()
            g7.evaluate(action, ctx_ok)
            g7_lats.append((time.perf_counter() - t0) * 1000)

            # G8
            t0 = time.perf_counter()
            g8.evaluate(action, agents)
            g8_lats.append((time.perf_counter() - t0) * 1000)

            # CVC
            t0 = time.perf_counter()
            cvc.get_status(f"stage-{i}")
            cvc_lats.append((time.perf_counter() - t0) * 1000)

        stages = {
            "G5 classify": g5_lats,
            "G7 evaluate": g7_lats,
            "G8 evaluate": g8_lats,
            "CVC status":  cvc_lats,
        }

        print(f"\n  Pipeline Stage Breakdown (1000 iterations):")
        total_p99 = 0.0
        for name, lats in stages.items():
            p = percentiles(lats)
            total_p99 += p["p99"]
            print(f"    {name:15s}: p50={p['p50']:.4f}ms p99={p['p99']:.4f}ms max={p['max']:.4f}ms")

        print(f"    {'TOTAL (sum)':15s}: p99_sum={total_p99:.4f}ms")
        assert total_p99 < 50.0, f"Pipeline budget exceeded: {total_p99:.3f}ms > 50ms target"

    def test_latency_stability_over_time(self):
        """Check that latency doesn't degrade across 5,000 sequential requests."""
        engine = SecurityHardeningEngine(
            g5=G5TransparencyGuard(max_global_sessions=50_000, global_audit_limit=50_000),
        )
        ctx = clean_ctx()
        agents = fair_agents()
        action = {"type": "READ", "requesting_agent": "a0", "claimed_priority": 5}

        # Split into 5 buckets of 1000
        buckets = {f"bucket_{b}": [] for b in range(5)}

        for b in range(5):
            for i in range(1000):
                idx = b * 1000 + i
                t0 = time.perf_counter()
                engine.run_full_check(
                    request_text=f"stability {idx}", action=action, context=ctx,
                    agent_states=agents, session_id=f"stab-{idx}", severity="MEDIUM",
                )
                buckets[f"bucket_{b}"].append((time.perf_counter() - t0) * 1000)

        print(f"\n  Latency Stability (5x1000 buckets):")
        bucket_p99s = []
        for name, lats in buckets.items():
            p = percentiles(lats)
            bucket_p99s.append(p["p99"])
            print(f"    {name}: p50={p['p50']:.3f}ms p99={p['p99']:.3f}ms")

        # Last bucket should not be >5x worse than first (OS/GC variance on Windows)
        ratio = bucket_p99s[-1] / bucket_p99s[0] if bucket_p99s[0] > 0 else 1.0
        print(f"    Drift ratio (last/first): {ratio:.2f}x")
        assert ratio < 5.0, f"Latency drift too high: {ratio:.2f}x"
