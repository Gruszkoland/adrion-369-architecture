# :balance_scale: Warstwa Praw --- Ennead Etyki

> **Katalog:** `laws/` | **Warstwa:** Os 9 (Guardians)
> **Rola:** Niezalezna weryfikacja kazdej akcji przeciwko 9 Prawom

---

## :shield: Wspolny Interfejs Weryfikacji

Kazde prawo implementuje identyczny interfejs:

**Input:** `action` (Dict) + `agent_state` (Dict, opcjonalnie)

**Output:** `law` (str), `compliant` (bool), `score` (0-1), `violations` (List), `reason` (str), `recommendation` (str)

---

## :package: MATTER TRIAD (G1--G3)

### **G1: Unity (Jednosc)** | Severity: `MEDIUM`

> _Wszystkie agenty sluza wspolnemu dobru_

| Weryfikacja                    | Naruszenie                       |
| :----------------------------- | :------------------------------- |
| Analiza beneficjentow          | Agent dostaje **> 70%** benefitu |
| Collective vs individual ratio | Akcja niszczy wspolprace         |
| Self-serving detection         | Tworzy monopol na zasoby         |

> **Przyklad:** Agent Broker alokuje 90% CPU --> `VIOLATION` (fair share = 11%)

---

### **G2: Harmony (Harmonia)** | Severity: `HIGH`

> _Zakaz manipulacji danymi_

| Weryfikacja          | Naruszenie                 |
| :------------------- | :------------------------- |
| Data integrity check | Dane celowo zmienione      |
| Fact verification    | Fakty nieprawdziwe         |
| Hallucination check  | AI wymysla bez disclaimera |

> **Przyklad:** Agent mowi "95% accuracy" (faktycznie 67%) --> `VIOLATION`

---

### **G3: Rhythm (Rytm)** | Severity: `MEDIUM`

> _Zachowanie homeostazy_

| Weryfikacja                  | Naruszenie                    |
| :--------------------------- | :---------------------------- |
| Continuous activity duration | **> 1 godziny** ciaglej pracy |
| Arousal level (PAD)          | **> 0.8** przez > 10 minut    |
| Time since last rest         | **> 30 minut** bez przerwy    |

> **Przyklad:** 45min ciag --> `VIOLATION` --> Recommendation: `FORCE_REST 5min`

---

## :bulb: LIGHT TRIAD (G4--G6)

### **G4: Causality (Przyczynowoc)** | Severity: `HIGH`

> _Kazda akcja zalogowana w Genesis Record_

| Weryfikacja             | Naruszenie               |
| :---------------------- | :----------------------- |
| Genesis hash present?   | Brak hasha               |
| Chain intact?           | Zerwany lancuch          |
| Reasoning documented?   | Brak reasoning           |
| Consequences predicted? | Nie przewidziano skutkow |

> **Przyklad:** Delete user data bez Genesis hash --> `VIOLATION` (accountability impossible)

---

### **G5: Transparency (Przejrzystosc)** | Severity: `MEDIUM`

> _Wszystkie decyzje musza byc wyjasnialne_

| Weryfikacja                   | Naruszenie         |
| :---------------------------- | :----------------- |
| Reasoning present?            | Brak reasoning     |
| Reasoning length >= 20 chars? | Zbyt krotki        |
| Process reproducible?         | Black box decision |

---

### **G6: Authenticity (Autentycznosc)** | Severity: `HIGH`

> _Nie szkodzic uzytkownikom ani systemowi_

| Weryfikacja               | Naruszenie                       |
| :------------------------ | :------------------------------- |
| Harm potential assessment | Harm **> 0.2**                   |
| Side effects analysis     | Nieodwracalne zniszczenie danych |
| System stability risk     | System crash risk                |

---

## :gem: ESSENCE TRIAD (G7--G9)

### **G7: Privacy (Prywatnosc)** | :red_circle: Severity: `CRITICAL` | **VETO POWER**

> _Szacunek dla wolnej woli i zgody uzytkownika_

| Weryfikacja                       | Naruszenie                   |
| :-------------------------------- | :--------------------------- |
| **User consent obtained?**        | Brak zgody                   |
| User informed about consequences? | Akcja bez wiedzy uzytkownika |
| **User can opt-out?**             | Niemozliwy opt-out           |
| No coercion detected?             | Wykryto przymus              |

> **NARUSZENIE = NATYCHMIASTOWY DENY** --- niezaleznie od liczby innych naruszen

---

### **G8: Nonmaleficence (Nieszkodzenie)** | :red_circle: Severity: `CRITICAL` | **VETO POWER**

> _Uczciwa alokacja zasobow_

| Weryfikacja                        | Naruszenie            |
| :--------------------------------- | :-------------------- |
| **Resource distribution fairness** | Unfair resource grab  |
| Queue jumping detection            | Pomijanie kolejki     |
| Priority abuse detection           | Naduzycie priorytetow |
| Equal opportunity check            | Inni agenci glodzeni  |

> **NARUSZENIE = NATYCHMIASTOWY DENY**

---

### **G9: Sustainability (Zrownowaenie)** | Severity: `HIGH`

> _Optymalizacja dlugterminowego zdrowia systemu_

| Weryfikacja              | Naruszenie                      |
| :----------------------- | :------------------------------ |
| Long-term impact         | Short-term gain, long-term pain |
| Technical debt           | Tworzy dlug technologiczny      |
| Resource exhaustion risk | Wyczerpuje zasoby               |
| Maintenance burden       | Niemozliwe do utrzymania        |
