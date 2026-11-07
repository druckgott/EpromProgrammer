/**
 * 
 * Eprom Programmer
 * 
 * Copyright (C) 2021-2023 Ciprian Stingu
 * ciprian stingu at gmail dot com
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111 USA
 * or see <http://www.gnu.org/licenses/>
 * 
 */
//------------------------------------------------------------------------------
#pragma once

#include <Arduino.h>
//------------------------------------------------------------------------------

#define OPTIMIZE_FOR_SPEED

// --- Direkte Pin-Belegung für Arduino Mega ---
// Zwei Varianten: Steckbrett (Standard, README Kap. 4) und Lochraster-Shield
// (Build-Umgebung "shield", -DSHIELD, README Kap. 5). Die Shield-Belegung folgt der
// Platine: jeder EPROM-Pin liegt in derselben Reihe wie sein Mega-Pin.

#ifdef SHIELD
// Data Q0..Q7 (verteilt auf PORTL/PORTB -> Einzel-Pin-Zugriff)
#define D0_PIN 46
#define D1_PIN 48
#define D2_PIN 50
#define D3_PIN 53
#define D4_PIN 51
#define D5_PIN 49
#define D6_PIN 47
#define D7_PIN 45
// Adressen A0..A18
#define ADDR_PINS {44, 42, 40, 38, 36, 34, 32, 30, 33, 35, 41, 37, 28, 31, 29, 26, 24, 27, 25}
// Eprom control
#define NCE_PIN     43
#define NOE_PIN     39
#define VPP_EN_PIN  22 // Steuert die 12,75-V-Schaltstufe
#define VCC_EN_PIN  23 // Schaltet VCC von 5V auf 6,25V (nur Brennimpuls)
// Pin 52 bleibt frei
#else
// Data (Q0-Q7 mapping auf Mega Pins 22-29 / PORTA)
#define D0_PIN 22
#define D1_PIN 23
#define D2_PIN 24
#define D3_PIN 25
#define D4_PIN 26
#define D5_PIN 27
#define D6_PIN 28
#define D7_PIN 29
// Adressen A0..A18
#define ADDR_PINS {30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48}

// Eprom control
#define NCE_PIN     50
#define NOE_PIN     51
#define VPP_EN_PIN  52 // Steuert deinen 12.5V Transistor
#define VCC_EN_PIN  53 // Schaltet VCC von 5V auf 6,25V (nur Brennimpuls)
#endif
#define DATA_PINS {D0_PIN, D1_PIN, D2_PIN, D3_PIN, D4_PIN, D5_PIN, D6_PIN, D7_PIN}
// ponytail: geschätzte Einschwingzeit der VCC-Umschaltung, am Oszi nachmessen und anpassen
#define VCC_SETTLE_US 500

// Dummy-Definitionen (damit die Menüführung nicht abstürzt)
#define A13_VCC_PIN 0
#define A17_VCC_PIN 0
#define NO_VCC_PIN  0
#define A11_VPP_PIN 0
#define NOE_VPP_PIN 0
#define A15_VPP_PIN 0
#define A19_VPP_PIN 0
#define NO_VPP_PIN  0

// Serial & Timing
#define SERIAL_BUF_LEN 32
#define TEST_STEP_WAIT 2500
#define MIN_VCC 4.50
#define MAX_VCC 6.50
#define MIN_VPP 10.00
#define MAX_VPP 30.00

// ... Lass den Rest (COMMANDS, ENUMS) der Datei unangetastet ...

// commands
#define COMMAND_FLAG           "@CMD"
#define COMMAND_SET_EPROM_TYPE "TYPE"
#define COMMAND_VOLTAGE_INFO   "VINF"
#define COMMAND_READ_EPROM     "READ"
#define COMMAND_WRITE_EPROM    "WRIT"
#define COMMAND_TEST           "TEST"
#define RESPONSE_FLAG          "@RSP"
#define RESPONSE_OK            "OK  "
#define RESPONSE_ERROR         "ERR "
#define RESPONSE_BLOCK         "BLCK"
#define RESPONSE_READ_EPROM    COMMAND_READ_EPROM
#define RESPONSE_VOLTAGE_INFO  COMMAND_VOLTAGE_INFO
#define RESPONSE_TEST          COMMAND_TEST
#define RESPONSE_WRITE_EPROM   COMMAND_WRITE_EPROM
#define COMMAND_TEST_SPEED     "SPED"

enum COMMAND_MODE {
  WAIT,
  READ,
  WRITE,
  VOLTAGE,
  TEST,
  TEST_SPEED
};

enum EPROM_TYPE {
  NONE = 0,
  X16  = 1,  // 2716
  C16  = 2,  // 27C16
  X32  = 3,  // 2732
  C32  = 4,  // 27C32
  X64  = 5,  // 2764
  C64  = 6,  // 27C64
  X128 = 7,  // 27128
  C128 = 8,  // 27C128
  X256 = 9,  // 27256
  C256 = 10, // 27C256
  X512 = 11, // 27512
  C512 = 12, // 27C512
  C010 = 13, // 27C010
  C1D1 = 14, // 27C1001
  C020 = 15, // 27C020
  C2D1 = 16, // 27C2001
  C040 = 17, // 27C040
  C4D1 = 18, // 27C4001
  C080 = 19, // 27C080
  LAST_EPROM_TYPE
};

enum PRG_ALGO {
  UNDEFINED        = 0,
  STANDARD         = 1,
  FAST             = 2,
  LAST_ALGO
};
//------------------------------------------------------------------------------
