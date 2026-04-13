# 🔻 Degraded Mode — ADRION 369 v5.2

> **Moduł:** `core/degraded_mode.py` | **Warstwa:** Rdzeń (Core)
> **Wersja:** v5.2 (2026-04-11)
> **Problem:** Brak zdefiniowanego zachowania gdy Trinity / Hexagon / Guardians są niedostępne

---

## 🎯 Problem (v5.1 i wcześniej)

Dokumentacja opisywała tylko ścieżkę happy path. Brak explicit degraded mode oznaczał:
- Niezdefiniowane zachowanie pod obciążeniem lub atakiem DoS
- Ryzyko cichego PROCEED gdy warstwa jest pominięta przez wyjątek
- Brak gradacji — albo pełne działanie, albo crash

---

## 🏗️ Macierz Trybów Zdegradowanych (v5.2)

```
                 TRINITY         HEXAGON        GUARDIANS
                    │               │               │
                    ▼               ▼               ▼
  DOWN?        DENY HIGH+      DENY HIGH+      DENY WSZYSTKO
               (LOW→manual)    (LOW→manual)    (żadnych wyjątków)
```

| Niedostępna warstwa | Severity LOW | Severity MEDIUM | Severity HIGH | Severity CRITICAL |
|---------------------|-------------|-----------------|---------------|-------------------|
| Trinity DOWN | MANUAL_REVIEW | DENY | DENY | DENY |
| Hexagon DOWN | MANUAL_REVIEW | DENY | DENY | DENY |
| Guardians DOWN | DENY | DENY | DENY | DENY |
| Trinity + Hexagon DOWN | DENY | DENY | DENY | DENY |
| Guardians + cokolwiek | DENY | DENY | DENY | DENY |

> **Zasada:** Guardians nigdy nie mogą być pominięte. Jeśli Guardians DOWN → system DENY dla wszystkiego.

---

## ⚙️ Implementacja

