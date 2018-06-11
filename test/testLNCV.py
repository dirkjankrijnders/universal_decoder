#!/usr/bin/env python3
import logging
import unittest

from decconf.protocols.loconet import recieve_loconet_bytes, LNCV_confirmed_message, LNCVWriteMessage, \
    write_module_LNCV, start_module_LNCV_programming, stop_module_LNCV_programming, checksum_loconet_buffer, \
    format_loconet_message, LocoNet, read_module_LNCV, LNCVReadMessage, parse_LNCV_message, compute_PXCT_from_bytes, \
    switch


class TestLNCV(unittest.TestCase):
    def setUp(self):
        self.okCalled = False

    # noinspection PyUnusedLocal
    def message_confirmed(self, msg, reply):
        self.okCalled = True

    def test_recieve_loconet_bytes(self):
        input_buf = checksum_loconet_buffer(bytearray([LocoNet.OPC_GPOFF, 00]))
        self.assertEqual(recieve_loconet_bytes(input_buf), input_buf)
        input_buf = checksum_loconet_buffer(compute_PXCT_from_bytes(
            bytearray.fromhex('e50f05494b1f8011270402650002DA')))
        self.assertEqual(recieve_loconet_bytes(input_buf), input_buf)

    def test_write_confirmed_message(self):
        msg = write_module_LNCV(10001, 0, 2)
        reply = bytes.fromhex('ed2634df')
        mask = bytes.fromhex('ffffff00')

        cmsg = LNCV_confirmed_message(msg, reply, mask, self)
        self.assertFalse(cmsg.match(bytes.fromhex('ed2734ff')))
        self.assertFalse(self.okCalled)
        self.assertTrue(cmsg.match(bytes.fromhex('ed2634ff')))
        self.assertTrue(self.okCalled)

    def test_read_confirmed_message(self):
        msg = read_module_LNCV(10001, 2)
        reply = bytes([LocoNet.OPC_PEER_XFER, 15, LocoNet.LNCV_SRC_KPU, LocoNet.LNCV_MODULE_DSTL,
                       LocoNet.LNCV_MODULE_DSTH, LocoNet.LNCV_REQID_CFGREQUEST, 0, 17, 39, 2, 0, 0, 18, 0, 0])
        mask = bytes.fromhex('ffff00000000ffffffff0000000000')

        cmsg = LNCV_confirmed_message(msg, reply, mask, self)
        self.assertTrue(cmsg.match(bytes.fromhex('e50f01050021001127020012000000')))
        self.assertTrue(self.okCalled)
        self.okCalled = False

        cmsg = LNCVReadMessage(read_module_LNCV(10001, 2), self)
        self.assertTrue(cmsg.match(bytes.fromhex('e50f01050021001127020012000000')))
        self.assertTrue(self.okCalled)

    def testWriteCV(self):
        msg = write_module_LNCV(10001, 0, 2)
        cmsg = LNCVWriteMessage(msg, self)
        self.assertFalse(cmsg.match(bytes.fromhex('ed27')))
        self.assertFalse(self.okCalled)
        self.assertFalse(cmsg.match(bytes.fromhex('ed2734ff')))
        self.assertFalse(self.okCalled)
        self.assertTrue(cmsg.match(bytes.fromhex('b46d34ff')))
        self.assertTrue(self.okCalled)

    def testStartModuleLNCVProgramming(self):
        self.assertEqual(bytes.fromhex('ED0F0105002150112700007F000021'), start_module_LNCV_programming(10001, 255))

    def testStopModuleLNCVProgramming(self):
        self.assertEqual(bytes.fromhex('ED0F0105002110112700007F004021'), stop_module_LNCV_programming(10001, 255))

    def testMakeLNCVMessage(self):
        buf = bytearray.fromhex('e50f05494b1f8011270402650002DA')
        self.assertEqual(buf, checksum_loconet_buffer(buf))

    def test_parse_LNCV_message(self):
        buf = checksum_loconet_buffer(bytearray([LocoNet.OPC_GPOFF, 0]))
        self.assertEqual(parse_LNCV_message(buf), None)  # Length incorrect for LNCV message
        buf = bytearray(b'\0' * 15)
        self.assertEqual(parse_LNCV_message(buf), None)  # Length correct for LNCV message, opcode not
        buf = write_module_LNCV(10001, 0, 2)
        self.assertIsInstance(parse_LNCV_message(buf), dict)
        self.assertIsNotNone(parse_LNCV_message(buf).keys())
        info = list(parse_LNCV_message(buf).keys())
        info.sort()
        expected_keys = ['OPC', 'len', 'SRC', 'DSTL', 'DSTH', 'ReqId', 'PXCT1',
                         'deviceClass', 'lncvNumber', 'lncvValue', 'flags', 'checksum']
        expected_keys.sort()
        self.assertListEqual(info, expected_keys)
        self.assertEqual(parse_LNCV_message(buf)['deviceClass'], 10001)

    # noinspection PyTypeChecker
    def test_format_LNCV_message(self):
        msg = write_module_LNCV(10001, 0, 2)
        info = format_loconet_message(msg)
        expected_hex = "ED 0F 01 05 00 20 00 11 27 00 00 02 00 00 0D"
        self.assertEqual(expected_hex, info[0])
        expected_info = "OPC: 237, SRC: 1, DSTL: 5, DSTH: 0, ReqId: 32, deviceClass: 10001, lncvNumber: 0, " \
                        "lncvValue: 2, flags: 0"
        self.assertEqual(len(expected_info), len(info[1]))  # Can't easily check the contents of the string as it
        # depends the (random) order of the keys in the dictionary

        msg = LocoNet.OPC_GPOFF
        info = format_loconet_message([msg, 0x00])
        expected_hex = "82 00"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Power off"
        self.assertEqual(expected_info, info[1])

        msg = LocoNet.OPC_GPON
        info = format_loconet_message([msg, 0x00])
        expected_hex = "83 00"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Power on"
        self.assertEqual(expected_info, info[1])

        msg = LocoNet.OPC_INPUT_REP
        info = format_loconet_message([msg, 0x2A, 0x60, 0x07])
        expected_hex = "B2 2A 60 07"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Sensor 86: 0"
        self.assertEqual(expected_info, info[1])

        msg = LocoNet.OPC_INPUT_REP
        info = format_loconet_message([msg, 0x28, 0x60, 0x05])
        expected_hex = "B2 28 60 05"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Sensor 82: 0"
        self.assertEqual(expected_info, info[1])

        msg = LocoNet.OPC_INPUT_REP
        info = format_loconet_message([msg, 0x25, 0x70, 0x18])
        expected_hex = "B2 25 70 18"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Sensor 76: 1"
        self.assertEqual(expected_info, info[1])

        msg = LocoNet.OPC_INPUT_REP
        info = format_loconet_message([msg, 0x03, 0x44, 0x0A])
        expected_hex = "B2 03 44 0A"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Sensor 1031: 0"
        self.assertEqual(expected_info, info[1])

        msg = LocoNet.OPC_SW_REQ
        info = format_loconet_message([msg, 0x1e, 0x10, 0x41])
        expected_hex = "B0 1E 10 41"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Switch req 31: 0 - 1"
        self.assertEqual(expected_info, info[1])

    def test_switch_message(self):
        msg = switch(31, False, True)
        expected_msg = [LocoNet.OPC_SW_REQ, 0x1e, 0x10, 0x41]
        self.assertEqual(expected_msg, [int(b) for b in msg.msg]) 
		
        msg = switch(22, True, True)
        expected_msg = [LocoNet.OPC_SW_REQ, 0x15, 0x30, 0x6a]
        self.assertEqual(expected_msg, [int(b) for b in msg.msg]) 

        msg = switch(22, False, True)
        expected_msg = [LocoNet.OPC_SW_REQ, 0x15, 0x10, 0x4a]
        self.assertEqual(expected_msg, [int(b) for b in msg.msg]) 
		
        msg = switch(2, False, True)
        expected_msg = [LocoNet.OPC_SW_REQ, 0x01, 0x10, 0x5e]
        self.assertEqual(expected_msg, [int(b) for b in msg.msg]) 
		


if __name__ == '__main__':
    logger = logging.getLogger('decconf')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger = logging.getLogger('decconf.testLNCV')
    logger.info('Test LNCV version 1.0.')

    unittest.main()
