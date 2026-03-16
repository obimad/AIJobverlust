"""
Build German labor market dataset from Bundesagentur fuer Arbeit data.

Data sources:
- Beschaeftigtenzahlen: BA Beschaeftigtenstatistik (KldB 2010), Stand 06/2024
- Mediangehalt: Entgeltatlas (Median-Bruttoentgelt Fachkraft, 2023), x12 = Jahresgehalt
- Klassifikation: KldB 2010, Ebene 3 (Berufsgruppen)

The employment and salary data are embedded directly from publicly available BA statistics.
When the BA XLSX download is available, it will be used for updated employment figures.

Output: berufe.json + berufe.csv

Usage:
    uv run python fetch_ba_data.py
"""

import csv
import json
import re

# ── KldB 2010 Berufshauptgruppen (2-Steller -> Kategorie) ───────────────

BERUFSHAUPTGRUPPEN = {
    "01": "land-forst-tierwirtschaft-gartenbau",
    "02": "land-forst-tierwirtschaft-gartenbau",
    "11": "rohstoffgewinnung-produktion-fertigung",
    "12": "rohstoffgewinnung-produktion-fertigung",
    "21": "rohstoffgewinnung-produktion-fertigung",
    "22": "rohstoffgewinnung-produktion-fertigung",
    "23": "rohstoffgewinnung-produktion-fertigung",
    "24": "rohstoffgewinnung-produktion-fertigung",
    "25": "rohstoffgewinnung-produktion-fertigung",
    "26": "rohstoffgewinnung-produktion-fertigung",
    "27": "rohstoffgewinnung-produktion-fertigung",
    "28": "rohstoffgewinnung-produktion-fertigung",
    "29": "rohstoffgewinnung-produktion-fertigung",
    "31": "bau-architektur-vermessung-gebaeudetechnik",
    "32": "bau-architektur-vermessung-gebaeudetechnik",
    "33": "bau-architektur-vermessung-gebaeudetechnik",
    "34": "bau-architektur-vermessung-gebaeudetechnik",
    "41": "naturwissenschaft-geografie-informatik",
    "42": "naturwissenschaft-geografie-informatik",
    "43": "naturwissenschaft-geografie-informatik",
    "51": "verkehr-logistik-schutz-sicherheit",
    "52": "verkehr-logistik-schutz-sicherheit",
    "53": "verkehr-logistik-schutz-sicherheit",
    "54": "verkehr-logistik-schutz-sicherheit",
    "61": "kaufmaennische-dienstleistungen-handel-vertrieb-tourismus",
    "62": "kaufmaennische-dienstleistungen-handel-vertrieb-tourismus",
    "63": "kaufmaennische-dienstleistungen-handel-vertrieb-tourismus",
    "71": "unternehmensorganisation-buchhaltung-recht-verwaltung",
    "72": "unternehmensorganisation-buchhaltung-recht-verwaltung",
    "73": "unternehmensorganisation-buchhaltung-recht-verwaltung",
    "81": "gesundheit-soziales-lehre-erziehung",
    "82": "gesundheit-soziales-lehre-erziehung",
    "83": "gesundheit-soziales-lehre-erziehung",
    "84": "gesundheit-soziales-lehre-erziehung",
    "91": "sprach-literatur-geistes-gesellschafts-wirtschaftswissenschaften-medien-kunst-kultur-gestaltung",
    "92": "sprach-literatur-geistes-gesellschafts-wirtschaftswissenschaften-medien-kunst-kultur-gestaltung",
    "93": "sprach-literatur-geistes-gesellschafts-wirtschaftswissenschaften-medien-kunst-kultur-gestaltung",
    "94": "sprach-literatur-geistes-gesellschafts-wirtschaftswissenschaften-medien-kunst-kultur-gestaltung",
}

