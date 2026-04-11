# Trinity -- System Trzech Perspektyw

> **Modul:** `core/trinity.py`
> **Wersja:** 4.0 | **Status:** Aktywny
> **Matryca:** 3 perspektywy (LOGOS / ETHOS / EROS)

---

## Cel

**Orkiestracja trojwymiarowej analizy** w przestrzeni Material-Intellectual-Essential.
Kazde zapytanie uzytkownika przechodzi przez **trzy niezalezne perspektywy** rownoczesnie,
a wynik koncowy to **wazony sredni wynik** (Trinity Score) decydujacy o losie requestu.

---

## Jak dziala Trinity -- Pipeline krok po kroku

### 1. Input -- Odbiór zapytania

Surowy request uzytkownika trafia do Trinity Engine.
**Walidacja wejscia:** sprawdzenie formatu, obecnosci wymaganych pol, sanityzacja danych.

### 2. Delegation -- Wysylka do 3 perspektyw ROWNOCZESNIE

```
Request
  |
  +---> [Material Perspective]      # Zasoby, koszty, wykonalnosc
  |          |
  +---> [Intellectual Perspective]  # Logika, spojnosc, poprawnosc
  |          |
  +---> [Essential Perspective]     # Etyka, wartosc, wplyw na system
```

**Kluczowe:** wszystkie trzy perspektywy uruchamiaja sie **PARALLEL** (rownolegle),
nie sekwencyjnie. Kazda perspektywa zwraca score w zakresie `[0.0, 1.0]`.

### 3. Waiting -- Timeout 5 sekund

**Maksymalny czas oczekiwania: 5000 ms.**
Jesli ktorakolwiek perspektywa nie odpowie w ciagu 5 sekund:

- Zwraca **domyslny score = 0.0** (fail-safe)
- Loguje timeout warning
- Pipeline kontynuuje z dostepnymi wynikami

### 4. Synthesis -- Obliczanie Trinity Score

**Formula wazenia:**

```
Trinity Score = (w_m * S_material) + (w_i * S_intellectual) + (w_e * S_essential)
```

Gdzie:

- **S_material** -- score perspektywy materialnej `[0.0, 1.0]`
- **S_intellectual** -- score perspektywy intelektualnej `[0.0, 1.0]`
- **S_essential** -- score perspektywy esencjalnej `[0.0, 1.0]`
- **w_m, w_i, w_e** -- wagi (domyslnie: `w_m = 0.33, w_i = 0.34, w_e = 0.33`)

**Wynik koncowy:** `Trinity Score` -- wartosc z zakresu `[0.0, 1.0]`

### 5. Balance Check -- Kontrola rownowagi wymiarowej

**Formula odchylenia standardowego:**

```
mean = (S_material + S_intellectual + S_essential) / 3

std_dev = sqrt(
    ((S_material - mean)^2 + (S_intellectual - mean)^2 + (S_essential - mean)^2) / 3
)

Dimensional Balance = 1.0 - std_dev
```

**Prog nierownowagi: std_dev > 0.3**

Jesli odchylenie standardowe przekracza **0.3**, system oznacza wynik jako **IMBALANCED**.
Oznacza to, ze perspektywy sa zbyt rozbiezone -- jedna daje wysoki score,
a inna niski -- co wymaga interwencji lub eskalacji.

### 6. Decision Gate -- Brama decyzyjna

```
+--------------------------------------------------+
|              DECISION GATE LOGIC                  |
+--------------------------------------------------+
|                                                   |
|  IF all 3 scores > 0.7:                          |
|      --> PROCEED   (kontynuuj operacje)          |
|                                                   |
|  IF any score < 0.3:                             |
|      --> DENY      (odrzuc zapytanie)            |
|                                                   |
|  OTHERWISE (scores miedzy 0.3 a 0.7):           |
|      --> ESCALATE  (eskaluj do wyzszej decyzji)  |
|                                                   |
+--------------------------------------------------+
```

**Reguly bramy decyzyjnej:**

| Warunek                 | Decyzja      | Opis                                                 |
| ----------------------- | ------------ | ---------------------------------------------------- |
| **Wszystkie 3 > 0.7**   | **PROCEED**  | Pelna zgoda perspektyw -- operacja bezpieczna        |
| **Ktorykolwiek < 0.3**  | **DENY**     | Krytyczny deficyt w jednym wymiarze -- blokada       |
| **Pozostale przypadki** | **ESCALATE** | Niepewnosc -- wymaga recenzji lub dodatkowej analizy |

---

## Metryki eksportowane

| Metryka                 | Typ   | Zakres       | Opis                                             |
| ----------------------- | ----- | ------------ | ------------------------------------------------ |
| **Trinity Score**       | float | `[0.0, 1.0]` | Wazona srednia trzech perspektyw                 |
| **Dimensional Balance** | float | `[0.0, 1.0]` | `1.0 - std_dev` (im wyzej, tym lepsza rownowaga) |
| **Processing Time**     | int   | milisekundy  | Calkowity czas przetwarzania pipeline            |

---

## Zaleznosci (Dependencies)

```
core/trinity.py
  |
  +---> perspectives/material.py       # Analiza zasobow i kosztow
  +---> perspectives/intellectual.py   # Analiza logiczna i spojnosciowa
  +---> perspectives/essential.py      # Analiza etyczna i wartosciowa
```

**Kazdy modul perspektywy** implementuje interfejs:

```python
def evaluate(request: dict, context: dict) -> PerspectiveResult:
    """Zwraca score [0.0, 1.0] i uzasadnienie."""
    ...
```

---

## Przyklad przeplywu

```
User Request: "Wykonaj arbitraz na produkcie X"
  |
  +--> Material:      score = 0.85  (zasoby dostepne, koszt akceptowalny)
  +--> Intellectual:  score = 0.72  (logika poprawna, brak sprzecznosci)
  +--> Essential:     score = 0.91  (etycznie bezpieczne, brak naruszen)
  |
  Trinity Score = (0.33 * 0.85) + (0.34 * 0.72) + (0.33 * 0.91) = 0.826
  Std Dev = 0.079 (< 0.3 -- BALANCED)
  Decision: PROCEED (wszystkie > 0.7)
```

---

## Powiazanie z Matryca 3-6-9

Trinity stanowi **pierwsza warstwe** (warstwa "3") w Matrycy 3-6-9:

- **3** perspektywy Trinity (Material / Intellectual / Essential)
- **6** trybow Hexagon (Inventory / Empathy / Process / Debate / Healing / Action)
- **9** praw Guardian Laws (G1-G9)

Razem tworza **przestrzen decyzyjna 162D** (3 x 6 x 9 = 162 wymiarow).
