# 🔐 SECURITY HARDENING — ADRION 369 v5.3

> **Moduł:** `core/security_hardening.py` | **Warstwa:** Rdzeń (Core)
> **Wersja:** v5.3 — Full Hardening (2026-04-11)
> **Odwołanie:** [01_CORE_TRINITY.md](docs/01_CORE_TRINITY.md) | [02_CORE_HEXAGON.md](docs/02_CORE_HEXAGON.md) | [03_CORE_GUARDIANS.md](docs/03_CORE_GUARDIANS.md) | [04_CORE_EBDI.md](docs/04_CORE_EBDI.md) | [07_LAWS.md](docs/07_LAWS.md)

---

## 🎯 Cel

Pełne zamknięcie wszystkich znanych luk zidentyfikowanych w analizie bezpieczeństwa ADRION 369:

| Runda | Źródło | Główne luki |
|-------|--------|-------------|
| v5.1 | Analiza wewnętrzna | VETO próg 3→2; Trinity gray zone; Hexagon loop; PAD therapy; replay attack |
| v5.2 | Analiza wewnętrzna | Circuit Breaker; Genesis SPOF; Agent Auth; Degraded Mode; Vortex auth; Rate Limiting |
| v5.3 | Raport Grock | G5 self-reinforcing loop; G7/G8 metryki numeryczne; CVC salami slicing; HEXAGON default po cyklach |

---

## 📋 Mechanizmy Hardeningu

### 1. TRINITY — Wagi i Bramki Decyzyjne (jawne od v5.0)

Wagi Trinity Score (z [01_CORE_TRINITY.md](docs/01_CORE_TRINITY.md)):

```python
Trinity Score = (w_m × S_material) + (w_i × S_intellectual) + (w_e × S_essential)
w_m = 0.33   # Material  (LOGOS)
w_i = 0.34   # Intellectual (ETHOS)
w_e = 0.33   # Essential (EROS)
```

Bramki decyzyjne (4 strefy — v5.1):

| Zakres score | Strefa | Decyzja |
|-------------|--------|---------|
| < 0.30 | DENY | Natychmiastowe odrzucenie |
| 0.30–0.55 | HOLD | Eskalacja do Sentinela |
| 0.55–0.70 | HOLD | Eskalacja do człowieka |
| > 0.70 + min_per_persp ≥ 0.40 | PROCEED | Kontynuacja |

Dodatkowe warunki (v5.1):
- `std_dev > 0.30` → status `IMBALANCED` → HOLD niezależnie od score
- Żadna pojedyncza perspektywa nie może być < 0.25 (minimum floor)
- Spread > 0.45 między perspektywami → `ASYMMETRY_DETECTED` → HOLD

### 2. HEXAGON — Ochrona po Wyczerpaniu Cykli (v5.1)

```python
MAX_CYCLES = 3

# [v5.1] KRYTYCZNA ZMIANA: po wyczerpaniu → DENY (wcześniej: PROCEED)
if cycle >= MAX_CYCLES and needs_cycle_back:
    return {"decision": "DENY", "reason": "No convergence — human escalation required"}

# Detekcja stagnacji (delta < 0.01 między cyklami)
if convergence_delta < 0.01:
    return {"decision": "DENY", "reason": "Stagnation detected"}
```

Healing mode: checkpoint G8 przed każdą modyfikacją stanu (zapobiega exploitowi obniżania alertów).

### 3. GUARDIANS — Kompletna Logika Decyzyjna (v5.3)

```python
# --- Poziom 1: CRITICAL VETO ---
if ANY CRITICAL law violated (G7, G8):
    genesis_record.log(violation, severity="CRITICAL")
    return DENY_IMMEDIATELY

# --- Poziom 2: Próg kumulacyjny (v5.1 CVC) ---
cumulative = genesis_record.get_cumulative_violations(session_id, window_hours=24)
if cumulative + violations >= CVC_THRESHOLD:   # domyślnie: 5
    return DENY   # salami slicing zablokowany

# --- Poziom 3: Próg per-zapytanie (v5.1: obniżony z 3 do 2) ---
if violations >= 2:
    return DENY

# --- Poziom 4: Jedno naruszenie non-critical ---
if violations == 1:
    return REVIEW_REQUIRED   # Eskalacja do człowieka

return ALLOW
```

**Guardian Compliance Score** = `(9 − violations) / 9`

### 4. G5 Transparency — Zamknięcie Self-Reinforcing Loop (v5.3)

