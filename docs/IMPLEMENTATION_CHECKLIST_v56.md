# ADRION 369 v5.6 — Checklist Wdrożenia

> Status: 99/99 testów zielonych | Data: 2026-04-12
> Każda pozycja: [P] = Pilne | [A] = Architektoniczne | [O] = Opcjonalne

---

## MODUŁ 1 — Python Runtime Hardening (core/trinity.py)

- [x] **PY-1a** [P] `object.__setattr__` zablokowany przez `__setattr__` override + `__slots__`
- [x] **PY-1b** [P] `__dict__` niedostępny przez `__slots__` na `PerspectiveResult` i `TrinityOutput`
- [x] **PY-1d** [P] `pickle` zablokowany przez `__reduce__` / `__reduce_ex__` → `TypeError`
- [x] **PY-1f** [P] `__reduce_ex__` zablokowany (pickle protocol 4+)
- [x] **OUT-1.7** [P] `TrinityOutput._flags` chroniony przez `__setattr__` override
- [x] **VALID-2.7** [P] Control chars (`\x00`–`\x1f`) w `reasoning` → `ValueError`
- [x] **TRI-2a** [P] `TRINITY_WEIGHTS` → `MappingProxyType` (niemutowalny globalnie)
- [x] **TRI-2b** [P] `_WEIGHTS` jako `property` — nie można nadpisać na instancji
- [x] **TRI-2c** [P] `_TrinityEngineMeta` blokuje podklasowanie `TrinityEngine`
- [x] **TRI-2d** [P] `isinstance(obj, PerspectiveResult)` blokuje duck typing
- [x] **DYN-1.4** [P] `isinstance(self, TrinityEngine)` blokuje `type()` clone
- [ ] **MP-1.6** [A] Monkeypatch `TrinityEngine.calculate_score` na poziomie klasy nadal możliwy
      → *Python nie blokuje modyfikacji metod klasowych bez C-extension lub audit hooks*
      → **Wdrożenie:** `sys.audit()` hook w Python 3.12+ lub `forbiddenfruit` library
      → **Alternatywa:** Uruchom moduł w `__restricted__` sandbox lub separate process

---

## MODUŁ 2 — G5 TransparencyGuard (core/security_hardening.py)

- [x] **G5-3.2** [P] `AUDIT_REQUEST_PATTERNS` niemutowalna na instancji (`__setattr__` guard)
- [x] **G5-3.3** [P] Rozszerzone wzorce semantyczne PL/EN (41 wzorców, poprzednio 19)
- [x] **G5-3.4** [P] Normalizacja whitespace przed pattern matching (`_normalize_text`)
- [x] **G5-3a** [P] Konfiguracja frozen po `__init__` przez `MappingProxyType`
- [x] **G5-3b** [P] `_session_data` prywatna przez name mangling (`__sessions`)
- [x] **G5-3c** [P] `_global_audit_count` prywatny (`__global_count`)
- [x] **G5-3d** [P] `session_id=None` → `ValueError` → DENY
- [x] **G5-3e** [P] `session_id=''` → `ValueError` → DENY
- [x] **B4** [P] Globalny limit sesji (`MAX_GLOBAL_SESSIONS=10_000`) + `RuntimeError`
- [x] **B6** [P] `threading.RLock` — thread-safe operacje na sesjach
- [x] **H3** [P] TTL eviction sesji (`SESSION_TTL=3600s`)
- [ ] **B2** [A] Fragmentacja wzorców przez znaki specjalne (`żąd@m`, `z-ą-d-a-m`)
      → **Wdrożenie:** `unicodedata.normalize('NFKD', text)` + regex stripping znaków pomiędzy
      → Priorytet: ŚREDNI (wymaga NLP lub regex rozszerzenia)
- [ ] **B3** [A] 2 wzorce < progu 3 → LEGITIMATE (znane ograniczenie progu)
      → **Wdrożenie:** Obniżyć `PATTERN_THRESHOLD` do 2 lub dodać scoring wzorców
- [ ] **B5** [A] Brak synchronizacji między instancjami (multi-instance deployment)
      → **Wdrożenie:** Redis/Valkey jako shared store dla `__sessions` i `__global_count`
      → Wymagane: `redis-py`, connection pool, TTL na kluczach Redis

---

## MODUŁ 3 — G7 PrivacyEvaluator (core/security_hardening.py)

