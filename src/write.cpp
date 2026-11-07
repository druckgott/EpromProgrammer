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
#include "write.h"
#include "read.h"
//------------------------------------------------------------------------------
//write a byte to eprom
void WriteDataByte(uint8_t data)
{
#ifdef SHIELD
  for(uint8_t i = 0; i < 8; i++) {
    digitalWrite(dataPins[i], (data >> i) & 0x01);
  }
#else
  PORTA = data; // Schreibt das Byte gleichzeitig auf alle 8 Pins
#endif
}
//------------------------------------------------------------------------------

void StartWriteData(void)
{
  extern EPROM_TYPE EpromSelected;
  
  SetDataMode(true);

  switch(EpromSelected)
  {
    case EPROM_TYPE::X16:
    case EPROM_TYPE::C16:
      digitalWrite(NCE_PIN, LOW);
      digitalWrite(NOE_PIN, HIGH);
      break;
      
    default:
      digitalWrite(NCE_PIN, HIGH);
      digitalWrite(NOE_PIN, HIGH);
  }
}
//------------------------------------------------------------------------------

void EndWriteData(void)
{
  SetDataMode(false);

  digitalWrite(NCE_PIN, HIGH);
  digitalWrite(NOE_PIN, HIGH);
}
//------------------------------------------------------------------------------

bool WriteEprom(void)
{
  extern EPROM_TYPE EpromSelected;
  extern uint32_t EpromEndAddress;
  extern uint8_t *SerialBuffer;
  extern PRG_ALGO ProgrammingAlgorithm;

  for(uint32_t i = 0; i < EpromEndAddress; i += SERIAL_BUF_LEN)
  { 
    Serial.print(F(RESPONSE_FLAG));
    Serial.print(F(RESPONSE_BLOCK));
    Serial.println(i);
    Serial.flush();

    // Host schickt erst nach der Anforderung; großzügig warten statt 400/750 ms Wettlauf
    unsigned long waited = WaitForData(SERIAL_BUF_LEN, 10000);

    uint8_t count = Serial.readBytes(SerialBuffer, SERIAL_BUF_LEN);
    if(count != SERIAL_BUF_LEN)
    {
      Serial.print(F(RESPONSE_FLAG));
      Serial.print(F(RESPONSE_ERROR));
      Serial.print(count);
      Serial.print(F(" bytes received for block 0x"));
      Serial.print(i, HEX);
      Serial.print(F(" after "));
      Serial.print(waited);
      Serial.println(F(" ms"));
      Serial.flush();
      return false;
    }

    StartWriteData();

    bool writeResult = true;
    switch(EpromSelected)
    {
      case EPROM_TYPE::X16:
      case EPROM_TYPE::C16:
        writeResult = WriteBlockX16(i);
        break;
      
      default:
        switch(ProgrammingAlgorithm)
        {
          case PRG_ALGO::FAST:
            writeResult = WriteFastBlock(i);
            break;
            
          default:
            writeResult = WriteStandardBlock(i);
        }
    }
    
    if(!writeResult) {
      return false;
    }

    Serial.print(F(RESPONSE_FLAG));
    Serial.println(F(RESPONSE_OK));
    Serial.flush();
  }
  
  return true;
}
//------------------------------------------------------------------------------

