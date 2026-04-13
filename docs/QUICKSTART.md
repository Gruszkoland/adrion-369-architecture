# QUICKSTART.md — ADRION 369 Integration Guide

> Quick Start for developers integrating ADRION 369 with external systems.  
> **Version:** 5.6.0 | **Date:** 2026-04-13

---

## 1. What is ADRION 369?

ADRION 369 is an ethical AI governance layer that evaluates every AI agent action through a **3-6-9 decision matrix**:

- **Trinity (3):** Three perspectives (Material, Intellectual, Essential) produce a weighted score
- **Hexagon (6):** Six operational modes process the request (max 3 cycles)
- **Guardians (9):** Nine ethical laws vote on the action (G7 Privacy + G8 Nonmaleficence are CRITICAL)

**Result:** Every action gets one of: `PROCEED`, `HOLD_HUMAN_REVIEW`, `HOLD_SENTINEL_REVIEW`, or `DENY`.

---

## 2. Installation

```bash
# Clone the repository
git clone https://github.com/Gruszkoland/adrion-369-architecture.git
cd adrion-369-architecture

# Install dependencies (only pytest needed for testing)
pip install pytest

# Verify: run all 99 tests
python -m pytest tests/ -v
```

**Requirements:** Python 3.9+ (no external dependencies for core modules).

---

## 3. Core Integration — Python

### 3.1 Trinity Score Evaluation

```python
from core.trinity import TrinityEngine, PerspectiveResult

engine = TrinityEngine()

# Create perspective results (score: 0.0-1.0, reasoning: min 20 chars)
material     = PerspectiveResult(score=0.85, reasoning="Material analysis: resource cost within budget limits and SLA.")
intellectual = PerspectiveResult(score=0.90, reasoning="Intellectual analysis: logic consistent, no contradictions found.")
essential    = PerspectiveResult(score=0.80, reasoning="Essential analysis: aligns with core organizational values.")

result = engine.calculate_score(material, intellectual, essential)

print(result.decision)   # "PROCEED" | "HOLD_HUMAN_REVIEW" | "HOLD_SENTINEL_REVIEW" | "DENY"
print(result.score)      # 0.8510 (weighted: 0.33*0.85 + 0.34*0.90 + 0.33*0.80)
print(result.flags)      # () or ("IMBALANCED:std_dev=0.0408", "ASYMMETRY_DETECTED:spread=0.1000")
print(result.status)     # "BALANCED" | "IMBALANCED" | "ASYMMETRIC"
```

### 3.2 Security Hardening Pipeline

```python
from core.security_hardening import SecurityHardeningEngine

engine = SecurityHardeningEngine()

result = engine.run_full_check(
    request_text="User requests data export",
    action={"type": "EXPORT", "requesting_agent": "a0", "claimed_priority": 5},
    context={
        "consent_signals": ["explicit_confirmation"],
        "informed_signals": ["consequences_explained", "risks_disclosed", "data_usage_explained"],
        "opt_out_available": True,
        "coercion_signals": [],
    },
    agent_states=[
        {"agent_id": "a0", "resource_allocation": 0.2, "queue_position": 0, "base_priority": 5},
        {"agent_id": "a1", "resource_allocation": 0.2, "queue_position": 1, "base_priority": 5},
        {"agent_id": "a2", "resource_allocation": 0.2, "queue_position": 2, "base_priority": 5},
    ],
    session_id="user-session-abc123",
    severity="HIGH",
)

print(result["decision"])      # "ALLOW" | "DENY" | "DENY_IMMEDIATELY" | "HOLD_HUMAN_REVIEW"
print(result.get("severity"))  # "HIGH"
print(result.get("cvc_status"))  # "OK" | "WATCH" | "BLOCK"
```

---

## 4. Decision Thresholds

| Parameter | Value | Effect |
|-----------|-------|--------|
| `DENY_THRESHOLD` | 0.30 | Score < 0.30 = automatic DENY |
| `HOLD_SENTINEL_THRESHOLD` | 0.55 | Score 0.30-0.55 = Sentinel review |
| `HOLD_HUMAN_THRESHOLD` | 0.70 | Score 0.55-0.70 = Human review |
| `MIN_PER_PERSPECTIVE` | 0.25 | Any perspective < 0.25 = DENY |
| `MIN_PROCEED_PER_PERSP` | 0.40 | Any perspective < 0.40 blocks PROCEED |
| `ASYMMETRY_SPREAD` | 0.45 | max-min spread >= 0.45 = ASYMMETRY flag |

---

## 5. G7 Privacy — Consent Requirements

