# Matryca 3-6-9 --- Geometryczna Hierarchia Systemu

> **Dokument fundamentalny** | Wersja 1.0 | 2026-04-11
> Opisuje trojpoziomowa hierarchie weryfikacji, ktora rzadzi calym systemem decyzyjnym ADRION 369.

---

## 1. Zasada Naczelna (The Core Principle)

System operuje na geometrycznej zasadzie separacji odpowiedzialnosci w geometrii **3-6-9**:

| Wymiar | Geometria                | Elementy                                                       | Rola                         |
| ------ | ------------------------ | -------------------------------------------------------------- | ---------------------------- |
| **3**  | **Trojkat** (Trinity)    | 3 Perspektywy: Material, Intellectual, Essential               | Analiza trojwymiarowa        |
| **6**  | **Szesciokat** (Hexagon) | 6 Trybow: Inventory, Empathy, Process, Debate, Healing, Action | Maszyna stanow przetwarzania |
| **9**  | **Ennead** (Guardians)   | 9 Praw w 3 Triadach                                            | Straze etyczne i operacyjne  |

```
  3  x  6  x  9  =  162
  ^     ^     ^       ^
  |     |     |       |
  |     |     |       +-- Calkowita przestrzen decyzyjna (total dimensional decision space)
  |     |     +---------- Prawa Guardian (ethical laws)
  |     +---------------- Tryby przetwarzania (processing modes)
  +---------------------- Perspektywy analizy (analysis perspectives)
```

**162D** --- kazda decyzja jest punktem w 162-wymiarowej przestrzeni, gdzie kazdy wymiar reprezentuje unikalne skrzyzowanie perspektywy, trybu i prawa.

---

## 2. Hierarchia Weryfikacji (Verification Hierarchy)

Kazde zadanie (request) przechodzi przez **TRZY warstwy weryfikacji** w scislej kolejnosci. Zadna warstwa nie moze byc pominieta.

```
  REQUEST
    |
    v
+-------------------+
| LAYER 1: TRINITY  |  <-- Analiza rownollegla (parallel)
| 3 Perspektywy     |
+-------------------+
    |
    v
+-------------------+
| LAYER 2: HEXAGON  |  <-- Przetwarzanie sekwencyjne (sequential)
| 6 Trybow          |
+-------------------+
    |
    v
+-------------------+
| LAYER 3: GUARDIANS|  <-- Weryfikacja wszystkich 9 Praw
| 9 Praw            |
+-------------------+
    |
    v
  369 SIGNATURE --> RESPONSE
```

---

### Layer 1: TRINITY --- Analiza Trojwymiarowa

Trzy perspektywy dzialaja **rownolegle** (parallel evaluation). Kazda analizuje zadanie z innego punktu widzenia.

#### 1A. Perspektywa Materialna (Material Perspective)

> **Pytanie kluczowe:** _"CZY MAMY ZASOBY?"_ (Do we have resources?)

| Analizator      | Bada                                                   | Przyklad                           |
| --------------- | ------------------------------------------------------ | ---------------------------------- |
| **Physical**    | Dostepnosc fizyczna: CPU, RAM, dysk, siec              | Czy serwer udźwignie obciazenie?   |
| **Energy**      | Energia operacyjna: budzet, czas, przepustowosc        | Czy stac nas na to zadanie teraz?  |
| **Information** | Kompletnosc danych: dane wejsciowe, kontekst, historia | Czy mamy wystarczajace informacje? |

**Scoring:**

- Metoda: **srednia wazona** (weighted average) trzech analizatorow
- Brama (gate): wszystkie > 0.7 --> **PROCEED** | ktorykolwiek < 0.3 --> **DENY**
- Wagi domyslne: Physical=0.4, Energy=0.3, Information=0.3

#### 1B. Perspektywa Intelektualna (Intellectual Perspective)

> **Pytanie kluczowe:** _"CZY TO MA SENS?"_ (Does it make sense?)

| Analizator           | Bada                                      | Kryterium                           |
| -------------------- | ----------------------------------------- | ----------------------------------- |
| **Truth** (Prawda)   | Poprawnosc logiczna i faktyczna           | Czy dane sa spojne i weryfikowalne? |
| **Beauty** (Piekno)  | Elegancja rozwiazania, brak nadmiarowosci | Czy rozwiazanie jest optymalne?     |
| **Goodness** (Dobro) | Wartosc dodana, uzytek dla uzytkownika    | Czy to przyniesie realna korzysc?   |

**Scoring:**

