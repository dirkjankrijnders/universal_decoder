#include <OneWire.h>

#include <LinkedList.h>

#include "config.h"
#define VERSION 10609

uint16_t features = 0;

#if PINSERVO == 1
#warning "USING SERVO"
  #include <Servo.h>
  features = features | 1;
#endif

/* We're a loconet decoder! */
#include <utility/ln_config.h>
#include <LocoNet.h>

/* Include the CV handling and the pin functionalities */
#include "decoder_conf.h"
#include "configuredpins.h"
#include "cvaccess.h"
#include "bus_configuredpins.h"

decoder_conf_t EEMEM _CV = {
#include "default_conf.h"
};

#define MAX 25
ConfiguredPin* confpins[MAX];
uint8_t pins_conf = 0;

/* TLC5947 Support*/
#if TLC_SUPPORT
#include "Adafruit_TLC5947.h"
#warning "TLC SUpport"
// How many boards do you have chained?
#define NUM_TLC5974 1

#ifdef TLC_PROTO
#define data   2
#define clock   3
#define latch   4
#define oe  -1  // set to -1 to not use the enable pin (its optional)
#else
#warning pro micro
#define data   16
#define clock   15
#define latch   10
#define oe  -1  // set to -1 to not use the enable pin (its optional)
#endif
Adafruit_TLC5947 tlc = Adafruit_TLC5947(NUM_TLC5974, clock, data, latch);
#endif // TLC_SUPPORT

/* PCA9685 Support */

#include <Adafruit_PWMServoDriver.h>

#ifdef SOFTWARE_I2C
#endif 

// Default address = 0x40
Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver();
//features = features | 4;

void enableServos();
void disableServos();

bool pins_busy = false;

LinkedList<uint8_t> pins_to_update;
/* 
The LocoNet CV related stuff
*/
#define ARTNR 10001

lnMsg *LnPacket;

LocoNetCVClass lnCV;

boolean programmingMode;

OneWire ds(A3);
byte addr[8];
byte dsdata[9];

#define START_FLASH 3

#ifndef LOCONET_TX_PIN
  #define LOCONET_TX_PIN 7
#endif

#define POWER_VOLTAGE_PIN A2

#define STARTUP_CODE_CV 2

#define STARTUP_CODE_OK 240
#define STARTUP_CODE_CV_CHANGED 239
#define STARTUP_CODE_BOOT_FAILED 238

extern int __bss_start, __bss_end;

void dumpPacket(UhlenbrockMsg&);

int freeRam () {
  extern int __heap_start, *__brkval;
  int v;
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
};

void flash_led(int number) {
  #if defined(__AVR_ATmega328PB__) 
    for (uint8_t ii = 0; ii < number; ii++){
      PORTE |= (1 << PE0); // Turn LED on
      delay(125);
      PORTE &= ~(1 << PE0); // Turn LED off
      delay(125);
    }
  #endif
}

uint16_t readTemperature() {
  ds.reset();
  ds.select(addr);
  ds.write(0x44,1);         // start conversion, with parasite power on at the end

  delay(1000);     // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.

  ds.reset();
  ds.select(addr);    
  ds.write(0xBE);         // Read Scratchpad

  for (uint8_t i = 0; i < 9; i++) {           // we need 9 bytes
    dsdata[i] = ds.read();
  }
  int16_t raw = (dsdata[1] << 8) | dsdata[0];
  byte cfg = (dsdata[4] & 0x60);
  // at lower res, the low bits are undefined, so let's zero them
  if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
  else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
  else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
  //// default is 12 bit resolution, 750 ms conversion time
  return raw; // To be devided by 16;
}

uint16_t readPowerVoltage() {
  uint16_t adcValue = analogRead(POWER_VOLTAGE_PIN);
  return adcValue * 4.887585533 * 13;
}

void reportSlot(uint16_t slot, uint16_t state) {
  DEBUG(F("Reporting slot "));
  DEBUG(slot);
  DEBUG(F(" Address: "));
  DEBUG(confpins[slot]->_address);
  DEBUG(F(" State: "));
  DEBUGLN(state);
  if (slot == 0)
    return;
	LocoNet.reportSensor(confpins[slot]->_address, state);
}

