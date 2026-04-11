# **Warstwa Inteligencji -- Agenty i Uczenie**

> **Warstwa 11** | ADRION 369 — Multi-Agent AI Orchestration System
> Dokument opisuje architekture wieloagentowa, system archetypow, panel skeptykow oraz petle samodoskonalenia.

---

## **Agent Swarm (9 Specjalistycznych Agentow)**

System ADRION 369 wykorzystuje **roj 9 wyspecjalizowanych agentow AI**, z ktorych kazdy odpowiada za odrebna domene wiedzy i dzialania. Agenty operuja rownolegle w ramach **Trinity-EBDI 162D Decision Framework**, komunikujac sie przez wspoldzielony kontekst decyzyjny.

### **Librarian** — Zarzadzanie Wiedza

- **Domena:** Knowledge management, fact retrieval, dokumentacja systemowa
- **Odpowiedzialnosc:**
  - Indeksowanie i przeszukiwanie **Genesis Record** (baza wiedzy projektu)
  - Wyszukiwanie faktow i precedensow decyzyjnych
  - Utrzymywanie spojnosci dokumentacji miedzy komponentami
  - Dostarczanie kontekstu historycznego dla decyzji agentow
- **Port MCP:** `9004` (Genesis microservice)
- **Kluczowe API:** `GET /genesis/search`, `POST /genesis/index`, `GET /genesis/facts`

### **SAP** — Analiza Procesow Biznesowych

- **Domena:** Business process analysis, compliance checking
- **Odpowiedzialnosc:**
  - Analiza procesow biznesowych pod katem efektywnosci i zgodnosci
  - Weryfikacja compliance z regulacjami (GDPR, PCI-DSS, SOC2)
  - Mapowanie procesow na wymagania **Guardian Laws**
  - Generowanie raportow zgodnosci i audytow procesowych
- **Integracja:** Wspolpraca z **Auditor** przy walidacji i z **Sentinel** przy kontroli dostepu

### **Auditor** — Audyt Jakosci i Bezpieczenstwa

- **Domena:** Code review, security auditing, quality assurance
- **Odpowiedzialnosc:**
  - Przeglad kodu pod katem bezpieczenstwa (SQL injection, XSS, CSRF)
  - Audyt jakosci — zgodnosc z wzorcami architektonicznymi
  - Walidacja **Guardian Laws** w kontekscie zmian kodu
  - Generowanie raportow audytowych z rekomendacjami
- **Walidacja:** Kazda decyzja Auditor przechodzi przez **Skeptics Panel** (3 niezalezne glosy)

### **Sentinel** — Monitoring Bezpieczenstwa

- **Domena:** Security monitoring, threat detection, access control
- **Odpowiedzialnosc:**
  - Ciagle monitorowanie zagrozne systemowych w czasie rzeczywistym
  - Wykrywanie anomalii w ruchu sieciowym i zachowaniu uzytkownikow
  - Zarzadzanie kontrola dostepu i uprawnieniami
  - Egzekwowanie **Guardian Law G7 (Privacy)** i **G8 (Nonmaleficence)** — prawa CRITICAL z prawem veto
- **Port MCP:** `9002` (Guardian microservice)
- **Reakcja:** Natychmiastowe **DENY** przy wykryciu naruszen CRITICAL

### **Architect** — Projektowanie Systemow

- **Domena:** System design, architecture decisions, technical planning
- **Odpowiedzialnosc:**
  - Podejmowanie decyzji architektonicznych w ramach **Trinity Score**
  - Planowanie techniczne z uwzglednieniem 3 perspektyw (Material/Intellectual/Essential)
  - Projektowanie nowych komponentow i integracji
  - Utrzymywanie spojnosci architektonicznej miedzy Flask, Go Vortex i MCP Layer
- **Framework decyzyjny:** Kazda decyzja oceniana w przestrzeni **162D** (3 x 6 x 9)

### **Healer** — Naprawa i Regulacja Emocjonalna

- **Domena:** Error recovery, system healing, emotional regulation
- **Odpowiedzialnosc:**
  - Automatyczna naprawa bledow i przywracanie stabilnosci systemu
  - Zarzadzanie **Circuit Breaker** — otwarcie/zamkniecie obwodow dla LLM, Stripe, Apify, XRP
  - Regulacja stanu emocjonalnego agentow (wektor **PAD**: Pleasure-Arousal-Dominance)
  - Balansowanie temperatury decyzyjnej po stresujacych zdarzeniach
- **Port MCP:** `9005` (Healer microservice)
- **Mechanizm:** Etap 5 Hexagonu — **Healing** — uruchamiany po kazdym cyklu decyzyjnym

### **Navigator** — Organizacja i Routing

