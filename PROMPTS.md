# depotdiary — Prompts für Claude Code

Voraussetzung: `CLAUDE.md` liegt im Projektordner. Alle Prompts unten setzen voraus, dass Claude Code sie gelesen hat.
Reihenfolge einhalten — Prompt 1 baut das Fundament, alles danach nutzt es.

---

## 1 · Bootstrap — einmalig, baut den Generator

```
Lies CLAUDE.md vollständig.

Baue mir ein wiederverwendbares Slide-System in Python mit Pillow.

Struktur:
  brand.py      – Farben, Schriftpfade, Maße, alle Konstanten aus CLAUDE.md
  render.py     – die Render-Engine
  posts/        – ein Skript pro Post
  output/       – erzeugte Dateien

render.py muss folgende Funktionen bereitstellen:

  slide_hook(eyebrow, headline, subline)
  slide_text(eyebrow, headline, body)
  slide_rows(eyebrow, headline, rows, note)      # rows = [(Label, Wert, Farbe)]
  slide_card(eyebrow, headline, big, small, body)
  slide_cta(eyebrow, headline, body)
  slide_title(word, subtitle)                    # Titelkarte für Highlights

Anforderungen:

- In Headlines markiert *Sternchen* ein Wort, das kursiv und in #1A4D3C
  gesetzt wird. Der Rest bleibt schwarz und aufrecht.
  Vor Satzzeichen darf kein Leerzeichen entstehen.
- Der gesamte Inhaltsblock wird vertikal zentriert, nicht oben angesetzt.
  Kein toter Raum im unteren Drittel.
- Fußbereich auf jeder Slide: Trennlinie, gesperrtes "DEPOT DIARY",
  Seitenzahl rechts, Disclaimer darunter.
- Automatischer Zeilenumbruch. Wenn eine Headline mehr als drei Zeilen
  braucht, Schriftgrad selbstständig reduzieren.
- Nichts unterhalb von 88 % der Bildhöhe.
- Jeder Post wird in beiden Formaten ausgegeben:
  output/<name>/instagram_4x5/  (1080x1350)
  output/<name>/tiktok_9x16/    (1080x1920, 4:5-Slide zentriert auf #F2F0EA)
- Zusätzlich pro Post eine uebersicht.png als Kontaktabzug zur Kontrolle.

Baue zum Schluss einen Beispielpost mit sechs Slides und zeig mir den
Kontaktabzug.
```

---

## 2 · Einzelner Post

```
Neuer Post: <THEMA>

Kernaussage: <IN EINEM SATZ>
Slides: 6
Kategorie: Erklärstück | Depot-Update | Fehler | Quartalszahlen

Beachte die Sprachregel aus CLAUDE.md. Erste Person, keine Empfehlung,
keine Bewertung, keine Prognose.

Liefere:
1. Die Slides in beiden Formaten
2. Den Kontaktabzug
3. Die Caption nach dem Schema aus CLAUDE.md, mit Frage am Ende
4. Ein Voiceover-Skript: pro Slide ein gesprochener Satz,
   Gesamtlänge 35–45 Sekunden, gesprochene Hook zuerst
```

---

## 3 · Monatliches Depot-Update

```
Hier sind meine aktuellen Positionen:

<Positionsname>  <Wert in Euro>
...
Cash: <Betrag>

Rechne daraus:
- Allokation in vier Kategorien: Einzelaktien, ETFs & Fonds,
  Bitcoin & BTC-Treasuries (Bitcoin + MSTR + Metaplanet), Gold & Silber
- Dieselbe Aufstellung zusätzlich inklusive Cash
- Die acht größten Einzelpositionen in Prozent
- Veränderung gegenüber dem letzten Monat, falls Vormonatsdaten vorliegen

Baue daraus das Depot-Update, sechs Slides.
Absolute Beträge kommen nirgends vor — ausschließlich Prozente.
Lege die Rohdaten als data/depot_<JJJJ-MM>.json ab, damit der nächste
Monat vergleichen kann.
```

---

## 4 · Quartalszahlen