void setSlot(uint16_t slot, uint16_t port, uint16_t state = 0) {
  if (slot == 0)
    return;
  if (slot < pins_conf)
    confpins[slot]->set(port, state);
}

void setSlot(uint16_t slot, uint16_t state) {
  setSlot(slot, state, 0);
}
void reportSensor(uint16_t address, bool state) {
  LocoNet.reportSensor(address, state);
}

uint16_t check_pin(uint16_t pin) {
  if ((pin == 0) | (pin == 1) | (pin == 5) | (pin == 8)) return 255; // Pin 8 on 328, 4 on m32u4
  return pin;
}

void configureSlot(uint8_t slot) {
  uint8_t pin_config;
  uint16_t pin, address, pos1, pos2, speed, fbslot1, fbslot2, powerpin, secondary_address;
  bool cumulative, force_on, report_inverse, keep_update;
  
    pin_config = eeprom_read_byte((uint8_t*)&(_CV.pin_conf[slot]));
    pin   = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.arduinopin));
    pin = check_pin(pin);
    address = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.address));
    switch (pin_config) {
      case 2: //Servo
        //ServoSwitch(i,0);
        pos1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos1));
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos2));
        speed = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.speed));
        fbslot1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.fbslot1));
        fbslot2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.fbslot2));
        powerpin = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pwrslot));
        confpins[slot] = new ServoSwitch(slot, pin, address, pos1, pos2, speed, powerpin, fbslot1, fbslot2);
        confpins[slot]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.state)));
        break;
      case 1: // Input
        report_inverse = ((eeprom_read_word((uint16_t*)&(_CV.conf[slot].input.options)) & 0x01) == 0x01);
        keep_update = ((eeprom_read_word((uint16_t*)&(_CV.conf[slot].input.options)) & 0x02) == 0x02);
        secondary_address  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].input.secadd));
        confpins[slot] = new InputPin(slot, pin, address, report_inverse, secondary_address, keep_update);
        break;
      case 3: // Output
        cumulative = ((eeprom_read_word((uint16_t*)&(_CV.conf[slot].output.options)) & 0x01) == 0x01);
        force_on = ((eeprom_read_word((uint16_t*)&(_CV.conf[slot].output.options)) & 0x02) == 0x02);
        confpins[slot] = new OutputPin(slot, pin, address, cumulative, force_on);
        break;
      case 4: // Dual action
        pos1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos1));
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos2));
        speed = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.speed));
        pin_config = eeprom_read_word((uint16_t*)&(_CV.conf[slot].output.options));

        confpins[slot] = new DualAction(slot, pin, address, pos1, pos2, speed, pin_config);
        confpins[slot]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.state)));
        break;
      case 5: // Switch magnet
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].magnet.arduinopin2));
        speed  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].magnet.duration));
        fbslot1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].magnet.fbslot1));
        fbslot2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].magnet.fbslot2));
        pos2 = check_pin(pos2);
        confpins[slot] = new MagnetSwitch(slot, pin, address, pos2, speed, fbslot1, fbslot2);
        confpins[slot]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[slot].magnet.state)));
          break;
      case 6: // Multiport
        pos1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].multiport.baseslot));
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].multiport.nslots));
        confpins[slot] = new MultiPort(slot, pin, address, pos1, pos2);
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].multiport.baseslot));
        confpins[slot]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[slot].multiport.state)));
        break;
#if TLC_SUPPORT
      case 101: // TLC5947 PWM LED Controller.
        DEBUGLN(F("TLC Pin"))
        pos1 = 512; //eeprom_read_word((uint16_t*)&(_CV.conf[slot].led.value1));
        pin_config = 0;
        confpins[slot] = new TLC5947pin(&tlc, slot, pin, address, pin, pos1);
        confpins[slot]->print();
        break;
