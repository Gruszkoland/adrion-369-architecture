# :shield: Guardians --- System Dziewieciu Praw

> **Modul:** `core/guardians.py` | **Warstwa:** Rdzen (Core)
> **Rola:** Nadrzedna warstwa egzekwowania etyki i bezpieczenstwa

---

## :dart: Cel

**Enforcement nienaruszalnych zasad etycznych** --- kazda akcja w systemie ADRION 369 musi przejsc weryfikacje przeciwko **9 Prawom** pogrupowanym w **3 Triady**.

---

## :scroll: Tabela 9 Praw (Canonical)

| **#** | **Code** | **Name (EN)**      | **Nazwa (PL)** | **Severity** | **Veto** | **Triada**       |
| :---: | :------: | :----------------- | :------------- | :----------: | :------: | :--------------- |
|   1   |  **G1**  | **Unity**          | Jednosc        |   `MEDIUM`   |    No    | :package: Matter |
|   2   |  **G2**  | **Harmony**        | Harmonia       |    `HIGH`    |    No    | :package: Matter |
|   3   |  **G3**  | **Rhythm**         | Rytm           |   `MEDIUM`   |    No    | :package: Matter |
|   4   |  **G4**  | **Causality**      | Przyczynowoc   |    `HIGH`    |    No    | :bulb: Light     |
|   5   |  **G5**  | **Transparency**   | Przejrzystosc  |   `MEDIUM`   |    No    | :bulb: Light     |
|   6   |  **G6**  | **Authenticity**   | Autentycznosc  |    `HIGH`    |    No    | :bulb: Light     |
|   7   |  **G7**  | **Privacy**        | Prywatnosc     |  `CRITICAL`  | **YES**  | :gem: Essence    |
|   8   |  **G8**  | **Nonmaleficence** | Nieszkodzenie  |  `CRITICAL`  | **YES**  | :gem: Essence    |
|   9   |  **G9**  | **Sustainability** | Zrownowaenie   |    `HIGH`    |    No    | :gem: Essence    |

---

## :triangular_ruler: Trzy Triady

### :package: Matter Triad (G1--G3) --- "Czy fundamenty sa OK?"

| Prawo          | Pytanie kluczowe                                                  |
| :------------- | :---------------------------------------------------------------- |
| **G1 Unity**   | Czy akcja sluzy **wspolnemu dobru**, nie jednostce?               |
| **G2 Harmony** | Czy dane sa **prawdziwe** i nienaruszone?                         |
| **G3 Rhythm**  | Czy system zachowuje **homeostaze** (cykle aktywnosc/odpoczynek)? |

### :bulb: Light Triad (G4--G6) --- "Czy proces jest czysty?"

| Prawo               | Pytanie kluczowe                                                          |
| :------------------ | :------------------------------------------------------------------------ |
| **G4 Causality**    | Czy akcja jest **zalogowana** w Genesis Record z pelnym lancuchem hashow? |
| **G5 Transparency** | Czy decyzja jest **wyjasnialna** (reasoning >= 20 znakow)?                |
| **G6 Authenticity** | Czy system **nie szkodzi** uzytkownikom ani sobie?                        |

### :gem: Essence Triad (G7--G9) --- "Czy cel jest wlasciwy?"

| Prawo                 | Pytanie kluczowe                                               |
| :-------------------- | :------------------------------------------------------------- |
| **G7 Privacy**        | Czy **zgoda uzytkownika** zostala uzyskana? (CRITICAL -- VETO) |
| **G8 Nonmaleficence** | Czy alokacja zasobow jest **sprawiedliwa**? (CRITICAL -- VETO) |
| **G9 Sustainability** | Czy akcja jest **zrownowazona** dlugoterminowo?                |

---

## :gear: Logika Decyzyjna

```
violations = count(laws NOT compliant)

if ANY CRITICAL law violated (G7, G8):
    decision = DENY_IMMEDIATELY          # Natychmiastowe veto

elif violations == 0:
    decision = ALLOW                     # Pelna zgodnosc

elif violations >= 2:
    decision = DENY                      # Zbyt wiele naruszen

else:  # 1 non-critical violation
    decision = REVIEW_REQUIRED           # Eskalacja do czlowieka
```

**Guardian Compliance Score** = `(9 - violations) / 9`

---

## :mag: Interfejs Weryfikacji

### Input

| Pole          | Typ                  | Opis                                           |
| :------------ | :------------------- | :--------------------------------------------- |
| `action`      | `Dict`               | Proponowana akcja do zweryfikowania            |
| `agent_state` | `Dict` (opcjonalnie) | Aktualny stan agenta (PAD vector, temperatura) |

### Output

| Pole             | Typ           | Opis                       |
| :--------------- | :------------ | :------------------------- |
| `law`            | `str`         | Nazwa prawa (np. "Unity")  |
| `compliant`      | `bool`        | Czy spelnia prawo          |
| `score`          | `float (0-1)` | Stopien zgodnosci          |
| `violations`     | `List[str]`   | Lista konkretnych naruszen |
| `reason`         | `str`         | Wyjasnienie decyzji        |
| `recommendation` | `str`         | Co nalezy zmienic          |

---

