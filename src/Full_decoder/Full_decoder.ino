#include <OneWire.h>
#include <LinkedList.h>

#include "config.h"
#define VERSION 10502


#if PINSERVO == 1
#warning "USING SERVO"
  #include <Servo.h>
  features = features | 1;
#endif

/* We're a loconet decoder! */
#include <LocoNet.h>

/* Include the CV handling and the pin functionalities */
#include "decoder_conf.h"
#include "configuredpins.h"
#include "cvaccess.h"
#include "bus_configuredpins.h"

decoder_conf_t EEMEM _CV = {
#include "default_conf.h"
};

#define MAX 24
ConfiguredPin* confpins[MAX];
uint8_t pins_conf = 0;
uint8_t features = 0;

/* TLC5947 Support*/
#if TLC_SUPPORT
#include "Adafruit_TLC5947.h"

// How many boards do you have chained?
#define NUM_TLC5974 1

#ifdef TLC_PROTO
#define data   10
#define clock   16
#define latch   14
#define oe  -1  // set to -1 to not use the enable pin (its optional)
#else
#define data   16
#define clock   15
#define latch   10
#define oe  -1  // set to -1 to not use the enable pin (its optional)
#endif
Adafruit_TLC5947 tlc = Adafruit_TLC5947(NUM_TLC5974, clock, data, latch);
#endif // TLC_SUPPORT

/* PCA9685 Support */

#include <Adafruit_PWMServoDriver.h>

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

#ifndef LOCONET_TX_PIN
  #define LOCONET_TX_PIN 7
#endif

#define POWER_VOLTAGE_PIN A2

extern int __bss_start, __bss_end;

int freeRam () {
  extern int __heap_start, *__brkval;
  int v;
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
};

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
  DEBUG("Reporting slot ");
  DEBUG(slot);
  DEBUG(" Address: ");
  DEBUG(confpins[slot]->_address);
  DEBUG(" State: ");
  DEBUGLN(state);
  if (slot == 0)
    return;
	LocoNet.reportSensor(confpins[slot]->_address, state);
}

void setSlot(uint16_t slot, uint16_t state) {
  if (slot == 0)
    return;
  if (slot < MAX)
    confpins[slot]->set(state, 0);
}
void reportSensor(uint16_t address, bool state) {
  LocoNet.reportSensor(address, state);
}

void configureSlot(uint8_t slot) {
  uint8_t pin_config;
  uint16_t pin, address, pos1, pos2, speed, fbslot1, fbslot2, powerpin, secondary_address;
  bool cumulative, force_on, report_inverse, keep_update;
  
    pin_config = eeprom_read_byte((uint8_t*)&(_CV.pin_conf[slot]));
    pin   = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.arduinopin));
    address = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.address));
    DEBUGLN(pin_config);
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
        confpins[slot] = new MagnetSwitch(slot, pin, address, pos2, speed, fbslot1, fbslot2);
        confpins[slot]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[slot].magnet.state)));
          break;
#if TLC_SUPPORT
      case 101: // TLC5947 PWM LED Controller.
        pos1 = eeprom_read_word((uint16_t*)&(_CV.conf[slot].led.value1));
        pin_config = ((eeprom_read_word((uint16_t*)&(_CV.conf[slot].led.function)) & 0x01) == 0x01);
        confpins[slot] = new TLC5947pin(&tlc, slot, pin, address, pin_config, pin, pos1);
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
    DEBUG("Pin #");
    DEBUGLN(slot);
    confpins[slot]->print();
    pins_to_update.add(slot);
}
void setup() {
#ifdef USE_SERIAL
#warning Debug!
  Serial.begin(57600);
  while (!Serial){
    ;
  }
#endif

  DEBUG("Universal decoder v");  
  DEBUGLN(VERSION);
  DEBUG("Module address: ");
  DEBUGLN(eeprom_read_byte(&_CV.address));
  LocoNet.init(LOCONET_TX_PIN);
  
  uint8_t i = 0;
  DEBUG("Max # of pins:");
  DEBUGLN(MAX);
  pins_conf = eeprom_read_byte((uint8_t*)&(_CV.pins_conf));
  if (pins_conf > MAX) pins_conf = MAX;
  DEBUGLN(freeRam());
  for (i = 0; i < pins_conf; i++) {
    configureSlot(i);
    DEBUGLN(freeRam())
  }
#if TLC_SUPPORT
  tlc.begin();
  features = features | 4;
#endif //TLC_SUPPORT
  features = features | 2;
#if PINSERVO
  features = features | 1;
#endif
  ds.reset_search();
  delay(250);
  if (!ds.search(addr)) {
    ds.reset_search();
    for (uint8_t i = 0; i < 7 ; i++) {
      addr[i] = 0x00;
    }
    DEBUGLN("No ds18s20 found for UID");
  } 

#ifdef DEBUG_OUTPUT
    else {
    DEBUG("UID: ");
    for (uint8_t i = 0; i < 7; i++) {
      Serial.print(i);
      Serial.print(addr[i], HEX);
    }
    DEBUGLN(".");
  }    
#endif

  pca.begin();
  pca.setPWMFreq(70);

#ifdef POWER_VOLTAGE_PIN
  pinMode(POWER_VOLTAGE_PIN, INPUT);
  Serial.print("Power voltage in mV: ");
  Serial.println(readPowerVoltage());
#endif
}
uint8_t current_pin_list;

