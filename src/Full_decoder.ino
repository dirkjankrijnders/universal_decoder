/*
If serial output is desired uncommment the #undef line. For production, i.e.
without computer connected this line should be commented out. 
*/
#define DEBUG_OUTPUT
//#undef DEBUG_OUTPUT

#ifdef DEBUG_OUTPUT
#define USE_SERIAL
#define DEBUG(x) Serial.print(x)
#define DEBUGLN(x) Serial.println(x)
#else
#define DEBUG(x)
#define DEBUGLN(x)
#endif

/* We're a loconet decoder! */
#include <LocoNet.h>

/* Include the CV handling and the pin functionalities */
#include "decoder_conf.h"
#include "configuredpins.h"
#include "cvaccess.h"

decoder_conf_t EEMEM _CV = {
#include "default_conf.h"
};

#define MAX 24
ConfiguredPin* confpins[MAX];

/* Power to pins management */
#define servoEnablePin 15

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

void reportSlot(uint16_t slot, uint16_t state) {
	LocoNet.reportSensor(confpins[slot]->_address, state);
}

void reportSwitch(uint16_t slot, uint16_t state){
	ServoSwitch* confslot = (ServoSwitch*)confpins[slot];
#ifdef DS54
	uint16_t address = confslot->address;
	byte AddrH = ( (--address >> 7) & 0x0F ) | OPC_SW_REP_INPUTS  ;
	byte AddrL = ( address) & 0x7F ;

	if ( state == 0 )
		AddrH |= OPC_SW_REP_SW  ;
	if ( state == 1 )
		AddrH |= OPC_SW_REP_HI  ;
	if ( state == 2 )
		AddrH |= OPC_SW_REP_HI | OPC_SW_REP_SW ;
	
	LocoNet.send(OPC_SW_REP, AddrL, AddrH );
#else
	if ( state == 0 ) {
		reportSlot(confslot->_fbslot1, 0);
		reportSlot(confslot->_fbslot2, 0);
		//LocoNet.reportSensor(Address, 0);
		//LocoNet.reportSensor(Address+10, 0);
	} else if( state == 1 ) {
		reportSlot(confslot->_fbslot1, 1);
		reportSlot(confslot->_fbslot2, 0);
		//LocoNet.reportSensor(Address, 1);
		//LocoNet.reportSensor(Address+10, 0);		
	} else if( state == 2 ) {
		reportSlot(confslot->_fbslot1, 0);
		reportSlot(confslot->_fbslot2, 1);
		//LocoNet.reportSensor(Address, 0);
		//LocoNet.reportSensor(Address+10, 1);
	}
#endif
}

void reportSensor(uint16_t address, bool state) {
  LocoNet.reportSensor(address, state);
}

void setup() {
  pinMode( servoEnablePin, OUTPUT);
  disableServos();
#ifdef USE_SERIAL
  Serial.begin(57600);
  while (!Serial){
    ;
  }
#endif

  DEBUGLN("Universal decoder v0.0");  
  LocoNet.init(LOCONET_TX_PIN);
  
  uint8_t i = 0;
  uint8_t pin_config;
  uint16_t pin, address, pos1, pos2, speed, fbslot1, fbslot2;
  DEBUG("Max # of pins:");
  DEBUGLN(MAX);
   
  for (i = 0; i < MAX; i++) {
    pin_config = eeprom_read_byte((uint8_t*)&(_CV.pin_conf[i]));
    pin   = eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.arduinopin));
    address = eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.address));
    switch (pin_config) {
      case 2: //Servo
        //ServoSwitch(i,0);
        pos1  = eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.pos1));
        pos2  = eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.pos2));
        speed = eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.speed));
        fbslot1  = eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.fbslot1));
        fbslot2  = eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.fbslot2));
        confpins[i] = new ServoSwitch(i, pin, address, pos1, pos2, speed, servoEnablePin, fbslot1, fbslot2);
		confpins[i]->restore_state(eeprom_read_word((uint16_t*)&(_CV.conf[i].servo.state)));
        break;
      default:
        confpins[i] = new InputPin(i, pin, address);
        break;
    }
    DEBUG("Pin #");
    DEBUGLN(i);
    confpins[i]->print();
  }
  programmingMode = false;
}

void loop() {
	pins_busy = false;
  for (uint8_t i =0 ; i < MAX ; i++) {
	 confpins[i]->update();
  };
  
  /*** LOCONET ***/
  LnPacket = LocoNet.receive();
  if (LnPacket) {
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

void enableServos() {
	digitalWrite(servoEnablePin, HIGH);
}

void disableServos() {
	digitalWrite(servoEnablePin, LOW);
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

    if (lncvAddress < 255) {
      DEBUG(cv2address(lncvAddress));
      DEBUG(bytesizeCV(lncvAddress));
      DEBUG((uint8_t)lncvValue);
      write_cv(&_CV, lncvAddress, lncvValue);      
      DEBUG(read_cv(&_CV, lncvAddress));
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
