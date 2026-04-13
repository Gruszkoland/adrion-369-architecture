# 📜 Genesis Record — Hardening v5.2

> **Moduł:** `core/genesis_record.py` | **Warstwa:** Infrastruktura
> **Wersja:** v5.2 (2026-04-11)
> **Problem:** Genesis Record jako single point of failure — brak dostępu = ryzyko cichego PROCEED

---

## 🎯 Problem (v5.1 i wcześniej)

Genesis Record był wymagany przez G4 (Causality) i CVC — ale dokumentacja nie definiowała zachowania gdy jest **niedostępny lub uszkodzony**. System mógł:
- Milcząco pominąć logowanie i kontynuować → PROCEED bez audytu
- Wywołać wyjątek bez obsługi → niezdefiniowane zachowanie

**Reguła v5.2:** Brak dostępu do Genesis Record = **automatyczny DENY** dla akcji HIGH i CRITICAL.

---

## ⚙️ Architektura Odporności (v5.2)

```
                    ┌─────────────────────────────┐
                    │     GenesisRecord Facade     │
                    └──────────────┬──────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               ▼                   ▼                   ▼
        ┌────────────┐    ┌──────────────┐    ┌─────────────┐
        │  Primary   │    │   Replica    │    │  Emergency  │
        │  DB/Redis  │    │  (hot copy)  │    │  Local WAL  │
        └────────────┘    └──────────────┘    └─────────────┘
         Główny zapis      Failover auto.       Ostatnia deska
```

### Tryby dostępności

| Tryb | Genesis dostępny? | Zachowanie |
|------|-------------------|------------|
| `FULL` | Primary OK | Normalne działanie |
| `REPLICA` | Primary DOWN, Replica OK | Automatyczny failover — transparentny |
| `EMERGENCY` | Oba DOWN, WAL OK | Zapis lokalny — synchronizacja po powrocie |
| `UNAVAILABLE` | Wszystko DOWN | **DENY** dla HIGH/CRITICAL; ALLOW tylko LOW |

---

## 🐍 Implementacja

