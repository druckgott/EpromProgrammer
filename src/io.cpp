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
#include "defines.h"
#include "io.h"
//------------------------------------------------------------------------------
// set read/write eprom mode
void SetDataMode(bool write)
{
  if(write) {
    DDRA = 0xFF; // Setzt Mega Pins 22-29 als OUTPUT (extrem schnell)
  } else {
    DDRA = 0x00; // Setzt Mega Pins 22-29 als INPUT
    PORTA = 0xFF; // Aktiviert die internen Pull-Up Widerstände
  }
}
//------------------------------------------------------------------------------

void GenerateAddress(uint32_t address, uint8_t *registerOne, uint8_t *registerTwo, uint8_t *registerThree)
{
  extern EPROM_TYPE EpromSelected;
  extern uint32_t EpromEndAddress;
  extern COMMAND_MODE CommandMode;
  
  *registerOne = 0;
  *registerTwo = 0;
  *registerThree = 0;
  
  switch(EpromSelected)
  {
    case EPROM_TYPE::X16:
    case EPROM_TYPE::C16:
      address &= EpromEndAddress;
      *registerOne = address & 0xFF;
      *registerTwo = (address & 0xFF00) >> 8;
      // A11 is VPP which in case of read need to be at VCC
      if(CommandMode == READ) {
        *registerTwo |= 0x08;
      }
      break;
      
    case EPROM_TYPE::X64:
    case EPROM_TYPE::C64:
    case EPROM_TYPE::X128:
    case EPROM_TYPE::C128:
      address &= EpromEndAddress;
      *registerOne = address & 0xFF;
      *registerTwo = (address & 0xFF00) >> 8;
      // A14 is nPGM whci in case of read need to be at VCC
      // A15 is VPP which in case of read need to be at VCC
      if(CommandMode == READ) {
        *registerTwo |= 0xC0;
      }
      break;

    case EPROM_TYPE::X256:
    case EPROM_TYPE::C256:
      address &= EpromEndAddress;
      *registerOne = address & 0xFF;
      *registerTwo = (address & 0xFF00) >> 8;
      // A15 is VPP which in case of read need to be at VCC
      if(CommandMode == READ) {
        *registerTwo |= 0x80;
      }
      break;
      
    default:
      address &= EpromEndAddress;
      *registerOne = address & 0xFF;
      *registerTwo = (address & 0xFF00) >> 8;
      *registerThree = (address & 0xFF0000) >> 16;
      break;
  }
}

const int addrPins[] = {30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48};
//------------------------------------------------------------------------------
// set the address using 3 register values
// registerOne   = addresses A0  -> A7
// registerTwo   = addresses A8  -> A15
// registerThree = addresses A16 -> A19 (the most significative 4 bits are 0)
void SetAddress(uint8_t registerOne, uint8_t registerTwo, uint8_t registerThree)
{
  // Baut die 3 Register wieder zu einer 32-Bit Adresse zusammen
  uint32_t fullAddr = registerOne | (registerTwo << 8) | ((uint32_t)registerThree << 16);
  
  // Schaltet die Pins 30 bis 48 direkt
  for(int i = 0; i < 19; i++) {
    digitalWrite(addrPins[i], (fullAddr >> i) & 0x01);
  }
}
//------------------------------------------------------------------------------
//disable vpp
void SetVppOff(void)
{
  digitalWrite(VPP_EN_PIN, LOW); // Schaltet deine 12.5V ab
}

//------------------------------------------------------------------------------
//enable one pin for vpp
void SetVppOn(uint8_t vppPin)
{
  digitalWrite(VPP_EN_PIN, HIGH); // Schaltet deine 12.5V ein
}
//------------------------------------------------------------------------------
//reset the circuit to a known state
void InitializeEpromToAKnownState(void)
{
  // disable nCE
  digitalWrite(NCE_PIN, HIGH);
  // disable nOE
  digitalWrite(NOE_PIN, HIGH);
  // disable A13 VCC
  //digitalWrite(A13_VCC_PIN, LOW);
  // disable A17 VCC
  //digitalWrite(A17_VCC_PIN, LOW);

  // disable VPP
  SetVppOff();

  // Data
  SetDataMode(false);

  // no address
  SetAddress(0, 0, 0);
}
//------------------------------------------------------------------------------

