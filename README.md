# EPROM Programmer – Arduino Mega + Web-App

UV-EPROMs (getestet mit **ST M27C4001**) auslesen und beschreiben mit einem **Arduino Mega 2560**, direkt verdrahtet ohne Schieberegister. Bedient wird das Ganze über eine **Web-App im Browser** (Chrome/Edge, Web Serial API) – direkt unter Windows, ohne WSL oder Treiber-Umwege.

Anwendungsbeispiel: das CPU-Game-ROM eines Flippers **The Simpsons Pinball Party (Stern, 2003, Whitestar-System)** auf einen M27C4001 brennen – siehe [Beispiel: Simpsons Pinball Party](#beispiel-simpsons-pinball-party-stern).

Basiert auf dem EpromProgrammer von Ciprian Stingu (Arduino Nano + Schieberegister + Linux-Qt-GUI), Lizenz GPL v2. Das ursprüngliche Projekt ist unter [`archive/`](archive/README.md) dokumentiert.

## Stand

| Funktion | Status |
| :--- | :--- |
| Verbinden über Web-App (COM-Port, CH340) | ✅ funktioniert |
| Lesen 27C4001 (512 KiB) inkl. Live-Hex-Dump, Leer-Prüfung | ✅ funktioniert |
| Speichern als `.bin` | ✅ eingebaut |
| Schreiben (Fast) mit Live-Fortschritt | ✅ läuft am Gerät, gemessen ca. 636 B/s (27C4001 ≈ 14 min) |
| Automatisches Verify nach dem Schreiben | ⚠️ eingebaut, kompletter Durchlauf am Gerät noch ausstehend |
| VCC-Umschaltung 5 V ↔ 6,25 V (Pin 53) | ⚠️ in Betrieb (Fast), Umschaltzeit **noch nicht mit dem Oszi nachgemessen** |
| Spannungsmessung Vcc/Vpp | ❌ nicht vorhanden – die Firmware meldet einfach die angeforderten Werte zurück |

## Projektstruktur

| Ordner | Inhalt |
| :--- | :--- |
| `src/` | Firmware für den Arduino Mega (PlatformIO) |
| `web/` | Web-App (`index.html`, eine Datei, keine Abhängigkeiten) |
| `images/` | Fotos, Pinout und Schaltpläne |
| `archive/` | Alte Linux-Qt-GUI und Doku des ursprünglichen Nano-Projekts |
| `hardware/`, `FreeCAD/` | PCB und Gehäuse des **ursprünglichen Nano-Aufbaus** (passen nicht zum Mega-Aufbau) |

## Fotos

Arduino Mega mit EPROM-Sockel und Breadboard für die Schaltstufen, versorgt über ein Labornetzteil:

![Aufbau mit Labornetzteil](images/mega_aufbau.jpg)

![EPROM-Sockel auf dem Mega](images/mega_sockel.jpg)

---

# Aufbau: Arduino Mega, direkt verdrahtet

Dieses Projekt ermöglicht das Auslesen und Beschreiben von UV-EPROMs (speziell **ST M27C4001 / 27C040**) mit einem Arduino Mega 2560.
Durch die hohe Anzahl an Pins am Mega werden **keine Schieberegister** benötigt. Das EPROM wird direkt verkabelt.

Alle Tabellen unten enthalten jetzt drei Spalten, damit keine Verwechslung mehr möglich ist:
- **EPROM Pin** = die physische Pin-Nummer am Gehäuse (1–32, wie im Pinout-Bild eingekreist)
- **Chip-Label** = die Bezeichnung, die exakt so auf dem Pinout-Diagramm des Herstellers steht (z. B. `VSS`, nicht "GND")
- **Bedeutung / Arduino-Pin** = Erklärung bzw. Zielpin am Arduino Mega

## ⚠️ Wichtiger Warnhinweis
Das M27C4001 arbeitet beim **Lesen** mit 5V, benötigt zum **Schreiben** (Brennen) jedoch zwingend:
- **12,75V ± 0,25V an Pin 1 (Chip-Label `VPP`)**
- **6,25V ± 0,25V an Pin 32 (Chip-Label `VCC`)** — nicht nur 5V!

**Verbinde NIEMALS die 12,75V direkt mit einem Pin des Arduinos!** Dies zerstört den Mikrocontroller sofort. Nutze zwingend die unten beschriebene Transistor-Schaltung.

**Power-Sequencing-Regel (laut Datenblatt zwingend einzuhalten):**
> VCC muss gleichzeitig mit oder vor VPP angelegt werden. Beim Abschalten gilt die umgekehrte Reihenfolge: VPP zuerst runter, dann VCC.

D.h. in der Steuerlogik (Sketch) immer: **VCC hoch → dann VPP hoch** beim Start des Schreibens, und **VPP runter → dann VCC runter** beim Beenden. Niemals VPP ohne anliegendes VCC schalten.

Datenblatt: https://www.datasheet-pdf.info/entry/M27C4001

---

## 1. Spannungsversorgung (Power)

| EPROM Pin | Chip-Label | Bedeutung | Anschluss am Arduino Mega / Schaltung |
| :--- | :--- | :--- | :--- |
| 16 | **VSS** | Masse (0V) — *im Pinout-Bild steht `VSS`, nicht "GND"* | `GND` (Masse) |
| 32 | **VCC** | Versorgungsspannung | **Schaltbare Versorgung: 5V zum Lesen / 6,25V ± 0,25V zum Schreiben** (siehe Abschnitt 6) |
| 1 | **VPP** | Programmierspannung | *Geht an den Ausgang der Transistor-Schaltung (siehe Abschnitt 5)* |

![Pinout_M27C4001](images/M27C4001.png)

> **Hinweis:** Anders als in älteren Bauanleitungen oft angenommen, reicht ein fester 5V-Anschluss an VCC **nicht** aus. Für den Programmiermodus muss VCC auf 6,25V angehoben werden – sonst läuft der Chip außerhalb der Spezifikation und das Programmieren funktioniert nicht zuverlässig (Datenblatt: "TA = 25°C; VCC = 6,25V ± 0,25V; VPP = 12,75V ± 0,25V" im Programmiermodus).

---

## 2. Daten-Pins (PORTA für maximale Geschwindigkeit)

| EPROM Pin | Chip-Label | Arduino Mega Pin |
| :--- | :--- | :--- |
| 13 | **Q0** | Digital `22` |
| 14 | **Q1** | Digital `23` |
| 15 | **Q2** | Digital `24` |
| 17 | **Q3** | Digital `25` |
| 18 | **Q4** | Digital `26` |
| 19 | **Q5** | Digital `27` |
| 20 | **Q6** | Digital `28` |
| 21 | **Q7** | Digital `29` |

![Pinout_M27C4001](images/M27C4001.png)

---

## 3. Adress-Pins

| EPROM Pin | Chip-Label | Arduino Mega Pin |
| :--- | :--- | :--- |
| 12 | **A0** | Digital `30` |
| 11 | **A1** | Digital `31` |
| 10 | **A2** | Digital `32` |
| 9 | **A3** | Digital `33` |
| 8 | **A4** | Digital `34` |
| 7 | **A5** | Digital `35` |
| 6 | **A6** | Digital `36` |
| 5 | **A7** | Digital `37` |
| 27 | **A8** | Digital `38` |
| 26 | **A9** | Digital `39` |
| 23 | **A10** | Digital `40` |
| 25 | **A11** | Digital `41` |
| 4 | **A12** | Digital `42` |
| 28 | **A13** | Digital `43` |
| 29 | **A14** | Digital `44` |
| 3 | **A15** | Digital `45` |
| 2 | **A16** | Digital `46` |
| 30 | **A17** | Digital `47` |
| 31 | **A18** | Digital `48` |

![Pinout_M27C4001](images/M27C4001.png)

---

## 4. Steuer-Pins

| EPROM Pin | Chip-Label | Bedeutung | Arduino Mega Pin |
| :--- | :--- | :--- | :--- |
| 22 | **Ē** (im Bild als "E" mit Überstrich) | Chip Enable (Aktiv LOW) | Digital `50` |
| 24 | **Ḡ** (im Bild als "G" mit Überstrich) | Output Enable (Aktiv LOW) | Digital `51` |
| - | *(kein EPROM-Pin, externe Steuerlogik)* | VPP_EN — steuert deine VPP-Transistor-Schaltung | Digital `52` |
| - | *(kein EPROM-Pin, externe Steuerlogik)* | VCC_EN — steuert deine VCC-Umschaltung 5V ↔ 6,25V | Digital `53` |

![Pinout_M27C4001](images/M27C4001.png)

> **Zur Klarstellung:** Auf dem Chip-Gehäuse selbst sind nur `Ē` (Pin 22) und `Ḡ` (Pin 24) aufgedruckt — "CE" und "OE" sind nur die gebräuchlichen Namen dafür in Datenblättern/Schaltplänen, keine eigenen Chip-Labels. `VPP_EN` und `VCC_EN` sind keine EPROM-Pins, sondern nur die Bezeichnungen, die *du* für die beiden Steuerleitungen zu deinen Transistor-Schaltungen vergibst.

> **Hinweis SPI:** Digital 50–53 sind auf dem Mega gleichzeitig die Hardware-SPI-Pins (MISO/MOSI/SCK/SS). Solange du kein weiteres SPI-Gerät (z. B. SD-Karten-Modul) parallel nutzt, ist das unproblematisch.

---

## 5. Die 12,75V VPP Transistor-Schaltung (High-Side Switch)

Um die 12,75V schnell und sicher ein- und auszuschalten, baust du eine kleine Schaltung auf dem Breadboard auf. Arduino-Pin 52 steuert diese Schaltung.

**Aus deinem vorhandenen Bauteil-Sortiment verwenden wir hier: NPN = `BC337`, PNP = `BC327`.**
Beide sind für bis zu 45V / 800mA spezifiziert — bei nur 12,75V und wenigen mA Laststrom (IPP max. 50mA laut Datenblatt) ist das mehr als ausreichend Reserve.

### Benötigte Bauteile:
* 1x externes DC-Netzteil (exakt **12,75V ± 0,25V**, einstellbar)
* 1x **BC337** (NPN)
* 1x **BC327** (PNP)
* 2x 1kΩ Widerstand
* 1x 10kΩ Widerstand
* 1x Schottky-Diode (z. B. 1N5819) — *statt Standard-Silizium-Diode, siehe Begründung unten*

> **Pinout BC337 / BC327 (TO-92):** Flache Seite zu dir, Beinchen nach unten → von links nach rechts **C – B – E** (Kollektor – Basis – Emitter). Das ist bei beiden identisch, nur die Stromrichtung (NPN vs. PNP) unterscheidet sich. Achtung: Das ist eine andere Pin-Reihenfolge als z. B. bei 2N3904/2N3906 (dort EBC) — beim Verdrahten also nicht verwechseln.

### Aufbau der Schaltung:

1. **Gemeinsame Masse:** Verbinde den Minus-Pol (GND) deines 12,75V-Netzteils zwingend mit dem GND des Arduinos.
2. **Der Steuereingang:** Verbinde Arduino **Pin 52** über einen **1kΩ Widerstand** mit der **Basis (mittleres Bein)** des **BC337**.
3. **NPN Masse:** Verbinde den **Emitter (rechtes Bein)** des **BC337** mit **GND**.
4. **Verbindung der Transistoren:** Verbinde den **Kollektor (linkes Bein)** des **BC337** über den zweiten **1kΩ Widerstand** mit der **Basis (mittleres Bein)** des **BC327**.
5. **Der 12,75V Eingang:** Verbinde den **Emitter (rechtes Bein)** des **BC327** mit dem Plus-Pol (**12,75V**) deines Netzteils.
6. **Pull-Up für Sicherheit:** Setze den **10kΩ Widerstand** zwischen den Emitter (12,75V) und die Basis des **BC327** (hält ihn standardmäßig sicher abgeschaltet).
7. **Der VPP Ausgang:** Der **Kollektor (linkes Bein)** des **BC327** geht direkt an **Pin 1 (Chip-Label `VPP`)** des EPROMs.

### Der Dioden-Trick (Für das Auslesen):
Das EPROM verlangt, dass am VPP-Pin während des reinen Auslesens VPP = VCC anliegt.
* Setze die **Schottky-Diode** so ein, dass der Strom vom **VCC-Pin des EPROMs** zum **VPP-Pin des EPROMs** fließen kann (der Ring/Strich der Diode zeigt zum EPROM-VPP-Pin).
* **Warum Schottky statt Standarddiode?** Eine normale Silizium-Diode (1N4148/1N4007) hat ca. 0,6–0,7V Flussspannung – dann läge VPP beim Lesen nur bei ca. 4,3–4,4V statt der geforderten ~5V (VPP = VCC). Eine Schottky-Diode hat nur ca. 0,2–0,3V Abfall und liegt damit deutlich näher an der Spezifikation.
* **Wichtig:** Die Diode muss vom **VCC-Pin** des EPROMs abgehen, nicht fest vom 5V-Arduino-Pin — da VCC bei dir jetzt schaltbar zwischen 5V und 6,25V ist (siehe Abschnitt 6), folgt VPP beim Lesen automatisch dem aktuellen VCC-Pegel.
* Wenn Arduino Pin 52 auf HIGH schaltet und die vollen 12,75V aus der Transistor-Schaltung auf VPP treiben, sperrt die Diode in Rückwärtsrichtung und schützt den Rest der Schaltung.

![VPP Transistor-Schaltung](images/vpp_schaltung.svg)

---

## 6. Die VCC-Umschaltung (5V ↔ 6,25V)

> **Stand Firmware:** Beim **Fast**-Algorithmus (wenn die Web-App Vcc > 5,5 V anfordert) schaltet die Firmware Pin 53 nur für jeden Brennimpuls: VCC hoch → VPP an → Impuls → VPP aus → VCC zurück auf 5 V → Verify. Das Verify läuft bei 5 V, damit das EPROM die Datenleitungen nicht mit 6,25 V in die Mega-Pins treibt (ATmega max. ca. 5,5 V). Die Einschwingzeit `VCC_SETTLE_US` (500 µs, `src/defines.h`) ist geschätzt – am Oszi nachmessen. **Standard** bleibt bei 5 V.

Damit VCC im Programmiermodus auf 6,25V angehoben werden kann, baust du eine zweite High-Side-Switch-Schaltung auf — nach demselben Prinzip wie die VPP-Schaltung in Abschnitt 5, aber mit einem anderen Transistorpaar aus deinem Bestand, damit du die beiden Schaltungen auf dem Breadboard nicht verwechselst:

**Für die VCC-Schaltung verwenden wir: NPN = `S8050`, PNP = `S8550`.**

> **Pinout S8050 / S8550 (TO-92):** Flache Seite zu dir, Beinchen nach unten → von links nach rechts **E – B – C** (Emitter – Basis – Kollektor). Achtung: Das ist die *umgekehrte* Reihenfolge zu BC337/BC327 (dort CBE) — die beiden Schaltungen sehen auf dem Breadboard also unterschiedlich verdrahtet aus, obwohl sie funktional identisch sind.

### Benötigte Bauteile:
* 1x zweite Spannungsquelle (exakt **6,25V ± 0,25V**, einstellbar)
* 1x **S8050** (NPN)
* 1x **S8550** (PNP)
* 2x 1kΩ Widerstand
* 1x 10kΩ Widerstand
* 1x **zweite Schottky-Diode** (z. B. 1N5819) — *zwingend erforderlich, siehe Punkt 8 unten, sonst bleibt VCC im Lesemodus stromlos!*

### Aufbau:

Du brauchst dafür eine **zweite Spannungsquelle mit 6,25V** (z. B. ein zweites Netzteil oder ein mit LM317 auf 6,25V eingestellter Regler). Das normale 5V des Arduinos bleibt als Standard-VCC bestehen; die 6,25V werden nur während des Programmierens dazugeschaltet.

1. **Gemeinsame Masse:** GND der 6,25V-Quelle mit GND des Arduinos verbinden.
2. **Steuereingang:** Arduino **Pin 53** über einen **1kΩ Widerstand** an die **Basis (mittleres Bein)** des **S8050**.
3. **NPN Masse:** **Emitter (linkes Bein)** des S8050 an GND.
4. **Verbindung:** **Kollektor (rechtes Bein)** des S8050 über einen zweiten **1kΩ Widerstand** an die **Basis (mittleres Bein)** des **S8550**.
5. **6,25V-Eingang:** **Emitter (linkes Bein)** des S8550 an den Plus-Pol der 6,25V-Quelle.
6. **Pull-Up:** **10kΩ Widerstand** zwischen 6,25V-Plus und Basis des S8550 (Schaltung ist im Ruhezustand sicher aus).
7. **Ausgang:** **Kollektor (rechtes Bein)** des S8550 geht auf den **VCC-Pin (Pin 32, Chip-Label `VCC`) des EPROMs**.
8. ⚠️ **5V-Grundversorgung (zwingend erforderlich, nicht optional!):** Verbinde eine **zweite Schottky-Diode** (z. B. 1N5819) zwischen dem 5V-Arduino-Pin und dem VCC-Pin des EPROMs — genau wie beim VPP-Dioden-Trick in Abschnitt 5:
   * **Anode** (Ende ohne Ring) → **5V-Pin des Arduino Mega**
   * **Kathode** (Ende mit Ring) → **Pin 32 (VCC) des EPROMs**, also an denselben Knoten, an dem auch der Kollektor des S8550 ankommt.

> **Warum ist diese Diode nötig?** Solange Arduino-Pin 53 im Lesemodus `LOW` ist, sperrt der PNP-Transistor S8550 komplett — er lässt die 6,25V nicht durch. Ohne diese Diode bekommt Pin 32 des EPROMs beim Lesen **0 Volt**, der Chip ist stromlos und zieht alle Datenleitungen wie ein "totes Bauteil" auf Masse (Auslesen liefert dann nur `00`-Bytes). Mit der Diode fließen im Ruhezustand ca. 4,7V vom Arduino-5V-Pin zum EPROM-VCC — genug zum Lesen. Beim Schreiben schaltet der S8550 die vollen 6,25V auf VCC; die Diode sperrt dann automatisch rückwärts, sodass die 6,25V nicht in den 5V-Pin des Arduinos zurückfließen und ihn beschädigen können.

**Wichtig für die Sequenz:** Dein Sketch muss VCC **immer zuerst** auf 6,25V bringen (Pin 53 HIGH), **bevor** VPP auf 12,75V geschaltet wird (Pin 52 HIGH) — und beim Beenden umgekehrt: erst VPP auf 0 (Pin 52 LOW), dann VCC zurück auf 5V (Pin 53 LOW).

![VCC-Umschaltung](images/vcc_schaltung.svg)

### Restliche Bauteile aus deinem Bestand (Reserve / Alternativen)

Falls du BC337/BC327 oder S8050/S8550 mal ersetzen musst, hier die Pinouts der übrigen Transistoren aus deiner Liste — **Achtung, teils unterschiedliche Pin-Reihenfolge**, immer vor dem Einlöten prüfen:

| Typ | Polarität | TO-92 Pinout (flache Seite zu dir, Beine unten, links→rechts) |
| :--- | :--- | :--- |
| 2N3904 | NPN | E – B – C |
| 2N2222 | NPN | E – B – C |
| C1815 | NPN | E – C – B |
| A1015 | PNP | E – C – B |
| 2N2907 | PNP | E – B – C |
| 2N3908* | PNP | *vermutlich 2N3906 gemeint (EBC) — Aufdruck am Bauteil prüfen, „2N3908" ist keine gängige Standardbezeichnung* |

*C1815/A1015 haben zudem nur max. 150mA Kollektorstrom — für diese Schaltung (wenige mA) trotzdem problemlos ausreichend, aber als Hauptschalter etwas knapper dimensioniert als BC337/BC327.*

---

---

# Firmware (Arduino Mega)

Die Firmware liegt in `src/` und wird mit [PlatformIO](https://platformio.org/) gebaut (`platformio.ini`, Umgebung `megaatmega2560`):

```bash
pio run                                   # bauen
pio run -t upload --upload-port COM10     # flashen (COM-Port anpassen)
```

Vor dem Flashen die Verbindung in der Web-App trennen – der COM-Port kann nur von einem Programm gleichzeitig genutzt werden.

Nach dem Start meldet sich die Firmware mit 115200 Baud mit `27[C]XXXX programmer (Mega Direct)`.

| Pin | Funktion |
| :--- | :--- |
| 22–29 (PORTA) | Daten Q0–Q7 |
| 30–48 | Adressen A0–A18 |
| 50 | Ē (Chip Enable) |
| 51 | Ḡ (Output Enable) |
| 52 | VPP_EN (12,75-V-Schaltstufe) |
| 53 | VCC_EN (6,25-V-Schaltstufe, nur Fast) |

---

# Web-App (Lesen & Schreiben im Browser)

Die Bedienung läuft direkt im Browser über die **Web Serial API**. Kein WSL, kein VNC, keine Installation – nur Chrome oder Edge.

## Starten

```bash
cd web
python -m http.server 8765 --bind 127.0.0.1
```

Dann im Browser `http://127.0.0.1:8765/index.html` öffnen. (Web Serial braucht `localhost`/`127.0.0.1` oder HTTPS.)

## Bedienung

1. **Verbinden** klicken und den Port des Arduino wählen (z. B. `USB-SERIAL CH340 (COM10)`). Der Mega wird dabei neu gestartet, die App wartet auf die Meldung `27[C]XXXX programmer`.

   ![Port-Auswahl](images/webapp_port.png)
2. **Typ** des EPROMs wählen (z. B. 27C4001). Algorithmus, Vcc und Vpp werden aus der Typ-Tabelle vorbelegt und können angepasst werden.
3. **Lesen** – der Inhalt erscheint live als Hex-Dump. Danach wird angezeigt, ob das EPROM leer ist (alles `FF`). **Speichern** legt den Inhalt als `.bin` ab.

   ![Lesen mit Live-Hex-Dump](images/webapp_lesen.png)
4. **Datei öffnen** (`.bin`) – ist die Datei kleiner als das EPROM, wird der Rest mit `FF` aufgefüllt.
5. **Schreiben** – brennt die Datei blockweise (32 Byte) und liest danach automatisch zur Kontrolle zurück. Bereits richtige Bytes und `FF`-Bytes werden übersprungen – ein abgebrochener Schreibvorgang kann also einfach neu gestartet werden.

   Während des Schreibens zeigt die App unter dem Balken eine Live-Zeile mit Adresse, Prozent, Tempo (B/s), Laufzeit, geschätzter Restzeit und **„letzte Antwort vor X s“**. Die Firmware meldet sich nach jedem Block; kommt länger als 5 s nichts, wird die Zeile rot („keine Antwort vom Programmer“). Alle 15 s landet eine Fortschrittszeile im Log, bei einem Fehler zusätzlich die letzten 40 Serial-Ereignisse.

   ![Schreiben mit Live-Fortschritt](images/webapp_schreiben.png)
6. **Verify** – vergleicht das EPROM mit der geladenen Datei und meldet die erste Abweichung.

Nur ein Programm kann den COM-Port gleichzeitig nutzen (Arduino-IDE-Monitor, PlatformIO-Monitor usw. vorher schließen).

## Hinweise

* Die Firmware sendet beim Lesen Hex-Text (`FF FF …`), nicht Binärdaten. Gemessen ca. 3,3 KB/s – ein 27C4001 (512 KiB) braucht damit rund 2,5–3 Minuten.
* Schreiben: **Fast** (110-µs-Impulse, Vcc 6,25 V) schafft gemessen ca. 636 B/s. **Standard** brennt jedes Byte mit mind. 50 ms – ein voller 27C4001 dauert damit rund 7 Stunden. Die App zeigt die Schätzung vor dem Start an.
* Das Feld **Vcc** stellt keine Spannung ein: Ab 5,5 V schaltet die Firmware bei Fast nur Pin 53 (6,25-V-Quelle über den S8550). Die 6,25 V müssen an der zweiten Netzteilquelle eingestellt sein.
* Die Firmware misst Vcc/Vpp nicht – die Werte in der App werden nur übertragen. Die Spannungen müssen am Netzteil bzw. an den Schaltstufen stimmen.
* Die alte Linux-Qt-GUI (WSL1 + VNC) liegt in [`archive/`](archive/README.md) und wird nicht mehr gepflegt.

## Beispiel: Simpsons Pinball Party (Stern)

*The Simpsons Pinball Party* (Stern, 2003) läuft auf dem **Sega/Stern-Whitestar**-System. Das Spielprogramm steckt im **CPU-Game-EPROM U210** auf der CPU/Sound-Platine. Die letzte Version ist **CPU 5.00** (`spp-cpu.500`, 1 Mbit = 128 KiB, Stand 2. Juli 2007). Laut Release-Notes setzt die CPU-Version 4.00 auch Display-ROM 4.00 oder neuer voraus – das Display-ROM also mit aktualisieren.

So wurde es hier gemacht:

1. Das 128-KiB-Image 4× hintereinander zu 512 KiB zusammengesetzt (`spp-cpu-512k.500`), damit es auf einem **M27C4001** unabhängig von den oberen Adressleitungen gleich aussieht:
   ```bash
   cat spp-cpu.500 spp-cpu.500 spp-cpu.500 spp-cpu.500 > spp-cpu-512k.500
   ```
2. In der Web-App Typ **27C4001**, Algorithmus **Fast** (Vcc 6,25 V, Vpp 12,75 V), Datei öffnen, **Schreiben** – Dauer ca. 14 Minuten plus Verify.

> Nicht geprüft: welche EPROM-Größen der U210-Sockel der Whitestar-Platine ohne Jumperänderung annimmt. Vor dem Einsetzen Platine/Service-Unterlagen prüfen. Alle ICs auf Whitestar-CPU/Sound-Platinen sitzen mit der **Kerbe nach unten** ([PinWiki](https://pinwiki.com/wiki/index.php/Sega/Stern_Whitestar_Repair)).

Quellen: [PinWiki – Sega/Stern Whitestar Repair](https://pinwiki.com/wiki/index.php/Sega/Stern_Whitestar_Repair), [Pinside – TSPP Versionen/U210](https://pinside.com/pinball/forum/topic/tspp-another-noob-question-sorry).

## Unterstützte EPROM-Typen

Die Web-App bietet alle Typen der Firmware an (jeweils die „Generic“-Werte für Vpp/Vcc, von Hand änderbar): 2716, 27C16, 2732, 27C32, 2764, 27C64, 27128, 27C128, 27256, 27C256, 27512, 27C512, 27C010, 27C1001, 27C020, 27C2001, 27C040, 27C4001, 27C080.

**Einschränkungen des Mega-Aufbaus:**
* Die Verdrahtung oben ist für 32-polige Chips mit dem Pinout des **M27C4001 / 27C040** gemacht. 24- und 28-polige Typen (2716 … 27512) haben ein anderes Pinout und brauchen eine eigene Verdrahtung – ungetestet.
* Es sind nur die Adressleitungen A0–A18 verdrahtet (max. 512 KiB). Der **27C080 (1 MiB)** braucht A19 und wird mit diesem Aufbau nicht vollständig gelesen/geschrieben.

## Chip-Info

![CHIP](images/chip.png)

## Lizenz

GPL v2, siehe [LICENSE](LICENSE).