```python
import time
import json
import threading
from pathlib import Path
from enum import Enum

class GenesisAvailability(Enum):
    FULL        = "FULL"
    REPLICA     = "REPLICA"
    EMERGENCY   = "EMERGENCY"
    UNAVAILABLE = "UNAVAILABLE"

class GenesisRecord:
    """
    Odporny na awarie rejestr audytu ADRION 369.
    v5.2: SPOF protection — 3-poziomowy fallback + reguła DENY przy niedostępności.
    """

    SEVERITY_DENY_THRESHOLD = {"HIGH", "CRITICAL"}   # Te severity wymagają Genesis

    def __init__(self, primary_url: str, replica_url: str, wal_path: str):
        self.primary_url  = primary_url
        self.replica_url  = replica_url
        self.wal_path     = Path(wal_path)
        self._lock        = threading.Lock()
        self._availability = GenesisAvailability.FULL
        self._wal_buffer  = []

    # ── Publiczne API ────────────────────────────────────────────────────────

    def log_action(self, action: dict, severity: str = "MEDIUM") -> dict:
        """
        Główna metoda logowania. Zwraca wynik z informacją o dostępności.
        Jeśli Genesis niedostępny i severity HIGH/CRITICAL → zwraca DENY.
        """
        availability = self._check_availability()

        if availability == GenesisAvailability.UNAVAILABLE:
            if severity in self.SEVERITY_DENY_THRESHOLD:
                # [v5.2] KRYTYCZNA REGUŁA: brak Genesis = DENY dla HIGH/CRITICAL
                return {
                    "logged": False,
                    "genesis_decision": "DENY",
                    "reason": "Genesis Record unavailable — cannot guarantee audit trail for HIGH/CRITICAL action",
                    "availability": availability.value
                }
            else:
                # LOW severity — dozwolone bez logowania, ale zapamiętaj lokalnie
                self._buffer_to_wal(action, severity)
                return {
                    "logged": False,
                    "genesis_decision": "ALLOW_WITHOUT_LOG",
                    "reason": "Genesis unavailable — LOW action allowed, buffered to WAL",
                    "availability": availability.value
                }

        # Zapisz do dostępnego backendu
        record = self._build_record(action, severity)
        success = self._write(record, availability)

        if not success:
            # Zapis się nie powiódł mimo wykrytej dostępności — użyj WAL
            self._buffer_to_wal(action, severity)
            if severity in self.SEVERITY_DENY_THRESHOLD:
                return {
                    "logged": False,
                    "genesis_decision": "DENY",
                    "reason": "Genesis write failed — action blocked",
                    "availability": "WRITE_ERROR"
                }

        return {
            "logged": True,
            "genesis_decision": "PROCEED",
            "record_hash": record["hash"],
            "availability": availability.value
        }

    def get_cumulative_violations(self, session_id: str, window_hours: int = 24) -> int:
        """Zwraca skumulowane naruszenia sesji z ostatnich N godzin"""
        availability = self._check_availability()
        if availability == GenesisAvailability.UNAVAILABLE:
            # Bezpieczny domyślny: zakładamy najgorsze
            return 999
        return self._query_violations(session_id, window_hours)

    def verify_chain_integrity(self) -> dict:
        """Weryfikuje ciągłość łańcucha hashów"""
        try:
            broken_links = self._scan_chain()
            return {
                "intact": len(broken_links) == 0,
                "broken_links": broken_links,
                "checked_at": time.time()
            }
        except Exception as e:
            return {
                "intact": False,
                "error": str(e),
                "genesis_decision": "DENY"   # Nie możemy zaufać łańcuchowi
            }

    # ── Prywatne metody ──────────────────────────────────────────────────────

    def _check_availability(self) -> GenesisAvailability:
        """Sprawdza dostępność w kolejności: Primary → Replica → WAL → UNAVAILABLE"""
        if self._ping(self.primary_url):
            self._availability = GenesisAvailability.FULL
        elif self._ping(self.replica_url):
            self._availability = GenesisAvailability.REPLICA
        elif self.wal_path.exists():
            self._availability = GenesisAvailability.EMERGENCY
        else:
            self._availability = GenesisAvailability.UNAVAILABLE
        return self._availability

    def _build_record(self, action: dict, severity: str) -> dict:
        import hashlib
        timestamp = time.time()
        payload = json.dumps({"action": action, "severity": severity, "ts": timestamp}, sort_keys=True)
        record_hash = hashlib.sha3_256(payload.encode()).hexdigest()
        return {
            "timestamp": timestamp,
            "severity": severity,
            "action": action,
            "hash": record_hash,
            "prev_hash": self._get_last_hash()  # Łańcuch
        }

    def _buffer_to_wal(self, action: dict, severity: str):
        """Write-Ahead Log — lokalny bufor gdy Primary i Replica niedostępne"""
        with self._lock:
            entry = {"ts": time.time(), "action": action, "severity": severity}
            self._wal_buffer.append(entry)
            # Flush do pliku
            with open(self.wal_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def sync_wal_to_primary(self):
        """Synchronizuje lokalny WAL z Primary po przywróceniu dostępu"""
        if not self.wal_path.exists():
            return
        with open(self.wal_path) as f:
            entries = [json.loads(line) for line in f if line.strip()]
        synced = 0
        for entry in entries:
            result = self._write(entry, GenesisAvailability.FULL)
            if result:
                synced += 1
        if synced == len(entries):
            self.wal_path.unlink()  # Usuń WAL po pełnej synchronizacji
        return {"synced": synced, "total": len(entries)}

    def _ping(self, url: str) -> bool:
        """Sprawdza czy endpoint odpowiada"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def _write(self, record: dict, availability: GenesisAvailability) -> bool:
        target = self.primary_url if availability == GenesisAvailability.FULL else self.replica_url
        try:
            import urllib.request
            data = json.dumps(record).encode()
            req = urllib.request.Request(f"{target}/records", data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status in (200, 201)
        except Exception:
            return False

    def _get_last_hash(self) -> str:
        return "genesis_root"  # Placeholder — implementacja zależna od DB

    def _query_violations(self, session_id: str, window_hours: int) -> int:
        return 0  # Placeholder — implementacja zależna od DB

    def _scan_chain(self) -> list:
        return []  # Placeholder — implementacja zależna od DB
```

---

## 🔧 Konfiguracja (config/genesis_config.yaml)

```yaml
genesis_record:
  primary_url: "http://genesis-primary:5432"
  replica_url: "http://genesis-replica:5432"
  wal_path: "/var/adrion/genesis_wal.jsonl"

  availability_rules:
    # Dla jakich severity wymagamy Genesis
    require_genesis_for: ["HIGH", "CRITICAL"]
    # LOW może działać bez Genesis (z bufferowaniem do WAL)
    allow_without_genesis: ["LOW", "MEDIUM"]

  chain_integrity:
    verify_on_startup: true
    verify_interval_minutes: 60
    broken_chain_action: DENY_ALL   # Jeśli łańcuch jest przerwany → blokuj wszystko

  wal_sync:
    auto_sync_on_primary_restore: true
    sync_interval_seconds: 300
```

---

## 📋 Changelog

| Wersja | Data | Zmiana |
|--------|------|--------|
| v5.1 | 2026-04-11 | Genesis używany przez CVC i G4 |
| v5.2 | 2026-04-11 | SPOF protection: 3-poziomowy fallback (Primary→Replica→WAL→UNAVAILABLE); reguła DENY przy niedostępności dla HIGH/CRITICAL; WAL sync |