```
Quartalszahlen-Post zu <UNTERNEHMEN>, das ich im Depot halte.

Trage aus den veröffentlichten Zahlen zusammen:
Umsatz, Gewinn je Aktie, Nettomarge, Wachstum gegenüber Vorjahresquartal,
Ausblick des Unternehmens im Wortlaut.

Jede Zahl mit Quartal, Datum und Quelle.

Strikt: Nur referieren, was das Unternehmen veröffentlicht hat.
Keine Einordnung, ob das gut oder schlecht ist. Kein Kursziel.
Kein Satz darüber, was die Aktie jetzt machen wird.

Der einzige persönliche Teil ist: "Ich halte die Aktie seit <ZEITRAUM>,
und das waren die Zahlen."
```

---

## 5 · Highlight-Serie

```
Baue eine Story-Highlight-Serie zu <THEMA>, <ANZAHL> Slides plus Titelkarte.

Format 1080x1920. Titelkarte: das Thema klein geschrieben mit Punkt,
darunter kurze Linie und ein kursiver Untertitel.

Inhalt: erklärend, für jemanden der bei null anfängt. Keine Empfehlung.
Nummeriere die Dateien in Anzeigereihenfolge.
```

---

## 6 · Website

```
Baue eine statische Website für depotdiary.

Seiten:
  /            Depot-Allokation, aktuelle Zahlen, die letzten Posts
  /archiv      alle Posts, durchsuchbar, nach Datum und Kategorie filterbar
  /wissen      die Erklärstücke als lesbare Artikel
  /ueber       wer dahintersteht, plus Disclaimer und Impressum

Technik: statisches HTML, kein Framework, kein Build-Schritt.
Inhalte kommen aus JSON-Dateien in content/, damit neue Posts nur
einen Eintrag brauchen.

Design exakt nach CLAUDE.md — gleiche Farben, gleiche Serif, gleiche
Ruhe. Die Seite muss aussehen wie eine Fortsetzung der Slides.

Mobil zuerst: Über 80 % der Besucher kommen aus der Instagram-Bio.

Auf jeder Seite im Fuß: "Keine Anlageberatung. Nur mein eigener Weg."
```

---

## 7 · Automatisches Posten — mit Vorbehalt

```
Baue eine Veröffentlichungs-Pipeline für Instagram über die Meta Graph API.

Voraussetzungen, die ich selbst einrichte:
- Instagram Business-Konto, verknüpft mit einer Facebook-Seite
- Meta-Developer-App mit Berechtigung instagram_content_publish
- Langlebiger Access Token

Der Token wird aus einer .env gelesen und niemals in den Code oder in
die Ausgabe geschrieben. .env kommt in .gitignore.

Die API nimmt keine lokalen Dateien — Slides müssen unter einer
öffentlichen URL liegen. Baue den Upload-Schritt mit ein und sag mir,
welchen Hosting-Weg du vorschlägst.

Ablauf: Slides hochladen → Carousel-Container erzeugen → veröffentlichen →
Ergebnis protokollieren.

Baue einen Trockenlauf-Modus, der alles vorbereitet und nur den letzten
Schritt auslässt.
```

**Bevor du das nutzt:** Automatisiertes Posten nimmt dir die Gewohnheit, in der ersten Stunde nach Veröffentlichung in der App zu sein und Kommentare zu beantworten. Bei einem Account unter etwa 2.000 Followern ist genau das der stärkste Wachstumshebel. Automatisiere die Erstellung — poste vorerst von Hand.

---

## 8 · Wöchentlicher Ablauf

```
Wochenlauf für die kommende Woche.

1. Depot-Update aus den Zahlen, die ich gleich schicke
2. Vier Erklärstücke aus themen/backlog.md, jeweils sechs Slides
3. Alle Posts in beiden Formaten plus Kontaktabzüge
4. Captions und Voiceover-Skripte
5. Eine Übersicht: welcher Post an welchem Tag

Zeig mir am Ende alle Kontaktabzüge zur Freigabe, bevor irgendetwas
das Ausgabeverzeichnis verlässt.
```