void loop() {

  if (!(pins_to_update.size() == 0)) {
	  current_pin_list += 1;
    if (current_pin_list >= pins_to_update.size())
      current_pin_list = 0;
    //DEBUG("Updating pin ");
    //DEBUGLN(pins_to_update.get(current_pin_list));
    if (!confpins[pins_to_update.get(current_pin_list)]->update()) { // Update the first item, as long as update() returns true, otherwise...
      //pins_to_update.push(pins_to_update.first());
      DEBUG("Done updating ");
      DEBUGLN(pins_to_update.get(current_pin_list));
      pins_to_update.remove(current_pin_list); // ..drop the first item
      DEBUG(pins_to_update.size());
      DEBUGLN(" active pins left in the queue");
    }
    // DEBUGLN(freeRam())
  }
  
  /*** LOCONET ***/
  LnPacket = LocoNet.receive();
  if (LnPacket) {
  	DEBUG(".");
    uint8_t packetConsumed(LocoNet.processSwitchSensorMessage(LnPacket));
    if (packetConsumed == 0) {
      DEBUG("Loop ");
      DEBUG((int)LnPacket);
      dumpPacket(LnPacket->ub);
      packetConsumed = lnCV.processLNCVMessage(LnPacket);
      DEBUG("End Loop\n");
    }
      DEBUG(pins_to_update.size());
      DEBUGLN(" active pins left in the queue");
    DEBUGLN(freeRam())
  }
};

void notifySwitchRequest( uint16_t Address, uint8_t Output, uint8_t Direction ) {
  DEBUG("Switch Request: ");
  DEBUG(Address);
  DEBUG(':');
  DEBUG(Direction ? "Closed" : "Thrown");
  DEBUG(" - ");
  DEBUGLN(Output ? "On" : "Off");
  for (uint8_t i =0 ; i < MAX ; i++) {
    if (confpins[i]->_address == Address){
      // Set new state
      confpins[i]->set(Direction, Output);
      // Add to the update queue
    pins_to_update.add(i);
      // Call update once to get started
      confpins[i]->update();
      // Save the state
      eeprom_write_word((uint16_t*)&(_CV.conf[i].servo.state), confpins[i]->get_state());
      DEBUG("Thrown switch: ");
      DEBUG(i);
      DEBUG(" to :");
      confpins[i]->print_state();
      DEBUG("\n");
    }
  }

}

void dumpPacket(UhlenbrockMsg & ub) {
#ifdef DEBUG_OUTPUT
  Serial.print(" PKT: ");
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

  DEBUG("Enter notifyLNCVread(");
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

        DEBUG("\nEeprom address: ");
        DEBUG(((uint16_t)&(_CV.address)+cv2address(lncvAddress)));
        DEBUG(" LNCV Value: ");
        DEBUG(lncvValue);
        DEBUG("\n");

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

      DEBUG("ArtNr invalid.\n");

      return -1;
    }
  } else {

    DEBUG("Ignoring Request.\n");

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

      DEBUG("Programming started");

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

  DEBUG("Enter notifyLNCVwrite(");
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
      DEBUG(read_cv(&_CV, lncvAddress));
      if (lncvAddress > 31 && false) {
        uint8_t slot = cv2slot(lncvAddress);
        DEBUG("\n");
        DEBUG("Slot: ");
        DEBUG(slot);
        DEBUG(" SlotCV: ");
        DEBUG(cv2slotcv(lncvAddress, slot));
        DEBUG("\n");
        confpins[slot]->set_pin_cv(cv2slotcv(lncvAddress, slot), lncvValue);
        confpins[slot]->print();
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

    DEBUG("Artnr Invalid.\n");

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

  DEBUG("notifyLNCVprogrammingStop ");

  if (programmingMode) {
    if (ArtNr == ARTNR && ModuleAddress == eeprom_read_byte(&_CV.address)) {
      programmingMode = false;

      DEBUG("End Programing Mode.\n");


      commitLNCVUpdate();
    }
    else {
      if (ArtNr != ARTNR) {

        DEBUG("Wrong Artnr.\n");


        return;
      }
      if (ModuleAddress != eeprom_read_byte(&_CV.address)) {

        DEBUG("Wrong Module Address.\n");


        return;
      }
    }
  }
  else {

    DEBUG("Ignoring Request.\n");


  }
}

int8_t notifyLNCVdiscover( uint16_t & ArtNr, uint16_t & ModuleAddress ) {
  DEBUG("Discover: ");
  DEBUG(ArtNr);
  DEBUG(ARTNR);
  uint16_t MyModuleAddress = eeprom_read_byte(&_CV.address);
  ModuleAddress = MyModuleAddress;
  ArtNr = ARTNR;
  DEBUG(ModuleAddress);
  return LNCV_LACK_OK;
}
