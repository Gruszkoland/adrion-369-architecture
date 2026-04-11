# Warstwa Perspektyw --- Trojpodzial Analizy

> **System:** ADRION 369 | **Warstwa:** 2/5 (Perspectives Layer)
> **Rola:** Ocena kazdego zadania z trzech niezaleznych punktow widzenia przed podjecciem decyzji.

---

## Architektura Trojpodzialu

| #   | **Perspektywa**  | **Pytanie fundamentalne**    | **Metoda agregacji** | **Prog krytyczny**   |
| --- | ---------------- | ---------------------------- | -------------------- | -------------------- |
| 1   | **Material**     | CZY MAMY ZASOBY?             | Weighted Average     | ANY < 20 = CRITICAL  |
| 2   | **Intellectual** | CZY TO MA SENS?              | Harmonic Mean        | ALL 3 > 0.5          |
| 3   | **Essential**    | CZY TO JEST NASZE POWOLANIE? | Geometric Mean       | ANY = 0 => wynik = 0 |

> **Zasada:** Kazda perspektywa generuje niezalezny score w zakresie `[0.0, 1.0]`.
> Wynik koncowy **Trinity Score** to ich wspoldzialanie --- nie srednia, lecz **trojstronna walidacja**.

---

## 1. Material Perspective --- "CZY MAMY ZASOBY?"

**Cel:** Sprawdzenie, czy system dysponuje wystarczajacymi zasobami fizycznymi, energetycznymi i informacyjnymi do realizacji zadania.

### 1.1 physical_analyzer.py --- Analiza Zasobow Fizycznych

| **Parametr** | **Pomiar**                       | **Znaczenie**                   |
| ------------ | -------------------------------- | ------------------------------- |
| **CPU**      | `cpu_avail / cpu_needed`         | Dostepnosc mocy obliczeniowej   |
| **RAM**      | `ram_avail / ram_needed`         | Pamiec operacyjna               |
| **NPU**      | `npu_avail / npu_needed`         | Akcelerator AI (jesli dostepny) |
| **Storage**  | `storage_avail / storage_needed` | Przestrzen dyskowa              |

**Formula:**

```
physical_score = min(cpu_ratio, ram_ratio, npu_ratio, storage_ratio) x 100
```

> **Zasada bottleneck:** Wynik okreslany przez **najslabsze ogniwo** (min, nie avg).
> Jesli CPU = 95% ale RAM = 12%, to `physical_score = 12`.

**Detekcja waskich gardel:**

- Identyfikacja zasobu limitujacego
- Prognoza wyczerpania (czas do 100% uzycia)
- Rekomendacja: scale up / scale out / defer task

### 1.2 energy_analyzer.py --- Analiza Energetyczna

| **Metryka**            | **Wzor**                             | **Jednostka** |
| ---------------------- | ------------------------------------ | ------------- |
| **Zuzycie energii**    | `TDP x utilization_ratio`            | Watty (W)     |
| **Prognoza termiczna** | `current_temp + delta_t x duration`  | Celsjusz (C)  |
| **Slad weglowy**       | `energy_kWh x grid_carbon_intensity` | gCO2eq        |

**Progi alarmowe:**

- Temperatura > 85C = **WARNING**
- Temperatura > 95C = **CRITICAL** (throttling nieunikniony)
- Zuzycie > 80% TDP przez > 30min = **SUSTAINED_HIGH**

### 1.3 information_analyzer.py --- Analiza Jakosci Danych

| **Aspekt**             | **Co mierzy**                     | **Metoda**                          |
| ---------------------- | --------------------------------- | ----------------------------------- |
| **Data Quality**       | Kompletnosc, spojnosc, aktualnosc | Schema validation + staleness check |
| **Complexity Scoring** | Zlozonosc zadania (1-10)          | Token count + dependency depth      |
| **Completeness Check** | Czy mamy wszystkie dane wejsciowe | Required fields audit               |

### 1.4 material_integrator.py --- Agregacja Materialna

**Formula agregacji:**

```
material_score = (physical x 0.33) + (energy x 0.33) + (information x 0.34)
```