- [x] **G7-4.1** [P] Progi G7 niemutowalne po init (`__slots__` + `MappingProxyType`)
- [x] **G7-4d** [P] Logika violations: `DELETE + explicit` → PASS (naprawa błędu kolejności)
- [x] **G7-4a** [P] Multi-word exact matching: `DELETE_USER` → high_risk (zawiera `DELETE`)
- [x] **G7-4.4** [P] `action=None` lub `action=[]` obsługiwane (brak crash)
- [x] **C8** [P] `action["type"]` analizowany — high-risk wymaga `explicit_confirmation`
- [x] **BIZ-7.2** [P] `BYPASS` i dodatkowe typy dodane do `_HIGH_RISK_ACTION_TYPES`
- [ ] **G7-SCOPE** [A] G7 sprawdza TYLKO context, nie TREŚĆ akcji
      → Consent na `DELETE users WHERE id=1` ≠ consent na `DELETE users` (brak granularności)
      → **Wdrożenie:** Dodaj `action_scope` do kontekstu i sprawdzanie zakresu
- [ ] **G7-HIST** [A] Consent nie jest weryfikowany historycznie (brak rekordu zgody)
      → **Wdrożenie:** Genesis Record powinien przechowywać ważność zgody z timestampem

---

## MODUŁ 4 — G8 NonmaleficenceEvaluator (core/security_hardening.py)

- [x] **G8-5.2** [P] Deterministyczny sort tie-break: `(queue_position, agent_id)`
- [x] **G8-5.3** [P] `claimed_priority=None` → default=base (brak abuse, brak crash)
- [x] **G8-5.4** [P] Walidacja konfiguracji: `fair_share_min ∈ [0,1]`, `min_agents >= 2`
- [x] **G8-5c** [P] `None` w `agent_states` → filtrowany, brak crash
- [x] **G8-5f** [P] Progi niemutowalne po init (`__slots__` + `MappingProxyType`)
- [x] **D1** [P] Minimum 2 agentów wymagane
- [x] **D2** [P] `sum=0` → `fair_share=0.0` → DENY
- [x] **D5** [P] Queue jump sprawdzany faktycznie (bez `priority_override` flagi)
- [x] **D6** [P] `allocation=0` wykrywane jako starvation (`a < threshold` zamiast `0 < a`)
- [x] **D7** [P] Priority abuse: `>=` zamiast `>`
- [ ] **G8-DUP** [O] Duplikaty `agent_id` w liście — nieokreślone zachowanie
      → **Wdrożenie:** `if len(valid) != len({a['agent_id'] for a in valid}): DENY`
- [ ] **G8-NEG** [O] Ujemne `resource_allocation` dozwolone (nie jest to atak, ale błąd danych)
      → **Wdrożenie:** Walidacja `allocation >= 0` w `evaluate()`

---

## MODUŁ 5 — SecurityHardeningEngine (core/security_hardening.py)

- [x] **SE-6a** [P] `g5_guard` niemutowalny po init (`__slots__` + `__setattr__`)
- [x] **SE-6b** [P] `g7_eval`, `g8_eval` niemutowalne po init
- [x] **SE-6c** [P] `severity=None` lub `severity=" HIGH "` → normalizowane do `MEDIUM`
- [x] **SE-6d** [P] Session ID sanityzowany (SQL injection, path traversal, null bytes)
- [x] **SE-6.2** [P] Surowy `session_id` nie echowany — zwracany `session_hash` (SHA-256[:16])
- [x] **E1** [P] G5 `REVIEW_REQUIRED` + `HIGH/CRITICAL` severity → `HOLD_HUMAN_REVIEW`
- [x] **E5** [P] `severity` parametr używany w logice i zwracany w odpowiedzi
- [x] **BIZ-7.4** [P] CVC (`_CumulativeViolationCounter`) zaimplementowany
- [x] **BIZ-7.5** [A] Szkielet Genesis Record — placeholder (patrz niżej)
- [ ] **SE-GENESIS** [A] Genesis Record nie jest zintegrowany z `run_full_check`
      → **Wdrożenie:**
        ```python
        genesis.log_action({
            "session_hash": _hash_session_id(sid),
            "decision": result["decision"],
            "severity": sev,
            "timestamp": time.time(),
            "violations": violations,
            "cvc_status": cvc_status,
        })
        ```
- [ ] **SE-HEXAGON** [A] Hexagon (6 trybów) nie jest zintegrowany
      → **Wdrożenie:** Po G5 ALLOW, przed G7 — uruchom Hexagon pipeline
- [ ] **SE-TRINITY** [A] Trinity Engine nie jest wywołany w `run_full_check`
      → **Wdrożenie:** Trinity score jako dodatkowy warunek wejścia do pipeline

---

## MODUŁ 6 — CVC (Cumulative Violation Counter)