- **Domena:** Data organization, routing, resource discovery
- **Odpowiedzialnosc:**
  - Organizacja przeplywu danych miedzy agentami
  - Routing zapytan do odpowiednich specjalistow
  - Odkrywanie i mapowanie zasobow systemowych
  - Optymalizacja sciezek komunikacji w architekturze MCP
- **Integracja:** Wspolpraca z **MCP Router** (port `9000`) jako warstwa orkiestracji

### **Creator** — Generowanie i Tworzenie

- **Domena:** Code generation, content creation, creative solutions
- **Odpowiedzialnosc:**
  - Generowanie kodu na podstawie specyfikacji architektonicznych
  - Tworzenie tresci dokumentacyjnych i raportow
  - Proponowanie kreatywnych rozwiazan problemow technicznych
  - Generowanie prototypow i proof-of-concept
- **LLM Backend:** Ollama (lokalne) z fallback na OpenRouter, **canary deploy** dla nowych modeli

### **Broker** — Alokacja Zasobow i Optymalizacja

- **Domena:** Resource allocation, negotiation, optimization
- **Odpowiedzialnosc:**
  - Alokacja zasobow obliczeniowych miedzy agentami
  - Negocjowanie priorytetow miedzy konkurujacymi zadaniami
  - Optymalizacja kosztow operacyjnych (LLM tokens, API calls, compute)
  - Zarzadzanie **Rate Limiter** — sliding window, per-endpoint throttling
- **Metryki:** Koszt per decyzja, utilization rate, throughput agentow

---

## **Archetypes (System Osobowosci)**

Kazdy agent moze przyjac jeden z **4 archetypow**, ktore ksztaltuja jego zachowanie decyzyjne. Archetypy sa dynamiczne — agent przesuwa sie miedzy nimi w zaleznosci od kontekstu i stanu emocjonalnego (**PAD vector**).

### **Guardian** — Straznik

- **Charakterystyka:** Konserwatywny, bezpieczenstwo jako priorytet, awersja do ryzyka
- **Temperatura decyzyjna:** Niska (T=0.1-0.3)
- **Dominujace Guardian Laws:** G7 Privacy, G8 Nonmaleficence, G9 Sustainability
- **Kiedy aktywowany:**
  - Wykrycie zagrozen bezpieczenstwa
  - Operacje na danych wrazliwych
  - Decyzje z nieodwracalnymi konsekwencjami
- **Zachowanie:** Preferuje sprawdzone rozwiazania, wymaga dodatkowej walidacji, czesto eskaluje do **Skeptics Panel**

### **Rebel** — Buntownik

- **Charakterystyka:** Kreatywny, przesuwajacy granice, innowacyjny
- **Temperatura decyzyjna:** Wysoka (T=0.7-0.9)
- **Dominujace Guardian Laws:** G1 Unity, G3 Rhythm, G6 Authenticity
- **Kiedy aktywowany:**
  - Zadania wymagajace kreatywnych rozwiazan
  - Prototypowanie i eksploracja
  - Przezwyciezanie blokad decyzyjnych
- **Zachowanie:** Proponuje nietypowe podejscia, kwestionuje zalozenia, toleruje wyzsze ryzyko

### **Sage** — Medrzec

- **Charakterystyka:** Madry, syntetyzujacy, zrownowazona perspektywa
- **Temperatura decyzyjna:** Srednia (T=0.4-0.6)
- **Dominujace Guardian Laws:** G2 Harmony, G4 Causality, G5 Transparency
- **Kiedy aktywowany:**
  - Zlezone decyzje wymagajace wielu perspektyw
  - Konflikty miedzy agentami
  - Strategiczne planowanie dlugoterminowe
- **Zachowanie:** Syntetyzuje sprzeczne stanowiska, szuka rownowagi, uwzglednia dlugoterminowe konsekwencje

### **Shadow** — Cien

- **Charakterystyka:** Czujny, wykrywajacy ukryte zagrozenia, podejrzliwy
- **Temperatura decyzyjna:** Bardzo niska (T=0.05-0.2)
- **Dominujace Guardian Laws:** G7 Privacy, G8 Nonmaleficence, G4 Causality
- **Kiedy aktywowany:**
  - Podejrzenie manipulacji lub ataku
  - Analiza edge cases i scenariuszy awarii
  - Weryfikacja integralnosci danych
- **Zachowanie:** Szuka ukrytych wad, analizuje najgorsze scenariusze, weryfikuje zalozenia innych agentow

### **Dynamika Przejsc Miedzy Archetypami**

```
           Niskie ryzyko          Wysokie ryzyko
           Stabilny PAD           Niestabilny PAD
                |                       |
    Rebel <-----.-----> Sage <-----.-----> Guardian
                |                       |
                v                       v
             Creator               Shadow/Sentinel
           (tworzenie)            (ochrona/analiza)
```