```python
from enum import Enum
from typing import Optional

class LayerStatus(Enum):
    HEALTHY   = "HEALTHY"
    DEGRADED  = "DEGRADED"   # Odpowiada, ale wolno / z błędami
    DOWN      = "DOWN"        # Nie odpowiada

class SystemMode(Enum):
    FULL_OPERATION  = "FULL_OPERATION"   # Wszystkie warstwy OK
    DEGRADED_L1     = "DEGRADED_L1"      # Trinity lub Hexagon DOWN
    DEGRADED_L2     = "DEGRADED_L2"      # Trinity I Hexagon DOWN
    GUARDIANS_ONLY  = "GUARDIANS_ONLY"   # Tylko Guardians działają
    EMERGENCY_DENY  = "EMERGENCY_DENY"   # Guardians DOWN → DENY wszystko
    MAINTENANCE     = "MAINTENANCE"      # Planowana przerwa


class DegradedModeController:
    """
    Kontroler trybu zdegradowanego.
    Określa dozwolone akcje na podstawie dostępności warstw.
    """

    def __init__(self):
        self.layer_status = {
            "trinity":   LayerStatus.HEALTHY,
            "hexagon":   LayerStatus.HEALTHY,
            "guardians": LayerStatus.HEALTHY,
            "ebdi":      LayerStatus.HEALTHY,
            "genesis":   LayerStatus.HEALTHY,
        }
        self._mode = SystemMode.FULL_OPERATION
        self._mode_since = time.time()

    def update_layer_status(self, layer: str, status: LayerStatus):
        """Aktualizuje status warstwy i przelicza tryb systemu"""
        old_status = self.layer_status.get(layer)
        self.layer_status[layer] = status

        if old_status != status:
            self._recalculate_mode()
            genesis_record.log_event({
                "type": "LAYER_STATUS_CHANGE",
                "layer": layer,
                "from": old_status.value if old_status else None,
                "to": status.value,
                "new_system_mode": self._mode.value
            })

    def _recalculate_mode(self):
        """Przelicza tryb systemu na podstawie aktualnych statusów warstw"""
        g_down    = self.layer_status["guardians"] == LayerStatus.DOWN
        t_down    = self.layer_status["trinity"]   == LayerStatus.DOWN
        h_down    = self.layer_status["hexagon"]   == LayerStatus.DOWN
        gen_down  = self.layer_status["genesis"]   == LayerStatus.DOWN

        if g_down or gen_down:
            # Guardians lub Genesis DOWN → najwyższy alert
            self._mode = SystemMode.EMERGENCY_DENY
        elif t_down and h_down:
            self._mode = SystemMode.DEGRADED_L2
        elif t_down or h_down:
            self._mode = SystemMode.DEGRADED_L1
        else:
            self._mode = SystemMode.FULL_OPERATION

        self._mode_since = time.time()

    def evaluate_request(self, request: dict, severity: str) -> dict:
        """
        Główna decyzja w trybie zdegradowanym.
        Wywołuje odpowiedni handler dla aktualnego trybu systemu.
        """
        handlers = {
            SystemMode.FULL_OPERATION:  self._handle_full,
            SystemMode.DEGRADED_L1:     self._handle_degraded_l1,
            SystemMode.DEGRADED_L2:     self._handle_degraded_l2,
            SystemMode.GUARDIANS_ONLY:  self._handle_guardians_only,
            SystemMode.EMERGENCY_DENY:  self._handle_emergency_deny,
            SystemMode.MAINTENANCE:     self._handle_emergency_deny,
        }
        handler = handlers.get(self._mode, self._handle_emergency_deny)
        return handler(request, severity)

    def _handle_full(self, request, severity) -> dict:
        """Normalna ścieżka — wszystkie warstwy OK"""
        return {"mode": "FULL_OPERATION", "proceed": True}

    def _handle_degraded_l1(self, request, severity) -> dict:
        """Trinity lub Hexagon DOWN"""
        if severity in ("HIGH", "CRITICAL"):
            return {
                "mode": "DEGRADED_L1",
                "proceed": False,
                "decision": "DENY",
                "reason": f"Layer(s) unavailable — {severity} actions blocked in degraded mode"
            }
        elif severity == "MEDIUM":
            return {
                "mode": "DEGRADED_L1",
                "proceed": False,
                "decision": "DENY",
                "reason": "MEDIUM actions blocked in degraded mode — too risky without full pipeline"
            }
        else:  # LOW
            return {
                "mode": "DEGRADED_L1",
                "proceed": False,
                "decision": "MANUAL_REVIEW",
                "reason": "LOW action queued for human review — system in degraded mode",
                "queue": "human_operator_queue"
            }

    def _handle_degraded_l2(self, request, severity) -> dict:
        """Trinity I Hexagon DOWN — tylko Guardians"""
        if severity == "LOW":
            # Tylko Guardians — wystarczy dla prostych LOW akcji
            return {
                "mode": "DEGRADED_L2",
                "proceed": True,
                "skip_layers": ["TRINITY", "HEXAGON"],
                "mandatory_layers": ["GUARDIANS"],
                "warning": "Operating in Guardians-only mode"
            }
        return {
            "mode": "DEGRADED_L2",
            "proceed": False,
            "decision": "DENY",
            "reason": "Only Guardians layer available — non-LOW actions blocked"
        }

    def _handle_guardians_only(self, request, severity) -> dict:
        return self._handle_degraded_l2(request, severity)

    def _handle_emergency_deny(self, request, severity) -> dict:
        """Guardians DOWN lub Genesis DOWN — DENY dla wszystkiego"""
        return {
            "mode": self._mode.value,
            "proceed": False,
            "decision": "DENY",
            "reason": "EMERGENCY: Guardians or Genesis Record unavailable — all actions blocked",
            "mode_since": self._mode_since,
            "escalate": "human_operator"
        }

    @property
    def current_mode(self) -> SystemMode:
        return self._mode

    def status_report(self) -> dict:
        return {
            "mode": self._mode.value,
            "mode_since": self._mode_since,
            "layers": {k: v.value for k, v in self.layer_status.items()},
            "all_healthy": self._mode == SystemMode.FULL_OPERATION
        }


# ── Watchdog — ciągłe monitorowanie warstw ──────────────────────────────────

class LayerWatchdog:
    """
    Monitoruje dostępność warstw i aktualizuje DegradedModeController.
    Uruchamiany jako osobny wątek.
    """

    HEALTH_ENDPOINTS = {
        "trinity":   "http://localhost:8003/health/trinity",
        "hexagon":   "http://localhost:8003/health/hexagon",
        "guardians": "http://localhost:8003/health/guardians",
        "ebdi":      "http://localhost:1740/health",
        "genesis":   "http://localhost:5432/health",
    }
    CHECK_INTERVAL = 10  # sekund

    def __init__(self, controller: DegradedModeController):
        self.controller = controller
        self._running = False

    def start(self):
        """Uruchom watchdog w tle"""
        import threading
        self._running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        while self._running:
            for layer, url in self.HEALTH_ENDPOINTS.items():
                status = self._check(url)
                self.controller.update_layer_status(layer, status)
            time.sleep(self.CHECK_INTERVAL)

    def _check(self, url: str) -> LayerStatus:
        import urllib.request
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    return LayerStatus.HEALTHY
                return LayerStatus.DEGRADED
        except Exception:
            return LayerStatus.DOWN
```

---

## 📊 Dashboard Trybów

```
ADRION 369 — System Status
══════════════════════════════════════════════════════
  TRINITY    [████████████] HEALTHY
  HEXAGON    [████████░░░░] DEGRADED   ← wolne odpowiedzi
  GUARDIANS  [████████████] HEALTHY
  EBDI       [████████████] HEALTHY
  GENESIS    [████████████] HEALTHY

  TRYB SYSTEMU:  ⚠ DEGRADED_L1
  OD:            2026-04-11 14:23:07 (12 min)
  AKCJE HIGH+:   ZABLOKOWANE
  AKCJE LOW:     MANUAL_REVIEW (kolejka: 3 oczekujące)
══════════════════════════════════════════════════════
```

---

## 📋 Changelog

| Wersja | Data | Zmiana |
|--------|------|--------|
| v5.2 | 2026-04-11 | Nowy moduł — DegradedModeController; LayerWatchdog; 5 trybów zdegradowanych; macierz decyzji severity vs. dostępność warstw |
