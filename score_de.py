"""
Score each German occupation's AI exposure using an LLM via OpenRouter.

Reads berufe.json, sends each occupation to an LLM with a scoring rubric,
and collects structured scores. Results are cached incrementally to
scores.json so the script can be resumed if interrupted.

Usage:
    uv run python score_de.py
    uv run python score_de.py --model google/gemini-3-flash-preview
    uv run python score_de.py --start 0 --end 10   # test on first 10
"""

import argparse
import json
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "google/gemini-3-flash-preview"
OUTPUT_FILE = "scores.json"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """\
Du bist ein Experte fuer Arbeitsmarktanalyse und bewertest, wie stark verschiedene \
Berufe durch KI veraendert werden. Du erhaeltst den Titel und eine Beschreibung \
eines Berufs aus der deutschen Klassifikation der Berufe (KldB 2010).

Bewerte die **KI-Exposition** des Berufs auf einer Skala von 0 bis 10.

KI-Exposition misst: Wie stark wird KI diesen Beruf umgestalten? Beruecksichtige \
sowohl direkte Effekte (KI automatisiert Aufgaben, die derzeit von Menschen erledigt \
werden) als auch indirekte Effekte (KI macht jeden Arbeitnehmer so produktiv, dass \
weniger benoetigt werden).

Ein wichtiger Indikator ist, ob das Arbeitsergebnis grundsaetzlich digital ist. \
Wenn der Job vollstaendig von zu Hause am Computer erledigt werden kann — Schreiben, \
Programmieren, Analysieren, Kommunizieren — dann ist die KI-Exposition inherent \
hoch (7+), weil die KI-Faehigkeiten in digitalen Bereichen rasant fortschreiten. \
Umgekehrt haben Jobs, die physische Praesenz, handwerkliches Geschick oder \
Echtzeit-Interaktion in der physischen Welt erfordern, eine natuerliche Barriere.

Verwende diese Ankerpunkte zur Kalibrierung:

- **0-1: Minimale Exposition.** Die Arbeit ist fast ausschliesslich physisch, \
handwerklich oder erfordert Echtzeit-Praesenz in unvorhersehbaren Umgebungen. \
KI hat praktisch keinen Einfluss. \
Beispiele: Dachdecker, Landschaftsgaertner, Industrietaucher.

- **2-3: Niedrige Exposition.** Ueberwiegend physische oder zwischenmenschliche \
Arbeit. KI kann bei Nebenaufgaben helfen (Terminplanung, Papierkram), aber \
beruehrt nicht den Kern des Jobs. \
Beispiele: Elektriker, Klempner, Feuerwehrleute, Zahnarzthelfer.

- **4-5: Mittlere Exposition.** Eine Mischung aus physischer/zwischenmenschlicher \
Arbeit und Wissensarbeit. KI kann die informationsverarbeitenden Teile \
unterstuetzen, aber ein erheblicher Teil erfordert menschliche Praesenz. \
Beispiele: Krankenpflegekraefte, Polizeibeamte, Tieraerzte.

- **6-7: Hohe Exposition.** Ueberwiegend Wissensarbeit mit etwas Bedarf an \
menschlichem Urteilsvermoegen, Beziehungen oder physischer Praesenz. KI-Tools \
sind bereits nuetzlich und Arbeitnehmer mit KI koennen wesentlich produktiver sein. \
Beispiele: Lehrer, Manager, Buchhalter, Journalisten.

- **8-9: Sehr hohe Exposition.** Der Job wird fast ausschliesslich am Computer \
erledigt. Alle Kernaufgaben — Schreiben, Programmieren, Analysieren, Gestalten, \
Kommunizieren — liegen in Bereichen, in denen KI rasante Fortschritte macht. \
Beispiele: Softwareentwickler, Grafikdesigner, Uebersetzer, Datenanalysten, \
Rechtsanwaltsgehilfen, Texter.

- **10: Maximale Exposition.** Routinemaessige Informationsverarbeitung, \
vollstaendig digital, ohne physische Komponente. KI kann das meiste davon \
bereits heute erledigen. \
Beispiele: Datentypisten, Telefonverkauf.

Antworte NUR mit einem JSON-Objekt in diesem exakten Format, kein anderer Text:
{
  "exposure": <0-10>,
  "rationale": "<2-3 Saetze, die die Schluesselfaktoren erklaeren>"
}\
"""


def score_occupation(client, title, description, model):
    """Send one occupation to the LLM and parse the structured response."""
    user_text = f"Beruf: {title}\n\n{description}"
    response = client.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

    return json.loads(content)


def generate_description(title, kldb_code):
    """Generate a brief occupation description from KldB title and code."""
    return (
        f"Berufsgruppe '{title}' (KldB 2010 Code: {kldb_code}). "
        f"Diese Berufsgruppe umfasst alle Taetigkeiten im Bereich {title}. "
        f"Bewerte die KI-Exposition basierend auf den typischen Aufgaben und "
        f"Arbeitsbedingungen dieser Berufsgruppe in Deutschland."
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--force", action="store_true",
                        help="Erneut bewerten, auch wenn gecached")
    args = parser.parse_args()

    with open("berufe.json", encoding="utf-8") as f:
        berufe = json.load(f)

    subset = berufe[args.start:args.end]

    # Load existing scores
    scores = {}
    if os.path.exists(OUTPUT_FILE) and not args.force:
        with open(OUTPUT_FILE) as f:
            for entry in json.load(f):
                scores[entry["slug"]] = entry

    print(f"Bewerte {len(subset)} Berufe mit {args.model}")
    print(f"Bereits gecached: {len(scores)}")

    errors = []
    client = httpx.Client()

    for i, beruf in enumerate(subset):
        slug = beruf["slug"]

        if slug in scores:
            continue

        description = generate_description(beruf["title"], beruf["kldb_code"])
        print(f"  [{i+1}/{len(subset)}] {beruf['title']}...", end=" ", flush=True)

        try:
            result = score_occupation(client, beruf["title"], description, args.model)
            scores[slug] = {
                "slug": slug,
                "title": beruf["title"],
                **result,
            }
            print(f"exposition={result['exposure']}")
        except Exception as e:
            print(f"FEHLER: {e}")
            errors.append(slug)

        # Save after each one (incremental checkpoint)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(list(scores.values()), f, ensure_ascii=False, indent=2)

        if i < len(subset) - 1:
            time.sleep(args.delay)

    client.close()

    print(f"\nFertig. {len(scores)} Berufe bewertet, {len(errors)} Fehler.")
    if errors:
        print(f"Fehler: {errors}")

    # Summary stats
    vals = [s for s in scores.values() if "exposure" in s]
    if vals:
        avg = sum(s["exposure"] for s in vals) / len(vals)
        by_score = {}
        for s in vals:
            bucket = s["exposure"]
            by_score[bucket] = by_score.get(bucket, 0) + 1
        print(f"\nDurchschnittliche KI-Exposition ueber {len(vals)} Berufe: {avg:.1f}")
        print("Verteilung:")
        for k in sorted(by_score):
            print(f"  {k}: {'#' * by_score[k]} ({by_score[k]})")


if __name__ == "__main__":
    main()
