#include "config.h"

#if PINSERVO == 1
#warning "USING SERVO"
  #include <Servo.h>
#endif

#define VERSION 10200
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

/* TLC5947 Support*/
#include "Adafruit_TLC5947.h"

// How many boards do you have chained?
#define NUM_TLC5974 1

#define data   10
#define clock   16
#define latch   14
#define oe  -1  // set to -1 to not use the enable pin (its optional)

Adafruit_TLC5947 tlc = Adafruit_TLC5947(NUM_TLC5974, clock, data, latch);

/* PCA9685 Support */

#include <Adafruit_PWMServoDriver.h>

// Default address = 0x40
Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver();


void enableServos();
void disableServos();

bool pins_busy = false;

/* 
The LocoNet CV related stuff
*/
#define ARTNR 10001

lnMsg *LnPacket;

LocoNetCVClass lnCV;

boolean programmingMode;

#define LOCONET_TX_PIN 5

extern int __bss_start, __bss_end;

int freeRam () {
  extern int __heap_start, *__brkval;
  int v;
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
};

void reportSlot(uint16_t slot, uint16_t state) {
  DEBUG("Reporting slot ");
  DEBUG(slot);
  DEBUG(" Address: ");
  DEBUG(confpins[slot]->_address);
  DEBUG(" State: ");
  DEBUGLN(state);
	LocoNet.reportSensor(confpins[slot]->_address, state);
}

void setSlot(uint16_t slot, uint16_t state) {
  if (slot < MAX)
    confpins[slot]->set(state, 0);
}
void reportSensor(uint16_t address, bool state) {
  LocoNet.reportSensor(address, state);
}

void configureSlot(uint8_t slot) {
  uint8_t pin_config;
  uint16_t pin, address, pos1, pos2, speed, fbslot1, fbslot2, powerpin;

    pin_config = eeprom_read_byte((uint8_t*)&(_CV.pin_conf[slot]));
    pin   = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.arduinopin));
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
        confpins[slot] = new InputPin(slot, pin, address);
        break;
      case 3: // Output
        pin_config = ((eeprom_read_word((uint16_t*)&(_CV.conf[slot].output.options)) & 0x01) == 0x01);
        confpins[slot] = new OutputPin(slot, pin, address, pin_config);
        break;
      case 4: // Dual action
        pos1  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos1));
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.pos2));
        speed = eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.speed));
        pin_config = eeprom_read_word((uint16_t*)&(_CV.conf[slot].output.options));

        confpins[slot] = new DualAction(slot, pin, address, pos1, pos2, speed, pin_config);
        confpins[slot]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[slot].servo.state)));
        break;
      case 101: // TLC5947 PWM LED Controller.
        pin_config = ((eeprom_read_word((uint16_t*)&(_CV.conf[slot].output.options)) & 0x01) == 0x01);
        confpins[slot] = new TLC5947pin(&tlc, slot, pin, address, pin_config, pin, 1000);
        break;
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
}
void setup() {
#ifdef USE_SERIAL
  Serial.begin(57600);
 /* while (!Serial){
    ;
  }*/
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
  for (i = 0; i < pins_conf; i++) {
    configureSlot(i);
  }
  tlc.begin();
  
  pca.begin();
  pca.setPWMFreq(70);

  programmingMode = false;
}

void loop() {
	pins_busy = false;
  for (uint8_t i =0 ; i < pins_conf ; i++) {
	 confpins[i]->update();
  };
  
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
      confpins[i]->set(Direction, Output);
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
      uint8_t slot = cv2slot(lncvAddress);
      DEBUG("\n");
      DEBUG("Slot: ");
      DEBUG(slot);
      DEBUG(" SlotCV: ");
      DEBUG(cv2slotcv(lncvAddress, slot));
      DEBUG("\n");
      confpins[slot]->set_pin_cv(cv2slotcv(lncvAddress, slot), lncvValue);
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