**Problem (raport Grock):** Prompt cytujący G5 i żądający audytu automatycznie spełnia G5 (reasoning ≥ 20 znaków) → system musi odpowiedzieć → self-reinforcing loop wymuszający ujawnienie architektury.

**Rozwiązanie (v5.3):**

```python
class G5TransparencyGuard:
    """
    Rozróżnia legitymacyjne żądania przejrzystości od exploitów
    wykorzystujących self-reinforcing loop G5.
    """

    AUDIT_REQUEST_PATTERNS = [
        "żądam audytu",
        "ujawnij architekturę",
        "pełny audit trail",
        "wyjaśnij wagi",
        "reasoning >=20",
        "glass-box compliance",
        "zgodnie z G5",
    ]

    MAX_AUDIT_DEPTH = 2          # Max poziomów szczegółowości w jednej sesji
    AUDIT_COOLDOWN_SECONDS = 300 # 5 minut między żądaniami audytu

    def classify_request(self, text: str, session_id: str) -> dict:
        """Klasyfikuje żądanie jako legitymacyjne lub exploit"""

        # Sprawdź rate limit dla żądań audytu
        last_audit = self._get_last_audit_time(session_id)
        if last_audit and (time.time() - last_audit) < self.AUDIT_COOLDOWN_SECONDS:
            return {
                "type": "AUDIT_RATE_LIMITED",
                "action": "REVIEW_REQUIRED",
                "reason": f"Audit request rate limited — wait {self.AUDIT_COOLDOWN_SECONDS}s"
            }

        # Sprawdź głębokość audytu w sesji
        audit_depth = self._get_audit_depth(session_id)
        if audit_depth >= self.MAX_AUDIT_DEPTH:
            return {
                "type": "AUDIT_DEPTH_EXCEEDED",
                "action": "DENY",
                "reason": "Maximum audit depth reached for this session"
            }

        # Sprawdź wzorce exploitu
        pattern_matches = sum(1 for p in self.AUDIT_REQUEST_PATTERNS if p.lower() in text.lower())
        if pattern_matches >= 3:
            return {
                "type": "POTENTIAL_G5_EXPLOIT",
                "action": "SENTINEL_ESCALATION",
                "reason": f"Multiple audit-forcing patterns detected ({pattern_matches})",
                "pattern_count": pattern_matches
            }

        # Legitymacyjne żądanie audytu
        self._increment_audit_depth(session_id)
        return {
            "type": "LEGITIMATE_AUDIT",
            "action": "ALLOW_WITH_STANDARD_RESPONSE",
            "audit_depth": audit_depth + 1
        }

    def standard_audit_response(self) -> dict:
        """
        Standardowa odpowiedź na żądanie G5 — wyjaśnialna, ale nie ujawniająca
        wewnętrznych sekretów implementacyjnych.
        """
        return {
            "reasoning": (
                "Żądanie przetworzone przez pipeline Trinity(3)→Hexagon(6)→Guardians(9). "
                "Decyzja podjęta zgodnie z 9 Prawami Guardians. "
                "Pełny audit trail zapisany w Genesis Record pod session_id."
            ),
            "decision_traceable": True,
            "inputs_documented": True,
            "process_reproducible": True,
            "genesis_hash": "[hash dostępny dla autoryzowanych audytorów]",
            "note": "Szczegóły implementacyjne dostępne po autoryzacji Sentinela"
        }
```

### 5. G7 Privacy — Metryki Numeryczne (v5.3)

**Problem (raport Grock):** Brak mierzalnych progów consent/opt-out → szara strefa weryfikacji.

