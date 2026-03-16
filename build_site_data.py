"""
Build a compact JSON for the website by merging berufe.csv with AI exposure scores.

Reads berufe.csv (for stats) and scores.json (for AI exposure).
Writes site/data.json.

Usage:
    uv run python build_site_data.py
"""

import csv
import json


def main():
    # Load AI exposure scores
    scores = {}
    try:
        with open("scores.json", encoding="utf-8") as f:
            scores_list = json.load(f)
        scores = {s["slug"]: s for s in scores_list}
    except FileNotFoundError:
        print("Warnung: scores.json nicht gefunden. KI-Exposition wird leer sein.")

    # Load CSV stats
    with open("berufe.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Merge
    data = []
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})
        data.append({
            "title": row["title"],
            "slug": slug,
            "category": row["category"],
            "pay": int(row["pay"]) if row["pay"] else None,
            "jobs": int(row["jobs"]) if row["jobs"] else None,
            "outlook": int(row["outlook"]) if row["outlook"] else None,
            "outlook_desc": row["outlook_desc"] if row["outlook_desc"] else None,
            "education": row["education"],
            "exposure": score.get("exposure"),
            "exposure_rationale": score.get("rationale"),
            "url": row.get("url", ""),
        })

    import os
    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"{len(data)} Berufe nach site/data.json geschrieben")
    total_jobs = sum(d["jobs"] for d in data if d["jobs"])
    print(f"Gesamtbeschaeftigte: {total_jobs:,}")


if __name__ == "__main__":
    main()