**Czynniki wplywajace na przesuniecie:**

- **Wektor PAD** (Pleasure-Arousal-Dominance) — stan emocjonalny agenta
- **Kontekst zadania** — typ operacji, poziom ryzyka, wrazliwosc danych
- **Historia doswiadczen** — wzorce sukcesu/porazki z **Transcendence Loop**
- **Sygnaly od innych agentow** — eskalacje, ostrzezenia, rekomendacje

---

## **Skeptics Panel**

**Skeptics Panel** to mechanizm **trojstronnej walidacji**, ktory zapewnia obiektywnosc decyzji krytycznych. Wykorzystuje **3 niezalezne instancje Claude** operujace na roznych temperaturach, glosujace niezaleznie nad kazda decyzja.

### **Sklad Panelu**

| Rola             | Temperatura | Profil                               | Wrazliwosc na ryzyko                              |
| ---------------- | ----------- | ------------------------------------ | ------------------------------------------------- |
| **Conservative** | T=0.1       | Wysoka ostrozosc, minimalne ryzyko   | **Wysoka** — flaguje nawet marginalne zagrozenia  |
| **Balanced**     | T=0.5       | Umiarkowana ocena, pragmatyzm        | **Srednia** — wazy ryzyko vs. korzysci            |
| **Creative**     | T=0.9       | Niska ostrozosc, kreatywne podejscie | **Niska** — akceptuje wyzsze ryzyko dla innowacji |

### **Proces Glosowania**

```
  Decyzja do walidacji
         |
    +----+----+----+
    |         |         |
    v         v         v
[T=0.1]   [T=0.5]   [T=0.9]
Conservative Balanced  Creative
    |         |         |
    v         v         v
  DENY     APPROVE   APPROVE
    |         |         |
    +----+----+----+
         |
    Consensus Engine
         |
    +---------+---------+
    |         |         |
  3x DENY  2x DENY   3x APPROVE
  = DENY   = ESCALATE = APPROVE
```

### **Reguly Konsensusu**

- **3x DENY** — Natychmiastowe odrzucenie. Decyzja zablokowana.
- **3x APPROVE** — Pelna zgoda. Decyzja zatwierdzona.
- **2x DENY + 1x APPROVE** — **ESCALATE** — przekazanie do czlowieka lub wyzszego poziomu decyzyjnego.
- **1x DENY + 2x APPROVE** — **ESCALATE** — jesli DENY pochodzi od Conservative (T=0.1), traktowane powazniej.
- **Veto CRITICAL:** Jesli jakikolwiek glos identyfikuje naruszenie **Guardian Law G7 (Privacy)** lub **G8 (Nonmaleficence)**, wynik = **DENY** niezaleznie od pozostalych glosow.

### **Kiedy Uruchamiany**

- Decyzje o severity **HIGH** lub **CRITICAL**
- Operacje na danych osobowych (GDPR scope)
- Transakcje finansowe powyzej progu
- Zmiany architektoniczne wplywajace na wiecej niz 1 komponent
- Eskalacje od agentow w archetypie **Shadow**

---

## **Transcendence Loop (Petla Samodoskonalenia)**

**Transcendence Loop** to mechanizm ciaglego uczenia sie systemu agentowego. Kazde doswiadczenie jest rejestrowane, analizowane i wykorzystywane do ewolucji agentow.

### **Etap 1: Experience Collection**

Kazde zadanie wykonane przez agenta generuje rekord **Experience**:

```
Experience {
    task_id:          string       // identyfikator zadania
    agent_id:         string       // ktory agent wykonal
    archetype:        string       // aktywny archetyp w momencie wykonania
    temperature:      float        // temperatura decyzyjna
    context: {
        domain:       string       // domena zadania
        complexity:   int          // zlozonosc (1-10)
        risk_level:   string       // LOW/MEDIUM/HIGH/CRITICAL
        guardian_laws: []string    // ktore Guardian Laws byly relevantne
    }
    outcome: {
        success:      bool         // czy zadanie zakonczone sukcesem
        trinity_score: {
            material:     float    // wynik materialny
            intellectual: float    // wynik intelektualny
            essential:    float    // wynik esencjonalny
        }
        guardian_violations: []string  // naruszone prawa (jesli jakiekolwiek)
    }
    emotional_state: {
        pleasure:     float        // P w PAD (-1.0 do 1.0)
        arousal:      float        // A w PAD (-1.0 do 1.0)
        dominance:    float        // D w PAD (-1.0 do 1.0)
    }
    lessons: []string              // wyciagniete wnioski (auto-generowane)
    timestamp:        datetime     // czas wykonania
}
```

### **Etap 2: Pattern Extraction (co 100 doswiadczen)**