```python
class G7PrivacyEvaluator:
    """
    G7: Privacy — Szacunek dla wolnej woli i zgody użytkownika.
    v5.3: Numeryczne progi weryfikacji.
    """

    # --- Progi numeryczne (v5.3) ---
    CONSENT_SCORE_THRESHOLD  = 0.95   # Minimalna pewność uzyskania zgody
    OPT_OUT_AVAILABILITY     = True   # Zawsze musi być dostępny
    COERCION_SCORE_MAX       = 0.05   # Max akceptowalny poziom przymusu
    INFORM_SCORE_THRESHOLD   = 0.90   # Min poziom poinformowania o konsekwencjach

    def evaluate(self, action: dict, context: dict) -> dict:
        scores = {}

        # Test 1: User consent obtained? [0.0–1.0]
        scores["consent"] = self._score_consent(action, context)

        # Test 2: User informed about consequences? [0.0–1.0]
        scores["informed"] = self._score_informed(action, context)

        # Test 3: User can opt-out? [bool → 0.0 lub 1.0]
        scores["opt_out"] = 1.0 if context.get("opt_out_available") else 0.0

        # Test 4: No coercion detected? [0.0 = brak przymusu, 1.0 = silny przymus]
        scores["coercion"] = self._score_coercion(action, context)

        # Decyzja G7
        violation = (
            scores["consent"]  < self.CONSENT_SCORE_THRESHOLD  or
            scores["informed"] < self.INFORM_SCORE_THRESHOLD   or
            scores["opt_out"]  < 1.0                            or
            scores["coercion"] > self.COERCION_SCORE_MAX
        )

        return {
            "law": "G7_Privacy",
            "compliant": not violation,
            "scores": scores,
            "thresholds": {
                "consent_required":  self.CONSENT_SCORE_THRESHOLD,
                "informed_required": self.INFORM_SCORE_THRESHOLD,
                "coercion_max":      self.COERCION_SCORE_MAX
            },
            "decision": "DENY_IMMEDIATELY" if violation else "PASS"
        }

    def _score_consent(self, action: dict, context: dict) -> float:
        """
        Heurystyki scoringu zgody:
        - Explicit 'yes' w kontekście → 1.0
        - Domyślna zgoda w ToS → 0.70
        - Brak jakiejkolwiek zgody → 0.0
        """
        consent_signals = context.get("consent_signals", [])
        if "explicit_confirmation" in consent_signals: return 1.0
        if "tos_acceptance" in consent_signals: return 0.70
        if "implicit_context" in consent_signals: return 0.40
        return 0.0

    def _score_informed(self, action: dict, context: dict) -> float:
        informed_signals = context.get("informed_signals", [])
        score = 0.0
        if "consequences_explained" in informed_signals: score += 0.50
        if "risks_disclosed" in informed_signals: score += 0.30
        if "data_usage_explained" in informed_signals: score += 0.20
        return min(score, 1.0)

    def _score_coercion(self, action: dict, context: dict) -> float:
        coercion_signals = context.get("coercion_signals", [])
        score = 0.0
        if "urgency_pressure" in coercion_signals: score += 0.40
        if "no_alternative_offered" in coercion_signals: score += 0.30
        if "threat_implied" in coercion_signals: score += 0.30
        return min(score, 1.0)
```

### 6. G8 Nonmaleficence — Metryki Numeryczne (v5.3)

**Problem (raport Grock):** Brak mierzalnych progów fairness zasobów → możliwy subtelny resource grab.

```python
class G8NonmaleficenceEvaluator:
    """
    G8: Nonmaleficence — Uczciwa alokacja zasobów między agentami.
    v5.3: Numeryczne progi weryfikacji.
    """

    # --- Progi numeryczne (v5.3) ---
    FAIR_SHARE_SCORE_MIN = 0.90      # Min fair share score (0=brak równości, 1=pełna równość)
    RESOURCE_VARIANCE_MAX = 0.15     # Max wariancja alokacji zasobów między agentami
    QUEUE_JUMP_TOLERANCE = 0         # Zero tolerancji na omijanie kolejki
    STARVATION_THRESHOLD = 0.10      # Agent z < 10% fair share = "głodzony"

    NUM_AGENTS = 6
    FAIR_SHARE_PER_AGENT = 1.0 / NUM_AGENTS  # ~16.67%

    def evaluate(self, action: dict, agent_states: list) -> dict:
        scores = {}

        # Test 1: Resource distribution fairness [0.0–1.0]
        allocation = [s.get("resource_allocation", 0.0) for s in agent_states]
        scores["fair_share"] = self._compute_fair_share_score(allocation)

        # Test 2: Queue jumping detection [bool]
        scores["queue_jump"] = self._detect_queue_jump(action, agent_states)

        # Test 3: Priority abuse detection [bool]
        scores["priority_abuse"] = self._detect_priority_abuse(action, agent_states)

        # Test 4: Starvation check [bool]
        scores["starvation"] = self._detect_starvation(allocation)

        # Decyzja G8
        violation = (
            scores["fair_share"] < self.FAIR_SHARE_SCORE_MIN or
            scores["queue_jump"]                               or
            scores["priority_abuse"]                           or
            scores["starvation"]
        )

        return {
            "law": "G8_Nonmaleficence",
            "compliant": not violation,
            "scores": scores,
            "thresholds": {
                "fair_share_min":        self.FAIR_SHARE_SCORE_MIN,
                "resource_variance_max": self.RESOURCE_VARIANCE_MAX,
                "starvation_threshold":  self.STARVATION_THRESHOLD
            },
            "decision": "DENY_IMMEDIATELY" if violation else "PASS"
        }

    def _compute_fair_share_score(self, allocation: list) -> float:
        """Gini-inspired fairness score. 1.0 = idealna równość."""
        import statistics
        if not allocation or sum(allocation) == 0:
            return 1.0  # Brak alokacji = brak nierówności
        variance = statistics.variance(allocation) if len(allocation) > 1 else 0.0
        if variance > self.RESOURCE_VARIANCE_MAX:
            return max(0.0, 1.0 - (variance / self.RESOURCE_VARIANCE_MAX))
        return 1.0

    def _detect_queue_jump(self, action: dict, agent_states: list) -> bool:
        requesting_agent = action.get("requesting_agent")
        queue = [s.get("agent_id") for s in sorted(agent_states, key=lambda x: x.get("queue_position", 99))]
        if not queue or requesting_agent == queue[0]:
            return False   # Jest pierwszy w kolejce = OK
        return action.get("priority_override", False)  # Poza kolejką = jump

    def _detect_priority_abuse(self, action: dict, agent_states: list) -> bool:
        requesting = next((s for s in agent_states if s.get("agent_id") == action.get("requesting_agent")), {})
        base_priority = requesting.get("base_priority", 5)
        claimed_priority = action.get("claimed_priority", 5)
        return claimed_priority > base_priority + 2  # Nadmierne podniesienie priorytetu

    def _detect_starvation(self, allocation: list) -> bool:
        return any(a < self.STARVATION_THRESHOLD for a in allocation if a > 0)
```