void DisplayBlockError(uint32_t address, uint8_t expected, uint8_t actual)
{
  Serial.flush();
  Serial.print(F(RESPONSE_FLAG));
  Serial.print(F(RESPONSE_ERROR));
  Serial.print(F("Wrote 0x"));
  Serial.print(expected, HEX);
  Serial.print(F(", read 0x"));
  Serial.print(actual, HEX);
  Serial.print(F(", address 0x"));
  Serial.println(address, HEX);
  Serial.flush();
}
//------------------------------------------------------------------------------
// Vor dem Brennen lesen (Adresse muss gesetzt sein). true = kein Impuls nötig:
// Byte stimmt schon (*ok = true, z.B. Wiederholung nach Abbruch) oder es ist eine 0
// gesetzt, wo eine 1 hin muss (*ok = false, nur durch Löschen behebbar).
bool AlreadyWritten(uint32_t address, uint8_t expected, bool *ok)
{
  uint8_t current = VerifyData();
  *ok = (current == expected);
  if(*ok) {
    return true;
  }
  if((current & expected) != expected)
  {
    DisplayBlockError(address, expected, current);
    return true;
  }
  return false;
}
//------------------------------------------------------------------------------
// 2716 & 27C16 Eproms
bool WriteBlockX16(uint32_t i)
{
  extern uint8_t EpromVppPin;
  extern uint8_t *SerialBuffer;

  SetDataMode(true);
  
  for(uint8_t j = 0; j < SERIAL_BUF_LEN; j++)
  {
    if(SerialBuffer[j] == 0xFF) {
      continue;
    }
    
    uint8_t registerOne, registerTwo, registerThree;
        
    GenerateAddress(i + j, &registerOne, &registerTwo, &registerThree);
    SetAddress(registerOne, registerTwo, registerThree);
    
    SetVppOn(EpromVppPin);

    WriteDataByte(SerialBuffer[j]);
      
    digitalWrite(NCE_PIN, HIGH);
    delay(45); // should wait between 45 and 55 ms
    digitalWrite(NCE_PIN, LOW);
        
    SetVppOff();

    // Verify byte
    uint8_t verify = VerifyData();
    if(SerialBuffer[j] != verify) 
    {
      DisplayBlockError(i + j, SerialBuffer[j], verify);
      return false;
    }
  }

  return true;
}
//------------------------------------------------------------------------------
// All > 2716 & 27C16 Eproms
bool WriteStandardBlock(uint32_t i)
{
  extern uint8_t EpromVppPin;
  extern uint8_t *SerialBuffer;

  SetDataMode(true);
  bool writeOk;
  
  for(uint8_t j = 0; j < SERIAL_BUF_LEN; j++)
  {
    if(SerialBuffer[j] == 0xFF) {
      continue;
    }
    
    uint8_t registerOne, registerTwo, registerThree;
        
    GenerateAddress(i + j, &registerOne, &registerTwo, &registerThree);
    SetAddress(registerOne, registerTwo, registerThree);

    if(AlreadyWritten(i + j, SerialBuffer[j], &writeOk)) {
      if(!writeOk) return false;
      continue;
    }

    for(uint8_t k = 1; k <= 10; k++) 
    {
      SetVppOn(EpromVppPin);
  
      WriteDataByte(SerialBuffer[j]);
      
      digitalWrite(NCE_PIN, LOW);
      delay(50); // should wait between 45 and 55 ms
      digitalWrite(NCE_PIN, HIGH);
        
      SetVppOff();
    
      // Verify byte
      uint8_t verify = VerifyData();
      if(SerialBuffer[j] == verify) {
        break;
      }
      else if(k < 10) 
      {
        delay(1);
        continue;
      }

      DisplayBlockError(i + j, SerialBuffer[j], verify);
      return false;
    }
  }

  return true;
}
//------------------------------------------------------------------------------
// 110uS programming impulse
// similar with Flasrite algorithm
bool WriteFastBlock(uint32_t i)
{
  extern uint8_t EpromVppPin;
  extern uint8_t *SerialBuffer;

  SetDataMode(true);  
  bool writeOk;
  for(uint8_t j = 0; j < SERIAL_BUF_LEN; j++)
  {
    if(SerialBuffer[j] == 0xFF) {
      continue;
    }
    
    uint8_t registerOne, registerTwo, registerThree;

    GenerateAddress(i + j, &registerOne, &registerTwo, &registerThree);
    SetAddress(registerOne, registerTwo, registerThree);

    if(AlreadyWritten(i + j, SerialBuffer[j], &writeOk)) {
      if(!writeOk) return false;
      continue;
    }

    for(uint8_t k = 1; k <= 10; k++)
    {
      SetVccProgram(true);
      SetVppOn(EpromVppPin);

      WriteDataByte(SerialBuffer[j]);

      digitalWrite(NCE_PIN, LOW);
      delayMicroseconds(110);
      digitalWrite(NCE_PIN, HIGH);

      SetVppOff();
      // Verify bei 5V, sonst treibt das EPROM Q0-Q7 mit 6,25V in die Mega-Pins
      SetVccProgram(false);

      // Verify byte
      uint8_t verify = VerifyData();
      
      if(SerialBuffer[j] == verify) {
        break;
      }
      else if(k < 10) 
      {
        delayMicroseconds(250);
        continue;
      }

      DisplayBlockError(i + j, SerialBuffer[j], verify);
      return false;
    }
  }

  return true;
}
//------------------------------------------------------------------------------

uint8_t VerifyData(void)
{
  StartReadData();
  uint8_t verify = ReadDataByte();
  EndVerifyData();
  return verify;
}
//------------------------------------------------------------------------------

void EndVerifyData(void)
{
  extern EPROM_TYPE EpromSelected;

  SetDataMode(true);
  
  switch(EpromSelected)
  {
    case EPROM_TYPE::X16:
    case EPROM_TYPE::C16:
        digitalWrite(NOE_PIN, HIGH);
        break;

    default:
      digitalWrite(NCE_PIN, HIGH);
      digitalWrite(NOE_PIN, HIGH);
  }
}
//------------------------------------------------------------------------------