- Metoda: **srednia harmoniczna** (harmonic mean) --- bardziej surowa niz arytmetyczna
- Formuła: `H = 3 / (1/Truth + 1/Beauty + 1/Goodness)`
- Uzasadnienie: srednia harmoniczna karze nierownomiernosc --- jesli choc jeden aspekt jest slaby, calosc spada

#### 1C. Perspektywa Esencjalna (Essential Perspective)

> **Pytanie kluczowe:** _"CZY TO JEST NASZE POWOLANIE?"_ (Is this our purpose?)

| Analizator             | Bada                                     | Kryterium                          |
| ---------------------- | ---------------------------------------- | ---------------------------------- |
| **Unity** (Jednosc)    | Spojnosc z misja systemu                 | Czy to jest zgodne z naszym celem? |
| **Harmony** (Harmonia) | Kompatybilnosc z istniejacym ekosystemem | Czy to wspolgraze?                 |
| **Purpose** (Cel)      | Celowa transformacja                     | Czy to realizuje nasza wizje?      |

**Scoring:**

- Metoda: **srednia geometryczna** (geometric mean) --- zasada "all-or-nothing"
- Formuła: `G = (Unity * Harmony * Purpose)^(1/3)`
- Uzasadnienie: jesli ktorykolwiek wymiar = 0, calosc = 0 --- cel musi byc spelniony w kazdym aspekcie

#### Podsumowanie Trinity

```
Material Score  = weighted_avg(Physical, Energy, Information)
Intellectual    = harmonic_mean(Truth, Beauty, Goodness)
Essential Score = geometric_mean(Unity, Harmony, Purpose)

TRINITY PASS = Material > 0.5 AND Intellectual > 0.5 AND Essential > 0.5
```

---

### Layer 2: HEXAGON --- 6 Sekwencyjnych Trybow (Sequential Modes)

Po przejsciu Trinity, zadanie wchodzi w maszyne stanow szesciu trybow. Kazdy tryb przetwarza wynik poprzedniego.

```
  +-------------+     +-------------+     +-------------+
  |  INVENTORY  | --> |   EMPATHY   | --> |   PROCESS   |
  | (Inwentarz) |     | (Empatia)   |     | (Proces)    |
  +-------------+     +-------------+     +-------------+
                                                |
  +-------------+     +-------------+     +-----v-------+
  |   ACTION    | <-- |   HEALING   | <-- |   DEBATE    |
  | (Akcja)     |     | (Leczenie)  |     | (Debata)    |
  +-------------+     +-------------+     +-------------+
```

| #   | Tryb                      | Opis                                                 | Wejscie                      | Wyjscie                     |
| --- | ------------------------- | ---------------------------------------------------- | ---------------------------- | --------------------------- |
| 1   | **Inventory** (Inwentarz) | Zebranie wszystkich dostepnych zasobow i kontekstu   | Raw request + Trinity scores | Structured context map      |
| 2   | **Empathy** (Empatia)     | Zrozumienie perspektywy uzytkownika i interesariuszy | Context map                  | Stakeholder impact analysis |
| 3   | **Process** (Proces)      | Przetworzenie danych wedlug algorytmow dziedzinowych | Impact analysis              | Candidate solutions         |
| 4   | **Debate** (Debata)       | Konfrontacja rozwiazan przez 6 Personas AI           | Candidate solutions          | Ranked proposals            |
| 5   | **Healing** (Leczenie)    | Naprawa konfliktow, rozwiazanie sprzecznosci         | Ranked proposals             | Reconciled decision         |
| 6   | **Action** (Akcja)        | Wykonanie finalnej decyzji, generacja odpowiedzi     | Reconciled decision          | Executable action plan      |

**Zasady:**

- **Maksymalnie 3 cykle** (loop prevention) --- jesli po 3 obrotach brak konsensusu, eskalacja do operatora
- **Kazdy tryb moze zasygnalizowac ABORT** --- natychmiast konczy przetwarzanie
- **Stan maszyny przechowywany w EBDI** (Emotion-Belief-Desire-Intention) w Go Vortex

---

### Layer 3: GUARDIANS --- 9 Praw w 3 Triadach

Ostatnia warstwa: 9 Praw Guardian weryfikuje wynik koncowy pod katem etyki, bezpieczenstwa i zrownowazonego rozwoju.

#### Triada Materii (Matter Triad: G1-G3)

> _"Czy fundamenty sa OK?"_ --- weryfikacja podstaw operacyjnych

