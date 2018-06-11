""" Python module for decoding the loconet protocol"""

import logging
import struct

LN_CHECKSUM_SEED = 0xFF
LNCV_fmt = '<BBBBBBBHHHBB'
LNCV_names = ['OPC', 'len', 'SRC', 'DSTL', 'DSTH', 'ReqId', 'PXCT1',
              'deviceClass', 'lncvNumber', 'lncvValue', 'flags', 'checksum']

""" Loconet class definition """


class LocoNet(object):
    OPC_BUSY = 0x81
    OPC_GPOFF = 0x82
    OPC_GPON = 0x83
    OPC_IDLE = 0x85
    OPC_LOCO_SPD = 0xa0
    OPC_LOCO_DIRF = 0xa1
    OPC_LOCO_SND = 0xa2
    OPC_SW_REQ = 0xb0
    OPC_SW_REP = 0xb1
    OPC_INPUT_REP = 0xb2
    OPC_UNKNOWN = 0xb3
    OPC_LONG_ACK = 0xb4
    OPC_SLOT_STAT1 = 0xb5
    OPC_CONSIST_FUNC = 0xb6
    OPC_UNLINK_SLOTS = 0xb8
    OPC_LINK_SLOTS = 0xb9
    OPC_MOVE_SLOTS = 0xba
    OPC_RQ_SL_DATA = 0xbb
    OPC_SW_STATE = 0xbc
    OPC_SW_ACK = 0xbd
    OPC_LOCO_ADR = 0xbf
    OPC_PEER_XFER = 0xe5
    OPC_SL_RD_DATA = 0xe7
    OPC_IMM_PACKET = 0xed
    OPC_IMM_PACKET_2 = 0xee
    OPC_WR_SL_DATA = 0xef
    OPC_MASK = 0x7f  # mask for acknowledge opcodes

    OPC_SW_REP_SW     = 0x20  # switch input, aux input otherwise    */
    OPC_SW_REP_HI     = 0x10  # input is HI, LO otherwise            */
    OPC_SW_REP_CLOSED = 0x20  # 'Closed' line is ON, OFF otherwise   */
    OPC_SW_REP_THROWN = 0x10  # 'Thrown' line is ON, OFF otherwise   */
    OPC_SW_REP_INPUTS = 0x40  # sensor inputs, outputs otherwise     */
    OPC_SW_REQ_DIR    = 0x20  # switch direction - closed/thrown     */
    OPC_SW_REQ_OUT    = 0x10  # output On/Off                        */

    OPC_INPUT_REP_CB = 0x40  # control bit, reserved otherwise      */
    OPC_INPUT_REP_SW = 0x20  # input is switch input, aux otherwise */
    OPC_INPUT_REP_HI = 0x10  # input is HI, LO otherwise            */

    LNCV_SRC_KPU = 0x01
    # KPU is, e.g., an IntelliBox
    # 0x02 has no associated meaning
    LNCV_SRC_TWINBOX_FRED = 0x03
    LNCV_SRC_IBSWITCH = 0x04
    LNCV_SRC_MODULE = 0x05

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

    logger = logging.getLogger('decconf.loconet')


# the valid range for module addresses (CV0) as per the LNCV spec.
#    LNCV_MIN_MODULEADDR (0)
#    LNCV_MAX_MODULEADDR (65534)

def recieve_loconet_bytes(buf: bytearray) -> bytearray:
    """
    Check the validity of a received loconet packet

    Arguments
    ---------
    buf: bytearray
        bytes to parse
    Returns
    -------
    Validated packet: bytearray

    """
    gotnewlength = 0
    readexplen = None
    for newbyte in buf:
        # Check if this is the beginning of a new packet
        if newbyte & 0x80:
            # if the ReadPacket index is not the same as the Read index then we
            # have recieved the start of the next packet without completing the
            # previous one which is an error
            """if( Buffer->ReadPacketIndex != Buffer->ReadIndex )
                Buffer->Stats.RxErrors++
            """
            accumulator = bytearray()
            checksum = LN_CHECKSUM_SEED
            gotnewlength = 0
            # Set the return packet pointer to NULL first
            tempMsg = None
            readexplen = 0
            if (newbyte & 0x60) == 0x60:
                readexplen = 0
            else:
                readexplen = ((newbyte & 0x60) >> 4) + 2

        elif gotnewlength == 0:
            if readexplen != 0:  # fixed length opcode found?
                gotnewlength = 1
                # If the Expected Length is 0 and the newbyte is not an Command
                # OPC code, then it must be the length byte for a variable
                # length packet
            else:
                readexplen = newbyte
                gotnewlength = 1

        # Do we have a complete packet
        accumulator = accumulator + bytes([newbyte])
        if len(accumulator) == readexplen:
            # Check if we have a good checksum
            if checksum == newbyte:
                # Set the return packet pointer
                tempMsg = accumulator
                # Buffer->Stats.RxPackets++
                # else
                # Buffer->Stats.RxErrors++

            else:
                LocoNet.logger.warning("Invalid packet recieved: {}"
                                       .format(accumulator))
            if tempMsg is not None:
                LocoNet.logger.debug("Packet recieved: 0x {}".
                                     format(" ".join("{:02x}".format(b) for b in tempMsg)))
                return bytearray(tempMsg)

        # Packet not complete so add the current byte to the checksum
        checksum ^= newbyte

    return bytearray()


