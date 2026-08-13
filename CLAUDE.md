# depotdiary — Projekt-Briefing für Claude Code

Dieses Dokument ist die Arbeitsanweisung. Lies es vollständig, bevor du irgendetwas erzeugst.
Leg es als `CLAUDE.md` in den Projektordner, dann wird es bei jedem Start automatisch geladen.

---

## 1. Wer der Absender ist

- 19 Jahre alt, Österreicher, investiert seit er **14** ist (erster Kauf: ein ETF)
- Erste Einzelaktie: Novo Nordisk
- Depot: ca. 23.800 € investiert, dazu 9.300 € Cash — **niemals absolute Beträge veröffentlichen**
- Matura mit 17, Zivildienst abgeschlossen, alles autodidaktisch erarbeitet
- Account: `@depotdiary` auf Instagram und TikTok

**Die Haltung, die jeden Text bestimmt:** Er erklärt *von daneben*, nicht *von oben*. Er ist kein Experte, sondern jemand, der es sich selbst beibringt und dabei zuschauen lässt. Fehler gehören dazu und werden benannt.

---

## 2. Die eiserne Sprachregel

> **Erzähle, was *er* tut. Sage nie, was *andere* tun sollen.**

| Erlaubt | Verboten |
|---|---|
| „Ich habe X gekauft, weil …" | „Kauf X" / „Du solltest X" |
| „Bei mir sieht das so aus" | „So solltest du es machen" |
| „Das habe ich falsch eingeschätzt" | „Diese Aktie ist unterbewertet" |
| Methode zeigen | Urteil fällen |

**Absolut verboten, ohne Ausnahme:**

- Kursziele
- Stop-Loss-Marken
- Kauf-, Verkaufs- oder Halteempfehlungen
- Tier-Lists oder Rankings **fremder** Aktien
- Bewertungen wie „günstig", „teuer", „unterbewertet"
- Prognosen über künftige Kursverläufe

Grund: Die BaFin hat im Januar 2026 gemeinsam mit der ESMA ein Finfluencer-Factsheet veröffentlicht. Konkrete Empfehlungen können als erlaubnispflichtige Anlageberatung gelten, und die MAR-Anzeigepflicht greift bei Anlagestrategieempfehlungen — Bußgelder bis 50.000 €. Ein Disclaimer hebt das **nicht** auf.

**Erlaubt und erwünscht:** Erklärwissen (was ist ein KGV, was ist EBITDA, wie funktioniert ein ETF), Berichte über das eigene Depot, eigene Kriterien, eigene Fehler, historische Fakten und veröffentlichte Unternehmenszahlen.

Jeder Post trägt im Fuß: `Keine Anlageberatung. Nur mein eigenes Depot.`
Bei Affiliate-Links zusätzlich sichtbar `Werbung` — nicht in den Hashtags versteckt.

---

## 3. Das Designsystem

### Farben — exakt diese, keine anderen

```
Hintergrund              #F2F0EA
Text · Struktur · Akzent #16181C
Grün (Akzentwort/Gewinn) #1A4D3C
Mittelgrün (Sekundär)    #4E8C6E
Ocker (Tertiär)          #B08A2E
Grau (Cash/Neutral)      #B7B1A4
Rot (nur Verluste)       #C0392B
Nebentext                #6E6A62
Karten/Flächen           #E7E3D9
Trennlinien              #D3CDC0
```

**Regel:** Farbe erscheint nur dort, wo Daten stehen. Struktur ist schwarz. Rot ausschließlich für negative Zahlen.

### Typografie

- Headlines: **DejaVu Serif Bold**, ein Wort pro Headline kursiv (`DejaVu Serif Bold Italic`) in `#1A4D3C`
- Fließtext: DejaVu Serif Regular, `#33352F`
- Eyebrow (Kategorielabel oben): Liberation Sans Bold, Versalien, Sperrung ca. 5 px, `#6E6A62`
- Keine dritte Schrift. Keine Effekte, keine Schatten, keine Verläufe.

### Layout

**Feed-Karussell:** 1080 × 1350 px
**Story / Reel / TikTok:** 1080 × 1920 px

Jede Slide:

