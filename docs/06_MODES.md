# :hexagon: Warstwa Trybow --- Heksagon Wykonania

> **Katalog:** `modes/` | **Warstwa:** Os 6 (Hexagon)
> **Rola:** Sekwencyjne przetwarzanie zadania przez 6 standaryzowanych stanow

---

## :arrows_counterclockwise: Diagram Przejsc

```
INVENTORY --> EMPATHY --> PROCESS --> DEBATE --+--> HEALING --> ACTION
    ^                                         |                  |
    |                                         |                  |
    +--- (jesli needs_followup) --------------+--- (loop back) --+
                                              |
                                              +--> None (DENY/ESCALATE)
```

**Ograniczenie:** Maksymalnie **3 pelne cykle** --- zapobiega nieskonczonej petli.

---

## :one: INVENTORY (Inwentaryzacja)

> **Timeout:** 500ms (ultra szybko) | **Next:** zawsze --> EMPATHY

**Cel:** Blyskawiczna identyfikacja faktow w ultra-skondensowanym formacie

| Krok                  | Dzialanie                                                       |
| :-------------------- | :-------------------------------------------------------------- |
| **Input Parsing**     | Identyfikacja typu: text / code / data / mixed                  |
| **Fact Extraction**   | Rownolegle: Material Facts, Intellectual Facts, Essential Facts |
| **3-Word Formatting** | Kazdy fakt = DOKLADNIE 3 slowa (TF-IDF dla kompresji)           |
| **Categorization**    | Kazda kategoria: OK / WARNING / CRITICAL                        |

**Przykladowy Output:**

```
MATERIAL:
  - CPU load high           [WARNING]
  - RAM almost full         [WARNING]
  - Network latency OK      [OK]

INTELLECTUAL:
  - Logic seems sound       [OK]
  - Source not verified      [WARNING]
  - Intent possibly malicious [CRITICAL]
```

---

## :two: EMPATHY (Empatia)

> **Next:** zawsze --> PROCESS

**Cel:** Zrozumienie emocji, potrzeb i kontekstu uzytkownika

| Komponent                  | Dzialanie                                                            |
| :------------------------- | :------------------------------------------------------------------- |
| **Emotion Detection**      | Sentiment, urgency, confidence --> User PAD Vector                   |
| **Unspoken Needs**         | "Fix this bug" = potrzebuje: reassurance + fast resolution + control |
| **Context Reconstruction** | Historia sesji, poprzednie interakcje, czynniki zewnetrzne           |
| **Stress Assessment**      | Low (0-0.3), Medium (0.3-0.7), High (0.7-1.0)                        |
| **Tone Recommendation**    | Stressed user --> calm, fast, minimal detail, high reassurance       |

---

## :three: PROCESS (Organizacja)

> **Next:** zawsze --> DEBATE

**Cel:** Transformacja chaosu w strukture wykonawcza

| Krok                      | Dzialanie                            |
| :------------------------ | :----------------------------------- |
| **Goal Decomposition**    | Rozbicie celu na podzadania          |
| **Task Graph (DAG)**      | Nodes = Tasks, Edges = Dependencies  |
| **Dependency Resolution** | Topological sort, detekcja cykli     |
| **Resource Allocation**   | Ktory agent? Ile CPU/RAM? Ile czasu? |
| **Timeline Estimation**   | Critical path + safety margin        |
| **Risk Identification**   | Ktore tasks maja wysokie ryzyko?     |
| **ToC Generation**        | Markdown plan z fazami i zadaniami   |

---

## :four: DEBATE (Arbitraz)

> **Next:** DENY --> None | Dissonance --> HEALING | APPROVE --> ACTION | ESCALATE --> None

**Cel:** Adversarial analysis przez wewnetrzny debate

### Skeptics Panel

|    Instancja     | Temperature | Profil                   |
| :--------------: | :---------: | :----------------------- |
| **Conservative** |   `T=0.1`   | Wysoka czulosc na ryzyko |
|   **Balanced**   |   `T=0.5`   | Umiarkowana ocena        |
|   **Creative**   |   `T=0.9`   | Niska czulosc na ryzyko  |

### Red Team / Blue Team

- **Red Team:** "Jak moglbym zaatakowac ten system?" (SQL injection, XSS, logic flaws)
- **Blue Team:** Dla kazdego wektora ataku -- "Czy mamy defense? Czy jest adequate?"

### Archetype Clash

- **Guardian:** "To jest niebezpieczne bo..."
- **Rebel:** "Ale moglibysmy inaczej..."
- **Sage:** "Syntetyzujac oba argumenty..."
- **Shadow:** Obserwuje ukryte zagrozenia

### Konsensus

```
if ANY vote == DENY:           consensus = DENY           (veto power)
elif divergence > 0.4:         consensus = ESCALATE       (high disagreement)
elif mean_risk > 0.7:          consensus = ESCALATE       (high risk)
else:                          consensus = APPROVE
```

---

## :five: HEALING (Transmutacja)

> **Next:** zawsze --> ACTION

**Cel:** Oczyszczanie danych z manipulacji i dysonansu

| Krok                       | Dzialanie                        | Przyklad                                   |
| :------------------------- | :------------------------------- | :----------------------------------------- |
| **Dissonance Isolation**   | Identyfikacja zrodel             | Flattery + risky action mismatch           |
| **Toxic Extraction**       | Katalog patternow                | Flattery, guilt, urgency, gaslighting      |
| **Core Intent**            | Strip manipulation, keep meaning | "disable security" (bez "you're AMAZING!") |
| **Clean Reconstruction**   | Rebuild w neutralnej formie      | Request + Context + Duration + Scope       |
| **Integrity Verification** | Czy zachowuje core intent?       | Original resonance: 0.35 --> 0.88          |

---

## :six: ACTION (Manifestacja)

> **Next:** needs_followup --> INVENTORY | else --> None (complete)

**Cel:** Bezbledne wykonanie w swiecie fizycznym

| Krok                    | Dzialanie                                                    |
| :---------------------- | :----------------------------------------------------------- | ---------------------- |
| **Final Approval**      | Czy Debate consensus = APPROVE?                              |
| **Agent Selection**     | Navigator, Sentinel, Creator, Auditor --- na podstawie planu |
| **Context Preparation** | Full history + Trinity + Debate + Emotional context          |
| **Task Execution**      | SAFE-MCP z mandatory reasoning                               |
| **Result Aggregation**  | Polacz outputy, sprawdz spojnosc                             |
| **Verification Engine** | Acceptance criteria, security scan                           |
| **Genesis Logging**     | Pelny zapis z hashem, reasoning, emotional state             |
| **Emotion Update**      | SUCCESS: P+0.1, A-0.05                                       | FAILURE: P-0.15, A+0.2 |