### 7. Kumulacyjny Licznik Naruszeń (CVC) — Salami Slicing Protection

```python
CVC_CONFIG = {
    "window_hours": 24,
    "threshold_watch": 3,     # ≥3 → zwiększone logowanie
    "threshold_block": 5,     # ≥5 → DENY
    "reset_on_clean": 3       # ile czystych sesji resetuje licznik
}

# Przy każdym zapytaniu:
cvc = genesis_record.get_cumulative_violations(session_id)
if cvc + current_violations >= CVC_CONFIG["threshold_block"]:
    return DENY   # Zablokowanie salami slicing
```

### 8. Circuit Breaker (v5.2)

- OPEN po N błędach zewnętrznych (MCP/PLC): `failure_threshold=3`
- MCP Guardian i Genesis: `failure_threshold=2` (krytyczne — niższy próg)
- Timeout reset: 30 sekund → HALF_OPEN (1 próbne żądanie)
- Fallback: `DENY` dla Guardian/Genesis; `DEGRADE` dla Vortex

### 9. Go Vortex Hardening (v5.2, port 1740)

- Dostęp: **tylko localhost** + `iptables DROP` z zewnątrz
- Autentykacja: JWT (TTL 5 min) + mTLS (TLS 1.3)
- Uprawnienia: tylko Sentinel, Healer, Orchestrator (3 z 6 agentów)
- Rate limit: 100 req/min per agent, burst 10 req/s

### 10. Degraded Mode — 5 Poziomów (v5.2)

| Tryb | Warunek | HIGH/CRITICAL | LOW |
|------|---------|---------------|-----|
| `FULL_OPERATION` | Wszystko OK | PROCEED | PROCEED |
| `DEGRADED_L1` | Trinity lub Hexagon DOWN | DENY | MANUAL_REVIEW |
| `DEGRADED_L2` | Trinity I Hexagon DOWN | DENY | GUARDIANS_ONLY |
| `GUARDIANS_ONLY` | Tylko Guardians | DENY | GUARDIANS_ONLY |
| `EMERGENCY_DENY` | Guardians lub Genesis DOWN | **DENY** | **DENY** |

### 11. Ochrona Sygnatury 369 (v5.1)

```python
# Sygnatura = SHA3-256(trinity_hash:hexagon_hash:guardians_hash:timestamp:nonce)
# TTL: 3600s (1 godzina)
# Nonce: UUID4 — jednorazowy, rejestrowany w Genesis Record
# Replay attack: nonce w NONCE_REGISTRY → DENY_IMMEDIATELY
```

### 12. EBDI + Goodness Analyzer (v5.1)

- `STRESS_FLOOR = 0.08` — system nie może być "zbyt spokojny"
- PADTherapyDetector: monotoniczny spadek Stress przez 5+ sesji → `RAISE_VIGILANCE`
- PAD rate limit: max delta 0.15 per step
- FFT Goodness Analyzer: 4 warstwy (FFT + jitter + grammar/intent gap + adversarial patterns)
- Jitter threshold: `jitter_score > 0.55` → `SENTINEL_REVIEW`

