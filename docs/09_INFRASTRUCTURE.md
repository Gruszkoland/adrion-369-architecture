# Warstwa Infrastruktury — Fundament Techniczny

> **Moduly:** AI-Binder, Genesis Record, Watchdog, Database
> **Rola:** Niskopoziomowa komunikacja, nienaruszalny audit trail, monitoring agentow i persystencja danych.

---

## 1. AI-Binder — Magistrala IPC

**AI-Binder** to wewnetrzna magistrala komunikacyjna oparta na **zero-copy shared memory** (`mmap`). Umozliwia blyskawiczna wymiane danych miedzy agentami bez kopiowania buforow.

### Struktura wiadomosci

```
[Header 64B] [Payload Variable] [Checksum 32B]
```

| **Pole**       | **Rozmiar** | **Typ**  | **Opis**                                      |
| -------------- | ----------- | -------- | --------------------------------------------- |
| `sender_id`    | **16B**     | `bytes`  | Unikalny identyfikator nadawcy                |
| `receiver_id`  | **16B**     | `bytes`  | Unikalny identyfikator odbiorcy               |
| `message_type` | **4B**      | `uint32` | Typ wiadomosci (enum)                         |
| `payload_size` | **4B**      | `uint32` | Rozmiar payloadu w bajtach                    |
| `timestamp`    | **8B**      | `uint64` | Unix timestamp w nanosekundach                |
| `flags`        | **16B**     | `bytes`  | Flagi sterujace (priorytet, TTL, szyfrowanie) |

### Parametry wydajnosciowe

| **Metryka**                    | **Wartosc**          | **Uwagi**                       |
| ------------------------------ | -------------------- | ------------------------------- |
| **Opoznienie (latency)**       | **< 10 ms**          | Srednie opoznienie end-to-end   |
| **Przepustowosc (throughput)** | **> 10 000 msg/sec** | Na pojedynczym rdzeniu CPU      |
| **Kopiowanie danych**          | **Zero-copy**        | Wspoldzielona pamiec `mmap`     |
| **Rozmiar headera**            | **64 bajty**         | Staly, niezalezny od payloadu   |
| **Rozmiar checksum**           | **32 bajty**         | SHA-256 integralnosc wiadomosci |

### Typy wiadomosci

| **Kod** | **Typ**            | **Kierunek**               |
| ------- | ------------------ | -------------------------- |
| `0x01`  | **TASK_REQUEST**   | Agent -> Orkiestrator      |
| `0x02`  | **TASK_RESPONSE**  | Orkiestrator -> Agent      |
| `0x03`  | **HEARTBEAT**      | Agent -> Watchdog          |
| `0x04`  | **STATUS_UPDATE**  | Agent -> System            |
| `0x05`  | **EMERGENCY_STOP** | System -> Wszyscy agenci   |
| `0x06`  | **LAW_VIOLATION**  | Guardian -> Genesis Record |

---

## 2. Genesis Record — Nienaruszalny Log

**Genesis Record** to **blockchain-style** nienaruszalny dziennik audytu. Kazdy rekord jest powiazany z poprzednim poprzez hash, tworz ac lancuch integralnosci.

### Struktura rekordu

| **Pole**        | **Typ**       | **Opis**                                                 |
| --------------- | ------------- | -------------------------------------------------------- |
| `id`            | `UUID`        | Unikalny identyfikator rekordu                           |
| `timestamp`     | `TIMESTAMPTZ` | Czas zdarzenia z dokladnoscia do mikrosekund             |
| `event_type`    | `VARCHAR(50)` | Typ zdarzenia (np. `DECISION`, `VIOLATION`, `HEARTBEAT`) |
| `agent_id`      | `UUID`        | Identyfikator agenta, ktory wygenerowat zdarzenie        |
| `payload`       | `JSONB`       | Pelne dane zdarzenia w formacie JSON                     |
| `previous_hash` | `CHAR(64)`    | Hash SHA-256 **poprzedniego** rekordu                    |
| `hash`          | `CHAR(64)`    | Hash SHA-256 **biezacego** rekordu                       |

### Weryfikacja lancucha