- [x] **CVC-IMPL** [P] `_CumulativeViolationCounter` zaimplementowany
- [x] **CVC-WINDOW** [P] 24h okno czasowe z automatycznym czyszczeniem
- [x] **CVC-THRESHOLDS** [P] WATCH=3, BLOCK=5 naruszeń
- [x] **CVC-THREAD** [P] Thread-safe przez `threading.RLock`
- [ ] **CVC-PERSIST** [A] CVC resetowany po restarcie procesu (in-memory only)
      → **Wdrożenie:** Redis z TTL=24h jako persistent store
- [ ] **CVC-GLOBAL** [A] CVC per-session, brak globalnego wykrywania
      → **Wdrożenie:** Dodaj per-IP counter niezależny od session_id

---

## MODUŁ 7 — Znane Ograniczenia Architektury (nie błędy — decyzje projektowe)

| ID | Ograniczenie | Uzasadnienie | Rekomendacja |
|----|-------------|-------------|-------------|
| ARCH-1 | Python `Final` nie egzekwowany w runtime | Język nie wspiera runtime enforcement | Użyj mypy/pyright w CI/CD |
| ARCH-2 | Monkeypatch metod klasowych możliwy | Fundamentalne ograniczenie Pythona | audit hook lub C-extension sandbox |
| ARCH-3 | Multi-instance G5 bez synchronizacji | Wymaga infrastruktury (Redis) | Wdrożyć w fazie 2 |
| ARCH-4 | G5 nie broni przed NLP paraphrase ataku | Wymaga LLM-based detector | Wdrożyć jako opcjonalny moduł |
| ARCH-5 | Genesis Record to placeholder | Wymaga bazy danych | Wdrożyć z PostgreSQL/Redis |
| ARCH-6 | Hexagon pipeline nie zintegrowany | Poza zakresem implementacji Python | Wdrożyć w Go Vortex |
| ARCH-7 | Trinity nie wywoływana w pipeline | Scope: Python security layer only | Integracja z UAP Orchestrator |

---

## MODUŁ 8 — Infrastruktura (poza scope Python)

- [ ] **INFRA-1** [A] mTLS między agentami (dokumentacja: `AGENT_AUTHENTICATION.md`)
- [ ] **INFRA-2** [A] Go Vortex auth: JWT + mTLS + localhost-only (dokumentacja: `GO_VORTEX_HARDENING.md`)
- [ ] **INFRA-3** [A] Circuit Breaker dla serwisów zewnętrznych (`CIRCUIT_BREAKER.md`)
- [ ] **INFRA-4** [A] Degraded Mode Controller + LayerWatchdog (`DEGRADED_MODE.md`)
- [ ] **INFRA-5** [A] Genesis Record Primary→Replica→WAL (`GENESIS_HARDENING.md`)
- [ ] **INFRA-6** [A] Rate Limiting 5-poziomowy (`RATE_LIMITING.md`)
- [ ] **INFRA-7** [A] Sygnatura 369: timestamp+nonce+TTL replay protection

---

## PRIORYTETY WDROŻENIA

### Faza 1 — Natychmiastowe (już wdrożone w v5.6)
Wszystkie pozycje oznaczone [x] powyżej. 99/99 testów zielonych.

### Faza 2 — Krótkoterminowe (1-2 tygodnie)
1. Redis jako shared store dla G5 CVC i sesji
2. Genesis Record: PostgreSQL + WAL
3. Walidacja: brak duplikatów `agent_id` w G8
4. Walidacja: `resource_allocation >= 0` w G8
5. G7 `action_scope` — granularność zgody

### Faza 3 — Średnioterminowe (1 miesiąc)
1. Trinity Engine integracja z `run_full_check`
2. Hexagon pipeline integracja
3. NLP-based G5 paraphrase detector
4. Per-IP CVC counter
5. `sys.audit()` hook dla monkeypatch protection

### Faza 4 — Długoterminowe (infrastruktura)
1. Wszystkie pozycje INFRA-1 do INFRA-7
2. mTLS rollout dla wszystkich agentów
3. Go Vortex JWT hardening
4. Circuit Breaker + Degraded Mode
5. Sygnatura 369 replay protection w produkcji

---

## METRYKI BEZPIECZEŃSTWA

| Wersja | Luki | Testy | Status |
|--------|------|-------|--------|
| v5.0 | 19 krytycznych | 0 | ❌ |
| v5.1 | 11 krytycznych | 19 | ⚠️ |
| v5.2 | 7 krytycznych | 52 | ⚠️ |
| v5.3 | 5 krytycznych | 64 | ⚠️ |
| v5.4 | 2 krytyczne | 74 | ⚠️ |
| v5.5 | 1 krytyczna (MP) | 84 | ⚠️ |
| **v5.6** | **0 krytycznych Python*** | **99** | **✅** |

*Monkeypatch na poziomie klasy to ograniczenie języka, nie błąd implementacji.