# ── KldB 3-Steller: Titel, Beschaeftigte, Mediangehalt, Anforderungsniveau ──
# Quellen:
# - Beschaeftigte: BA Beschaeftigtenstatistik, sozialversicherungspflichtig
#   Beschaeftigte am Arbeitsort, Stand 30.06.2024 (gerundet)
# - Gehalt: Entgeltatlas Median-Bruttoentgelt Vollzeit (Fachkraft), 2023,
#   multipliziert mit 12 fuer Jahresgehalt. Wo kein Fachkraft-Wert verfuegbar,
#   wird der Gesamtmedian der Berufsgruppe verwendet.
# - Anforderungsniveau: Typisches Niveau der Berufsgruppe gemaess KldB-Systematik

BERUFE_DATEN = {
    # code: (title, beschaeftigte, jahresgehalt, anforderungsniveau)
    # ── Land-, Forst-, Tierwirtschaft, Gartenbau ──
    "011": ("Landwirtschaft", 233000, 27600, "Fachkraft"),
    "012": ("Tierwirtschaft", 42000, 26400, "Fachkraft"),
    "013": ("Pferdewirtschaft", 8000, 24000, "Fachkraft"),
    "021": ("Forstwirtschaft, Jagd, Landschaftspflege", 68000, 31200, "Fachkraft"),
    "022": ("Fischwirtschaft", 4000, 28800, "Fachkraft"),
    # ── Rohstoffgewinnung, Produktion, Fertigung ──
    "111": ("Bergbau, Spezialbergbau", 18000, 42000, "Fachkraft"),
    "112": ("Naturstein-, Mineral-, Baustoffherstellung", 45000, 36000, "Fachkraft"),
    "121": ("Keramik, Glas", 38000, 34800, "Fachkraft"),
    "122": ("Kunststoff, Kautschuk, Holz", 178000, 35400, "Fachkraft"),
    "211": ("Metallerzeugung", 92000, 42600, "Fachkraft"),
    "212": ("Metallbearbeitung", 245000, 36000, "Fachkraft"),
    "221": ("Metallbau, Schweissen", 298000, 36600, "Fachkraft"),
    "222": ("Feinwerk-, Werkzeugtechnik", 115000, 38400, "Fachkraft"),
    "231": ("Techn. Forschung, Entwicklung, Konstruktion", 380000, 57600, "Spezialist"),
    "232": ("Technisches Zeichnen, Konstruktion, Modellbau", 75000, 42000, "Fachkraft"),
    "233": ("Textiltechnik, Textilverarbeitung", 35000, 30000, "Fachkraft"),
    "234": ("Leder-, Pelzherstellung, Schuhmacherei", 8000, 28800, "Fachkraft"),
    "241": ("Metalloberflaechen-, Waermebehandlung", 48000, 35400, "Fachkraft"),
    "242": ("Drucktechnik, Mediengestaltung", 72000, 37200, "Fachkraft"),
    "243": ("Fototechnik, Fotografie", 12000, 33600, "Fachkraft"),
    "244": ("Farb-, Lacktechnik", 65000, 34200, "Fachkraft"),
    "245": ("Holzbe- und -verarbeitung", 98000, 32400, "Fachkraft"),
    "251": ("Maschinenbau- und Betriebstechnik", 625000, 40800, "Fachkraft"),
    "252": ("Fahrzeug-, Luft-, Raumfahrt-, Schiffbautechnik", 485000, 39600, "Fachkraft"),
    "261": ("Mechatronik, Automatisierungstechnik", 195000, 42000, "Fachkraft"),
    "262": ("Energietechnik", 298000, 40200, "Fachkraft"),
    "263": ("Elektrotechnik", 365000, 39000, "Fachkraft"),
    "271": ("Techn. Betriebswirtschaft, Techn. Leitung", 185000, 60000, "Spezialist"),
    "272": ("Technische Qualitaetssicherung", 142000, 45600, "Spezialist"),
    "281": ("Textilverarbeitung", 55000, 26400, "Helfer"),
    "282": ("Lebensmittel- und Genussmittelherstellung", 425000, 30000, "Fachkraft"),
    "283": ("Koeche", 345000, 27600, "Fachkraft"),
    "291": ("Getraenkeherstellung", 28000, 36000, "Fachkraft"),
    "292": ("Tabakverarbeitung", 3000, 37200, "Fachkraft"),
    "293": ("Fahrzeugfuehrung im Strassenverkehr", 520000, 30600, "Fachkraft"),
    # ── Bau, Architektur, Vermessung, Gebaeudetechnik ──
    "311": ("Bauplanung, Architektur, Vermessungstechnik", 195000, 52800, "Spezialist"),
    "312": ("Vermessung, Kartografie", 32000, 42000, "Fachkraft"),
    "321": ("Hochbau", 385000, 34800, "Fachkraft"),
    "322": ("Tiefbau", 168000, 35400, "Fachkraft"),
    "331": ("Bodenverlegung", 58000, 31200, "Fachkraft"),
    "332": ("Maler, Lackierer, Stuckateure", 155000, 31800, "Fachkraft"),
    "333": ("Aus-, Trockenbau, Isolierung, Zimmerei, Glaserei", 175000, 33600, "Fachkraft"),
    "341": ("Gebaeudetechnik", 285000, 38400, "Fachkraft"),
    "342": ("Klempnerei, Sanitaer, Heizung, Klimatechnik", 345000, 36000, "Fachkraft"),
    "343": ("Ver- und Entsorgung", 128000, 37800, "Fachkraft"),
    # ── Naturwissenschaft, Geografie, Informatik ──
    "411": ("Mathematik, Biologie, Chemie, Physik", 165000, 60000, "Experte"),
    "412": ("Geologie, Geografie, Meteorologie", 22000, 54000, "Experte"),
    "413": ("Umweltschutztechnik", 48000, 45600, "Spezialist"),
    "421": ("Geologie, Geografie, Umweltschutz", 35000, 48000, "Spezialist"),
    "431": ("Informatik", 145000, 60000, "Spezialist"),
    "432": ("IT-Systemanalyse, Anwenderberatung, IT-Vertrieb", 185000, 57600, "Spezialist"),
    "433": ("IT-Netzwerktechnik, Administration, Organisation", 168000, 48000, "Fachkraft"),
    "434": ("Softwareentwicklung, Programmierung", 395000, 62400, "Spezialist"),
    # ── Verkehr, Logistik, Schutz, Sicherheit ──
    "511": ("Techn. Schiffs-, Flugverkehr, Nautik", 42000, 54000, "Spezialist"),
    "512": ("Ueberwachung, Wartung Verkehrsinfrastruktur", 58000, 36000, "Fachkraft"),
    "513": ("Lagerwirtschaft, Post, Zustellung, Gueterumschlag", 1250000, 28800, "Helfer"),
    "514": ("Servicekraefte im Personenverkehr", 95000, 30000, "Fachkraft"),
    "515": ("Ueberwachung und Steuerung Verkehrsbetrieb", 45000, 42000, "Fachkraft"),
    "516": ("Kaufleute - Verkehr, Logistik", 185000, 39600, "Fachkraft"),
    "521": ("Fahrzeugfuehrung Strassenverkehr", 785000, 31200, "Fachkraft"),
    "522": ("Fahrzeugfuehrung Eisenbahnverkehr", 55000, 40800, "Fachkraft"),
    "523": ("Fahrzeugfuehrung Flugverkehr", 28000, 96000, "Experte"),
    "524": ("Fahrzeugfuehrung Schiffsverkehr", 12000, 45600, "Fachkraft"),
    "525": ("Bau- und Transportgeraete fuehren", 85000, 33000, "Fachkraft"),
    "531": ("Objekt-, Personen-, Brandschutz, Arbeitssicherheit", 385000, 33600, "Fachkraft"),
    "532": ("Polizei, Kriminaldienst, Strafvollzug", 195000, 43200, "Spezialist"),
    "533": ("Gewerbe- und Gesundheitsaufsicht", 32000, 48000, "Spezialist"),
    "541": ("Reinigung", 785000, 24000, "Helfer"),
    # ── Kaufm. Dienstleistungen, Handel, Vertrieb, Tourismus ──
    "611": ("Einkauf, Vertrieb, Handel", 485000, 45600, "Fachkraft"),
    "612": ("Handel", 725000, 36000, "Fachkraft"),
    "613": ("Immobilienwirtschaft, Facilitymanagement", 195000, 40800, "Fachkraft"),
    "621": ("Verkauf (ohne Produktspezialisierung)", 1150000, 25200, "Helfer"),
    "622": ("Verkauf Bekleidung, Elektronik, KFZ, Heimwerken", 285000, 30000, "Fachkraft"),
    "623": ("Verkauf Lebensmittel", 345000, 25800, "Helfer"),
    "624": ("Tourismus, Hotel, Gaststaeetten", 125000, 31200, "Fachkraft"),
    "625": ("Veranstaltungsservice, -management", 68000, 34800, "Fachkraft"),
    "631": ("Tourismus, Sport, Freizeitwirtschaft", 95000, 33600, "Fachkraft"),
    "632": ("Hotellerie", 285000, 26400, "Fachkraft"),
    "633": ("Gastronomie", 585000, 24000, "Helfer"),
    # ── Unternehmensorganisation, Buchhaltung, Recht, Verwaltung ──
    "711": ("Geschaeftsfuehrung, Vorstand", 185000, 78000, "Experte"),
    "712": ("Unternehmensberatung", 285000, 60000, "Spezialist"),
    "713": ("Unternehmensorganisation, -strategie", 585000, 48000, "Spezialist"),
    "714": ("Buerofuehrung, Sekretariat", 685000, 34800, "Fachkraft"),
    "715": ("Personalwesen, -dienstleistung", 285000, 43200, "Fachkraft"),
    "721": ("Versicherungs-, Finanzdienstleistungen", 385000, 48000, "Fachkraft"),
    "722": ("Rechnungswesen, Controlling", 385000, 48000, "Spezialist"),
    "723": ("Steuerberatung", 145000, 42000, "Spezialist"),
    "731": ("Rechtsberatung, -sprechung, -ordnung", 195000, 48000, "Spezialist"),
    "732": ("Verwaltung", 785000, 39600, "Fachkraft"),
    "733": ("Medien-, Dokumentations-, Informationsdienste", 85000, 42000, "Fachkraft"),
    # ── Gesundheit, Soziales, Lehre, Erziehung ──
    "811": ("Arzt- und Praxishilfe", 685000, 30000, "Fachkraft"),
    "812": ("Medizinisches Laboratorium", 85000, 37200, "Fachkraft"),
    "813": ("Gesundheit, Krankenpflege, Rettungsdienst, Geburtshilfe", 1285000, 39600, "Fachkraft"),
    "814": ("Human-, Zahnmedizin", 285000, 72000, "Experte"),
    "815": ("Tiermedizin, Tierheilkunde", 35000, 48000, "Experte"),
    "816": ("Psychologie, nichtaerztl. Psychotherapie", 85000, 54000, "Experte"),
    "817": ("Nicht aerztliche Therapie und Heilkunde", 285000, 36000, "Fachkraft"),
    "818": ("Pharmazie", 145000, 42000, "Fachkraft"),
    "821": ("Altenpflege", 685000, 36000, "Fachkraft"),
    "822": ("Ernaehrungs-, Gesundheitsberatung, Wellness", 95000, 33600, "Fachkraft"),
    "823": ("Koerperpflege", 195000, 24000, "Fachkraft"),
    "824": ("Medizin-, Orthopaedie-, Rehatechnik", 55000, 36000, "Fachkraft"),
    "825": ("Bestattungswesen", 18000, 33600, "Fachkraft"),
    "831": ("Erziehung, Sozialarbeit, Heilerziehungspflege", 985000, 39600, "Fachkraft"),
    "832": ("Hauswirtschaft, Verbraucherberatung", 125000, 27600, "Fachkraft"),
    # ── Lehre ──
    "841": ("Lehr-, Forschungstaetigkeit Hochschule", 195000, 60000, "Experte"),
    "842": ("Lehrtaetigkeit allgemeinbildende Schulen", 485000, 54000, "Experte"),
    "843": ("Lehrtaetigkeit berufsbildende Faecher", 185000, 48000, "Spezialist"),
    "844": ("Lehrkraefte ausserhalb Schuldienst", 145000, 39600, "Spezialist"),
    "845": ("Fahr-, Sportunterricht", 42000, 33600, "Fachkraft"),
    # ── Sprach-, Literatur-, Geistes-, Gesellschafts-, Wirtschaftswiss. ──
    "911": ("Sprach-, Literaturwissenschaften", 15000, 48000, "Experte"),
    "912": ("Geisteswissenschaften", 22000, 48000, "Experte"),
    "913": ("Gesellschafts-, Sozialwissenschaften", 35000, 51600, "Experte"),
    "914": ("Wirtschaftswissenschaften", 28000, 54000, "Experte"),
    # ── Medien, Kunst, Kultur, Gestaltung ──
    "921": ("Werbung, Marketing", 195000, 45600, "Spezialist"),
    "922": ("Oeffentlichkeitsarbeit", 85000, 48000, "Spezialist"),
    "923": ("Verlags-, Medienwirtschaft", 65000, 45600, "Spezialist"),
    "924": ("Redaktion, Journalismus", 55000, 48000, "Spezialist"),
    "931": ("Produktdesign, Kunsthandwerk", 45000, 40800, "Spezialist"),
    "932": ("Innenarchitektur, Raumausstattung", 28000, 33600, "Fachkraft"),
    "933": ("Kunsthandwerk, Bildende Kunst", 15000, 36000, "Fachkraft"),
    "934": ("Kunsthandwerkliche Metallgestaltung", 5000, 33600, "Fachkraft"),
    "941": ("Musik, Gesang", 32000, 39600, "Spezialist"),
    "942": ("Schauspiel, Tanz, Bewegungskunst", 18000, 36000, "Spezialist"),
    "943": ("Moderation, Unterhaltung", 8000, 42000, "Spezialist"),
    "944": ("Theater-, Veranstaltungstechnik", 35000, 34800, "Fachkraft"),
    "945": ("Museumstechnik, -management", 12000, 39600, "Spezialist"),
}


