# :brain: EBDI --- Model Emocjonalny Agenta

> **Modul:** `core/ebdi_model.py` | **Warstwa:** Rdzen (Core)
> **Rola:** Regulacja stanu wewnetrznego systemu

---

## :dart: Cel

Implementacja modelu **Emotion-Belief-Desire-Intention** z wektorami **PAD** (Pleasure-Arousal-Dominance) dla kazdego agenta w systemie.

---

## :bar_chart: Wektor PAD

| **Komponent**     | **Zakres** | **Znaczenie**                           | **Wartosc neutralna** |
| :---------------- | :--------: | :-------------------------------------- | :-------------------: |
| **P** (Pleasure)  | `[-1, 1]`  | Przyjemnosc --- od bolu do radosci      |         `0.5`         |
| **A** (Arousal)   |  `[0, 1]`  | Pobudzenie --- od spokoju do ekscytacji |         `0.1`         |
| **D** (Dominance) | `[-1, 1]`  | Dominacja --- od uleglosci do kontroli  |         `0.5`         |

### Stan inicjalny agenta

```
Pleasure    = 0.5    # neutralny
Arousal     = 0.1    # spokojny
Dominance   = 0.5    # zbalansowany
Temperature = 0.7    # kreatywny (parametr LLM)
```

---

## :zap: Przetwarzanie Zdarzen (Event Processing)

Kazde zdarzenie w systemie modyfikuje wektor PAD agenta:

| **Event**          | **Pleasure** | **Arousal** | **Dominance** |
| :----------------- | :----------: | :---------: | :-----------: |
| `anomaly_detected` |   **-0.1**   |  **+0.2**   |      --       |
| `success`          |  **+0.15**   |  **-0.05**  |      --       |
| `failure`          |   **-0.2**   |  **+0.15**  |   **-0.1**    |
| `threat_detected`  |   **-0.3**   |  **+0.3**   |   **+0.1**    |
| `task_completed`   |   **+0.1**   |  **-0.05**  |   **+0.05**   |
| `rest_period`      |  **+0.05**   |  **-0.1**   |      --       |

---

## :thermometer: Obliczanie Temperatury

**Temperatura** (parametr kreatywnosci LLM) jest dynamicznie regulowana na podstawie stresu:

```
stress = Arousal x (1 - Pleasure)

Temperature = max(0.1, 1.0 - stress)
```

| **Stan**     | **Arousal** | **Pleasure** | **Stress** |         **Temperature**          |
| :----------- | :---------: | :----------: | :--------: | :------------------------------: |
| Spokojny     |     0.1     |     0.5      |    0.05    |  **0.95** (wysoka kreatywnosc)   |
| Czujny       |     0.3     |     0.4      |    0.18    |             **0.82**             |
| Zestresowany |     0.6     |     0.2      |    0.48    |        **0.52** (ostrony)        |
| Paranoidalny |     0.9     |     -0.3     |    1.17    | **0.10** (minimalna kreatywnosc) |

---

## :recycle: Homeostaza

System automatycznie dryfuje do stanu neutralnego co **1 sekunde**:

```
Arousal  = Arousal  x 0.95                          # drift down (zanik pobudzenia)
Pleasure = (Pleasure + baseline_pleasure) / 2       # drift to baseline
```

**Efekt:** Bez nowych zdarzen agent powoli wraca do spokojnego, neutralnego stanu.

---

## :performing_arts: Mapowanie Emocji

Na podstawie wektora PAD agent jest klasyfikowany do jednego z 4 stanow:

```
if Arousal > 0.8 AND Pleasure < -0.3:
    state = PARANOID         # Wysoka czujnosc + negatywne emocje

elif Arousal > 0.5:
    state = STRESSED         # Wysoka czujnosc

elif Arousal > 0.2:
    state = ALERT            # Umiarkowana czujnosc

else:
    state = CALM             # Stan neutralny / spokojny
```

### Wplyw stanu na zachowanie agenta

| **Stan**     | **Temperature** | **Zachowanie**                       | **Archetyp dominujacy** |
| :----------- | :-------------: | :----------------------------------- | :---------------------- |
| **CALM**     |    0.7--1.0     | Kreatywny, eksploracyjny, otwarty    | Rebel / Sage            |
| **ALERT**    |    0.5--0.7     | Skoncentrowany, celowy, efektywny    | Navigator / Creator     |
| **STRESSED** |    0.3--0.5     | Ostrony, szybkie decyzje, minimalizm | Sentinel / Auditor      |
| **PARANOID** |    0.1--0.3     | Defensywny, blokujacy, eskalujacy    | Guardian / Shadow       |

---

## :chart_with_upwards_trend: Kluczowe Metryki

| **Metryka**              |  **Zakres**  | **Opis**                           |
| :----------------------- | :----------: | :--------------------------------- |
| **PAD Vector**           |  `(P,A,D)`   | Trojwymiarowy stan emocjonalny     |
| **Current Temperature**  | `0.1 -- 1.0` | Parametr kreatywnosci LLM          |
| **Emotional State**      |    `enum`    | CALM / ALERT / STRESSED / PARANOID |
| **Time Since Last Rest** |     `ms`     | Czas od ostatniego odpoczynku      |
| **Stress Level**         |   `0 -- 1`   | `Arousal x (1 - Pleasure)`         |
| **Homeostasis Drift**    |   `0 -- 1`   | Odleglosc od baseline              |

---

## :link: Zaleznosci

**EBDI jest self-contained** --- nie zalezy od innych modulow.

Natomiast inne moduly **korzystaja z EBDI**:

- **Hexagon / Action Mode** --- aktualizuje emocje po sukcesie/porazce
- **Guardians / Rhythm Law (G3)** --- sprawdza czy agent potrzebuje odpoczynku
- **Intelligence / Agent Swarm** --- dobiera archetyp na podstawie stanu emocjonalnego
- **SAFE-MCP** --- dolacza stan emocjonalny do kazdej wiadomosci

---

## :link: Powiazanie z Matryca 3-6-9

EBDI jest **regulatorem wewnetrznym** systemu --- dziala na poziomie kazdego agenta i wplywa na sposob przetwarzania w calym pipeline 3-6-9:

```
EBDI State --> Temperature --> LLM creativity
         |
         +--> Archetype selection --> Agent behavior
         |
         +--> Guardian G3 (Rhythm) --> Rest enforcement
```