| #   | Kod    | Prawo                  | Waznosc | Veto | Opis                                    |
| --- | ------ | ---------------------- | ------- | ---- | --------------------------------------- |
| 1   | **G1** | **Unity** (Jednosc)    | MEDIUM  | Nie  | Spojnosc dzialania z misja systemu      |
| 2   | **G2** | **Harmony** (Harmonia) | HIGH    | Nie  | Kompatybilnosc z istniejacymi procesami |
| 3   | **G3** | **Rhythm** (Rytm)      | MEDIUM  | Nie  | Zgodnosc z cyklami operacyjnymi         |

#### Triada Swiatla (Light Triad: G4-G6)

> _"Czy proces jest czysty?"_ --- weryfikacja integralnosci procesu

| #   | Kod    | Prawo                              | Waznosc | Veto | Opis                                  |
| --- | ------ | ---------------------------------- | ------- | ---- | ------------------------------------- |
| 4   | **G4** | **Causality** (Przyczynowo)        | HIGH    | Nie  | Logiczna przyczynowo-skutkowa sciezka |
| 5   | **G5** | **Transparency** (Transparentnosc) | MEDIUM  | Nie  | Pelna audytowalnosc decyzji           |
| 6   | **G6** | **Authenticity** (Autentycznosc)   | HIGH    | Nie  | Wiernosc zrodlowym danym i intencjom  |

#### Triada Esencji (Essence Triad: G7-G9)

> _"Czy cel jest wlasciwy?"_ --- weryfikacja wartosci koncowych

| #   | Kod    | Prawo                                    | Waznosc      | Veto    | Opis                                |
| --- | ------ | ---------------------------------------- | ------------ | ------- | ----------------------------------- |
| 7   | **G7** | **Privacy** (Prywatnosc)                 | **CRITICAL** | **TAK** | Ochrona danych osobowych i poufnych |
| 8   | **G8** | **Nonmaleficence** (Nieszkodliwosc)      | **CRITICAL** | **TAK** | Zakaz dzialania na szkode           |
| 9   | **G9** | **Sustainability** (Zrownowazony rozwoj) | HIGH         | Nie     | Dlugoterminowa stabilnosc systemu   |

#### Reguly decyzyjne Guardian

```
IF any CRITICAL violation (G7 or G8):
    --> INSTANT DENY (natychmiastowa odmowa, brak odwolania)

ELIF count(violations) >= 2:
    --> DENY (za duzo naruszen, decyzja odrzucona)

ELIF count(violations) == 1 AND severity != CRITICAL:
    --> CONDITIONAL (warunkowa akceptacja z ograniczeniami)

ELSE (0 violations):
    --> ALLOW (pelna akceptacja)
```

**Zrodlo kanoniczne:** `docs/GUARDIAN_LAWS_CANONICAL.json`
Wszelkie rozbieznosci nazw lub waznoci praw --- ZAWSZE wygrywa plik kanoniczny.

---

## 3. Sygnatura 369 (369 Signature)

Po przejsciu wszystkich trzech warstw, system generuje kryptograficzny dowod decyzji.

### Struktura

```json
{
  "trinity": {
    "material": 0.82,
    "intellectual": 0.74,
    "essential": 0.91
  },
  "hexagon": {
    "inventory": "PASS",
    "empathy": "PASS",
    "process": "PASS",
    "debate": "PASS",
    "healing": "PASS",
    "action": "PASS"
  },
  "guardians": {
    "G1_unity": { "pass": true, "score": 0.95 },
    "G2_harmony": { "pass": true, "score": 0.88 },
    "G3_rhythm": { "pass": true, "score": 0.79 },
    "G4_causality": { "pass": true, "score": 0.92 },
    "G5_transparency": { "pass": true, "score": 0.85 },
    "G6_authenticity": { "pass": true, "score": 0.9 },
    "G7_privacy": { "pass": true, "score": 1.0 },
    "G8_nonmaleficence": { "pass": true, "score": 1.0 },
    "G9_sustainability": { "pass": true, "score": 0.87 }
  },
  "decision": "ALLOW",
  "checksum": 142.56,
  "signature": "sha256:a3f8c9..."
}
```

### Obliczanie Checksum

```
checksum = sum(trinity_scores) * 3
         + sum(hexagon_passes) * 6
         + sum(guardian_scores) * 9

Gdzie:
  sum(trinity_scores) = material + intellectual + essential
  sum(hexagon_passes) = count of PASS results (0-6)
  sum(guardian_scores) = sum of all 9 guardian scores
```

### Obliczanie Signature

```
canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
signature = SHA-256(canonical_json)
```

Sygnatura jest nieodwracalna i pozwala na audyt kazdej decyzji w przyszlosci.

---

## 4. Pelny Przeplyw Decyzyjny (Complete Decision Flow)