def checksum_loconet_buffer(buf: bytearray) -> bytearray:
    """Replaces the last byte of buf with the checksum over the over bytes

    Arguments
    ---------
    buf: bytearray
        Packet to calculate the checksum on, checksum is put in the last byte

    Returns
    -------
    Buffer with checksum: bytearray
    """
    checksum = LN_CHECKSUM_SEED
    # noinspection PyTypeChecker
    for new_byte in buf[:-1]:
        checksum ^= new_byte
    buf[-1] = checksum
    return buf


def compute_bytes_from_PXCT(buf: bytearray) -> bytearray:
    """
    Reconstruct 8th bits of the date bytes from the PXCT byte. This function is used on incoming packets.

    Arguments
    ---------
    buf: bytearray
        Packet to reconstruct

    Returns
    -------
    Reconstructed packet: bytearray
    """
    mask = 0x01
    # Data has only 7 bytes, so we consider only 7 bits from PXCT1
    for i in range(7):
        if (buf[6] & mask) != 0x00:
            # Bit was set
            buf[7 + i] |= 0x80
        mask <<= 1

    buf[6] = 0x00
    return buf


def compute_PXCT_from_bytes(buf):
    """
    Remove the 8th bit form the data bytes and put them in the PXCT1 byte, this is how the packet will go over the wire.
    So this function is called before sending the packet.

    Arguments
    ---------
    buf: bytearray
        Packet as constructed

    Returns
    -------
    Deconstructed packet: bytearray
    """
    mask = 0x01
    buf[6] = 0x00
    # Data has only 7 bytes, so we consider only 7 bits from PXCT1
    for i in range(7):
        if (buf[7 + i] & 0x80) != 0x00:
            buf[6] |= mask  # add bit to PXCT1
            buf[7 + i] &= 0x7F  # remove bit from data byte
        mask <<= 1
    return buf


def parse_LNCV_message(buf):
    if len(buf) != 15:
        return None

    if (buf[0] == LocoNet.OPC_IMM_PACKET) or (buf[0] == LocoNet.OPC_PEER_XFER):
        buf = compute_bytes_from_PXCT(buf)
        # noinspection PyTypeChecker
        pkt = struct.unpack(LNCV_fmt, buf)
        return dict(list(zip(LNCV_names, pkt)))
    else:
        return None


def format_loconet_message(data: bytearray) -> str:
    lncv = parse_LNCV_message(data)
    info = "info"
    if lncv is not None:
        del lncv['len']
        del lncv['PXCT1']
        del lncv['checksum']
        info = ", ".join(["{}: {}".format(k, v) for k, v in lncv.items()])
    elif data[0] == LocoNet.OPC_GPOFF:
        info = "Power off"
    elif data[0] == LocoNet.OPC_GPON:
        info = "Power on"
    elif data[0] == LocoNet.OPC_SW_REQ:
        addr = (data[1] | ((data[2] & 0x0F) << 7))
        addr +=1
        if data[2] & LocoNet.OPC_INPUT_REP_SW :
            addr += 1
        onoff = (data[2] & LocoNet.OPC_SW_REQ_OUT) >> 4
        state = (data[2] & LocoNet.OPC_SW_REQ_DIR)
        info = "Switch req %i: %i - %i" % (addr, state, onoff)

    elif data[0] == LocoNet.OPC_INPUT_REP:
        addr = (data[1] | ((data[2] & 0x0F) << 7)) << 1
        addr +=1
        if data[2] & LocoNet.OPC_INPUT_REP_SW :
            addr += 1
        state = (data[2] & LocoNet.OPC_INPUT_REP_HI) >> 4
        info = "Sensor {}: {}".format(addr, state)

    return " ".join("{:02x}".format(b) for b in data).upper(), info


class LNMessage(object):
    """docstring for LNMessage"""

    def __init__(self, buf, expect_reply=False):
        super(LNMessage, self).__init__()
        self.msg = buf
        self.expectReply = expect_reply


def switch(address: int, position: bool, state: bool = True):
    buf = [LocoNet.OPC_SW_REQ]
    address -= 1
    buf.append(address & 0xFF)
    buf.append((address >> 7) & 0x0F)
    buf.append(0x01)
    if position:
        buf[2] |= LocoNet.OPC_SW_REQ_DIR
    if state:
        buf[2] |= LocoNet.OPC_SW_REQ_OUT
    buf = checksum_loconet_buffer(bytearray(buf))
    return LNMessage(buf)


