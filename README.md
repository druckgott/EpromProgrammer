# EpromProgrammer
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
All the files which you need in order to create the PCBs are in the [hardware](hardware) folder.

## Case
The files for 3D printing a case are available in [FreeCAD](FreeCAD) folder

## Limitations in current implementation
* No Windows support, but it should be easy to implement

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
![Inside](images/inside.jpg) ![Assembled Programmer](images/case.jpg)

## GUI images
![Write](images/write.jpg) ![Verify](images/verify.jpg) ![EPROM options](images/eprom.jpg)


# Arduino Mega EPROM Programmer (Direct Wiring)

Dieses Projekt ermöglicht das Auslesen und Beschreiben von UV-EPROMs (speziell **ST M27C4001 / 27C040**) mit einem Arduino Mega 2560.
Durch die hohe Anzahl an Pins am Mega werden **keine Schieberegister** benötigt. Das EPROM wird direkt verkabelt.

## ⚠️ Wichtiger Warnhinweis
Das M27C4001 ist ein **5V-Baustein**, benötigt zum *Schreiben* (Brennen) jedoch zwingend **12,5V an Pin 1 (VPP)**. 
**Verbinde NIEMALS die 12,5V direkt mit einem Pin des Arduinos!** Dies zerstört den Mikrocontroller sofort. Nutze zwingend die unten beschriebene Transistor-Schaltung.

https://www.datasheet-pdf.info/entry/M27C4001

---

## 1. Spannungsversorgung (Power)

| EPROM Pin | Name | Anschluss am Arduino Mega / Schaltung |
| :--- | :--- | :--- |
| 16 | **GND** | `GND` (Masse) |
| 32 | **VCC** | `5V` Pin des Arduinos |
| 1 | **VPP** | *Geht an den Ausgang der Transistor-Schaltung (siehe unten)* |

![Pinout_M27C4001](images/M27C4001.png) 
---

## 2. Daten-Pins (PORTA für maximale Geschwindigkeit)

| EPROM Pin | Name | Arduino Mega Pin |
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

| EPROM Pin | Name | Arduino Mega Pin |
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

| EPROM Pin | Name | Arduino Mega Pin | Funktion |
| :--- | :--- | :--- | :--- |
| 22 | **CE** | Digital `50` | Chip Enable (Aktiv LOW) |
| 24 | **OE** | Digital `51` | Output Enable (Aktiv LOW) |
| - | **VPP_EN**| Digital `52` | **Steuert deine VPP Transistor-Schaltung** |

![Pinout_M27C4001](images/M27C4001.png) 

---

## 5. Die 12,5V VPP Transistor-Schaltung (High-Side Switch)

Um die 12,5V blitzschnell und sicher ein- und auszuschalten, musst du eine kleine Schaltung auf dem Breadboard aufbauen. Der Arduino-Pin 52 steuert diese Schaltung.

### Benötigte Bauteile:
* 1x externes DC-Netzteil (exakt **12,0V bis 12,5V**)
* 1x NPN-Transistor (z. B. 2N3904, BC547)
* 1x PNP-Transistor (z. B. 2N3906, BC557)
* 2x 1kΩ Widerstand
* 1x 10kΩ Widerstand
* 1x Standard-Diode (z. B. 1N4148 oder 1N4007)

### Aufbau der Schaltung:

1. **Gemeinsame Masse:** Verbinde den Minus-Pol (GND) deines 12,5V-Netzteils zwingend mit dem GND des Arduinos.
2. **Der Steuereingang:** Verbinde Arduino **Pin 52** über einen **1kΩ Widerstand** mit der Basis (B) des **NPN**-Transistors.
3. **NPN Masse:** Verbinde den Emitter (E) des **NPN**-Transistors mit **GND**.
4. **Verbindung der Transistoren:** Verbinde den Kollektor (C) des **NPN**-Transistors über den zweiten **1kΩ Widerstand** mit der Basis (B) des **PNP**-Transistors.
5. **Der 12,5V Eingang:** Verbinde den Emitter (E) des **PNP**-Transistors mit dem Plus-Pol (**12,5V**) deines Netzteils.
6. **Pull-Up für Sicherheit:** Setze den **10kΩ Widerstand** zwischen den Emitter (12,5V) und die Basis (B) des **PNP**-Transistors (das hält ihn standardmäßig sicher abgeschaltet).
7. **Der VPP Ausgang:** Der Kollektor (C) des **PNP**-Transistors geht direkt an **Pin 1 (VPP)** des EPROMs.

### Der Dioden-Trick (Für das Auslesen):
Das EPROM verlangt, dass am VPP-Pin während des reinen Auslesens 5V anliegen. 
* Setze die **Diode** so ein, dass der Strom vom **5V-Pin des Arduinos** zum **Pin 1 (VPP) des EPROMs** fließen kann (der silberne Strich der Diode zeigt zum EPROM). 
* **Warum?** So bekommt der VPP-Pin standardmäßig fast 5V zum Lesen. Wenn der Arduino Pin 52 auf HIGH setzt und die vollen 12,5V aus deiner Schaltung auf den EPROM-Pin schießen, blockiert die Diode diese Spannung rückwärts und schützt deinen Arduino vor dem Durchschmoren.
