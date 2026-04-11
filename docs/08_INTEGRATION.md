# Warstwa Integracji — Spojnosc Systemu

> **Modul:** `system_369.py`, `signature.py`, `validator.py`
> **Rola:** Laczenie trzech warstw (Trinity, Hexagon, Guardians) w jeden **spojny pipeline decyzyjny**.

---

## 1. `system_369.py` — Glowny Orkiestrator

**Orkiestrator** jest sercem systemu ADRION 369. Laczy **3 perspektywy**, **6 trybow** i **9 praw** w jeden przeplyw przetwarzania.

### Pipeline przetwarzania

| **Krok** | **Opis**                                                                              | **Warstwa** |
| -------- | ------------------------------------------------------------------------------------- | ----------- |
| **1.**   | Request arrives — walidacja wejscia                                                   | Input       |
| **2.**   | **Trinity Analysis** — 3 perspektywy rownoczesnie (Material, Intellectual, Essential) | Trinity     |
| **3.**   | Jesli wynik = **DENY** — natychmiastowy return z uzasadnieniem                        | Trinity     |
| **4.**   | **Hexagon Processing** — 6 sekwencyjnych trybow przetwarzania                         | Hexagon     |
| **5.**   | Jesli wynik = **INCOMPLETE** — return ze statusem czesciowym                          | Hexagon     |
| **6.**   | **Guardian Enforcement** — weryfikacja wszystkich 9 praw                              | Guardians   |
| **7.**   | **Synteza decyzji** — agregacja wynikow z trzech warstw                               | Integration |
| **8.**   | **Generowanie 369 Signature** — kryptograficzny dowod integralnosci                   | Signature   |
| **9.**   | Return response — pelna odpowiedz z raportem                                          | Output      |

### Struktura wyjsciowa (JSON)

```json
{
  "trinity": {
    "material_score": 0.85,
    "intellectual_score": 0.92,
    "essential_score": 0.78,
    "trinity_score": 0.85,
    "dimensional_balance": 0.94
  },
  "hexagon": {
    "modes_executed": 6,
    "cycles_performed": 2,
    "final_status": "COMPLETE"
  },
  "guardians": {
    "all_laws_satisfied": true,
    "violations": [],
    "triad_compliance": 1.0
  },
  "final_decision": "APPROVE",
  "reasoning": "Wszystkie warstwy zgodne...",
  "369_signature": "a1b2c3...f6:162.00"
}
```

### Klucze decyzyjne

| **Pole**                       | **Typ**  | **Opis**                                   |
| ------------------------------ | -------- | ------------------------------------------ |
| `trinity.trinity_score`        | `float`  | Srednia wazona 3 perspektyw (0.0 — 1.0)    |
| `trinity.dimensional_balance`  | `float`  | Rownowaga miedzy wymiarami (1.0 = idealna) |
| `hexagon.final_status`         | `string` | `COMPLETE` / `INCOMPLETE` / `ERROR`        |
| `guardians.all_laws_satisfied` | `bool`   | `true` = zadne prawo nie zostalo naruszone |
| `guardians.triad_compliance`   | `float`  | Zgodnosc z triada 3-6-9 (0.0 — 1.0)        |
| `final_decision`               | `string` | **APPROVE** / **DENY** / **REVIEW**        |
| `369_signature`                | `string` | Kryptograficzny hash + checksum            |

---

## 2. `signature.py` — 369 Signature

**Sygnatura 369** to kryptograficzny dowod integralnosci calego procesu decyzyjnego. Gwarantuje, ze wynik nie zostal zmodyfikowany po wygenerowaniu.

### Proces generowania

| **Krok** | **Operacja**            | **Detale**                                                       |
| -------- | ----------------------- | ---------------------------------------------------------------- |
| **1.**   | **Zbieranie danych**    | 3 perspektywy + 6 trybow + 9 praw                                |
| **2.**   | **Kanonizacja JSON**    | Sorted keys, brak bialych znakow, kodowanie **UTF-8**            |
| **3.**   | **Hash SHA-256**        | Jednokierunkowy hash calego payloadu                             |
| **4.**   | **Obliczenie checksum** | `(sum(3_perspectives) x 3 + sum(6_modes) x 6 + sum(9_laws) x 9)` |
| **5.**   | **Zapis sygnatury**     | `f"{hash}:{checksum:.2f}"`                                       |

### Wzor checksum

```
checksum = (P1 + P2 + P3) * 3
         + (M1 + M2 + M3 + M4 + M5 + M6) * 6
         + (L1 + L2 + L3 + L4 + L5 + L6 + L7 + L8 + L9) * 9
```

| **Symbol** | **Znaczenie**                                                   |
| ---------- | --------------------------------------------------------------- |
| `P1..P3`   | Wyniki 3 perspektyw Trinity (Material, Intellectual, Essential) |
| `M1..M6`   | Statusy 6 trybow Hexagon (0.0 lub 1.0)                          |
| `L1..L9`   | Wyniki 9 praw Guardian (0.0 — 1.0)                              |

### Przyklad sygnatury

```
a7f3b2c1d4e5f6a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2:162.00
```

> **Wartosc 162.00** — maksymalny checksum oznacza pelna zgodnosc wszystkich warstw (3x3 + 6x6 + 9x9 = 9 + 36 + 81 = 126... wartosc zalezy od wynikow).

---

## 3. `validator.py` — Walidator Spojnosci

**Walidator** sprawdza wewnetrzna spojnosc wynikow na **czterech poziomach**.

### Poziomy walidacji

| **Poziom** | **Nazwa**                   | **Co sprawdza**                                           |
| ---------- | --------------------------- | --------------------------------------------------------- |
| **1**      | **Trinity Consistency**     | Czy `trinity_score` = prawidlowa srednia z 3 perspektyw   |
| **2**      | **Hexagon Consistency**     | Czy `modes_executed` = 6 i wszystkie statusy sa poprawne  |
| **3**      | **Guardian Consistency**    | Czy `all_laws_satisfied` zgadza sie z lista `violations`  |
| **4**      | **Cross-layer Consistency** | Czy decyzja finalna jest logiczna wzgledem wynikow warstw |

### Reguly walidacji cross-layer

| **Warunek**                                 | **Oczekiwana decyzja**  | **Jesli niezgodna** |
| ------------------------------------------- | ----------------------- | ------------------- |
| `guardians.violations` zawiera **CRITICAL** | **DENY**                | **BLAD KRYTYCZNY**  |
| `guardians.violations.length >= 2`          | **DENY**                | **BLAD KRYTYCZNY**  |
| `trinity_score < 0.3`                       | **DENY** lub **REVIEW** | Ostrzezenie         |
| `hexagon.final_status = "INCOMPLETE"`       | **REVIEW**              | Ostrzezenie         |
| Wszystkie warstwy OK                        | **APPROVE**             | Informacja          |

### Wynik walidacji

```json
{
  "valid": true,
  "checks_passed": 4,
  "checks_total": 4,
  "details": [
    { "check": "trinity_consistency", "status": "PASS" },
    { "check": "hexagon_consistency", "status": "PASS" },
    { "check": "guardian_consistency", "status": "PASS" },
    { "check": "cross_layer_consistency", "status": "PASS" }
  ]
}
```

---

> **Uwaga:** Warstwa integracji jest **krytyczna** dla poprawnosci systemu. Kazda zmiana w `system_369.py`, `signature.py` lub `validator.py` wymaga pelnego uruchomienia testow: `python -m pytest tests/ -q --cov=arbitrage --cov-fail-under=80`
