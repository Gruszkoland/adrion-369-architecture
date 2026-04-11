# :arrows_counterclockwise: Przeplywy Danych i Diagramy Architektoniczne

> **Rola:** Wizualizacja kompletnych przeplywow w systemie ADRION 369

---

## :one: Complete Request Flow

```
                        User Request
                             |
                             v
                    +------------------+
                    |    System 369    |
                    |   Orkiestrator   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
        +---------+   +-----------+   +----------+
        |MATERIAL |   |INTELLECTUAL|  |ESSENTIAL |
        | Physical|   |  Truth    |   |  Unity   |
        | Energy  |   |  Beauty   |   | Harmony  |
        | Info    |   | Goodness  |   | Purpose  |
        +----+----+   +-----+-----+  +----+-----+
              |              |              |
              +--------------+--------------+
                             |
                   Trinity Score >= 0.7?
                      |            |
                     YES          NO --> DENY
                      |
                      v
              +------------------+
              |     HEXAGON      |
              | 1. Inventory     |
              | 2. Empathy       |
              | 3. Process       |
              | 4. Debate        | <-- Skeptics Panel
              | 5. Healing       | <-- if dissonance
              | 6. Action        | --> Genesis Record
              +--------+---------+
                       |
                  Complete?
                   |       |
                  YES     NO --> return status
                   |
                   v
              +------------------+
              |   GUARDIANS      |
              | Matter (G1-G3)   |
              | Light  (G4-G6)   |
              | Essence(G7-G9)   |
              +--------+---------+
                       |
                   Violations?
                |      |      |
               0     1-2    3+ --> DENY
               |      |
             ALLOW  REVIEW
                       |
                       v
              +------------------+
              | 369 Signature    |
              | SHA-256 + Check  |
              +--------+---------+
                       |
                       v
                  User Response
```

---

## :two: Layer Dependency Diagram

```
+-----------------------------------------------+
|           Interface Layer                      | <-- User
|    (Dashboard, CLI, SDK)                       |
+----------------------+------------------------+
                       |
+----------------------v------------------------+
|           Integration Layer                    |
|    (System 369, Signature, Validator)          |
+------+---------------+---------------+--------+
       |               |               |
+------v------+ +------v------+ +------v--------+
|   Trinity   | |  Hexagon    | |  Guardians    |
| (3 Perspect)| | (6 Modes)   | | (9 Laws)      |
+------+------+ +------+------+ +------+--------+
       |               |               |
+------v---------------v---------------v--------+
|           Infrastructure Layer                 |
|    (AI-Binder, Genesis Record, Watchdog, DB)   |
+-----------------------------------------------+
```

### Zaleznosci miedzywarstwowe

| Warstwa            | Zalezy od                                        | Dostarcza                          |
| :----------------- | :----------------------------------------------- | :--------------------------------- |
| **Interface**      | Integration                                      | UI, CLI, SDK                       |
| **Integration**    | Core (Trinity, Hexagon, Guardians)               | Orkiestracja, signature, walidacja |
| **Trinity**        | Perspectives (Material, Intellectual, Essential) | Trinity Score                      |
| **Hexagon**        | Modes (6 trybow)                                 | Processed result                   |
| **Guardians**      | Laws (9 praw)                                    | Compliance decision                |
| **Infrastructure** | -- (fundament)                                   | IPC, persistence, monitoring       |

---

## :three: Przeplyw Danych Miedzy Komponentami

```
Request --> [Trinity] --> trinity_result
                              |
                              v
            [EBDI] <--- [Hexagon Mode 1: Inventory]
              |              |
              |              v
              +-------> [Hexagon Mode 2: Empathy] --> user_context
                              |
                              v
                        [Hexagon Mode 3: Process] --> task_plan
                              |
                              v
              [Skeptics] --> [Hexagon Mode 4: Debate] --> consensus
                              |
                              v (if dissonance)
                        [Hexagon Mode 5: Healing] --> clean_request
                              |
                              v
              [SAFE-MCP] --> [Hexagon Mode 6: Action] --> [Genesis Record]
                              |
                              v
                        [Guardians] --> compliance_result
                              |
                              v
                        [369 Signature] --> signed_response
```

---

## :four: Kluczowe Metryki Systemu

### Trinity Metrics

| Metryka                 | Zakres | Opis                               |
| :---------------------- | :----: | :--------------------------------- |
| **Trinity Score**       |  0--1  | Srednia wazona 3 perspektyw        |
| **Dimensional Balance** |  0--1  | 1 = perfekcyjna rownowaga          |
| **Material Score**      | 0--100 | Dostepnosc zasobow                 |
| **Intellectual Score**  |  0--1  | Sens logiczny (harmonic mean)      |
| **Essential Score**     |  0--1  | Alignment z misja (geometric mean) |

### Hexagon Metrics

| Metryka               | Typ  | Opis                                |
| :-------------------- | :--: | :---------------------------------- |
| **Cycles Performed**  | int  | Liczba pelnych obiegow (max 3)      |
| **Modes Executed**    | list | Lista wykonanych trybow             |
| **Completion Status** | enum | complete / incomplete / forced_stop |

### Guardian Metrics

| Metryka                 |   Zakres   | Opis                                   |
| :---------------------- | :--------: | :------------------------------------- |
| **Guardian Compliance** |    0--1    | `(9 - violations) / 9`                 |
| **Violations Count**    |    0--9    | Liczba naruszen                        |
| **Triad Compliance**    | 3 x (0--1) | Osobne wyniki Matter / Light / Essence |

### EBDI Metrics

| Metryka             |  Zakres  | Opis                               |
| :------------------ | :------: | :--------------------------------- |
| **PAD Vector**      | (P,A,D)  | Stan emocjonalny agenta            |
| **Temperature**     | 0.1--1.0 | Parametr kreatywnosci LLM          |
| **Emotional State** |   enum   | CALM / ALERT / STRESSED / PARANOID |
| **Stress Level**    |   0--1   | `Arousal x (1 - Pleasure)`         |

### System Integrity

| Metryka             | Opis                                              |
| :------------------ | :------------------------------------------------ |
| **Genesis Chain**   | INTACT / BROKEN --- integralnosc lancucha hashow  |
| **369 Signature**   | VALID / INVALID --- kryptograficzny dowod decyzji |
| **Watchdog Status** | Wszystkie agenty alive? Heartbeat OK?             |