For **standard actions**, consent score must be >= 0.95.

For **high-risk actions** (DELETE, EXPORT, ADMIN, BYPASS, ACTUATE, WRITE_FIRMWARE, etc.), consent must be >= 0.98, requiring `explicit_confirmation`.

### Consent Signal Scores

| Signal | Score |
|--------|-------|
| `explicit_confirmation` | 1.00 |
| `written_agreement` | 0.98 |
| `tos_acceptance` | 0.70 |
| `implicit_context` | 0.40 |
| *(none)* | 0.00 |

---

## 6. G8 Nonmaleficence — Fairness Requirements

| Check | Threshold | Effect |
|-------|-----------|--------|
| Fair share | >= 0.90 | Resource distribution must be fair |
| Variance | <= 0.15 | Low allocation variance required |
| Starvation | < 0.10 | Any agent below 10% = violation |
| Min agents | >= 2 | At least 2 agents required in context |

---

## 7. HTTP API Integration (Flask)

If integrating with the Flask application:

```
POST /api/v1/evaluate
Content-Type: application/json

{
  "request_text": "...",
  "action": {"type": "READ", "requesting_agent": "agent-1"},
  "context": { ... },
  "agent_states": [ ... ],
  "session_id": "your-session-id",
  "severity": "MEDIUM"
}

Response:
{
  "decision": "ALLOW",
  "details": { "g5": {...}, "g7": {...}, "g8": {...} },
  "session_hash": "a1b2c3d4e5f67890",
  "severity": "MEDIUM",
  "cvc_status": "OK"
}
```

Full API docs: `http://localhost:8003/api/docs` (Swagger UI)

---

## 8. Handling Decisions in Your Application

```python
result = engine.run_full_check(...)

match result["decision"]:
    case "ALLOW":
        execute_action()
    case "DENY" | "DENY_IMMEDIATELY":
        log_denial(result)
        notify_user("Action denied by security policy")
    case "HOLD_HUMAN_REVIEW":
        queue_for_human_review(result)
    case "HOLD_SENTINEL_REVIEW":
        escalate_to_sentinel(result)
    case "SENTINEL_ESCALATION":
        alert_security_team(result)
    case "CVC_BLOCK":
        block_session(result)
        log_salami_slicing_attempt(result)
```

---

## 9. Architecture Overview

```
Your Application
      |
      v
SecurityHardeningEngine.run_full_check()
      |
      +-- CVC pre-check (salami slicing detection)
      +-- Input sanitization (session_id, severity)
      +-- G5 TransparencyGuard (audit request classification)
      +-- G7 PrivacyEvaluator (consent, informed, coercion, opt-out)
      +-- G8 NonmaleficenceEvaluator (fairness, queue, priority, starvation)
      +-- CVC post-record (violation counting)
      |
      v
Decision: ALLOW | DENY | HOLD | ESCALATE
```

---

## 10. Common Integration Patterns

### Pattern A: Middleware (Flask/FastAPI)

```python
@app.before_request
def adrion_check():
    result = security_engine.run_full_check(
        request_text=request.get_json().get("prompt", ""),
        action={"type": request.method, "requesting_agent": current_user.id},
        context=build_consent_context(current_user),
        agent_states=get_active_agents(),
        session_id=session.sid,
        severity=classify_severity(request),
    )
    if result["decision"] not in ("ALLOW",):
        return jsonify({"error": "blocked", "reason": result["decision"]}), 403
```

### Pattern B: Agent wrapper

```python
class SafeAgent:
    def __init__(self, agent, security_engine):
        self.agent = agent
        self.se = security_engine

    def execute(self, action, context, agents, session_id):
        result = self.se.run_full_check(
            request_text=str(action),
            action=action,
            context=context,
            agent_states=agents,
            session_id=session_id,
        )
        if result["decision"] == "ALLOW":
            return self.agent.execute(action)
        return {"blocked": True, "reason": result}
```

---

## 11. Key Rules

1. **Entry point:** `wsgi.py` -> `arbitrage.app.create_app()` (never `arbitrage_server.py`)
2. **Config:** `arbitrage.config.settings.*` (Pydantic BaseSettings, not raw `os.getenv`)
3. **SQL:** Parameterized only (`?` placeholders), never f-strings
4. **Guardian Laws:** Source of truth is `docs/GUARDIAN_LAWS_CANONICAL.json`
5. **Immutability:** All result objects are frozen — do not attempt to modify them

---

*ADRION 369 — Multi-Agent AI Orchestration System*  
*https://github.com/Gruszkoland/adrion-369-architecture*