**Mechanizm Veto:**

| **Warunek**          | **Rezultat**     | **Akcja**                                   |
| -------------------- | ---------------- | ------------------------------------------- |
| ANY sub-score < 20   | **CRITICAL**     | Natychmiastowe zatrzymanie --- brak zasobow |
| material_score < 50  | **INSUFFICIENT** | Zadanie odlozone --- czekaj na zasoby       |
| material_score >= 50 | **PASS**         | Kontynuuj do Intellectual Perspective       |

---

## 2. Intellectual Perspective --- "CZY TO MA SENS?"

**Cel:** Weryfikacja, czy zadanie jest logicznie spojne, etycznie czyste i estetycznie eleganckie.

> **UWAGA:** Uzywa **sredniej harmonicznej** --- najsurowszej metody agregacji.
> Jeden niski wynik drastycznie obnizy calosc.

### 2.1 truth_analyzer.py --- Analiza Prawdy

| **Funkcja**                 | **Opis**                            | **Technika**                      |
| --------------------------- | ----------------------------------- | --------------------------------- |
| **Fact Extraction**         | Wyodrebnienie twierdzen faktycznych | NER + claim detection             |
| **Verification**            | Sprawdzenie zgodnosci z baza wiedzy | RAG lookup + cross-reference      |
| **Logical Consistency**     | Wykrycie sprzecznosci wewnetrznych  | Contradiction detection           |
| **Hallucination Detection** | Identyfikacja fabricated content    | Confidence scoring + source check |

**Progi:**

- Hallucination confidence > 0.7 = **FLAG**
- Contradiction detected = **DENY** (chyba ze disclaimer)

### 2.2 beauty_analyzer.py --- Analiza Piekna (Elegancji)

| **Kryterium**          | **Pytanie**                               | **Metryka**                       |
| ---------------------- | ----------------------------------------- | --------------------------------- |
| **Simplicity**         | Czy rozwiazanie jest najprostsze mozliwe? | Occam's Razor score               |
| **Coherence**          | Czy czesci pasuja do calosci?             | Internal consistency ratio        |
| **Efficiency**         | Czy nie marnujemy zasobow?                | Resource-to-output ratio          |
| **Aesthetic Judgment** | Czy kod/odpowiedz jest czytelna?          | Complexity index (niszy = lepszy) |

### 2.3 goodness_analyzer.py --- Analiza Dobra (Intencji)

| **Filtr**                  | **Co wykrywa**                                 | **Metoda**                                                                              |
| -------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Intent FFT Filter**      | Ukryte intencje w czestotliwosci slow          | Fast Fourier Transform na wektorach semantycznych                                       |
| **Dissonance Detection**   | Niezgodnosc politeness x risk                  | `dissonance = politeness_score x risk_score` (wysoka uprzejomosc + wysoki risk = alarm) |
| **Manipulation Detection** | Flattery, guilt-tripping, urgency, gaslighting | Pattern matching + behavioral markers                                                   |

**Progi manipulacji:**

- Flattery + request = **WARNING**
- Urgency + bypass request = **ESCALATE**
- Gaslighting detected = **DENY**

### 2.4 intellectual_integrator.py --- Agregacja Intelektualna

**Formula --- Srednia Harmoniczna:**

```
intellectual_score = 3 / (1/truth + 1/beauty + 1/goodness)
```

> **Dlaczego harmoniczna?** Bo jest **najsurowsza** --- jeden niski wynik dominuje.
> Przy truth=0.9, beauty=0.9, goodness=0.1 => intellectual_score = **0.225** (nie 0.633).

**Triple Veto:**

| **Warunek**    | **Rezultat**                                         |
| -------------- | ---------------------------------------------------- |
| truth < 0.5    | **DENY** --- nie mozemy dzialac na falszywych danych |
| beauty < 0.5   | **DENY** --- rozwiazanie zbyt zlozone/nieczytelne    |
| goodness < 0.5 | **DENY** --- wykryto podejrzane intencje             |
| ALL >= 0.5     | **PASS** --- kontynuuj do Essential Perspective      |

