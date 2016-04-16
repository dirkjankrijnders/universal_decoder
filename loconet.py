import struct

LN_CHECKSUM_SEED = 0xFF
LNCV_fmt = '<BBBBBBBHHHBB'
LNCV_names = ['OPC', 'len', 'SRC', 'DSTL', 'DSTH', 'ReqId', 'PXCT1', 'deviceClass', 'lncvNumber', 'lncvValue', 'flags', 'checksum'];

class LocoNet(object):
	OPC_BUSY         = 0x81
	OPC_GPOFF        = 0x82
	OPC_GPON         = 0x83
	OPC_IDLE         = 0x85
	OPC_LOCO_SPD     = 0xa0
	OPC_LOCO_DIRF    = 0xa1
	OPC_LOCO_SND     = 0xa2
	OPC_SW_REQ       = 0xb0
	OPC_SW_REP       = 0xb1
	OPC_INPUT_REP    = 0xb2
	OPC_UNKNOWN      = 0xb3
	OPC_LONG_ACK     = 0xb4
	OPC_SLOT_STAT1   = 0xb5
	OPC_CONSIST_FUNC = 0xb6
	OPC_UNLINK_SLOTS = 0xb8
	OPC_LINK_SLOTS   = 0xb9
	OPC_MOVE_SLOTS   = 0xba
	OPC_RQ_SL_DATA   = 0xbb
	OPC_SW_STATE     = 0xbc
	OPC_SW_ACK       = 0xbd
	OPC_LOCO_ADR     = 0xbf
	OPC_PEER_XFER    = 0xe5
	OPC_SL_RD_DATA   = 0xe7
	OPC_IMM_PACKET   = 0xed
	OPC_IMM_PACKET_2 = 0xee
	OPC_WR_SL_DATA   = 0xef
	OPC_MASK         = 0x7f  # mask for acknowledge opcodes

	LNCV_SRC_MASTER  = 0x00
	LNCV_SRC_KPU     = 0x01
# KPU is, e.g., an IntelliBox
# 0x02 has no associated meaning
	LNCV_SRC_TWINBOX_FRED = 0x03
	LNCV_SRC_IBSWITCH = 0x04
	LNCV_SRC_MODULE  = 0x05

# Adresses for the 'DSTL'/'DSTH' part of an UhlenbrockMsg
	LNCV_BROADCAST_DSTL = 0x00
	LNCV_BROADCAST_DSTH = 0x00
	LNCV_INTELLIBOX_SPU_DSTL = 'I'
	LNCV_INTELLIBOX_SPU_DSTH = 'B'
	LNCV_INTELLIBOX_KPU_DSTL = 'I'
	LNCV_INTELLIBOX_KPU_DSTH = 'K'
	LNCV_TWINBOX_DSTH = 'T'
# For TwinBox, DSTL can be anything from 0 to 15
	LNCV_IBSWITCH_KPU_DSTL = 'I'
	LNCV_IBSWITCH_KPU_DSTH = 'S'
	LNCV_MODULE_DSTL = 0x05
	LNCV_MODULE_DSTH = 0x00


	LNCV_REQID_CFGREAD = 31
	LNCV_REQID_CFGWRITE = 32
	LNCV_REQID_CFGREQUEST = 33
# Flags for the 7th data Byte
	LNCV_FLAG_PRON = 0x80
	LNCV_FLAG_PROFF = 0x40
	LNCV_FLAG_RO = 0x01

# Error-codes for write-requests
	LNCV_LACK_ERROR_GENERIC = 0	
# Unsupported/non-existing CV
	LNCV_LACK_ERROR_UNSUPPORTED = 1
# CV is read only
	LNCV_LACK_ERROR_READONLY = 2
# Value out of range
	LNCV_LACK_ERROR_OUTOFRANGE = 3
# Everything OK
	LNCV_LACK_OK = 127

# the valid range for module addresses (CV0) as per the LNCV spec.
#	LNCV_MIN_MODULEADDR (0)
#	LNCV_MAX_MODULEADDR (65534)

def recvLnMsg(buf):
	for newByte in buf:
		# Check if this is the beginning of a new packet
		if( newByte & 0x80 ):
			# if the ReadPacket index is not the same as the Read index then we have received the
			# start of the next packet without completing the previous one which is an error
			"""if( Buffer->ReadPacketIndex != Buffer->ReadIndex )
				Buffer->Stats.RxErrors++ ;
			"""
			accumulator = bytearray();
			CheckSum = LN_CHECKSUM_SEED ;
			bGotNewLength = 0 ;
			# Set the return packet pointer to NULL first
			tempMsg = None ;
			ReadExpLen = 0;
			if ( ( newByte & 0x60 ) == 0x60 ):
				ReadExpLen = 0;
			else:
				ReadExpLen = ( ( newByte & 0x60 ) >> 4 ) + 2 ;
        	
		elif bGotNewLength == 0:
			if (ReadExpLen != 0):	# fixed length opcode found?
				bGotNewLength = 1 ;
				# If the Expected Length is 0 and the newByte is not an Command OPC code, then it must be
				# the length byte for a variable length packet
			elif(ReadExpLen == 0 ):
				ReadExpLen = newByte ;
				bGotNewLength = 1 ;
			else: 
				bGotNewLength = 0 ;
        	
		# Do we have a complete packet
		accumulator = accumulator + bytes([newByte]);
		if len(accumulator) == ReadExpLen:
			# Check if we have a good checksum
			if( CheckSum == newByte ) :
				# Set the return packet pointer
				tempMsg = accumulator;
				#Buffer->Stats.RxPackets++ ;
				#else
				#Buffer->Stats.RxErrors++ ;

			else:
				print("Invalid packet recieved: ", accumulator )
			if( tempMsg != None ):
				return bytearray(tempMsg);

		# Packet not complete so add the current byte to the checksum
		CheckSum ^= newByte ;

	return None ;
	
