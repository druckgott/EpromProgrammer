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
#include "read.h"
#include "io.h"
//------------------------------------------------------------------------------

//read a byte from eprom
uint8_t ReadDataByte(void)
{
  return PINA; // Liest alle 8 Pins (22-29) gleichzeitig ein
}
//------------------------------------------------------------------------------

void StartReadData(void)
{
  SetDataMode(false);
  
  digitalWrite(NCE_PIN, LOW);
  digitalWrite(NOE_PIN, LOW);
}
//------------------------------------------------------------------------------

void EndReadData(void)
{
  digitalWrite(NCE_PIN, HIGH);
  digitalWrite(NOE_PIN, HIGH);
}
//------------------------------------------------------------------------------

/*void ReadEprom(void)
{
  extern uint32_t EpromEndAddress;
  extern uint8_t *SerialBuffer;
  
  StartReadData();

  delay(10);
  
  for(uint32_t i = 0; i < EpromEndAddress; i += SERIAL_BUF_LEN)
  {
    for(uint8_t j = 0; j < SERIAL_BUF_LEN; j++) 
    {
      uint8_t registerOne, registerTwo, registerThree;
      
      GenerateAddress(i + j, &registerOne, &registerTwo, &registerThree);
      SetAddress(registerOne, registerTwo, registerThree);
      
      SerialBuffer[j] = ReadDataByte();
    }

    Serial.write(SerialBuffer, SERIAL_BUF_LEN);
    Serial.flush();
  }
  
  EndReadData();
}*/
void ReadEprom(void)
{
  extern uint32_t EpromEndAddress;
  
  StartReadData();
  delay(10);
  
  for(uint32_t i = 0; i < EpromEndAddress; i++)
  {
    uint8_t registerOne, registerTwo, registerThree;
    
    GenerateAddress(i, &registerOne, &registerTwo, &registerThree);
    SetAddress(registerOne, registerTwo, registerThree);
    
    uint8_t data = ReadDataByte();
    
    // Gibt die Daten als sauberen Text aus (z.B. "0A" oder "FF")
    if(data < 0x10) Serial.print("0");
    Serial.print(data, HEX);
    
    // Nach 32 Bytes einen Zeilenumbruch machen, sonst Leerzeichen
    if((i + 1) % 32 == 0) {
      Serial.println();
    } else {
      Serial.print(" ");
    }
  }
  
  EndReadData();
}

/*void ReadEprom(void)
{
  extern uint32_t EpromEndAddress;
  
  StartReadData();
  delay(10);
  
  for(uint32_t i = 0; i < EpromEndAddress; i++)
  {
    uint8_t registerOne, registerTwo, registerThree;
    
    GenerateAddress(i, &registerOne, &registerTwo, &registerThree);
    SetAddress(registerOne, registerTwo, registerThree);
    
    uint8_t data = ReadDataByte();
    
    // Sende IMMER exakt 2 Zeichen als Hex-Text (z.B. "0A" oder "FF") ohne Leerzeichen
    if(data < 0x10) Serial.print("0");
    Serial.print(data, HEX);
  }
  
  EndReadData();
}*/
//------------------------------------------------------------------------------