```
1. Dla kazdego rekordu R[i]:
   a. Oblicz hash(R[i]) z pol: id + timestamp + event_type + agent_id + payload
   b. Porownaj z zapisanym R[i].hash
   c. Sprawdz czy R[i].previous_hash == R[i-1].hash

2. Jesli jakikolwiek krok zawiedzie:
   -> ALERT: "Genesis chain integrity violation at record {id}"
   -> Natychmiastowe powiadomienie administratora
```

### Indeksy i partycjonowanie

| **Indeks**               | **Kolumny**             | **Cel**                        |
| ------------------------ | ----------------------- | ------------------------------ |
| `idx_genesis_agent_ts`   | `(agent_id, timestamp)` | Szybkie zapytania per-agent    |
| `idx_genesis_event_type` | `(event_type)`          | Filtrowanie po typie zdarzenia |
| **Partycjonowanie**      | `BY RANGE (timestamp)`  | Automatyczne partycje dzienne  |

### Typy zdarzen

| **Typ**              | **Opis**                              | **Priorytet** |
| -------------------- | ------------------------------------- | ------------- |
| `DECISION`           | Decyzja systemu (APPROVE/DENY/REVIEW) | **NORMAL**    |
| `VIOLATION`          | Naruszenie prawa Guardian             | **HIGH**      |
| `CRITICAL_VIOLATION` | Naruszenie prawa CRITICAL (G7, G8)    | **CRITICAL**  |
| `AGENT_START`        | Uruchomienie agenta                   | **LOW**       |
| `AGENT_STOP`         | Zatrzymanie agenta                    | **LOW**       |
| `HEARTBEAT_MISS`     | Brak heartbeatu od agenta             | **HIGH**      |
| `CHAIN_BREAK`        | Naruszenie integralnosci lancucha     | **CRITICAL**  |

---

## 3. Watchdog — Monitor Procesow

**Watchdog** to komponent monitorujacy napisany w **Rust**, odpowiedzialny za nadzor nad wszystkimi agentami w czasie rzeczywistym.

### Parametry monitoringu

| **Parametr**           | **Wartosc**   | **Opis**                                        |
| ---------------------- | ------------- | ----------------------------------------------- |
| **Heartbeat interval** | **2 sekundy** | Czestotliwosc wysylania heartbeatu przez agenta |
| **Heartbeat timeout**  | **5 sekund**  | Czas po ktorym agent uznawany za martwy         |
| **Health check loop**  | **1 sekunda** | Czestotliwosc petli sprawdzajacej zdrowie       |

### Kryteria zdrowia agenta

| **Kryterium**    | **Prog**          | **Akcja przy przekroczeniu**  |
| ---------------- | ----------------- | ----------------------------- |
| **Alive**        | Agent odpowiada   | Restart jesli martwy          |
| **Heartbeat**    | Ostatni < 5s temu | Ostrzezenie -> restart        |
| **Pamiec (RAM)** | **< 80%** limitu  | Ostrzezenie -> log -> restart |
| **CPU**          | **< 95%** limitu  | Ostrzezenie -> log            |

### Procedura restartu (Crash Recovery)

```
1. Wykrycie awarii agenta
   |
2. Log zdarzenia do Genesis Record
   |
3. Powiadomienie systemu (AGENT_CRASH event)
   |
4. Backoff restart:
   |-- Proba 1: czekaj  1 sekunde -> restart
   |-- Proba 2: czekaj  5 sekund  -> restart
   |-- Proba 3: czekaj 15 sekund  -> restart
   |
5. Jesli 3 proby nieudane:
   -> ALERT do administratora
   -> Agent oznaczony jako FAILED
   -> Zadania przekierowane do innego agenta
```

### Graceful Shutdown

| **Krok** | **Sygnal**  | **Timeout**   | **Opis**                             |
| -------- | ----------- | ------------- | ------------------------------------ |
| **1**    | `SIGTERM`   | —             | Wyslanie sygnalu zakonczenia         |
| **2**    | Oczekiwanie | **30 sekund** | Agent konczy biezace zadania         |
| **3**    | `SIGKILL`   | —             | Wymuszenie zakonczenia jesli timeout |

