# ⚡ Circuit Breaker — ADRION 369 v5.2

> **Moduł:** `core/circuit_breaker.py` | **Warstwa:** Infrastruktura
> **Wersja:** v5.2 (2026-04-11)
> **Problem:** Brak limitu czasowego na zewnętrznych serwisach → system może utknąć w oczekiwaniu

---

## 🎯 Cel

Circuit Breaker automatycznie przełącza w tryb bezpieczny (`OPEN`) po N nieudanych próbach komunikacji z serwisem zewnętrznym. Zapobiega kaskadowym awariom i nieskończonemu oczekiwaniu.

---

## ⚙️ Stany Circuit Breaker

```
  ┌─────────┐   N failures    ┌──────────┐
  │ CLOSED  │ ──────────────► │  OPEN    │
  │(normal) │                 │(blocked) │
  └─────────┘                 └──────────┘
       ▲                           │
       │    success                │ timeout_reset
       │                           ▼
  ┌────────────┐             ┌──────────────┐
  │   CLOSED   │ ◄────────── │  HALF_OPEN   │
  │            │             │ (1 probe ok) │
  └────────────┘             └──────────────┘
```

| Stan | Znaczenie | Akcja |
|------|-----------|-------|
| `CLOSED` | Normalne działanie | Przepuszcza żądania |
| `OPEN` | Serwis uznany za niesprawny | Natychmiastowy fallback (DENY dla CRITICAL) |
| `HALF_OPEN` | Test po timeout | 1 próbne żądanie — sukces→CLOSED, błąd→OPEN |

---

## 🐍 Implementacja

```python
import time
import threading
from enum import Enum
from typing import Callable, Any

class CBState(Enum):
    CLOSED    = "CLOSED"
    OPEN      = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    """
    Circuit Breaker dla zewnętrznych serwisów ADRION 369.
    Chroni: MCP Layer, SAFE-MCP (PLC), Go Vortex, Genesis Record.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,       # N błędów → OPEN
        timeout_seconds: float = 30.0,    # Czas w OPEN przed HALF_OPEN
        request_timeout: float = 5.0,     # Max czas oczekiwania na odpowiedź
        fallback_action: str = "DENY",    # Co robić gdy OPEN: DENY | DEGRADE
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.request_timeout = request_timeout
        self.fallback_action = fallback_action

        self.state = CBState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Wykonuje wywołanie przez circuit breaker"""
        with self._lock:
            if self.state == CBState.OPEN:
                if self._should_attempt_reset():
                    self.state = CBState.HALF_OPEN
                else:
                    return self._fallback(reason=f"Circuit OPEN for {self.name}")

        try:
            # Wykonaj z timeoutem
            result = self._call_with_timeout(func, args, kwargs)
            self._on_success()
            return result

        except TimeoutError:
            self._on_failure("timeout")
            return self._fallback(reason=f"Timeout ({self.request_timeout}s) — {self.name}")

        except Exception as e:
            self._on_failure(str(e))
            return self._fallback(reason=f"Error in {self.name}: {e}")

    def _call_with_timeout(self, func, args, kwargs):
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=self.request_timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError()

    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            self.state = CBState.CLOSED

    def _on_failure(self, reason: str):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CBState.OPEN
                genesis_record.log_event({
                    "type": "CIRCUIT_BREAKER_OPEN",
                    "service": self.name,
                    "reason": reason,
                    "failures": self.failure_count
                })

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.timeout_seconds

    def _fallback(self, reason: str) -> dict:
        """Bezpieczny fallback gdy serwis niedostępny"""
        if self.fallback_action == "DENY":
            return {
                "decision": "DENY",
                "reason": f"CIRCUIT_BREAKER: {reason}",
                "service": self.name,
                "state": self.state.value
            }
        elif self.fallback_action == "DEGRADE":
            # Tryb zdegradowany — ograniczona funkcjonalność
            return {
                "decision": "DEGRADED",
                "reason": f"CIRCUIT_BREAKER: {reason}",
                "service": self.name,
                "available_layers": ["GUARDIANS"]  # Tylko Guardians działają offline
            }

    @property
    def is_healthy(self) -> bool:
        return self.state == CBState.CLOSED

    def status(self) -> dict:
        return {
            "service": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time
        }


# ── Globalne instancje Circuit Breaker dla każdego serwisu ──────────────────

CIRCUIT_BREAKERS = {
    "mcp_router":    CircuitBreaker("mcp_router",    failure_threshold=3, request_timeout=5.0,  fallback_action="DENY"),
    "mcp_vortex":    CircuitBreaker("mcp_vortex",    failure_threshold=3, request_timeout=3.0,  fallback_action="DEGRADE"),
    "mcp_guardian":  CircuitBreaker("mcp_guardian",  failure_threshold=2, request_timeout=5.0,  fallback_action="DENY"),
    "mcp_genesis":   CircuitBreaker("mcp_genesis",   failure_threshold=2, request_timeout=5.0,  fallback_action="DENY"),
    "safe_mcp_plc":  CircuitBreaker("safe_mcp_plc",  failure_threshold=2, request_timeout=10.0, fallback_action="DENY"),
    "go_vortex":     CircuitBreaker("go_vortex",     failure_threshold=3, request_timeout=3.0,  fallback_action="DEGRADE"),
}

def get_circuit_breaker(service: str) -> CircuitBreaker:
    if service not in CIRCUIT_BREAKERS:
        raise ValueError(f"Unknown service: {service}. Register it in CIRCUIT_BREAKERS.")
    return CIRCUIT_BREAKERS[service]

def system_health_report() -> dict:
    """Raport zdrowia wszystkich serwisów"""
    return {
        "timestamp": time.time(),
        "services": {name: cb.status() for name, cb in CIRCUIT_BREAKERS.items()},
        "all_healthy": all(cb.is_healthy for cb in CIRCUIT_BREAKERS.values())
    }
```

---

## 🔧 Konfiguracja (config/circuit_breaker_config.yaml)

```yaml
circuit_breakers:
  mcp_guardian:
    failure_threshold: 2       # Niski próg — Guardians są krytyczne
    timeout_seconds: 30
    request_timeout: 5.0
    fallback_action: DENY      # Bez Guardians → zawsze DENY

  mcp_genesis:
    failure_threshold: 2
    timeout_seconds: 30
    request_timeout: 5.0
    fallback_action: DENY      # Bez Genesis Record → brak audytu → DENY

  go_vortex:
    failure_threshold: 3
    timeout_seconds: 60
    request_timeout: 3.0
    fallback_action: DEGRADE   # EBDI niedostępne → tryb zdegradowany (statyczny PAD)

  safe_mcp_plc:
    failure_threshold: 2
    timeout_seconds: 120       # PLC może mieć wolniejszy restart
    request_timeout: 10.0
    fallback_action: DENY      # Brak połączenia z PLC → blokuj komendy fizyczne
```

---

## 📋 Changelog

| Wersja | Data | Zmiana |
|--------|------|--------|
| v5.2 | 2026-04-11 | Nowy moduł — Circuit Breaker dla wszystkich serwisów zewnętrznych |
