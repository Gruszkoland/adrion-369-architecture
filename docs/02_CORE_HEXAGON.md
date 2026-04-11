# Hexagon -- System Szesciu Trybow

> **Modul:** `core/hexagon.py`
> **Wersja:** 4.0 | **Status:** Aktywny
> **Matryca:** 6 trybow przetwarzania (warstwa "6" w Matrycy 3-6-9)

---

## Cel

**Orkiestracja szesciu standaryzowanych stanow przetwarzania** (processing modes),
przez ktore przechodzi kazde zapytanie. Hexagon zapewnia **strukturalny i powtarzalny**
pipeline decyzyjny -- od zbierania faktow, przez debate, az po egzekucje.

---

## 6 Trybow Hexagonu

### 1. INVENTORY (Inwentaryzacja)

**Timeout:** 500 ms
**Cel:** Ekstrakcja faktow z zapytania w **formacie 3-slow** (fakt-klucz-wartosc).

```
Input:  "Chce kupic 100 sztuk produktu X za max 50 PLN/szt z dostawa do piątku"
Output: [
  {"fakt": "ilosc",    "klucz": "sztuki",   "wartosc": "100"},
  {"fakt": "cena_max", "klucz": "PLN/szt",  "wartosc": "50"},
  {"fakt": "termin",   "klucz": "dostawa",  "wartosc": "piatek"}
]
```

**Kluczowe:** Tryb INVENTORY **nie interpretuje** -- tylko ekstrahuje.
Jesli w 500 ms nie zdazy, przechodzi dalej z czesciowymi danymi.

---

### 2. EMPATHY (Empatia)

**Cel:** Detekcja emocji uzytkownika, analiza potrzeb, rekomendacja tonu odpowiedzi.

**Pipeline empatii:**

- **Emotion Detection** -- analiza sentymentu i emocji w tekscie
- **Needs Analysis** -- identyfikacja ukrytych potrzeb (np. pilnosc, frustracja, niepewnosc)
- **Tone Recommendation** -- sugerowany ton odpowiedzi (`formal`, `empathetic`, `direct`, `cautious`)

```
Input:  "To juz trzeci raz pytam o status zamowienia!!!"
Output: {
  "emotion": "frustration",
  "intensity": 0.85,
  "needs": ["szybka_odpowiedz", "potwierdzenie_statusu"],
  "recommended_tone": "empathetic"
}
```

---

### 3. PROCESS (Organizacja)

**Cel:** Dekompozycja celu na graf zadan z rozwiazywaniem zaleznosci.

**Pipeline organizacji:**

- **Goal Decomposition** -- rozbicie glownego celu na podzadania
- **Task Graph** -- budowa grafu zaleznosci (DAG)
- **Dependency Resolution** -- okreslenie kolejnosci wykonania

```
Goal: "Uruchom pipeline arbitrazu"
  |
  +---> Task 1: Sprawdz dostepnosc API (no deps)
  +---> Task 2: Pobierz dane cenowe (depends: Task 1)
  +---> Task 3: Uruchom analize Trinity (depends: Task 2)
  +---> Task 4: Wykonaj decyzje Guardian (depends: Task 3)
```

**Wynik:** posortowana lista zadan gotowa do wykonania przez tryb ACTION.

---

### 4. DEBATE (Arbitraz)

**Cel:** Wieloperspektywiczna debata z udzialem **Skeptics Panel**.

**Skeptics Panel -- 3 instancje Claude z rozna temperatura:**

| Instancja        | Temperature | Rola                                          |
| ---------------- | ----------- | --------------------------------------------- |
| **Conservative** | T = 0.1     | Ostrozna analiza, minimalizacja ryzyka        |
| **Balanced**     | T = 0.5     | Zrownowazony poglad, kompromis                |
| **Creative**     | T = 0.9     | Kreatywne rozwiazania, eksploracja mozliwosci |

**Metoda Red/Blue Team:**

- **Red Team** -- probuje znalezc slabosci, atakuje propozycje
- **Blue Team** -- broni propozycji, prezentuje argumenty za

```
Debate Output: {
  "consensus": 0.72,
  "red_team_concerns": ["koszt przekracza budzet o 15%"],
  "blue_team_arguments": ["ROI pozytywne w 3 miesiace"],
  "dissonance_detected": false,
  "recommendation": "PROCEED_WITH_CAUTION"
}
```

**Wazne:** Jesli **dissonance_detected = false**, tryb HEALING moze zostac **pominiety**
(sciezka warunkowa -- patrz diagram przejsc ponizej).

---

### 5. HEALING (Transmutacja)

**Cel:** Izolacja dysonansow, ekstrakcja toksycznych elementow, czysta rekonstrukcja.

**Pipeline transmutacji:**

- **Dissonance Isolation** -- identyfikacja sprzecznych elementow z DEBATE
- **Toxic Element Extraction** -- usuniecie elementow szkodliwych lub niespojnych
- **Clean Reconstruction** -- zbudowanie oczyszczonej wersji propozycji

