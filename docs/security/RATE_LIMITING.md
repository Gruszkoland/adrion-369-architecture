# 🚦 Rate Limiting — ADRION 369 v5.2

> **Moduł:** `core/rate_limiter.py` | **Warstwa:** Wejście systemu (API Gateway)
> **Wersja:** v5.2 (2026-04-11)
> **Problem:** Brak throttlingu → ataki DoS, masowe wymuszanie Loop Exhaustion, szum CVC

---

## 🎯 Problem (v5.1 i wcześniej)

System miał CVC (Cumulative Violation Counter) ale **brak limitowania na wejściu**. Atakujący mógł:
- Zalać system tysiącami żądań jednocześnie → degradacja Loop Exhaustion na dużą skalę
- Generować szum CVC przez masowe LOW-severity żądania → reset lub przepełnienie licznika
- Przeprowadzić atak DoS celując w najwolniejszy komponent (np. Hexagon z 3 cyklami)

---

## 🏗️ Wielopoziomowy Rate Limiter (v5.2)

```
Żądanie wchodzące
      │
      ▼
┌─────────────────┐
│  L1: Global     │  Max N req/s dla całego systemu
│  Rate Limit     │  Ochrona przed DoS
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  L2: Per-IP     │  Max M req/min per adres IP
│  Rate Limit     │  Ochrona przed pojedynczym atakującym
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  L3: Per-User   │  Max K req/min per uwierzytelniony user
│  Rate Limit     │  Dodatkowa ochrona per tożsamość
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  L4: Severity   │  HIGH/CRITICAL: max 5 req/min per user
│  Rate Limit     │  Kosztowne żądania mają własny limit
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  L5: Anomaly    │  Detekcja wzorców ataku (burst, scan)
│  Detector       │  Blokuje podejrzane sesje
└────────┬────────┘
         │
         ▼
    System ADRION 369
```

---

## 🐍 Implementacja

