# :satellite: Warstwa Komunikacji --- Protokoly

> **Katalog:** `communication/` | **Warstwa:** Komunikacja
> **Rola:** Bezpieczna wymiana wiadomosci miedzy agentami i swiatem zewnetrznym

---

## :closed_lock_with_key: SAFE-MCP Protocol

> **Security-Aware Framework for Explained Multi-agent Communication Protocol**

**Cel:** Wymuszenie **mandatory reasoning** dla wszystkich wiadomosci

### Struktura Wiadomosci

| **Pole**                  | **Typ**  |      **Wymagane**      | **Opis**                                   |
| :------------------------ | :------- | :--------------------: | :----------------------------------------- |
| `type`                    | enum     |          TAK           | `REQUEST` / `RESPONSE` / `EVENT` / `ERROR` |
| `sender`                  | agent_id |          TAK           | ID nadawcy                                 |
| `receiver`                | agent_id |          TAK           | ID odbiorcy                                |
| `action`                  | string   |          TAK           | Nazwa akcji                                |
| `payload`                 | any      |          TAK           | Dane                                       |
| `reasoning`               | string   | **TAK (min 20 chars)** | Wyjasnienie --- **OBOWIAZKOWE**            |
| `risk_score`              | 0-100    |          TAK           | Ocena ryzyka                               |
| `alternatives_considered` | list     |       WARUNKOWO        | Wymagane gdy risk > 70                     |
| `timestamp`               | ISO8601  |          TAK           | Musi byc < 60s                             |

### Reguly Walidacji

```
1. reasoning MUST be present
2. reasoning MUST be >= 20 characters
3. if risk_score > 70 --> alternatives MUST be present
4. timestamp MUST be recent (< 60s old)
```

### Enforcement

- Wiadomosc **bez reasoning** jest **REJECTED**
- AI-Binder **blokuje** non-compliant messages
- Kazde naruszenie **logowane** do Genesis Record

---

## :envelope: Message Bus --- Magistrala Wiadomosci

**Cel:** Pub/Sub system dla dystrybucji zdarzen

### Topics

| **Topic**            | **Opis**                          |
| :------------------- | :-------------------------------- |
| `agent.{id}.status`  | Status agenta (active/idle/error) |
| `agent.{id}.emotion` | Stan emocjonalny (PAD vector)     |
| `system.alert`       | Alerty systemowe                  |
| `system.metric`      | Metryki wydajnosci                |
| `task.created`       | Nowe zadanie                      |
| `task.completed`     | Zakonczenie zadania               |
| `law.violation`      | Naruszenie prawa Guardian         |

### Mechanizm

| Operacja      | Opis                                                                                   |
| :------------ | :------------------------------------------------------------------------------------- |
| **Publish**   | `message_bus.publish(topic, data)`                                                     |
| **Subscribe** | `message_bus.subscribe(topic, callback)` --- wspiera **wildcards** (`agent.*.emotion`) |
| **Routing**   | Topic matching, parallel delivery, **fire-and-forget** (no ack)                        |

---

## :globe_with_meridians: External API

### REST Endpoints

| **Metoda** | **Endpoint**             | **Opis**                           | **Auth** |
| :--------- | :----------------------- | :--------------------------------- | :------: |
| `POST`     | `/v1/request`            | Submit new request                 |    No    |
| `GET`      | `/v1/request/{id}`       | Get status + full 369 report       |    No    |
| `POST`     | `/v1/agent/{id}/command` | Direct agent command               | **YES**  |
| `GET`      | `/v1/metrics`            | System metrics (Prometheus format) |    No    |

### WebSocket

| **Endpoint**      | **Opis**                                  |
| :---------------- | :---------------------------------------- |
| `WS /v1/realtime` | Real-time updates --- subscribe to topics |

### Przykladowy Response (GET /v1/request/{id})

```json
{
  "status": "completed",
  "trinity_score": 0.85,
  "hexagon_status": "complete",
  "guardian_compliance": 1.0,
  "final_decision": "APPROVE",
  "369_signature": "a7f3e9c2...e4c1:24.75",
  "processing_time_ms": 1250
}
```
