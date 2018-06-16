# universal_decoder

implements a loconet compatible decoder with libdec and mrrwa LocoNet libraries. Supports all features from the libdec library and as such supports servo control with feedback, feedback on pin states and outputs on pins. 

Configuration is done using the decconf python program.


## Bootloader problems

The bootloaders on 32u4 boards is sometimes iffy, see: http://www.sowbug.com/post/16644998284/rescue-guide-for-your-adafruit-atmega32u4-breakout. So it is advised to use the Adafruit bootloader, which is included here (bin/BootloaderCDC.hex):


    avrdude -p m32u4 -U lfuse:w:0xFC:m -U hfuse:w:0xD0:m -U efuse:w:0xC3:m
    avrdude -p m32u4 -U flash:w:BootloaderCDC.hex