```python
import time
import threading
from collections import defaultdict, deque
from typing import Optional

class TokenBucket:
    """
    Klasyczny token bucket — pozwala na bursts ale limituje średnią.
    Thread-safe.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity:    max tokenów (burst size)
        refill_rate: tokenów/sekunda
        """
        self.capacity     = capacity
        self.refill_rate  = refill_rate
        self.tokens       = float(capacity)
        self.last_refill  = time.time()
        self._lock        = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now


class SlidingWindowCounter:
    """Licznik w oknie czasowym — dla limitów per IP/user"""

    def __init__(self, window_seconds: int, max_requests: int):
        self.window   = window_seconds
        self.max_req  = max_requests
        self.requests = deque()
        self._lock    = threading.Lock()

    def is_allowed(self) -> bool:
        with self._lock:
            now = time.time()
            # Usuń stare wpisy poza oknem
            while self.requests and self.requests[0] < now - self.window:
                self.requests.popleft()
            if len(self.requests) < self.max_req:
                self.requests.append(now)
                return True
            return False


class AdrionRateLimiter:
    """
    Wielopoziomowy rate limiter dla systemu ADRION 369.
    """

    # ── Limity globalne ──────────────────────────────────────────────────────
    GLOBAL_LIMIT = TokenBucket(capacity=500, refill_rate=100)  # 100 req/s, burst 500

    # ── Limity per severity (kosztowne żądania) ──────────────────────────────
    SEVERITY_LIMITS = {
        "LOW":      {"window": 60, "max": 60},    # 60/min
        "MEDIUM":   {"window": 60, "max": 30},    # 30/min
        "HIGH":     {"window": 60, "max": 10},    # 10/min
        "CRITICAL": {"window": 60, "max": 5},     # 5/min
    }

    def __init__(self):
        self._per_ip   = defaultdict(lambda: SlidingWindowCounter(60, 30))   # 30/min per IP
        self._per_user = defaultdict(lambda: SlidingWindowCounter(60, 50))   # 50/min per user
        self._per_user_severity = defaultdict(dict)
        self._anomaly  = AnomalyDetector()
        self._lock     = threading.Lock()

    def check(self, request: dict) -> dict:
        """
        Główna metoda sprawdzająca wszystkie poziomy.
        Zwraca {allowed: bool, reason: str, retry_after: int}
        """
        ip       = request.get("client_ip", "unknown")
        user_id  = request.get("user_id",   "anonymous")
        severity = request.get("severity",  "LOW")

        # L1: Global
        if not self.GLOBAL_LIMIT.consume():
            return self._deny("GLOBAL_RATE_LIMIT", retry_after=1)

        # L2: Per IP
        with self._lock:
            ip_counter = self._per_ip[ip]
        if not ip_counter.is_allowed():
            return self._deny(f"IP_RATE_LIMIT ({ip})", retry_after=30)

        # L3: Per User
        with self._lock:
            user_counter = self._per_user[user_id]
        if not user_counter.is_allowed():
            return self._deny(f"USER_RATE_LIMIT ({user_id})", retry_after=30)

        # L4: Per Severity
        severity_result = self._check_severity(user_id, severity)
        if not severity_result["allowed"]:
            return self._deny(
                f"SEVERITY_RATE_LIMIT ({severity})",
                retry_after=severity_result["retry_after"]
            )

        # L5: Anomaly detection
        anomaly = self._anomaly.check(ip, user_id, severity)
        if anomaly["detected"]:
            genesis_record.log_event({
                "type": "RATE_LIMIT_ANOMALY",
                "ip": ip,
                "user": user_id,
                "pattern": anomaly["pattern"]
            })
            return self._deny(f"ANOMALY_DETECTED: {anomaly['pattern']}", retry_after=300)

        return {"allowed": True, "remaining_global": self.GLOBAL_LIMIT.tokens}

    def _check_severity(self, user_id: str, severity: str) -> dict:
        cfg = self.SEVERITY_LIMITS.get(severity, self.SEVERITY_LIMITS["LOW"])
        with self._lock:
            if severity not in self._per_user_severity[user_id]:
                self._per_user_severity[user_id][severity] = SlidingWindowCounter(
                    cfg["window"], cfg["max"]
                )
            counter = self._per_user_severity[user_id][severity]

        if counter.is_allowed():
            return {"allowed": True}
        return {
            "allowed": False,
            "retry_after": cfg["window"]
        }

    def _deny(self, reason: str, retry_after: int = 60) -> dict:
        return {
            "allowed": False,
            "reason": reason,
            "retry_after": retry_after,
            "decision": "RATE_LIMITED"
        }


class AnomalyDetector:
    """
    Wykrywa wzorce ataku: burst, scan, loop exhaustion farming.
    """

    def __init__(self):
        self._patterns = defaultdict(deque)

    def check(self, ip: str, user_id: str, severity: str) -> dict:
        key = f"{ip}:{user_id}"
        now = time.time()
        self._patterns[key].append({"ts": now, "severity": severity})

        # Zachowaj tylko ostatnie 2 minuty
        while self._patterns[key] and self._patterns[key][0]["ts"] < now - 120:
            self._patterns[key].popleft()

        history = list(self._patterns[key])

        # Wzorzec 1: Burst — > 20 żądań w 5 sekund
        recent_5s = [r for r in history if r["ts"] > now - 5]
        if len(recent_5s) > 20:
            return {"detected": True, "pattern": "BURST_ATTACK"}

        # Wzorzec 2: HIGH/CRITICAL farming — > 8 HIGH+ w 2 minuty
        high_count = sum(1 for r in history if r["severity"] in ("HIGH", "CRITICAL"))
        if high_count > 8:
            return {"detected": True, "pattern": "HIGH_SEVERITY_FARMING"}

        # Wzorzec 3: Monotoniczne żądania — > 50 identycznych severity pod rząd
        if len(history) > 50:
            severities = [r["severity"] for r in history[-50:]]
            if len(set(severities)) == 1:
                return {"detected": True, "pattern": "MONOTONIC_SCAN"}

        return {"detected": False}
```

---

## 🔧 Konfiguracja (config/rate_limit_config.yaml)

```yaml
rate_limiter:
  global:
    capacity: 500          # burst max
    refill_rate: 100       # req/s

  per_ip:
    window_seconds: 60
    max_requests: 30

  per_user:
    window_seconds: 60
    max_requests: 50

  per_severity:
    LOW:      { window: 60, max: 60 }
    MEDIUM:   { window: 60, max: 30 }
    HIGH:     { window: 60, max: 10 }
    CRITICAL: { window: 60, max: 5  }

  anomaly_detection:
    burst_threshold: 20      # req w 5s
    high_severity_threshold: 8   # HIGH+ req w 2min
    monotonic_threshold: 50  # identycznych severity pod rząd

  responses:
    include_retry_after: true
    log_to_genesis: true
```

---

## 📋 Changelog

| Wersja | Data | Zmiana |
|--------|------|--------|
| v5.2 | 2026-04-11 | Nowy moduł — 5-poziomowy Rate Limiter (Global/IP/User/Severity/Anomaly); TokenBucket + SlidingWindow; AnomalyDetector (burst/farming/scan) |