```
Input:  { "proposal": "...", "dissonances": ["sprzecznosc_cenowa", "ryzyko_prawne"] }
Output: {
  "cleaned_proposal": "...",
  "removed_elements": ["sprzecznosc_cenowa"],
  "mitigated_risks": ["ryzyko_prawne -> dodano klauzule ochronna"],
  "healing_score": 0.88
}
```

**Tryb HEALING aktywuje sie TYLKO gdy** `dissonance_detected = true` w trybie DEBATE.

---

### 6. ACTION (Manifestacja)

**Cel:** Wybor agenta, przygotowanie kontekstu, egzekucja zadania, logowanie do Genesis Record.

**Pipeline manifestacji:**

- **Agent Selection** -- dobor najlepszego agenta AI do zadania
- **Context Preparation** -- zbudowanie pelnego kontekstu (fakty + empatia + plan + wynik debaty)
- **Task Execution** -- wykonanie zadania przez wybranego agenta
- **Genesis Logging** -- zapis wyniku do Genesis Record (audit trail)

```
Action Output: {
  "agent": "Librarian",
  "task_id": "task_2026_04_11_001",
  "result": { ... },
  "genesis_record_id": "GR-2026-04-11-001",
  "execution_time_ms": 1230
}
```

**Sciezka warunkowa:** Tryb ACTION moze **wrocic do INVENTORY** jesli wynik
egzekucji wymaga ponownej analizy (np. bledne dane wejsciowe).

---

## Maszyna stanow (State Machine)

### Petla glowna

```python
current_mode = Mode.INVENTORY
cycles = 0

while current_mode is not None and cycles < 3:
    result = execute_mode(current_mode, context)
    current_mode = determine_next_mode(result)
    cycles += 1
```

**Maksymalna liczba cykli: 3** -- zapobiega nieskonczonej petli.
Jesli po 3 cyklach pipeline nie zakonczyl pracy, zwraca ostatni dostepny wynik
z flaga `max_cycles_reached = true`.

### Diagram przejsc miedzy trybami

```
+-------------+     +----------+     +---------+
| 1.INVENTORY |---->| 2.EMPATHY|---->| 3.PROCESS|
+-------------+     +----------+     +---------+
                                          |
                                          v
                    +---------+     +---------+
                    |5.HEALING|<----| 4.DEBATE |
                    +---------+     +---------+
                         |               |
                         |    (brak      |
                         |  dysonansu)   |
                         v               v
                    +---------+     +---------+
                    | 6.ACTION|<----| 6.ACTION|
                    +---------+     +---------+
                         |
                         | (wymagana ponowna analiza)
                         v
                    +-------------+
                    | 1.INVENTORY |  <-- powrot (max 3 cykle)
                    +-------------+
```

### Sciezki warunkowe

| Warunek                      | Przejscie                     | Opis                                        |
| ---------------------------- | ----------------------------- | ------------------------------------------- |
| **DEBATE: brak dysonansu**   | DEBATE --> ACTION             | Pominiecie HEALING -- dane sa czyste        |
| **DEBATE: dysonans wykryty** | DEBATE --> HEALING --> ACTION | Pelna sciezka transmutacji                  |
| **ACTION: bledne dane**      | ACTION --> INVENTORY          | Powrot do poczatku (nowy cykl)              |
| **ACTION: sukces**           | ACTION --> None               | Zakonczenie pipeline                        |
| **cycles >= 3**              | (dowolny) --> None            | Wymuszony koniec -- zwrot ostatniego wyniku |

---

## Metryki eksportowane

| Metryka                      | Typ         | Opis                                   |
| ---------------------------- | ----------- | -------------------------------------- |
| **Mode Duration**            | int (ms)    | Czas trwania kazdego trybu             |
| **Total Cycles**             | int (1-3)   | Liczba przejsc przez pipeline          |
| **Dissonance Rate**          | float       | Procent requestow wymagajacych HEALING |
| **Agent Selection Accuracy** | float       | Trafnosc doboru agenta w trybie ACTION |
| **Healing Score**            | float (0-1) | Jakosc transmutacji w trybie HEALING   |

---

## Powiazanie z Matryca 3-6-9

Hexagon stanowi **druga warstwe** (warstwa "6") w Matrycy 3-6-9:

- **3** perspektywy Trinity (Material / Intellectual / Essential)
- **6** trybow Hexagon (Inventory / Empathy / Process / Debate / Healing / Action)
- **9** praw Guardian Laws (G1-G9)

Kazdy z 6 trybow Hexagonu operuje **wewnatrz** kazdej z 3 perspektyw Trinity,
a kazda operacja podlega **9 prawom** Guardian Laws.
Daje to **3 x 6 x 9 = 162 wymiary** przestrzeni decyzyjnej.

---

## Konfiguracja

```python
HEXAGON_CONFIG = {
    "inventory_timeout_ms": 500,
    "max_cycles": 3,
    "debate_temperatures": [0.1, 0.5, 0.9],
    "healing_threshold": 0.5,       # min dissonance score to trigger HEALING
    "action_retry_enabled": True,   # czy ACTION moze wrocic do INVENTORY
}
```