1. Schwarzer Vertikalbalken links, 16 px breit, volle Höhe
2. Eyebrow oben (z. B. `PORTFOLIO · 02`)
3. Inhaltsblock **vertikal zentriert** — Headline, darunter kurze Akzentlinie (200 px, `#1A4D3C`, 5 px), dann optional Karte/Zeilen, dann Fließtext
4. Fußbereich: Trennlinie, `DEPOT DIARY` gesperrt, Seitenzahl rechts, Disclaimer darunter
5. **Nichts unterhalb von 88 % der Höhe** — sonst schneidet Instagram ab

**Titelkarten** je Highlight: Wort klein geschrieben mit Punkt (`portfolio.`), sehr groß, darunter kurze Linie und ein kursiver Untertitel.

### Slide-Aufbau eines Karussells

- Slide 1: Hook. Eine Aussage, max. 12 Wörter, muss in 1,5 Sekunden zünden
- Slide 2 bis n−1: ein Gedanke pro Slide, zwei bis drei Zeilen
- Letzte Slide: CTA `Folgen für die Fortsetzung` plus Wortmarke

---

## 4. Technische Umsetzung

Erzeuge die Slides **programmatisch mit Python und Pillow**, nicht mit Bildgeneratoren. Gründe: exakt reproduzierbare Typografie, korrekte Zahlen, beliebig oft wiederholbar.

Schriften auf dem System:
```
/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf
/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf
/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf
/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf
```

Jeder Post wird **immer in beiden Formaten** ausgegeben:
- `output/<postname>/instagram_4x5/slide_1.png …`
- `output/<postname>/tiktok_9x16/slide_1.png …`

Die 9:16-Variante entsteht durch Zentrieren der 4:5-Slide auf einer Fläche in `#F2F0EA` — kein Blur, kein Zuschneiden.

---

## 5. Wiederkehrende Formate

| Format | Rhythmus | Inhalt |
|---|---|---|
| **Depot-Update** | monatlich | Allokation in Prozent, Veränderungen zum Vormonat |
| **Wochennotiz** | sonntags | Was ich gekauft habe — oder warum ich nichts gemacht habe |
| **Erklärstück** | 2×/Woche | Eine Kennzahl, ein Begriff, ein Kostenpunkt |
| **Quartalszahlen** | zur Saison | Veröffentlichte Zahlen einer Position aus dem Depot, faktisch referiert |
| **Fehler** | 1×/Woche | Eine eigene Fehlentscheidung und was sie gekostet hat |

**Quartalszahlen-Regel:** Nur berichten, was veröffentlicht wurde — Umsatz, Gewinn, Marge, Wachstum gegenüber Vorjahr, Ausblick des Unternehmens. Immer mit Datum und Quelle. **Keine** Einordnung, ob das gut oder schlecht für den Kurs ist. Erlaubt ist: „Ich halte die Aktie und das waren die Zahlen."

---

## 6. Der Wochenablauf

1. **Sonntag:** Aktuelle Depotwerte bereitstellen → Allokation neu berechnen → Depot-Update erzeugen
2. Vier bis fünf Posts für die Woche erzeugen, beide Formate
3. Captions mitschreiben — gleiche Stimme, Frage am Ende, Disclaimer, 6–8 Hashtags
4. Reels: Slides + Voiceover-Skript, Schnitt separat
5. Veröffentlichung terminieren

---

## 7. Captions

Aufbau: Hook aus Slide 1 aufgreifen → drei bis vier kurze Absätze → **eine Frage an die Leser** → Disclaimer → 6–8 Hashtags.

Ton: erste Person, kurze Sätze, keine Ausrufezeichen, keine Emojis, keine Superlative.

Hashtags: `#depot #aktien #etf #investieren #finanzen #vermögensaufbau #börse #sparplan`

---

## 8. Was dieses Projekt ausdrücklich nicht macht

- Keine KI-generierten Bilder oder Stockfotos — sie senken in dieser Nische sofort die Glaubwürdigkeit
- Keine Kursziele, keine Rankings fremder Aktien, keine Prognosen
- Keine absoluten Eurobeträge des Depots
- Keine Behauptung von Expertise
- Kein Verschweigen von Verlusten