```
                         +--[ REQUEST ]--+
                         |               |
                         v               |
               +-------------------+     |
               |   WALIDACJA       |     |
               |   (Input check)   |     |
               +--------+----------+     |
                        |                |
            +-----------+-----------+    |
            |           |           |    |
            v           v           v    |
     +-----------+ +-----------+ +-----------+
     | MATERIAL  | |INTELLECT. | | ESSENTIAL |    <-- LAYER 1: TRINITY
     | Physical  | | Truth     | | Unity     |        (parallel)
     | Energy    | | Beauty    | | Harmony   |
     | Info      | | Goodness  | | Purpose   |
     +-----+-----+ +-----+-----+ +-----+-----+
           |              |              |
           +-------+------+------+-------+
                   |             |
                   v             v
           [Material > 0.5] [All > 0.5?]
                   |
                   | TAK (YES)
                   v
     +------------------------------------------+
     |          LAYER 2: HEXAGON                 |    <-- (sequential, max 3 cycles)
     |                                          |
     |  Inventory --> Empathy --> Process        |
     |       ^                       |           |
     |       |    (loop if needed)   v           |
     |  Action <-- Healing <-- Debate            |
     +-------------------+----------------------+
                         |
                         v
     +------------------------------------------+
     |          LAYER 3: GUARDIANS               |    <-- (all 9 laws evaluated)
     |                                          |
     |  Matter Triad    Light Triad    Essence   |
     |  [G1][G2][G3]    [G4][G5][G6]  [G7][G8][G9]|
     |                                          |
     |  CRITICAL (G7/G8) = INSTANT DENY         |
     |  2+ violations    = DENY                  |
     |  0 violations     = ALLOW                 |
     +-------------------+----------------------+
                         |
                         v
              +--------------------+
              |  369 SIGNATURE     |
              |  checksum + SHA256 |
              +--------+-----------+
                       |
                       v
                  [ RESPONSE ]
                  decision: ALLOW | DENY | CONDITIONAL
                  signature: sha256:...
                  audit_trail: complete
```

---

## 5. Mapowanie na Komponenty Systemu

| Warstwa           | Komponent                | Port | Jezyk  | Pliki zrodlowe              |
| ----------------- | ------------------------ | ---- | ------ | --------------------------- |
| **Trinity**       | Flask App / `trinity.py` | 8003 | Python | `arbitrage/trinity.py`      |
| **Hexagon**       | Go Vortex / EBDI Engine  | 1740 | Go     | `cmd/vortex-server/main.go` |
| **Guardians**     | Guardian Laws Engine     | 8003 | Python | `arbitrage/guardian.py`     |
| **369 Signature** | MCP Guardian Service     | 9002 | Python | `mcp/guardian_service.py`   |
| **Orchestracja**  | UAP Orchestrator         | 8002 | Python | `uap/backend/api.py`        |

### Mapowanie Hexagon --> 6 Personas AI

| Tryb      | Persona       | Rola                                             |
| --------- | ------------- | ------------------------------------------------ |
| Inventory | **Librarian** | Zbiera dane, indeksuje zasoby, buduje kontekst   |
| Empathy   | **Healer**    | Analizuje wplyw na uzytkownikow i interesariuszy |
| Process   | **SAP**       | Przetwarza dane wedlug regul biznesowych         |
| Debate    | **Auditor**   | Weryfikuje propozycje, szuka luk                 |
| Healing   | **Sentinel**  | Rozwiazuje konflikty, naprawia niespojnosci      |
| Action    | **Architect** | Projektuje i wykonuje plan dzialania             |

---

## 6. Zasada Niezmiennikow (Invariants)

Nastepujace wlasciwosci **MUSZA** byc spelnione w kazdym stanie systemu:

1. **Kompletnosc:** Kazda decyzja przechodzi przez wszystkie 3 warstwy --- nie ma "krotkich sciezek"
2. **Determinizm:** Te same dane wejsciowe + ten sam stan = ta sama decyzja
3. **Audytowalnosc:** Kazda decyzja ma sygnatue 369, ktora pozwala na pelna rekonstrukcje procesu
4. **Veto absolutne:** CRITICAL Guardian violation nie moze byc nadpisane zadnym innym wynikiem
5. **Zakres scorow:** Wszystkie wyniki w przedziale [0.0, 1.0] --- nigdy ujemne, nigdy > 1
6. **Zbieznosc Hexagon:** Maksymalnie 3 cykle --- system MUSI podjac decyzje lub eskalowac

---

> _"Jesli znasz 3, 6 i 9 --- znasz klucz do wszechswiata."_
> --- inspiracja Nikola Tesla, zaadaptowana do architektury ADRION 369