def start_module_LNCV_programming(device_class, address):
    return make_LNCV_response(device_class, 0, address, LocoNet.LNCV_FLAG_PRON, opc=LocoNet.OPC_IMM_PACKET,
                              req=LocoNet.LNCV_REQID_CFGREQUEST)


def stop_module_LNCV_programming(device_class, address):
    return make_LNCV_response(device_class, 0, address, LocoNet.LNCV_FLAG_PROFF, opc=LocoNet.OPC_IMM_PACKET,
                              req=LocoNet.LNCV_REQID_CFGREQUEST)


def read_module_LNCV(device_class, cv):
    return make_LNCV_response(device_class, cv, 0, 0, opc=LocoNet.OPC_IMM_PACKET, req=LocoNet.LNCV_REQID_CFGREQUEST)


def write_module_LNCV(device_class, cv, value):
    return make_LNCV_response(device_class, cv, value, 0, opc=LocoNet.OPC_IMM_PACKET, req=LocoNet.LNCV_REQID_CFGWRITE)


def make_LNCV_response(first, second, third, last, opc=LocoNet.OPC_PEER_XFER, src=LocoNet.LNCV_SRC_KPU,
                       req=LocoNet.LNCV_REQID_CFGREAD):
    pkt = list(range(12))
    pkt[0] = opc
    pkt[1] = 15
    pkt[2] = src
    pkt[3] = LocoNet.LNCV_MODULE_DSTL
    pkt[4] = LocoNet.LNCV_MODULE_DSTH
    pkt[5] = req

    pkt[7] = first
    pkt[8] = second
    pkt[9] = third
    pkt[10] = last

    buf = bytearray(struct.pack(LNCV_fmt, *pkt))
    buf = compute_PXCT_from_bytes(buf)
    buf = checksum_loconet_buffer(buf)
    return buf


class LNCV_confirmed_message(LNMessage):
    def __init__(self, msg, reply, mask, src, retry=1):
        """
        Make a LNCV message that notifies the an object when the reply comes

        Arguments
        ---------
        msg: bytearray
            valid LNCV message that expects as reply
        reply: bytearray
            the expected reply, the exact values are check with in the mask
        mask: bytearray
            mask for the reply, only the bits specified are compared, al others are "don't care"
        src: object
            Object of which the messageConfirmed method is called when the decoder replies
        reply: int
            Number of retries before giving up, defaults to 1
        """
        super(LNCV_confirmed_message, self).__init__(msg, True)

        self.reply = reply
        self.mask = mask
        self.src = src
        self.retry = retry

        self.logger = logging.getLogger('decconf.Loconet.LNCVConfirmedMessage')

        self.send = False

    def match(self, reply):
        if len(reply) != len(self.mask):
            self.logger.debug("Wrong length: reply: {}, mask: {}".format(len(reply), len(self.mask)))
            return False
        self.logger.debug("reply: {}, exp. reply: {}, mask: {}".format(" ".join("{:02x}".format(b) for b in reply),
                                                                       " ".join("{:02x}".format(b) for b in self.reply),
                                                                       " ".join("{:02x}".format(b) for b in self.mask)))
        self.logger.debug('Comparing: {} == {}'.format(int.from_bytes(reply, 'big') & int.from_bytes(self.mask, 'big'),
                                                       (int.from_bytes(self.reply, 'big') & int.from_bytes(self.mask,
                                                                                                           'big'))))
        if int.from_bytes(reply, 'big') & int.from_bytes(self.mask, 'big') == int.from_bytes(self.reply,
                                                                                             'big') & int.from_bytes(
                self.mask, 'big'):
            self.src.message_confirmed(self, reply)
            return True

        return False


class LNCVReadMessage(LNCV_confirmed_message):
    def __init__(self, msg: bytearray, src: object):
        """
        Make a LNCV read message

        Arguments
        ---------
        msg: bytearray
            Message as created by read_module_LNCV
        src: object
            Object of which the messageConfirmed method is called when the decoder replies
        """
        mask = bytearray(b'\0' * 15)
        reply = bytearray(msg)
        reply[0] = 0xe5
        mask[0] = 0xff
        mask[1] = 0xff
        mask[7] = 0xff
        mask[8] = 0xff
        mask[9] = 0xff
        mask[10] = 0xff

        super(LNCVReadMessage, self).__init__(msg, reply, mask, src)


class LNCVWriteMessage(LNCV_confirmed_message):
    def __init__(self, msg, src):
        """
        Make a LNCV write message

        Arguments
        ---------
        msg: bytearray
            Message as created by write_module_LNCV
        src: object
            Object of which the messageConfirmed method is called when the decoder replies
        """
        mask = bytes.fromhex('ffff0000')
        reply = bytearray.fromhex('b46d7fff')
        reply[1] = msg[0] & 0x7f
        super(LNCVWriteMessage, self).__init__(msg, reply, mask, src)