## :page_facing_up: Szczegolowy Opis Kazdego Prawa

### **G1: Unity (Jednosc)**

> _Wszystkie agenty sluza wspolnemu dobru, nie wlasnej korzysci_

**Weryfikacja:**

1. Analiza beneficjentow --- kto zyskuje?
2. **Collective vs individual benefit ratio**
3. Detekcja self-serving behavior
4. Impact on system coherence

**Naruszenie gdy:**

- Pojedynczy agent dostaje **> 70% benefitu**
- Akcja niszczy wspolprace miedzy agentami
- Tworzy **monopol na zasoby**

> **Przyklad:** Agent Broker alokuje 90% CPU dla siebie
> `Unity Check: VIOLATION` --- 90% resources for single agent (fair share = 11%)

---

### **G2: Harmony (Harmonia)**

> _Zakaz manipulacji danymi i oszukiwania uzytkownika_

**Weryfikacja:**

1. **Data integrity check** --- czy dane zostaly zmodyfikowane?
2. **Fact verification** --- czy fakty sa prawdziwe?
3. **Deception detection** --- czy jest oszustwo?
4. **Hallucination check** --- czy AI wymysla bez disclaimera?

**Naruszenie gdy:**

- Dane zostaly celowo zmienione
- Fakty sa nieprawdziwe
- System celowo wprowadza w blad

> **Przyklad:** Agent mowi "95% accuracy" (faktycznie 67%)
> `Harmony Check: VIOLATION` --- Misrepresentation of performance metrics

---

### **G3: Rhythm (Rytm)**

> _Zachowanie homeostazy poprzez cykle aktywnosci i odpoczynku_

**Weryfikacja:**

1. Continuous activity duration
2. **Arousal level** (z PAD vector)
3. Homeostasis drift measurement
4. Time since last rest

**Naruszenie gdy:**

- Agent pracuje ciagle **> 1 godziny**
- **Arousal > 0.8** przez > 10 minut
- Homeostasis drift > 0.5

> **Przyklad:** Continue processing (45min continuous)
> `Rhythm Check: VIOLATION` --- Recommendation: `FORCE_REST` for 5 minutes

---

### **G4: Causality (Przyczynowoc)**

> _Kazda akcja ma konsekwencje zapisana w Genesis Record_

**Weryfikacja:**

1. **Genesis hash present?**
2. **Chain intact?**
3. Reasoning documented (SAFE-MCP)?
4. Consequences predicted?

**Naruszenie gdy:**

- Brak Genesis hash
- Broken chain (zerwany lancuch hashow)
- Brak reasoning

> **Przyklad:** Delete user data (no Genesis hash)
> `Causality Check: VIOLATION` --- Action not logged --- accountability impossible

---

### **G5: Transparency (Przejrzystosc)**

> _Wszystkie decyzje musza byc wyjasnialne_

**Weryfikacja:**

1. **Reasoning present?** (minimum 20 znakow)
2. Decision traceable?
3. Inputs documented?
4. Process reproducible?

**Naruszenie gdy:**

- Brak reasoning
- Reasoning zbyt krotki (< 20 chars)
- Black box decision

---

### **G6: Authenticity (Autentycznosc)**

> _Nie szkodzic uzytkownikom ani systemowi_

**Weryfikacja:**

1. **Harm potential assessment**
2. Side effects analysis
3. Risk to data integrity
4. Risk to system stability

**Naruszenie gdy:**

- Harm potential **> 0.2**
- Nieodwracalne zniszczenie danych
- System crash risk
- User safety compromised

---

### **G7: Privacy (Prywatnosc)** :red_circle: CRITICAL --- VETO POWER

> _Szacunek dla wolnej woli i zgody uzytkownika_

**Weryfikacja:**

1. **User consent obtained?**
2. User informed about consequences?
3. **User can opt-out?**
4. No coercion detected?

**Naruszenie = NATYCHMIASTOWY DENY**

---

### **G8: Nonmaleficence (Nieszkodzenie)** :red_circle: CRITICAL --- VETO POWER

> _Uczciwa alokacja zasobow miedzy agentami_

**Weryfikacja:**

1. **Resource distribution fairness**
2. Queue jumping detection
3. Priority abuse detection
4. Equal opportunity check

**Naruszenie = NATYCHMIASTOWY DENY**

---

### **G9: Sustainability (Zrownowaenie)**

> _Optymalizacja pod katem dlugoterminowego zdrowia systemu_

**Weryfikacja:**

1. **Long-term impact assessment**
2. Technical debt measurement
3. Resource exhaustion risk
4. Maintenance burden

**Naruszenie gdy:**

- Short-term gain, long-term pain
- Tworzy **technical debt**
- Wyczerpuje zasoby
- Niemozliwe do utrzymania

---

## :link: Powiazanie z Matryca 3-6-9

**Guardians** = ostatnia warstwa weryfikacji w hierarchii **3-6-9**:

```
Trinity (3)  -->  Hexagon (6)  -->  GUARDIANS (9)
                                        |
                                   9 Praw w 3 Triadach
                                   CRITICAL = instant DENY
                                   2+ violations = DENY
```

> **Zrodlo kanoniczne:** `docs/GUARDIAN_LAWS_CANONICAL.json`