---

## 4. Database — PostgreSQL 15+

**Warstwa persystencji** oparta na **PostgreSQL 15+** z rozszerzeniami JSONB dla elastycznego przechowywania danych agentow.

### Schemat tabel

#### Tabela: `genesis_log`

| **Kolumna**     | **Typ**       | **Ograniczenia**                             | **Opis**                  |
| --------------- | ------------- | -------------------------------------------- | ------------------------- |
| `id`            | `UUID`        | **PRIMARY KEY**, `DEFAULT gen_random_uuid()` | Unikalny ID rekordu       |
| `timestamp`     | `TIMESTAMPTZ` | **NOT NULL**, `DEFAULT NOW()`                | Czas zdarzenia            |
| `event_type`    | `VARCHAR(50)` | **NOT NULL**                                 | Typ zdarzenia             |
| `agent_id`      | `UUID`        | **NOT NULL**, `REFERENCES agents(id)`        | ID agenta                 |
| `payload`       | `JSONB`       | **NOT NULL**                                 | Dane zdarzenia            |
| `previous_hash` | `CHAR(64)`    | **NOT NULL**                                 | Hash poprzedniego rekordu |
| `hash`          | `CHAR(64)`    | **NOT NULL**, **UNIQUE**                     | Hash biezacego rekordu    |

#### Tabela: `agent_logs`

| **Kolumna**    | **Typ**       | **Ograniczenia**                      | **Opis**                            |
| -------------- | ------------- | ------------------------------------- | ----------------------------------- |
| `id`           | `BIGSERIAL`   | **PRIMARY KEY**                       | Auto-increment ID                   |
| `agent_id`     | `UUID`        | **NOT NULL**, `REFERENCES agents(id)` | ID agenta                           |
| `timestamp`    | `TIMESTAMPTZ` | **NOT NULL**                          | Czas logu                           |
| `level`        | `VARCHAR(10)` | **NOT NULL**                          | `DEBUG` / `INFO` / `WARN` / `ERROR` |
| `message`      | `TEXT`        | **NOT NULL**                          | Tresc logu                          |
| `genesis_hash` | `CHAR(64)`    | `REFERENCES genesis_log(hash)`        | **FK** do Genesis Record            |

#### Tabela: `agent_state`

| **Kolumna**       | **Typ**       | **Ograniczenia**                                  | **Opis**                                |
| ----------------- | ------------- | ------------------------------------------------- | --------------------------------------- |
| `agent_id`        | `UUID`        | **PRIMARY KEY**, `REFERENCES agents(id)`          | ID agenta                               |
| `pad_vector`      | `FLOAT[]`     | **NOT NULL**                                      | Wektor PAD (Pleasure-Arousal-Dominance) |
| `temperature`     | `FLOAT`       | **NOT NULL**, `CHECK (0.0 <= temperature <= 2.0)` | Temperatura decyzyjna agenta            |
| `emotional_state` | `VARCHAR(20)` | **NOT NULL**                                      | Stan emocjonalny (EBDI model)           |
| `last_updated`    | `TIMESTAMPTZ` | `DEFAULT NOW()`                                   | Ostatnia aktualizacja                   |

### Zasady bezpieczenstwa bazy danych

| **Regula**                 | **Opis**                                             |
| -------------------------- | ---------------------------------------------------- |
| **Parameterized SQL only** | Zawsze uzyj `?` placeholderow — **NIGDY** f-stringow |
| **Connection pooling**     | PgBouncer lub wbudowany pool (max 20 polaczen)       |
| **Graceful drain**         | `graceful_drain()` przed zamknieciem aplikacji       |
| **Backup**                 | Automatyczny `pg_dump` co 6 godzin                   |
| **Encryption at rest**     | Szyfrowanie dysku (LUKS / cloud-native)              |

---

> **Uwaga:** Warstwa infrastruktury wymaga **PostgreSQL 15+** z rozszerzeniem `pgcrypto` dla `gen_random_uuid()`. W srodowisku deweloperskim dopuszczalny jest **SQLite** jako fallback (patrz `arbitrage/database.py`).