#endif // TLC_SUPPORT
      case 102: // PCA9686
        pos1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos1));
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos2));
        speed = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.speed));
        fbslot1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.fbslot1));
        fbslot2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.fbslot2));
        powerpin = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pwrslot));
        confpins[slot] = new PCA9685Servo(&pca, slot, pin, address, pos1, pos2, speed, powerpin, fbslot1, fbslot2);
        confpins[slot]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.state)));
        break;
      default:
        confpins[slot] = new ConfiguredPin(slot, pin, address);
        break;
    }
    DEBUG(F("Pin #"));
    DEBUGLN(slot);
    DEBUG(F("Pin type:"))
    DEBUGLN(pin_config);
    confpins[slot]->print();
    pins_to_update.add(slot);
 }

void setup() {
#ifdef USE_SERIAL
  //Serial.begin(57600);
  Serial.begin(9600);
  while (!Serial){
    ;
  }
#warning Debug!
#endif

  DEBUG(F("Universal decoder v"));  
  DEBUGLN(VERSION);
  DEBUG(F("Module address: "));
  DEBUGLN(eeprom_read_byte(&_CV.address));

  #if defined(__AVR_ATmega328PB__) 
  DDRE |= (1 << PE0);
  #endif
  flash_led(START_FLASH);

  LocoNet.init(LOCONET_TX_PIN);
  
  pins_conf = eeprom_read_byte((uint8_t*)&(_CV.pins_conf));
  if (pins_conf > MAX - 1) pins_conf = MAX - 1;
  uint8_t i = 0;
  DEBUG(F("Max # of pins: "));
  DEBUG(pins_conf);
  DEBUG(F(" / "));
  DEBUGLN(MAX);
  #if TLC_SUPPORT
    tlc.begin();
    features = features | 4;
  #endif //TLC_SUPPORT
  #ifdef DEBUG_OUTPUT
    features = features | (1 << 3);
  #endif

  DEBUGLN(freeRam());
  //pins_conf = 0;
  if (read_cv(&_CV, STARTUP_CODE_CV) == STARTUP_CODE_BOOT_FAILED) {
    pins_conf = 0;
    return;
  }

  if (read_cv(&_CV, STARTUP_CODE_CV) == STARTUP_CODE_CV_CHANGED) {
    write_cv(&_CV, STARTUP_CODE_CV, STARTUP_CODE_BOOT_FAILED);
  }
  for (i = 0; i < pins_conf; i++) {
    configureSlot(i);
    DEBUG(freeRam())
    DEBUGLN(F(" bytes RAM free"))
  }
  #ifdef __AVR_ATmega328PB__
    confpins[pins_conf] = new OutputPin(pins_conf, 26, 0, false, false);
    pins_conf += 1;
  #endif
  features = features | 2;
#if PINSERVO
  features = features | 1;
#endif
  ds.reset_search();
  DEBUG(".");
  
  delay(250);
  if (!ds.search(addr)) {
    DEBUG(".");
    ds.reset_search();
    for (uint8_t j = 0; j < 7 ; j++) {
      addr[j] = 0x00;
    }
    DEBUGLN(F("No ds18s20 found for UID"));
  } 

#ifdef DEBUG_OUTPUT
    else {
    DEBUG(F("UID: "));
    for (uint8_t j = 0; j < 7; j++) {
      DEBUG(j);
      DEBUG2(addr[j], HEX);
    }
    DEBUGLN(F("."));
  }    
#endif

  #ifdef __AVR_ATmega328PB__
  DEBUG("328pb uid: ");
  for (uint8_t j = 0; j < 7; j++) {
    addr[j] = (byte)*((byte*)(0x0E + j));
    DEBUG2(addr[j], HEX);
  }
  DEBUGLN(".");
  #endif
  pca.begin();
  pca.setPWMFreq(70);

#ifdef POWER_VOLTAGE_PIN
  pinMode(POWER_VOLTAGE_PIN, INPUT);
  DEBUG(F("Power voltage in mV: "));
  DEBUGLN(readPowerVoltage());
#endif
  if (read_cv(&_CV, STARTUP_CODE_CV) == STARTUP_CODE_BOOT_FAILED) {
    write_cv(&_CV, STARTUP_CODE_CV, STARTUP_CODE_OK);
  }
  DEBUGLN("setup done");
}
uint8_t current_pin_list;

