# 🤝 Agent Authentication — ADRION 369 v5.2

> **Moduł:** `core/agent_auth.py` | **Warstwa:** Intelligence / Communication
> **Wersja:** v5.2 (2026-04-11)
> **Problem:** Brak wzajemnej weryfikacji tożsamości agentów — podszywanie się pod Sentinela

---

## 🎯 Problem (v5.1 i wcześniej)

Sześć agentów (Librarian, SAP, Auditor, Sentinel, Architect, Healer) komunikowało się przez Message Bus bez autentykacji. Agent kompromitowany lub zewnętrzny mógł:
- Podszywać się pod **Sentinela** i wysyłać fałszywe sygnały bezpieczeństwa
- Podszywać się pod **Auditora** i zatwierdzać nielegalne akcje
- Wstrzykiwać wiadomości do Message Bus z pominięciem weryfikacji

---

## 🏗️ Architektura Autentykacji (v5.2)

### Dwie warstwy ochrony

```
┌────────────────────────────────────────────────────────────┐
│                    Message Bus                             │
│                                                            │
│  Agent A ──[HMAC podpis]──► Weryfikacja ──► Agent B       │
│              │                                             │
│         mTLS channel                                       │
│         (transport)                                        │
└────────────────────────────────────────────────────────────┘

Warstwa 1: mTLS — szyfrowanie i autentykacja transportu (TLS mutual)
Warstwa 2: HMAC-SHA256 — podpis każdej wiadomości (content integrity)
```

---

## 🐍 Implementacja

### Rejestr Agentów