def checksumLnBuf(buf):
	CheckSum = LN_CHECKSUM_SEED ;
	for newByte in buf:
		CheckSum ^= newByte ;
	return bytearray(buf + bytes([CheckSum]));

def computeBytesFromPXCT(buf):
	mask = 0x01;
	# Data has only 7 bytes, so we consider only 7 bits from PXCT1
	for i in range(7):
		if ((buf[6] & mask) != 0x00):
			# Bit was set
			buf[7+i] |= 0x80;
		mask <<= 1;

	buf[6] = 0x00;
	return buf;


def computePXCTFromBytes(buf):
	mask = 0x01;
	buf[6] = 0x00;
	# Data has only 7 bytes, so we consider only 7 bits from PXCT1
	for i in range(7):
		if ((buf[7+i] & 0x80) != 0x00):
			buf[6] |= mask; #add bit to PXCT1
			buf[7+i] &= 0x7F;	# remove bit from data byte
		mask <<= 1;
	return buf
	
def parseLNCVmsg(buf):
	if len(buf) != 15:
		return None

		#	try:
	if (buf[0] == LocoNet.OPC_IMM_PACKET) or (buf[0] == LocoNet.OPC_PEER_XFER):
		buf = computeBytesFromPXCT(buf);
		pkt = struct.unpack(LNCV_fmt, buf);
		return dict(list(zip(LNCV_names, pkt)));
	else:
		return None

def startModuleLNCVProgramming(deviceClass, address):
	return makeLNCVresponse(deviceClass, 0, address, LocoNet.LNCV_FLAG_PRON, opc = LocoNet.OPC_IMM_PACKET, req = LocoNet.LNCV_REQID_CFGREQUEST);

def stopModuleLNCVProgramming(deviceClass, address):
	return makeLNCVresponse(deviceClass, 0, address, LocoNet.LNCV_FLAG_PROFF, opc = LocoNet.OPC_IMM_PACKET, req = LocoNet.LNCV_REQID_CFGREQUEST);
	
def readModuleLNCV(deviceClass, address, cv):
	return makeLNCVresponse(deviceClass, cv, 0, 0, opc = LocoNet.OPC_IMM_PACKET, req = LocoNet.LNCV_REQID_CFGREQUEST);

def writeModuleLNCV(deviceClass, address, cv, value):
	return makeLNCVresponse(deviceClass, cv, value, 0, opc = LocoNet.OPC_IMM_PACKET, req = LocoNet.LNCV_REQID_CFGWRITE);
	
def makeLNCVresponse(first, second, third, last, opc = LocoNet.OPC_PEER_XFER, src = LocoNet.LNCV_SRC_KPU, req = LocoNet.LNCV_REQID_CFGREAD):
	pkt = list(range(12));
	pkt[0] = opc
	pkt[1] = 15
	pkt[2] = src;
	pkt[3] = LocoNet.LNCV_MODULE_DSTL;
	pkt[4] = LocoNet.LNCV_MODULE_DSTH;
	pkt[5] = req;
	
	pkt[7] = first;
	pkt[8] = second;
	pkt[9] = third;
	pkt[10]= last;
	
	buf = bytearray(struct.pack(LNCV_fmt, *pkt))
	buf = computePXCTFromBytes(buf)
	buf = checksumLnBuf(buf[:-1]);
	return buf
	
class LNCVConfirmedMessage(object):
	def __init__(self, msg, reply, mask, src, retry = 1):
		super(LNCVConfirmedMessage, self).__init__();
		
		self.msg = msg
		self.reply = reply
		self.mask = mask
		self.src = src
		self.retry = retry;
		
		self.send = False;

	def match(self, reply):
		print("Compare: ", self.reply, " to ", reply)
		print(len(reply), " ?= ", len(self.mask))
		if len(reply) != len(self.mask):
			return False
		print("Length ok")
		print(int.from_bytes(reply, 'big') & int.from_bytes(self.mask, 'big'), (int.from_bytes(self.reply,'big') & int.from_bytes(self.mask, 'big')))
		if ((int.from_bytes(reply, 'big') & int.from_bytes(self.mask, 'big')) == (int.from_bytes(self.reply,'big') & int.from_bytes(self.mask, 'big'))):
			self.src.messageConfirmed(self, reply);
			return True
		
		return False

class LNCVReadMessage(LNCVConfirmedMessage):
	"""docstring for LNCVReadMessage"""
	def __init__(self, msg, src):
		mask  = bytearray(b'\0' * 15)
		reply = bytearray(msg);
		reply[0] = 0xe5;
		mask[0] = 0xff;
		print("MAsk:", mask)
		super(LNCVReadMessage, self).__init__(msg, reply, mask, src);
	
class LNCVWriteMessage(LNCVConfirmedMessage):
	"""docstring for LNCVReadMessage"""
	def __init__(self, msg, src):
		mask = bytearray(b'\0' * 4)
		reply  = bytearray.fromhex('b4ff7fff');
		reply[1] = msg[0] & 0x7f
		super(LNCVWriteMessage, self).__init__(msg, reply, mask, src);
		