void loop() {
  
  if (!(pins_to_update.size() == 0)) {
	  current_pin_list += 1;
    if (current_pin_list >= pins_to_update.size())
      current_pin_list = 0;
    // DEBUG(F("Updating pin "));
    // DEBUGLN(pins_to_update.get(current_pin_list));
    if (!confpins[pins_to_update.get(current_pin_list)]->update()) { // Update the first item, as long as update() returns true, otherwise...
      //pins_to_update.push(pins_to_update.first());
      DEBUG(F("Done updating "));
      DEBUGLN(pins_to_update.get(current_pin_list));
      pins_to_update.remove(current_pin_list); // ..drop the first item
      DEBUG(pins_to_update.size());
      DEBUGLN(F(" active pins left in the queue"));
    }
    // DEBUGLN(freeRam())
  }

  /*Serial.print(DDRB, HEX);
  Serial.print(", 0x");
  Serial.println(PINB, HEX);*/
  if (Serial.available() > 0) {
    if (Serial.read() == 'w') {
      uint16_t cv = Serial.parseInt();
      uint16_t val = Serial.parseInt();
      Serial.print(F("Write CV "));
      Serial.print(cv);
      Serial.print(F(": "));
      Serial.println(val);
      write_cv(&_CV, cv, val);
    }
  }

  /*** LOCONET ***/
  //DEBUG(".")
  LnPacket = LocoNet.receive();
  if (LnPacket) {
    // DEBUG(".")
    uint8_t packetConsumed(LocoNet.processSwitchSensorMessage(LnPacket));
    if (packetConsumed == 0) {
      DEBUG(F("Loop "));
      DEBUG((int)LnPacket);
      dumpPacket(LnPacket->ub);
      lnCV.processLNCVMessage(LnPacket);
      DEBUG(F("End Loop\n"));
    }
      DEBUG(pins_to_update.size());
      DEBUGLN(F(" active pins left in the queue"));
    DEBUGLN(freeRam())
  }

  #if defined(__AVR_ATmega328PB__)
  if (programmingMode) {
    PORTE ^= (1 << PE0);
  }
  #endif
};

void notifySwitchRequest( uint16_t Address, uint8_t Output, uint8_t Direction ) {
  DEBUG(F("Switch Request: "));
  DEBUG(Address);
  DEBUG(':');
  DEBUG(Direction ? "Closed" : "Thrown");
  DEBUG(" - ");
  DEBUGLN(Output ? "On" : "Off");
  for (uint8_t i =0 ; i < pins_conf ; i++) {
    if (confpins[i]->check_address(Address)){
    // if (confpins[i]->_address == Address){
      // Set new state
      confpins[i]->set(Direction, Output);
      // Add to the update queue
      pins_to_update.add(i);
      // Call update once to get started
      confpins[i]->update();
      // Save the state
      eeprom_write_word((uint16_t*)&(_CV.conf[i].servo.state), confpins[i]->get_state());
      DEBUG(F("Thrown switch: "));
      DEBUG(i);
      DEBUG(F(" to :"));
      confpins[i]->print_state();
      DEBUG("\n");
    }
  }

}

void dumpPacket(UhlenbrockMsg & ub) {
#ifdef DEBUG_OUTPUT
  Serial.print(F(" PKT: "));
  Serial.print(ub.command);
  Serial.print(" ");
  Serial.print(ub.mesg_size, HEX);
  Serial.print(" ");
  Serial.print(ub.SRC, HEX);
  Serial.print(" ");
  Serial.print(ub.DSTL, HEX);
  Serial.print(" ");
  Serial.print(ub.DSTH, HEX);
  Serial.print(" ");
  Serial.print(ub.ReqId, HEX);
  Serial.print(" ");
  Serial.print(ub.PXCT1, HEX);
  Serial.print(" ");
  for (int i(0); i < 8; ++i) {
    Serial.print(ub.payload.D[i], HEX);
    Serial.print(" ");
  }
  Serial.write("\n");
#endif
}

