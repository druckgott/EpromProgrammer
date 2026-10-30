# Archiv: alte Linux-Qt-GUI (EpQt)

Die Qt5-GUI lief nur unter Linux bzw. unter Windows über WSL1 + VNC. Sie ist durch die Web-App in [`web/`](../web) ersetzt und wird nicht mehr gepflegt.

## GUI images
![Write](../images/write.jpg) ![Verify](../images/verify.jpg) ![EPROM options](../images/eprom.jpg)


# EpromProgrammer GUI unter Windows (WSL1 & VNC-Browser-Methode)

Diese Anleitung beschreibt, wie die Linux-basierte Qt5-GUI des EpromProgrammers nativ unter Windows ausgeführt werden kann, ohne dass der C++-Code umgeschrieben oder ein externer X-Server (wie XLaunch/VcXsrv) installiert werden muss.

Wir nutzen **WSL1** (Windows Subsystem for Linux) in Kombination mit dem Qt-internen VNC-Server und `noVNC`, um die grafische Oberfläche direkt im Webbrowser (Chrome, Edge, Firefox) anzuzeigen.

---

## 🛠️ 1. Voraussetzungen & Installation

Öffne ein WSL-Terminal (z. B. Ubuntu 20.04 via VS Code) und installiere die benötigten Compiler, Bibliotheken und VNC-Tools:

```bash
sudo apt update
sudo apt install build-essential cmake git
sudo apt install libqt5widgets5 libqt5gui5 libqt5core5a qtwayland5
sudo apt install novnc websockify
```

⚠️ **Wichtiger Bugfix für WSL1 (Ubuntu 20.04):** WSL1 hat ein Problem mit der Komprimierung der Qt5Core-Bibliothek. Damit das Programm startet, muss ein inkompatibler Tag entfernt werden:

```bash
sudo strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5
```

---

## 🏗️ 2. Kompilieren (Build)

Lade den Code herunter, wechsle in das Verzeichnis und starte den Build-Prozess mit CMake:

```bash
# In den GUI-Ordner wechseln
cd /Pfad/zu/deinem/EpromProgrammer/archive/gui

# Build-Ordner erstellen und vorbereiten
mkdir build
cd build
cmake ..

# Programm kompilieren
make
```

Das ausführbare Programm `EpQt` befindet sich nun im `build`-Ordner.

---

## 🚀 3. Programm starten (Browser-Methode)

Da WSL1 keinen eigenen Monitor hat, lassen wir das Programm als unsichtbaren Server laufen und greifen das Bild über den Browser ab.

### Schritt 1: GUI im VNC-Modus starten (Terminal 1)

Bleibe im `build`-Ordner und starte die GUI als VNC-Server. (Das Terminal bleibt danach scheinbar stehen – das ist korrekt so!)

```bash
./EpQt -platform vnc
```

### Schritt 2: Web-Brücke starten (Terminal 2)

Öffne ein zweites Terminal-Fenster und starte `websockify`. Dieser Dienst übersetzt das VNC-Signal (Port 5900) für deinen Webbrowser (Port 8080):

```bash
websockify --web=/usr/share/novnc/ 8080 localhost:5900
```

### Schritt 3: GUI im Browser öffnen

Öffne in Windows deinen Webbrowser und rufe folgende Adresse auf:

👉 `http://localhost:8080/vnc.html`

Klicke auf **Connect** – die grafische Oberfläche des EpromProgrammers erscheint nun in deinem Browser!

---

## 🔌 4. Arduino / COM-Port verbinden

In WSL1 werden die COM-Ports von Windows exakt 1:1 auf Linux-Ports gemappt:

| Windows | Linux (WSL1) |
|---------|--------------|
| COM1    | `/dev/ttyS1` |
| COM9    | `/dev/ttyS9` |

### COM-Port prüfen (WSL1-Trick)

Da du WSL1 nutzt, hast du direkten Zugriff auf Windows-Befehle. Du kannst dir die aktiven COM-Ports ganz einfach anzeigen lassen, indem du dieses alte DOS-Kommando direkt in dein Linux-Terminal eintippst:

```bash
mode.com
```

Dieser Befehl listet alle aktuell unter Windows aktiven seriellen Schnittstellen auf (z. B. `Status von Gerät COM9:`). Wenn `COM9` dort auftaucht, weißt du sicher, dass er da ist und in Linux als `/dev/ttyS9` angesprochen werden kann.

### Rechte setzen

Falls die GUI beim Verbinden meldet, dass sie keine Berechtigung hat, musst du dem Port einmalig Lese- und Schreibrechte geben (Beispiel für COM9):

```bash
sudo chmod 666 /dev/ttyS9
```

Wähle danach einfach `/dev/ttyS9` in der GUI aus und klicke auf **Connect**. Das Terminal-Log sollte nun `Connected to eprom programmer.` anzeigen.

---

## 🩹 5. Troubleshooting: Programm hängt beim Auslesen (CH340-Problem)

Wenn das Auslesen eines EPROMs mitten im Vorgang stehen bleibt (z. B. hängt der Fortschritt an einer bestimmten Adresse wie `17EC0` und geht einfach nicht mehr weiter), liegt das erfahrungsgemäß **nicht** an der GUI, sondern am Windows-Treiber des CH340-USB-Chips, der auf vielen Arduino-Nano-Klonen verbaut ist.

**Ursache:** Windows legt für den CH340 standardmäßig große FIFO-Puffer an (im Gerätemanager meist auf `High (14)` bzw. `High (16)` voreingestellt). Windows schaufelt dadurch möglichst viele Daten auf einmal in den winzigen Hardware-Zwischenspeicher des Chips. Da WSL1 die Daten aber nicht in Echtzeit schnell genug abholt, läuft dieser Hardware-Puffer voll, und der Chip bricht die Übertragung hart ab — genau das äußert sich als "Hängenbleiben" beim Lesen.

### Lösung: FIFO-Puffer im Windows-Gerätetreiber deaktivieren

1. Öffne den **Windows Gerätemanager**.
2. Suche unter *Anschlüsse (COM & LPT)* den entsprechenden CH340-Port (z. B. `USB-SERIAL CH340 (COM9)`), Rechtsklick → **Eigenschaften**.
3. Wechsle zum Reiter **Anschlusseinstellungen** und klicke dort auf **Erweitert...** (*Advanced...*).
4. Im sich öffnenden Fenster siehst du die Option **Use FIFO buffers** mit zwei Reglern (Receive/Transmit), die standardmäßig auf `High (14)` / `High (16)` stehen.
5. **Nimm den Haken bei "Use FIFO buffers" komplett heraus** — alternativ kannst du testweise stattdessen beide Regler ganz nach links auf `Low (1)` schieben.
6. Klicke in beiden Fenstern auf **OK**, um die Einstellungen zu speichern.
7. Trenne den Arduino kurz vom USB-Port, stecke ihn wieder ein und starte in der GUI einen neuen Leseversuch.

### Falls das Problem trotzdem bestehen bleibt

Sollte WSL1 die rohen Binärdaten danach immer noch blockieren, ist der Windows-Treiber an dieser Stelle ein praktisch unüberwindbarer Flaschenhals. In diesem Fall bleibt als stressfreier Ausweg nur der Umbau der `read.cpp` auf reinen Hex-Text-Output, um das EPROM zuverlässig und vollständig auslesen zu können.
