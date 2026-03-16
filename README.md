# Deutscher Arbeitsmarkt - KI-Exposition

Interaktive Treemap-Visualisierung des deutschen Arbeitsmarkts mit KI-Expositionsanalyse.

Basierend auf [karpathy/jobs](https://github.com/karpathy/jobs) (US Job Market Visualizer), umgebaut fuer den deutschen Arbeitsmarkt mit Daten der Bundesagentur fuer Arbeit.

## Was wird visualisiert?

- **~130 Berufsgruppen** (KldB 2010, 3-Steller) als Treemap
- **Flaeche** proportional zur Beschaeftigtenzahl
- **Farbe** waehlbar: Mediangehalt, Anforderungsniveau, KI-Exposition
- Klick auf Kachel oeffnet BERUFENET-Seite

## Datenquellen

| Daten | Quelle | Stand |
|-------|--------|-------|
| Beschaeftigte | BA Beschaeftigtenstatistik (KldB 2010 Zeitreihe) | 2024 |
| Gehalt | Entgeltatlas API (Median-Bruttoentgelt) | 2023 |
| KI-Exposition | LLM-Schaetzung (Google Gemini via OpenRouter) | 2025 |
| Klassifikation | KldB 2010, Ebene 3 (Berufsgruppen) | - |

## Setup

```bash
# Python-Abhaengigkeiten installieren
uv sync

# Daten herunterladen und aufbereiten
uv run python fetch_ba_data.py

# KI-Exposition bewerten (benoetigt OPENROUTER_API_KEY in .env)
uv run python score_de.py

# Website-Daten generieren
uv run python build_site_data.py

# Lokal anzeigen
cd site && python -m http.server 8000
```

## Pipeline

```
fetch_ba_data.py     -> berufe.json, berufe.csv   (BA Statistik + Entgeltatlas)
score_de.py          -> scores.json                (LLM KI-Exposition)
build_site_data.py   -> site/data.json             (Merge fuer Website)
site/index.html      -> Treemap-Visualisierung     (Statisches HTML)
```

## Eigene Bewertungen

Der Scoring-Prompt in `score_de.py` kann angepasst werden, um Berufe nach beliebigen Kriterien zu bewerten -- z.B. Robotik-Exposition, Offshoring-Risiko, Klimawandel-Auswirkung. Einfach den `SYSTEM_PROMPT` aendern und die Pipeline neu ausfuehren.

## Lizenz

MIT