/**
   * Notifies the code on the reception of a read request.
   * Note that without application knowledge (i.e., art.-nr., module address
   * and "Programming Mode" state), it is not possible to distinguish
   * a read request from a programming start request message.
   */
int8_t notifyLNCVread(uint16_t ArtNr, uint16_t lncvAddress, uint16_t,
    uint16_t & lncvValue) {

  DEBUG(F("Enter notifyLNCVread("));
  DEBUG(ArtNr);
  DEBUG(", ");
  DEBUG(lncvAddress);
  DEBUG(", ");
  DEBUG(", ");
  DEBUG(lncvValue);
  DEBUG(")\n");
  
  // Step 1: Can this be addressed to me?
  // All ReadRequests contain the ARTNR. For starting programming, we do not accept the broadcast address.
  if (programmingMode) {
    if (ArtNr == ARTNR) {
		if (lncvAddress == 5){
			lncvValue = MAX;
			return LNCV_LACK_OK;
		} else if (lncvAddress < 320) {
        lncvValue = read_cv(&_CV, lncvAddress);

        DEBUG(F("\nEeprom address: "));
        DEBUG(((uint16_t)&(_CV.address)+cv2address(lncvAddress)));
        DEBUG(F(" LNCV Value: "));
        DEBUGLN(lncvValue);

        return LNCV_LACK_OK;
		  } else if (lncvAddress == 1018) {
        lncvValue = readTemperature();
        return LNCV_LACK_OK;
		  } else if (lncvAddress == 1019) {
        lncvValue = addr[0];
        lncvValue = lncvValue << 8;
        lncvValue |= addr[1]; 
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1020) {
        lncvValue = addr[2];
        lncvValue = lncvValue << 8;
        lncvValue |= addr[3]; 
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1021) {
        lncvValue = addr[4];
        lncvValue = lncvValue << 8;
        lncvValue |= addr[5]; 
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1022) {
        lncvValue = addr[6];
        lncvValue = lncvValue << 8;
        lncvValue |= addr[7]; 
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1023) {
        lncvValue = VERSION;
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1024) {
        lncvValue = freeRam();
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1025) {
        lncvValue = __bss_start;
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1026) {
        lncvValue = __bss_end;
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1027) {
        lncvValue = SP;
        return LNCV_LACK_OK;
      } else if ((lncvAddress > 1027) && (lncvAddress < 1033)){
        LnBufStats* stats = LocoNet.getStats();
        switch (lncvAddress) {
          case 1028:
          lncvValue = stats->RxPackets;
          break;
          case 1029:
          lncvValue = stats->RxErrors;
          break;
          case 1030:
          lncvValue = stats->TxPackets;
          break;
          case 1031:
          lncvValue = stats->TxErrors;
          break;
          case 1032:
          lncvValue = stats->Collisions;
        }
        return LNCV_LACK_OK;
      } else if (lncvAddress == 1034) {
          lncvValue = readPowerVoltage();
          return LNCV_LACK_OK;
      } else if (lncvAddress == 1035) {
          lncvValue = features;
          return LNCV_LACK_OK;
      } else {
        // Invalid LNCV address, request a NAXK
        return LNCV_LACK_ERROR_UNSUPPORTED;
      }
    } else {

      DEBUG(F("ArtNr invalid.\n"));

      return -1;
    }
  } else {

    DEBUG(F("Ignoring Request.\n"));

    return -1;
  }
}

