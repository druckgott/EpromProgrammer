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

---

# Ursprüngliches Projekt (Arduino Nano)
2716 through 27080 Eprom Programmer

A programmer for EPROMs with capacities between 2KiB (2716 series) and 1MiB (27C080 series).  
It uses an Arduino NANO and few other components.  
As a starting point I used the excelent [arduino_eprom27_programmer](https://github.com/walhi/arduino_eprom27_programmer) project

## Main features
* It supports a large number of EPROMs with different capacities
* 2 programming speeds (normal & fast). Fast programming speed is available if you configure the VCC correctly
* On fast programming alghoritm, writing a 27C040 EPROM takes around 290 seconds
* Error detection on writing
* Additional verify option

## Hardware
All the files which you need in order to create the PCBs are in the [hardware](../hardware) folder.

## Case
The files for 3D printing a case are available in [FreeCAD](../FreeCAD) folder

## Limitations in current implementation
* Bedienung über die Web-App nur in Chrome oder Edge (Web Serial API)

## Supported EPROMs
```
//------------- 2716 -------------
2716 - Generic, 2716 - AMD, ET2716, HN462716, 2716 - Intel, M2716, M5L2716K, MBM2716, MCM2716, uPD2716
//------------- 27C16 -------------
27C16 - Generic, 27C16 - National, AM2716B, NMC27C16B
//------------- 2732 -------------
2732 - Generic, AM2732, AM9732, F2732, HN462732, 2732A, M2732A, MBM2732, NTE2732A, TMM2732D, uPD2732A
//------------- 27C32 -------------
27C32 - Generic, AM2732B, NMC27C32B, WS57C43C
//------------- 2764 -------------
2764 - Generic, 2764A - Intel, M2764A, M5L2764K, NTE2764, TMM2764AD
//------------- 27C64 -------------
27C64 - Generic, 27C64 - Microchip, Cy7C266, MBM27C64, NMC27C64, TMS27C64
//------------- 27128 -------------
27128 - Generic, HN4827128G, HN27128, M27128A - Intel, M27128A - ST, M5L27128K, M5M27C128K, MBM27128, NTE21128, TMM27128AD, TMS27128, uPD27128
//------------- 27C128 -------------
27C128 - Generic, 27C128 - Microchip, AM27C128, AT27C128, CY27C128, LH57126, M27C128, MSM27C128, NM27C128 - Fairchild, NM27C128 - National, QP27C128, SMJ27C128, TMS27C128
//------------- 27256 -------------
27256 - Generic, A68C256, AT27256, 27256 - Intel, M5L27256K, MBM27256, MSM27256, TMM27256, uPD27256
//------------- 27C256 -------------
27C256 - Generic, 27C256 - Microchip, AM27C256, AM27H256, CXK27C256DQ, CY27C256, CY27H256, CY7C274, EM27C256, FM27C256, HN27C256A, HN27C256AG, IS27C256, M27C256B, M5M27C256K, MBM27C256, 27HC256, MSM27C256H, NM27C256 - Fairchild, NM27C256 - National, NM27LC256, NMC27C256, NMC87C257, NPX27C256, QP27C256, 27C256 - SEEQ, M27C256 - SEEQ, SMJ27C256 - ASI, SMJ27C256 - TI, SPM27C256, TC57256, TMS27C256, TMS87C257, uPD27C256
//------------- 27512 -------------
27512 - Generic, 27512 - Intel, AM27512, HN27512, M27512, M5L27512K, MSM27512, TMM27512AD
//------------- 27C512 -------------
27C512 - Generic, 27C512 - Microchip, 27C512 - Intel, 27C512 - Philips, AM27C512, CXK27C512DQ, CY27C512, CY27H512, EM27C512, FM27C512, HN27C512, IS27HC512, MBM27C512, MX27C512, NM27C512, NM27P512, SMJ27C512 - ASI, SMJ27C512 - TI, TC57512AD, TMS27C512, uPD27C512
//------------- 27C010 -------------
27C010 - Generic, AM27C010, AM27H010, AM27HB010, CY27C010, CY27H010, 27C010 - Intel, EM27C010, FM27C010, HN27C101, IS27C010, M5M27C101K, NM27C010 - Fairchild, NM27C010 - National, NMC27C010, SMJ27C010 - ASI, SMJ27C010 - TI, TMS27C010
//------------- 27C1001 -------------
27C1001 - Generic, CXK27C1001DQ, M27C1001, MBM27C1001, MSM27C1000, MX27C1000, TC57C1001, TC57H1001
//------------- 27C020 -------------
27C020 - Generic, AM27C020, CY27C020, 27C020 - Intel, EM27C020, IS27C020, NM27C020, TMS27C020
//------------- 27C2001 -------------
27C2001 - Generic, M27C2001, MSM27C2000, uPD27C2001
//------------- 27C040 -------------
27C040 - Generic, AM27C040, CY27C040, EM27C040, FM27C040, 27C040 - Intel, NM27C040, NXP27C040, SMJ27C040 - ASI, SMJ27C040 - Micross, SMJ27C040 - TI, TMS27C040
//------------- 27C4001 -------------
27C4001 - Generic, HN27C4001, M27C4001, MBM27C4001, MSM27C401, MX27C4000, TC57C4000, uPD27C4001
//------------- 27C080 -------------
27C080 - Generic, AM27C080, AT27LV080, M27C801, MX27C8000
```

## Programmer images
![Inside](../images/inside.jpg) ![Assembled Programmer](../images/case.jpg)