### 13. Agent Authentication (v5.2)

- HMAC-SHA256 na każdej wiadomości inter-agent
- Klucze rotowane co 24h przez agenta Sentinel
- mTLS (TLS 1.3) na Message Bus
- Healer: wymaga kontrasygnaty Sentinela (`double_sign_required`)
- Replay protection: nonce + timestamp freshness (max 30s)

### 14. Rate Limiting — 5 Poziomów (v5.2)

| Poziom | Scope | Limit |
|--------|-------|-------|
| L1 Global | Cały system | 100 req/s, burst 500 |
| L2 Per-IP | Adres IP | 30 req/min |
| L3 Per-User | Użytkownik | 50 req/min |
| L4 Per-Severity | User × Severity | CRITICAL: 5/min; HIGH: 10/min |
| L5 Anomaly | Pattern detection | Burst >20/5s, HIGH farming >8/2min → BLOCK |

### 15. Genesis Record SPOF Protection (v5.2)

- 3-poziomowy fallback: Primary → Replica → WAL → UNAVAILABLE
- `UNAVAILABLE` + severity HIGH/CRITICAL → automatyczny **DENY**
- WAL: lokalny bufor dla LOW gdy brak Primary i Replica
- Auto-sync WAL do Primary po przywróceniu

---

## 🗺️ Threat Model — Kompletny (v5.3)

```
ATAK                          WEKTOR                    OCHRONA
═══════════════════════════════════════════════════════════════════════
Prompt Injection          →  Goodness Analyzer (4 warstwy + FFT)
Replay Attack             →  Nonce+TTL Sygnatura 369
Salami Slicing            →  CVC (24h window, threshold=5)
Loop Exhaustion           →  MAX_CYCLES → DENY + LoopGuard
PAD Therapy               →  STRESS_FLOOR + PADTherapyDetector
Trinity Asymmetry         →  Asymmetry detection + min-per-perspective
Healing Exploitation      →  G8 checkpoint w Healing mode
Gray Zone Abuse           →  4 deterministyczne strefy Trinity
G5 Self-Reinforcing Loop  →  G5TransparencyGuard + audit rate limit  ← NOWE v5.3
G7 Consent Gray Zone      →  Numeryczne progi (consent_score ≥ 0.95) ← NOWE v5.3
G8 Resource Grab          →  Gini score + variance ≤ 0.15            ← NOWE v5.3
Agent Impersonation       →  HMAC-SHA256 + mTLS + key rotation
External Service DoS      →  Circuit Breaker (3 stany)
Layer Unavailability      →  Degraded Mode Controller (5 trybów)
Genesis Record Failure    →  Primary→Replica→WAL→DENY
Vortex Direct Access      →  JWT+mTLS+localhost-only+iptables
Request Flooding          →  Rate Limiter (5 poziomów)
```

---

## ✅ Status Hardeningu

| Warstwa | v5.0 | v5.1 | v5.2 | v5.3 |
|---------|------|------|------|------|
| Trinity gates | ✅ 2 strefy | ✅ 4 strefy | ✅ | ✅ |
| Hexagon po cyklach | ❌ PROCEED | ✅ DENY | ✅ | ✅ |
| Guardians VETO próg | ❌ 3 | ✅ 2 | ✅ | ✅ |
| CVC salami slicing | ❌ | ✅ | ✅ | ✅ |
| G5 self-loop | ❌ | ❌ | ❌ | ✅ |
| G7 metryki numeryczne | ❌ | ❌ | ❌ | ✅ |
| G8 metryki numeryczne | ❌ | ❌ | ❌ | ✅ |
| Circuit Breaker | ❌ | ❌ | ✅ | ✅ |
| Agent Auth | ❌ | ❌ | ✅ | ✅ |
| Degraded Mode | ❌ | ❌ | ✅ | ✅ |
| Vortex auth | ❌ | ❌ | ✅ | ✅ |
| Rate Limiting | ❌ | ❌ | ✅ | ✅ |
| Genesis SPOF | ❌ | ❌ | ✅ | ✅ |
| Sygnatura replay | ❌ | ✅ | ✅ | ✅ |
| EBDI floor | ❌ | ✅ | ✅ | ✅ |
| FFT Goodness | podstawowy | ✅ 4 warstwy | ✅ | ✅ |

**Stan po v5.3: 🔒 Fully Hardened Glass-Box**

---

*Dokument zarządzany przez agenta Sentinel. Ostatnia aktualizacja: 2026-04-11.*