void SelectEprom(EPROM_TYPE newEprom)
{
  extern EPROM_TYPE EpromSelected;
  extern uint8_t EpromVppPin;
  extern uint32_t EpromEndAddress;
  
  InitializeEpromToAKnownState();
  EpromSelected = newEprom;
  uint8_t epromVccPin = NO_VCC_PIN;
  
  switch(newEprom)
  {
    case EPROM_TYPE::X16:
    case EPROM_TYPE::C16:
      epromVccPin = A13_VCC_PIN;
      EpromVppPin = A11_VPP_PIN;
      EpromEndAddress = 0x07FF;
      break;
      
    case EPROM_TYPE::X32:
    case EPROM_TYPE::C32:
      epromVccPin = A13_VCC_PIN;
      EpromVppPin = NOE_VPP_PIN;
      EpromEndAddress = 0x0FFF;
      break;
      
    case EPROM_TYPE::X64:
    case EPROM_TYPE::C64:
      epromVccPin = A17_VCC_PIN;
      EpromVppPin = A15_VPP_PIN;
      EpromEndAddress = 0x1FFF;
      break;
      
    case EPROM_TYPE::X128:
    case EPROM_TYPE::C128:
      epromVccPin = A17_VCC_PIN;
      EpromVppPin = A15_VPP_PIN;
      EpromEndAddress = 0x3FFF;
      break;
      
    case EPROM_TYPE::X256:
    case EPROM_TYPE::C256:
      epromVccPin = A17_VCC_PIN;
      EpromVppPin = A15_VPP_PIN;
      EpromEndAddress = 0x7FFF;
      break;
      
    case EPROM_TYPE::X512:
    case EPROM_TYPE::C512:
      epromVccPin = A17_VCC_PIN;
      EpromVppPin = NOE_VPP_PIN;
      EpromEndAddress = 0xFFFF;
      break;

    case EPROM_TYPE::C010:
    case EPROM_TYPE::C1D1:
      epromVccPin = NO_VCC_PIN;
      EpromVppPin = A19_VPP_PIN;
      EpromEndAddress = 0x1FFFF;
      break;

    case EPROM_TYPE::C020:
    case EPROM_TYPE::C2D1:
      epromVccPin = NO_VCC_PIN;
      EpromVppPin = A19_VPP_PIN;
      EpromEndAddress = 0x3FFFF;
      break;
      
    case EPROM_TYPE::C040:
    case EPROM_TYPE::C4D1:
      epromVccPin = NO_VCC_PIN;
      EpromVppPin = A19_VPP_PIN;
      EpromEndAddress = 0x7FFFF;
      break;

    case EPROM_TYPE::C080:
      epromVccPin = NO_VCC_PIN;
      EpromVppPin = NOE_VPP_PIN;
      EpromEndAddress = 0xFFFFF;
      break;

    default:
      epromVccPin = NO_VCC_PIN;
      EpromVppPin = NO_VPP_PIN;
      EpromSelected = NONE;
      EpromEndAddress = 0;
  }

  //if(EpromSelected != EPROM_TYPE::NONE && epromVccPin != NO_VCC_PIN) {
  //  digitalWrite(epromVccPin, HIGH);
  //}
}
//------------------------------------------------------------------------------
//get the average vpp voltage
double GetVppVoltage(void)
{
  extern double VppRequired;
  return VppRequired; // Täuscht vor, dass exakt die geforderten 12.5V anliegen
}
//------------------------------------------------------------------------------
//get the average vcc voltage
double GetVccVoltage(void)
{
  extern double VccRequired;
  return VccRequired; // Täuscht vor, dass exakt 5V anliegen
}
//------------------------------------------------------------------------------

void WaitForData(void)
{
  unsigned long start = millis();
  while(Serial.available() < 0)
  {
    if(millis() - start > 1000) {
      break;
    }
    delay(1);
  }
}
//------------------------------------------------------------------------------