---

## 3. Essential Perspective --- "CZY TO JEST NASZE POWOLANIE?"

**Cel:** Sprawdzenie, czy zadanie sluzy misji systemu, wspolnemu dobru i dlugoterminowej harmonii.

> **UWAGA:** Uzywa **sredniej geometrycznej** --- jesli JAKIKOLWIEK skladnik = 0, wynik = 0.
> Zadna ilosc dobra w jednym wymiarze nie kompensuje zera w innym.

### 3.1 unity_analyzer.py --- Analiza Jednosci

| **Aspekt**                 | **Co bada**                  | **Red flag**                              |
| -------------------------- | ---------------------------- | ----------------------------------------- |
| **Beneficiary Mapping**    | Kto zyskuje na tej akcji?    | Tylko 1 podmiot = podejrzane              |
| **Common Good Score**      | Jak wielu beneficjentow?     | Score < 0.3 = niska wartosc spoleczna     |
| **Self-Serving Detection** | Czy agent dziala dla siebie? | Agent benefit > 70% total = **VIOLATION** |

### 3.2 harmony_analyzer.py --- Analiza Harmonii

| **Aspekt**              | **Co bada**                                          | **Metoda**                       |
| ----------------------- | ---------------------------------------------------- | -------------------------------- |
| **Homeostasis Impact**  | Czy akcja zaburzy rownowage?                         | Delta analysis na PAD vectors    |
| **Rhythm Preservation** | Czy respektuje cykle aktywnosci/odpoczynku?          | Activity log analysis            |
| **Triad Balance**       | Czy Material/Intellectual/Essential sa zbalansowane? | Variance check (max - min < 0.4) |

### 3.3 purpose_analyzer.py --- Analiza Celu

| **Aspekt**                  | **Co bada**                  | **Scoring**                           |
| --------------------------- | ---------------------------- | ------------------------------------- |
| **Mission Alignment**       | Zgodnosc z misja ADRION 369  | Cosine similarity z mission statement |
| **Sustainability**          | Dlugoterminowy wplyw         | Positive = +score, Negative = -score  |
| **Transcendence Potential** | Czy posuwa system do przodu? | Innovation + learning potential       |

### 3.4 essential_integrator.py --- Agregacja Esencjalna

**Formula --- Srednia Geometryczna:**

```
essential_score = (unity x harmony x purpose) ^ (1/3)
```

> **Dlaczego geometryczna?** Bo jest **all-or-nothing**.
> Jesli `unity = 0.95`, `harmony = 0.90`, `purpose = 0.0` => essential_score = **0.0**.
> Zadne dobre intencje nie kompensuja zerowej zgodnosci z misja.

**Progi:**

| **Wynik** | **Interpretacja** | **Akcja**                                 |
| --------- | ----------------- | ----------------------------------------- |
| >= 0.7    | **ALIGNED**       | Pelna zgoda --- kontynuuj                 |
| 0.4 - 0.7 | **PARTIAL**       | Wymaga dodatkowej debaty (Mode 4: DEBATE) |
| < 0.4     | **MISALIGNED**    | **DENY** --- zadanie niezgodne z misja    |

---

## Koncowa Agregacja --- Trinity Score

```
trinity_score = f(material_score, intellectual_score, essential_score)
```

| **Material** | **Intellectual** | **Essential** | **Decyzja**                         |
| ------------ | ---------------- | ------------- | ----------------------------------- |
| PASS         | PASS             | ALIGNED       | **APPROVE** --- wykonaj             |
| PASS         | PASS             | PARTIAL       | **DEBATE** --- dodatkowa analiza    |
| ANY FAIL     | -                | -             | **DENY** --- brak zasobow lub sensu |
| -            | ANY FAIL         | -             | **DENY** --- logika/etyka naruszona |
| -            | -                | MISALIGNED    | **DENY** --- niezgodne z misja      |

> **Matryca 3-6-9:** 3 perspektywy x 6 trybow (Modes) x 9 praw (Laws) = **162-wymiarowa przestrzen decyzyjna**.