int8_t notifyLNCVprogrammingStart(uint16_t & ArtNr, uint16_t & ModuleAddress) {
  // Enter programming mode. If we already are in programming mode,
  // we simply send a response and nothing else happens.
  uint16_t MyModuleAddress = eeprom_read_byte(&_CV.address);

  DEBUG(ArtNr);
  DEBUG(ModuleAddress);
  DEBUG(MyModuleAddress);


  if (ArtNr == ARTNR) {
    if (ModuleAddress == MyModuleAddress) {
      programmingMode = true;

      DEBUG(F("Programming started"));

      return LNCV_LACK_OK;
    } else if (ModuleAddress == 0xFFFF) {
      ModuleAddress = eeprom_read_byte(&_CV.address);
      return LNCV_LACK_OK;
    }
  }
  // Apparently another module is being programmed, so stop our programming.
  programmingMode = false;
  return -1;
}

  /**
   * Notifies the code on the reception of a write request
   */
int8_t notifyLNCVwrite(uint16_t ArtNr, uint16_t lncvAddress,
    uint16_t lncvValue) {
  //  dumpPacket(ub);
  if (!programmingMode) {
    return -1;
  }

  DEBUG(F("Enter notifyLNCVwrite("));
  DEBUG(ArtNr);
  DEBUG(", ");
  DEBUG(lncvAddress);
  DEBUG(", ");
  DEBUG(", ");
  DEBUG(lncvValue);
  DEBUG(")\n");

  if (ArtNr == ARTNR) {

    if (lncvAddress < 320) {
      DEBUG(cv2address(lncvAddress));
      DEBUG(bytesizeCV(lncvAddress));
      DEBUG((uint8_t)lncvValue);
      write_cv(&_CV, lncvAddress, lncvValue);
      write_cv(&_CV, STARTUP_CODE_CV, STARTUP_CODE_CV_CHANGED);
      DEBUG(read_cv(&_CV, lncvAddress));
      if (lncvAddress > 31) {
        uint8_t slot = cv2slot(lncvAddress);
        DEBUG("\n");
        DEBUG(F("Slot: "));
        DEBUG(slot);
        DEBUG(F(" SlotCV: "));
        DEBUG(cv2slotcv(lncvAddress, slot));
        DEBUG("\n");
        if (slot < pins_conf) {
          confpins[slot]->set_pin_cv(cv2slotcv(lncvAddress, slot), lncvValue);
          confpins[slot]->print();
          pins_to_update.add(slot);
        }
      }
      //delete(confpins[slot]);
      //configureSlot(slot);
      //lncv[lncvAddress] = lncvValue;
      return LNCV_LACK_OK;
    }
    else {
      return LNCV_LACK_ERROR_UNSUPPORTED;
    }

  }
  else {

    DEBUG(F("Artnr Invalid.\n"));

    return -1;
  }
}

void commitLNCVUpdate() {
	 // Reset the decoder to reread the configuration
	asm volatile ("  jmp 0");
}
  /**
   * Notifies the code on the reception of a request to end programming mode
   */
void notifyLNCVprogrammingStop(uint16_t ArtNr, uint16_t ModuleAddress) {

  DEBUG(F("notifyLNCVprogrammingStop "));

  if (programmingMode) {
    if (ArtNr == ARTNR && ModuleAddress == eeprom_read_byte(&_CV.address)) {
      programmingMode = false;
      #if defined(__AVR_ATmega328PB__)
      if (programmingMode) {
        PORTE &= ~(1 << PE0);
      }
      #endif

      DEBUG(F("End Programing Mode.\n"));


      commitLNCVUpdate();
    }
    else {
      if (ArtNr != ARTNR) {

        DEBUG(F("Wrong Artnr.\n"));


        return;
      }
      if (ModuleAddress != eeprom_read_byte(&_CV.address)) {

        DEBUG(F("Wrong Module Address.\n"));


        return;
      }
    }
  }
  else {

    DEBUG(F("Ignoring Request.\n"));


  }
}

int8_t notifyLNCVdiscover( uint16_t & ArtNr, uint16_t & ModuleAddress ) {
  DEBUG(F("Discover: "));
  DEBUG(ArtNr);
  DEBUG(ARTNR);
  uint16_t MyModuleAddress = eeprom_read_byte(&_CV.address);
  ModuleAddress = MyModuleAddress;
  ArtNr = ARTNR;
  DEBUG(ModuleAddress);
  return LNCV_LACK_OK;
}