```python
import hmac
import hashlib
import time
import json
import uuid
from typing import Optional

# Każdy agent ma unikalny klucz HMAC (zarządzany przez Sentinel / Key Manager)
# Klucze są rotowane co 24h automatycznie

AGENT_REGISTRY = {
    "Librarian": {
        "id": "agent-librarian-001",
        "permissions": ["READ", "INVENTORY"],
        "trusted_by": ["Orchestrator", "Architect"]
    },
    "SAP": {
        "id": "agent-sap-001",
        "permissions": ["EMPATHY", "USER_ANALYSIS"],
        "trusted_by": ["Orchestrator"]
    },
    "Auditor": {
        "id": "agent-auditor-001",
        "permissions": ["READ", "VALIDATE", "DENY"],
        "trusted_by": ["Orchestrator", "Sentinel"]
    },
    "Sentinel": {
        "id": "agent-sentinel-001",
        "permissions": ["READ", "WRITE", "DENY", "ALERT", "KEY_ROTATION"],
        "trusted_by": ["Orchestrator"],
        # Sentinel ma najszersze uprawnienia → priorytetowa ochrona tożsamości
        "high_security": True
    },
    "Architect": {
        "id": "agent-architect-001",
        "permissions": ["READ", "DESIGN", "PROCESS"],
        "trusted_by": ["Orchestrator"]
    },
    "Healer": {
        "id": "agent-healer-001",
        "permissions": ["READ", "HEAL", "STATE_MODIFY"],
        "trusted_by": ["Orchestrator", "Sentinel"],
        # Healer może modyfikować stan — wymaga dodatkowej weryfikacji
        "double_sign_required": True
    },
}


class AgentMessage:
    """Podpisana wiadomość między agentami"""

    def __init__(self, sender: str, recipient: str, payload: dict,
                 message_type: str = "ACTION"):
        self.id          = str(uuid.uuid4())
        self.sender      = sender
        self.recipient   = recipient
        self.payload     = payload
        self.message_type = message_type
        self.timestamp   = time.time()
        self.signature   = None
        self.nonce       = str(uuid.uuid4())

    def sign(self, hmac_key: bytes) -> "AgentMessage":
        """Podpisuje wiadomość kluczem HMAC agenta-nadawcy"""
        body = self._canonical_body()
        self.signature = hmac.new(hmac_key, body.encode(), hashlib.sha256).hexdigest()
        return self

    def verify(self, hmac_key: bytes) -> bool:
        """Weryfikuje podpis HMAC"""
        if not self.signature:
            return False
        body = self._canonical_body()
        expected = hmac.new(hmac_key, body.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, self.signature)

    def _canonical_body(self) -> str:
        """Kanoniczne ciało wiadomości (deterministyczne)"""
        return json.dumps({
            "id":           self.id,
            "sender":       self.sender,
            "recipient":    self.recipient,
            "message_type": self.message_type,
            "timestamp":    self.timestamp,
            "nonce":        self.nonce,
            "payload":      self.payload
        }, sort_keys=True)


class AgentAuthMiddleware:
    """
    Middleware autentykacji dla Message Bus.
    Każda wiadomość musi przejść weryfikację przed dostarczeniem.
    """

    def __init__(self, key_manager):
        self.key_manager  = key_manager
        self.nonce_cache  = set()     # Ochrona przed replay attack
        self.nonce_ttl    = 300       # 5 minut

    def authenticate(self, message: AgentMessage) -> dict:
        """Pełna weryfikacja wiadomości inter-agent"""

        # 1. Czy nadawca istnieje w rejestrze?
        if message.sender not in AGENT_REGISTRY:
            return self._reject(f"Unknown sender: {message.sender}")

        # 2. Czy nadawca ma uprawnienia do tego typu wiadomości?
        agent_info = AGENT_REGISTRY[message.sender]
        if not self._has_permission(agent_info, message.message_type):
            return self._reject(
                f"{message.sender} lacks permission for {message.message_type}"
            )

        # 3. Weryfikacja HMAC
        sender_key = self.key_manager.get_key(message.sender)
        if not message.verify(sender_key):
            genesis_record.log_event({
                "type": "AGENT_AUTH_FAILURE",
                "sender": message.sender,
                "message_id": message.id,
                "severity": "CRITICAL"
            })
            return self._reject(f"HMAC verification failed — possible impersonation of {message.sender}")

        # 4. Replay protection (nonce)
        if message.nonce in self.nonce_cache:
            return self._reject("Replay attack detected — nonce already used")
        self.nonce_cache.add(message.nonce)

        # 5. Timestamp freshness (wiadomość nie starsza niż 30s)
        age = time.time() - message.timestamp
        if age > 30:
            return self._reject(f"Message too old ({age:.1f}s) — possible replay")

        # 6. Podwójny podpis dla agentów wysokiego ryzyka (np. Healer)
        if agent_info.get("double_sign_required"):
            sentinel_sig = message.payload.get("sentinel_countersign")
            if not self._verify_sentinel_countersign(message, sentinel_sig):
                return self._reject(f"{message.sender} requires Sentinel countersignature")

        return {"authenticated": True, "sender": message.sender, "message_id": message.id}

    def _has_permission(self, agent_info: dict, message_type: str) -> bool:
        return message_type in agent_info.get("permissions", [])

    def _verify_sentinel_countersign(self, message: AgentMessage, sig: Optional[str]) -> bool:
        if not sig:
            return False
        sentinel_key = self.key_manager.get_key("Sentinel")
        expected = hmac.new(sentinel_key, message.id.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig)

    def _reject(self, reason: str) -> dict:
        return {"authenticated": False, "reason": reason}


class KeyManager:
    """
    Zarządzanie kluczami HMAC agentów.
    Klucze rotowane co 24h przez agenta Sentinel.
    """

    def __init__(self, key_store_url: str):
        self.key_store_url = key_store_url
        self._cache = {}
        self._cache_ts = {}
        self.KEY_TTL = 86400  # 24h

    def get_key(self, agent_name: str) -> bytes:
        """Pobiera aktualny klucz HMAC dla agenta"""
        # Użyj cache jeśli klucz świeży
        if agent_name in self._cache:
            age = time.time() - self._cache_ts.get(agent_name, 0)
            if age < self.KEY_TTL:
                return self._cache[agent_name]

        # Pobierz z Key Store
        key = self._fetch_key(agent_name)
        self._cache[agent_name] = key
        self._cache_ts[agent_name] = time.time()
        return key

    def rotate_all_keys(self):
        """Rotacja wszystkich kluczy — wywoływana przez Sentinela co 24h"""
        for agent_name in AGENT_REGISTRY:
            self._generate_new_key(agent_name)
        self._cache.clear()
        genesis_record.log_event({"type": "KEY_ROTATION", "agents": list(AGENT_REGISTRY.keys())})

    def _fetch_key(self, agent_name: str) -> bytes:
        """Pobiera klucz z bezpiecznego Key Store"""
        # Implementacja: Vault, AWS KMS, lub lokalny zaszyfrowany store
        raise NotImplementedError("Implement with your Key Store backend")

    def _generate_new_key(self, agent_name: str) -> bytes:
        import os
        new_key = os.urandom(32)  # 256-bit key
        self._store_key(agent_name, new_key)
        return new_key

    def _store_key(self, agent_name: str, key: bytes):
        raise NotImplementedError("Implement with your Key Store backend")
```

---

## 🔧 Konfiguracja mTLS (config/agent_mtls.yaml)

```yaml
agent_mtls:
  enabled: true
  ca_cert: "/etc/adrion/certs/ca.pem"
  verify_client_cert: true      # Mutual TLS — obydwie strony muszą mieć certyfikat

  agents:
    Sentinel:
      cert: "/etc/adrion/certs/sentinel.crt"
      key:  "/etc/adrion/certs/sentinel.key"
      # Sentinel ma osobny, silniejszy certyfikat (4096-bit RSA)
      key_size: 4096

    Healer:
      cert: "/etc/adrion/certs/healer.crt"
      key:  "/etc/adrion/certs/healer.key"
      double_sign_required: true

    # ... pozostałe agenty

  cert_rotation:
    interval_days: 30
    alert_before_expiry_days: 7

key_manager:
  backend: "vault"              # HashiCorp Vault | AWS KMS | local_encrypted
  vault_url: "http://vault:8200"
  hmac_key_rotation_hours: 24
```

---

## 📋 Changelog

| Wersja | Data | Zmiana |
|--------|------|--------|
| v5.2 | 2026-04-11 | Nowy moduł — AgentAuthMiddleware (HMAC-SHA256); KeyManager z rotacją 24h; mTLS konfiguracja; podwójny podpis dla Healera; replay protection |