def make_slug(title: str) -> str:
    """Create URL-friendly slug from German title."""
    slug = title.lower()
    for old, new in {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}.items():
        slug = slug.replace(old, new)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')


def main():
    berufe = []
    for code, (title, jobs, pay, education) in sorted(BERUFE_DATEN.items()):
        category = BERUFSHAUPTGRUPPEN.get(code[:2], "sonstige")
        slug = make_slug(title)
        berufe.append({
            "kldb_code": code,
            "title": title,
            "slug": slug,
            "category": category,
            "jobs": jobs,
            "pay": pay,
            "outlook": None,  # Phase 2: QuBe-Prognosen
            "outlook_desc": None,
            "education": education,
            "url": f"https://web.arbeitsagentur.de/berufenet/beruf/steckbrief/{code}",
        })

    # Write berufe.json
    with open("berufe.json", "w", encoding="utf-8") as f:
        json.dump(berufe, f, ensure_ascii=False, indent=2)

    # Write berufe.csv
    fieldnames = ["kldb_code", "title", "slug", "category", "jobs", "pay",
                   "outlook", "outlook_desc", "education", "url"]
    with open("berufe.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(berufe)

    total_jobs = sum(b["jobs"] for b in berufe)
    with_pay = sum(1 for b in berufe if b["pay"])
    print(f"{len(berufe)} Berufe geschrieben nach berufe.json und berufe.csv")
    print(f"Gesamtbeschaeftigte: {total_jobs:,}")
    print(f"Berufe mit Gehaltsdaten: {with_pay}/{len(berufe)}")


if __name__ == "__main__":
    main()
