<p align="center">
  <strong>ADRION 369</strong><br>
  <em>Multi-Agent AI Orchestration System</em><br>
  <code>v5.0</code> | Architecture Documentation
</p>

<p align="center">
  <em>"Gdybyś znał wspaniałość liczb 3, 6 i 9, miałbyś klucz do wszechświata."</em><br>
  <em>"If you knew the magnificence of 3, 6 and 9, you would have the key to the universe."</em><br>
  — Nikola Tesla
</p>

---

# Spis treści / Table of Contents

- [PL — Dokumentacja po polsku](#-pl--dokumentacja-po-polsku)
  - [Matryca 3-6-9](#-matryca-3-6-9--geometryczne-serce-systemu)
  - [Architektura](#-architektura)
  - [Przepływ decyzji](#-przepływ-decyzji)
  - [Dokumentacja](#-dokumentacja)
- [EN — English Documentation](#-en--english-documentation)
  - [The 3-6-9 Matrix](#-the-3-6-9-matrix--geometric-heart-of-the-system)
  - [Architecture](#-architecture)
  - [Decision Flow](#-decision-flow)
  - [Documentation](#-documentation)
- [Licencja / License](#-licencja--license)

---

# 🇵🇱 PL — Dokumentacja po polsku

## 🔺 MATRYCA 3-6-9 — Geometryczne serce systemu

**ADRION 369** opiera się na zasadzie geometrycznej **3 × 6 × 9 = 162-wymiarowa przestrzeń decyzyjna**.

Każda decyzja w systemie przechodzi przez trzy warstwy, z których każda mnoży przestrzeń analizy:

```
╔══════════════════════════════════════════════════════════════════════╗
║                      M A T R Y C A   3-6-9                         ║
║                                                                      ║
║   ┌─────────┐     ┌─────────────┐     ┌───────────────┐            ║
║   │    3    │  ×  │      6      │  ×  │       9       │  = 162D    ║
║   │ TRINITY │     │   HEXAGON   │     │   GUARDIANS   │            ║
║   └─────────┘     └─────────────┘     └───────────────┘            ║
║                                                                      ║
║   3 Perspektywy   6 Trybów           9 Praw Strażników             ║
║   Material         Inventory          Unity                          ║
║   Intellectual     Empathy            Harmony                        ║
║   Essential        Process            Rhythm                         ║
║                    Debate             Causality                      ║
║                    Healing            Transparency                   ║
║                    Action             Authenticity                   ║
║                                       Privacy                        ║
║                                       Nonmaleficence                 ║
║                                       Sustainability                 ║
║                                                                      ║
║   ─────────────────────────────────────────────────────────────     ║
║   Wymiary:  3 × 6 × 9 = 162 unikalne stany decyzyjne              ║
║   Każdy stan = (Perspektywa, Tryb, Prawo)                           ║
║   Każda decyzja = przejście przez PEŁNĄ matrycę                     ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Trzy warstwy matrycy

**🔺 Warstwa 3 — TRINITY (Perspektywy)**

| Perspektywa      | Rola                           | Pytanie kluczowe                        |
| ---------------- | ------------------------------ | --------------------------------------- |
| **Material**     | LOGOS — Prawda, dane, fakty    | _Czy to jest prawdziwe i mierzalne?_    |
| **Intellectual** | ETHOS — Dobro, etyka, wartości | _Czy to jest dobre i odpowiedzialne?_   |
| **Essential**    | EROS — Tworzenie, piękno, sens | _Czy to jest wartościowe i eleganckie?_ |

**⬡ Warstwa 6 — HEXAGON (Tryby)**

| #   | Tryb          | Funkcja                             |
| --- | ------------- | ----------------------------------- |
| 1   | **Inventory** | Zbieranie danych, stan zasobów      |
| 2   | **Empathy**   | Analiza perspektywy użytkownika     |
| 3   | **Process**   | Przetwarzanie i transformacja       |
| 4   | **Debate**    | Konfrontacja argumentów, konsensus  |
| 5   | **Healing**   | Naprawa, korekcja, samoregulacja    |
| 6   | **Action**    | Wykonanie, implementacja, odpowiedź |

**🛡️ Warstwa 9 — GUARDIANS (Prawa)**

| #   | Kod    | Prawo              | Triada  | Ważność  | Veto    |
| --- | ------ | ------------------ | ------- | -------- | ------- |
| 1   | **G1** | **Unity**          | Materia | MEDIUM   | Nie     |
| 2   | **G2** | **Harmony**        | Materia | HIGH     | Nie     |
| 3   | **G3** | **Rhythm**         | Materia | MEDIUM   | Nie     |
| 4   | **G4** | **Causality**      | Światło | HIGH     | Nie     |
| 5   | **G5** | **Transparency**   | Światło | MEDIUM   | Nie     |
| 6   | **G6** | **Authenticity**   | Światło | HIGH     | Nie     |
| 7   | **G7** | **Privacy**        | Esencja | CRITICAL | **TAK** |
| 8   | **G8** | **Nonmaleficence** | Esencja | CRITICAL | **TAK** |
| 9   | **G9** | **Sustainability** | Esencja | HIGH     | Nie     |

> **Zasada VETO:** Naruszenie prawa CRITICAL = natychmiastowe odrzucenie decyzji (DENY).
> Naruszenie 2+ dowolnych praw = odrzucenie decyzji (DENY).

### Triady Strażników

```
  ┌───────────────────────────────────────────────────────┐
  │                   9 PRAW STRAŻNIKÓW                   │
  │                                                       │
  │   TRIADA MATERII        TRIADA ŚWIATŁA                │
  │   ┌─────────────┐      ┌──────────────────┐          │
  │   │ G1 Unity    │      │ G4 Causality     │          │
  │   │ G2 Harmony  │      │ G5 Transparency  │          │
  │   │ G3 Rhythm   │      │ G6 Authenticity  │          │
  │   └─────────────┘      └──────────────────┘          │
  │                                                       │
  │              TRIADA ESENCJI                           │
  │              ┌────────────────────┐                   │
  │              │ G7 Privacy     [!] │                   │
  │              │ G8 Nonmalefi. [!] │                   │
  │              │ G9 Sustainability  │                   │
  │              └────────────────────┘                   │
  │              [!] = CRITICAL / VETO                    │
  └───────────────────────────────────────────────────────┘
```

---

## 🏗️ Architektura

```
                            ┌──────────────────┐
                            │   ŻĄDANIE (IN)   │
                            └────────┬─────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  🔺 TRINITY — 3 Perspektywy     │
                    │  Material | Intellectual | Essen.│
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  ⬡ HEXAGON — 6 Trybów           │
                    │  Inv | Emp | Proc | Deb | Hea | Act │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  🛡️ GUARDIANS — 9 Praw           │
                    │  G1-G3 Materia                   │
                    │  G4-G6 Światło                   │
                    │  G7-G9 Esencja                   │
                    │                                  │
                    │  CRITICAL violation? → DENY      │
                    │  2+ violations? → DENY           │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  📐 SYGNATURA 369               │
                    │  Digital Root + Rezonans 174Hz   │
                    │  Walidacja integralności          │
                    └────────────────┬────────────────┘
                                     │
                            ┌────────▼─────────┐
                            │  ODPOWIEDŹ (OUT) │
                            └──────────────────┘
```

### Komponenty systemu

| Komponent             | Port      | Rola                                                                 |
| --------------------- | --------- | -------------------------------------------------------------------- |
| **Flask App Factory** | 8003      | Główny backend, 5 Blueprintów, Guardian Laws Engine                  |
| **UAP Orchestrator**  | 8002      | 6 AI Personas (Librarian, SAP, Auditor, Sentinel, Architect, Healer) |
| **Go Vortex**         | 1740      | EBDI state machine, digital root oracle, puls 174Hz                  |
| **MCP Layer**         | 9000-9005 | 6 mikroserwisów (Router, Vortex, Guardian, Oracle, Genesis, Healer)  |

---

## 🔄 Przepływ decyzji

```
Żądanie → Trinity(3) → Hexagon(6) → Guardians(9) → Sygnatura 369 → Odpowiedź
```

1. **Żądanie** trafia do systemu
2. **Trinity** analizuje je z 3 perspektyw (Material, Intellectual, Essential)
3. **Hexagon** przetwarza przez 6 trybów operacyjnych
4. **Guardians** walidują zgodność z 9 prawami — naruszenie CRITICAL = natychmiastowy DENY
5. **Sygnatura 369** potwierdza integralność geometryczną (digital root)
6. **Odpowiedź** jest zwracana z pełnym audytem decyzyjnym

---

## 📚 Dokumentacja

| Plik                                                     | Opis                                                               |
| -------------------------------------------------------- | ------------------------------------------------------------------ |
| [`docs/00_MATRYCA_369.md`](docs/00_MATRYCA_369.md)       | **Matryca 3-6-9** — geometryczna hierarchia systemu                |
| [`docs/01_CORE_TRINITY.md`](docs/01_CORE_TRINITY.md)     | **Trinity** — System 3 Perspektyw                                  |
| [`docs/02_CORE_HEXAGON.md`](docs/02_CORE_HEXAGON.md)     | **Hexagon** — System 6 Trybów                                      |
| [`docs/03_CORE_GUARDIANS.md`](docs/03_CORE_GUARDIANS.md) | **Guardians** — System 9 Praw                                      |
| [`docs/04_CORE_EBDI.md`](docs/04_CORE_EBDI.md)           | **EBDI** — Model Emocjonalny Agenta                                |
| [`docs/05_PERSPECTIVES.md`](docs/05_PERSPECTIVES.md)     | Warstwa Perspektyw (Material / Intellectual / Essential)           |
| [`docs/06_MODES.md`](docs/06_MODES.md)                   | Warstwa Trybów (6 modes — szczegółowo)                             |
| [`docs/07_LAWS.md`](docs/07_LAWS.md)                     | Warstwa Praw (9 laws — szczegółowo)                                |
| [`docs/08_INTEGRATION.md`](docs/08_INTEGRATION.md)       | Warstwa Integracji (System 369, Signature, Validator)              |
| [`docs/09_INFRASTRUCTURE.md`](docs/09_INFRASTRUCTURE.md) | Warstwa Infrastruktury (AI-Binder, Genesis Record, Watchdog, DB)   |
| [`docs/10_COMMUNICATION.md`](docs/10_COMMUNICATION.md)   | Warstwa Komunikacji (SAFE-MCP, Message Bus, API)                   |
| [`docs/11_INTELLIGENCE.md`](docs/11_INTELLIGENCE.md)     | Warstwa Inteligencji (Agent Swarm, Archetypes, Transcendence Loop) |
| [`docs/12_DATA_FLOWS.md`](docs/12_DATA_FLOWS.md)         | Przepływy Danych i Diagramy                                        |

---

---

# 🇬🇧 EN — English Documentation

## 🔺 The 3-6-9 Matrix — Geometric Heart of the System

**ADRION 369** is built on a geometric principle: **3 x 6 x 9 = 162-Dimensional Decision Space**.

Every decision traverses three multiplicative layers, each expanding the analytical space:

```
╔══════════════════════════════════════════════════════════════════════╗
║                     T H E   3-6-9   M A T R I X                    ║
║                                                                      ║
║   ┌─────────┐     ┌─────────────┐     ┌───────────────┐            ║
║   │    3    │  x  │      6      │  x  │       9       │  = 162D    ║
║   │ TRINITY │     │   HEXAGON   │     │   GUARDIANS   │            ║
║   └─────────┘     └─────────────┘     └───────────────┘            ║
║                                                                      ║
║   3 Perspectives   6 Modes            9 Guardian Laws               ║
║   Material         Inventory          Unity                          ║
║   Intellectual     Empathy            Harmony                        ║
║   Essential        Process            Rhythm                         ║
║                    Debate             Causality                      ║
║                    Healing            Transparency                   ║
║                    Action             Authenticity                   ║
║                                       Privacy                        ║
║                                       Nonmaleficence                 ║
║                                       Sustainability                 ║
║                                                                      ║
║   ─────────────────────────────────────────────────────────────     ║
║   Dimensions:  3 x 6 x 9 = 162 unique decision states              ║
║   Each state = (Perspective, Mode, Law)                             ║
║   Each decision = full traversal of the ENTIRE matrix               ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Three layers of the matrix

**🔺 Layer 3 — TRINITY (Perspectives)**

| Perspective      | Principle                        | Core Question                 |
| ---------------- | -------------------------------- | ----------------------------- |
| **Material**     | LOGOS — Truth, data, facts       | _Is it real and measurable?_  |
| **Intellectual** | ETHOS — Good, ethics, values     | _Is it good and responsible?_ |
| **Essential**    | EROS — Creation, beauty, meaning | _Is it valuable and elegant?_ |

**⬡ Layer 6 — HEXAGON (Modes)**

| #   | Mode          | Function                                     |
| --- | ------------- | -------------------------------------------- |
| 1   | **Inventory** | Data gathering, resource state assessment    |
| 2   | **Empathy**   | User perspective analysis                    |
| 3   | **Process**   | Transformation and processing                |
| 4   | **Debate**    | Argument confrontation, consensus building   |
| 5   | **Healing**   | Repair, correction, self-regulation          |
| 6   | **Action**    | Execution, implementation, response delivery |

**🛡️ Layer 9 — GUARDIANS (Laws)**

| #   | Code   | Law                | Triad   | Severity | Veto    |
| --- | ------ | ------------------ | ------- | -------- | ------- |
| 1   | **G1** | **Unity**          | Matter  | MEDIUM   | No      |
| 2   | **G2** | **Harmony**        | Matter  | HIGH     | No      |
| 3   | **G3** | **Rhythm**         | Matter  | MEDIUM   | No      |
| 4   | **G4** | **Causality**      | Light   | HIGH     | No      |
| 5   | **G5** | **Transparency**   | Light   | MEDIUM   | No      |
| 6   | **G6** | **Authenticity**   | Light   | HIGH     | No      |
| 7   | **G7** | **Privacy**        | Essence | CRITICAL | **YES** |
| 8   | **G8** | **Nonmaleficence** | Essence | CRITICAL | **YES** |
| 9   | **G9** | **Sustainability** | Essence | HIGH     | No      |

> **VETO Rule:** Any CRITICAL law violation = instant decision rejection (DENY).
> 2+ violations of any severity = decision rejection (DENY).

### Guardian Triads

```
  ┌───────────────────────────────────────────────────────┐
  │                  9 GUARDIAN LAWS                       │
  │                                                       │
  │   MATTER TRIAD           LIGHT TRIAD                  │
  │   ┌─────────────┐      ┌──────────────────┐          │
  │   │ G1 Unity    │      │ G4 Causality     │          │
  │   │ G2 Harmony  │      │ G5 Transparency  │          │
  │   │ G3 Rhythm   │      │ G6 Authenticity  │          │
  │   └─────────────┘      └──────────────────┘          │
  │                                                       │
  │              ESSENCE TRIAD                            │
  │              ┌────────────────────┐                   │
  │              │ G7 Privacy     [!] │                   │
  │              │ G8 Nonmalefi. [!] │                   │
  │              │ G9 Sustainability  │                   │
  │              └────────────────────┘                   │
  │              [!] = CRITICAL / VETO                    │
  └───────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
                            ┌──────────────────┐
                            │   REQUEST (IN)   │
                            └────────┬─────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  🔺 TRINITY — 3 Perspectives     │
                    │  Material | Intellectual | Essen.│
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  ⬡ HEXAGON — 6 Modes             │
                    │  Inv | Emp | Proc | Deb | Hea | Act │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  🛡️ GUARDIANS — 9 Laws            │
                    │  G1-G3 Matter                    │
                    │  G4-G6 Light                     │
                    │  G7-G9 Essence                   │
                    │                                  │
                    │  CRITICAL violation? → DENY      │
                    │  2+ violations? → DENY           │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │  📐 369 SIGNATURE                │
                    │  Digital Root + 174Hz Resonance   │
                    │  Integrity Validation             │
                    └────────────────┬────────────────┘
                                     │
                            ┌────────▼─────────┐
                            │  RESPONSE (OUT)  │
                            └──────────────────┘
```

### System Components

| Component             | Port      | Role                                                                 |
| --------------------- | --------- | -------------------------------------------------------------------- |
| **Flask App Factory** | 8003      | Primary backend, 5 Blueprints, Guardian Laws Engine                  |
| **UAP Orchestrator**  | 8002      | 6 AI Personas (Librarian, SAP, Auditor, Sentinel, Architect, Healer) |
| **Go Vortex**         | 1740      | EBDI state machine, digital root oracle, 174Hz pulse                 |
| **MCP Layer**         | 9000-9005 | 6 microservices (Router, Vortex, Guardian, Oracle, Genesis, Healer)  |

---

## 🔄 Decision Flow

```
Request → Trinity(3) → Hexagon(6) → Guardians(9) → 369 Signature → Response
```

1. **Request** enters the system
2. **Trinity** evaluates from 3 perspectives (Material, Intellectual, Essential)
3. **Hexagon** processes through 6 operational modes
4. **Guardians** validate compliance with 9 laws — CRITICAL violation = instant DENY
5. **369 Signature** confirms geometric integrity via digital root computation
6. **Response** is returned with a full decision audit trail

---

## 📚 Documentation

| File                                                     | Description                                                      |
| -------------------------------------------------------- | ---------------------------------------------------------------- |
| [`docs/00_MATRYCA_369.md`](docs/00_MATRYCA_369.md)       | **The 3-6-9 Matrix** — geometric hierarchy of the system         |
| [`docs/01_CORE_TRINITY.md`](docs/01_CORE_TRINITY.md)     | **Trinity** — The 3 Perspectives System                          |
| [`docs/02_CORE_HEXAGON.md`](docs/02_CORE_HEXAGON.md)     | **Hexagon** — The 6 Modes System                                 |
| [`docs/03_CORE_GUARDIANS.md`](docs/03_CORE_GUARDIANS.md) | **Guardians** — The 9 Laws System                                |
| [`docs/04_CORE_EBDI.md`](docs/04_CORE_EBDI.md)           | **EBDI** — Agent Emotional Model                                 |
| [`docs/05_PERSPECTIVES.md`](docs/05_PERSPECTIVES.md)     | Perspectives Layer (Material / Intellectual / Essential)         |
| [`docs/06_MODES.md`](docs/06_MODES.md)                   | Modes Layer (6 modes in detail)                                  |
| [`docs/07_LAWS.md`](docs/07_LAWS.md)                     | Laws Layer (9 laws in detail)                                    |
| [`docs/08_INTEGRATION.md`](docs/08_INTEGRATION.md)       | Integration Layer (System 369, Signature, Validator)             |
| [`docs/09_INFRASTRUCTURE.md`](docs/09_INFRASTRUCTURE.md) | Infrastructure Layer (AI-Binder, Genesis Record, Watchdog, DB)   |
| [`docs/10_COMMUNICATION.md`](docs/10_COMMUNICATION.md)   | Communication Layer (SAFE-MCP, Message Bus, API)                 |
| [`docs/11_INTELLIGENCE.md`](docs/11_INTELLIGENCE.md)     | Intelligence Layer (Agent Swarm, Archetypes, Transcendence Loop) |
| [`docs/12_DATA_FLOWS.md`](docs/12_DATA_FLOWS.md)         | Data Flows and Diagrams                                          |

---

---

## 📄 Licencja / License

MIT License

Copyright (c) 2026 Adrian Halicki

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
