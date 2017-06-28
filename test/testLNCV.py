#!/usr/bin/env python3
import logging
import unittest

from decconf.protocols.loconet import LNCVConfirmedMessage, LNCVWriteMessage, writeModuleLNCV, \
    startModuleLNCVProgramming, stopModuleLNCVProgramming, checksum_loconet_buffer, \
    format_loconet_message, LocoNet


class TestLNCV(unittest.TestCase):
    def setUp(self):
        self.okCalled = False

    # noinspection PyUnusedLocal
    def messageConfirmed(self, msg, reply):
        self.okCalled = True

    def testConfirmedMessage(self):
        msg = writeModuleLNCV(10001, 0, 2)
        reply = bytes.fromhex('ed2634df')
        mask = bytes.fromhex('ffffff00')

        cmsg = LNCVConfirmedMessage(msg, reply, mask, self)
        self.assertFalse(cmsg.match(bytes.fromhex('ed2734ff')))
        self.assertFalse(self.okCalled)
        self.assertTrue(cmsg.match(bytes.fromhex('ed2634ff')))
        self.assertTrue(self.okCalled)

    def testWriteCV(self):
        msg = writeModuleLNCV(10001, 0, 2)
        cmsg = LNCVWriteMessage(msg, self)
        self.assertFalse(cmsg.match(bytes.fromhex('ed2734ff')))
        self.assertFalse(self.okCalled)
        self.assertTrue(cmsg.match(bytes.fromhex('b46d34ff')))
        self.assertTrue(self.okCalled)

    def testStartModuleLNCVProgramming(self):
        self.assertEqual(bytes.fromhex('ED0F0105002150112700007F000021'), startModuleLNCVProgramming(10001, 255))

    def testStopModuleLNCVProgramming(self):
        self.assertEqual(bytes.fromhex('ED0F0105002110112700007F004021'), stopModuleLNCVProgramming(10001, 255))

    def testMakeLNCVMessage(self):
        buf = bytearray.fromhex('e50f05494b1f8011270402650002DA')
        self.assertEqual(buf, checksum_loconet_buffer(buf))

    # noinspection PyTypeChecker
    def test_format_LNCV_message(self):
        msg = writeModuleLNCV(10001, 0, 2)
        info = format_loconet_message(msg)
        expected_hex = "ED 0F 01 05 00 20 00 11 27 00 00 02 00 00 0D"
        self.assertEqual(expected_hex, info[0])
        expected_info = "OPC: 237, SRC: 1, DSTL: 5, DSTH: 0, ReqId: 32, deviceClass: 10001, lncvNumber: 0, " \
                        "lncvValue: 2, flags: 0"
        self.assertEqual(expected_info, info[1])

        msg = LocoNet.OPC_GPOFF
        info = format_loconet_message([msg, 0x00])
        expected_hex = "82 00"
        self.assertEqual(expected_hex, info[0])
        expected_info = "Power off"
        self.assertEqual(expected_info, info[1])


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