Po zgromadzeniu **100 nowych doswiadczen** system uruchamia analize wzorcow:

- **Clustering sukcesu/porazki:** Grupowanie doswiadczen wedlug kontekstu (domena, zlozonosc, archetyp) i wyniku
- **Identyfikacja wzorcow:**
  - Ktore kombinacje archetyp + temperatura daja najlepsze wyniki w danej domenie
  - Ktore Guardian Laws sa najczesciej naruszane i przez ktorych agentow
  - Korelacje miedzy stanem emocjonalnym a jakoscia decyzji
- **Anomalie:** Wykrywanie nagylch zmian w skutecznosci agentow

### **Etap 3: Agent Evolution**

Na podstawie wyekstrahowanych wzorcow system aktualizuje parametry agentow:

| Parametr                   | Mechanizm aktualizacji                                 | Przyklad                                                          |
| -------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------- |
| **System prompts**         | Dodanie nowych instrukcji na podstawie lessons learned | "Zwracaj szczegolna uwage na SQL injection w UPDATE statements"   |
| **Temperatura bazowa**     | Adjustment +/-0.05 na podstawie success rate           | Agent z 60% success rate przy T=0.7 -> T=0.65                     |
| **Wagi archetypow**        | Przesuniecie prawdopodobienstwa aktywacji              | Wiecej Guardian w domenie security, wiecej Rebel w prototypowaniu |
| **Progi eskalacji**        | Dostosowanie na podstawie false positive/negative rate | Zmniejszenie progu eskalacji po missed threat                     |
| **Preferencje wspolpracy** | Ktorzy agenci najlepiej wspolpracuja                   | Auditor + Sentinel = 95% success w security tasks                 |

### **Etap 4: Performance Tracking**

System utrzymuje dashboard metryk dla kazdego agenta:

```
Agent Performance Dashboard
+------------------+--------+--------+--------+--------+
| Metryka          | Librar | Audit  | Sentl  | Archit |
+------------------+--------+--------+--------+--------+
| Success Rate     | 94.2%  | 91.7%  | 97.1%  | 88.3%  |
| Avg Temperature  | 0.45   | 0.25   | 0.15   | 0.55   |
| Dominant Archtype| Sage   | Shadow | Guard  | Sage   |
| Avg Trinity Score| 0.82   | 0.79   | 0.91   | 0.85   |
| Guardian Violat. | 0.3%   | 0.1%   | 0.0%   | 0.8%   |
| Emotional Stab.  | 0.91   | 0.87   | 0.95   | 0.83   |
+------------------+--------+--------+--------+--------+
```

**Metryki sledzone w czasie:**

- **Success rate** — procent zadan zakonczonych sukcesem (cel: > 90%)
- **Average temperature** — srednia temperatura decyzyjna (cel: stabilna w zakresie archetypu)
- **Emotional patterns** — trendy w wektorze PAD (cel: stabilnosc, brak dryfu)
- **Guardian compliance** — procent decyzji bez naruszen Guardian Laws (cel: > 99%)
- **Collaboration score** — skutecznosc wspolpracy z innymi agentami
- **Evolution velocity** — tempo adaptacji do nowych wzorcow

### **Cykl Zycia Petli**

```
    [Experience Collection]
           |
           | (ciagly — kazde zadanie)
           v
    [Pattern Extraction]
           |
           | (co 100 doswiadczen)
           v
    [Agent Evolution]
           |
           | (aktualizacja parametrow)
           v
    [Performance Tracking]
           |
           | (ciagly monitoring)
           v
    [Feedback to Experience Collection]
           |
           +---> Powrot do poczatku (petla nieskonczona)
```

---

## **Integracja Warstw**

Warstwa Inteligencji integruje sie z pozostalymi warstwami systemu ADRION 369:

| Warstwa docelowa       | Interfejs                                    | Kierunek                                                   |
| ---------------------- | -------------------------------------------- | ---------------------------------------------------------- |
| **Trinity Score**      | `evaluate_trinity(job, analysis, resources)` | Agenty dostarczaja analize -> Trinity ocenia               |
| **Guardian Laws**      | `evaluate_guardians(job, analysis, context)` | Agenty podlegaja 9 prawom Guardian                         |
| **EBDI State Machine** | Go Vortex port `1740`                        | Stan emocjonalny agentow (Emotion-Belief-Desire-Intention) |
| **Genesis Record**     | MCP port `9004`                              | Librarian zarzadza baza wiedzy                             |
| **MCP Router**         | Port `9000`                                  | Navigator routuje zapytania miedzy agentami                |
| **Circuit Breaker**    | `arbitrage/circuit_breaker.py`               | Healer zarzadza obwodami zabezpieczajacymi                 |
