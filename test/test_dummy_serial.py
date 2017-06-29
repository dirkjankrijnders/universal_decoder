import unittest
from decconf.interfaces.dummy_serial import DummyDecoder
from decconf.protocols.loconet import checksum_loconet_buffer, start_module_LNCV_programming, \
    stop_module_LNCV_programming, make_LNCV_response, read_module_LNCV, write_module_LNCV, parse_LNCV_message, \
    compute_PXCT_from_bytes
from decconf.protocols.loconet import LocoNet as Ln


class TestDummySerial(unittest.TestCase):
    def test_dummy_decoder_start_stop(self):
        address = 50
        decoder = DummyDecoder('')
        self.assertEqual(decoder.CVs[1], 0)
        self.assertEqual(decoder.programmingMode, False)
        decoder.CVs[1] = address
        self.assertEqual(decoder.CVs[1], address)

        buf = checksum_loconet_buffer(start_module_LNCV_programming(10001, address))
        expected_response = make_LNCV_response(10001, 0, address, 0x80, src=Ln.LNCV_SRC_MODULE)
        self.assertEqual(decoder.checkMsg(buf), expected_response)
        self.assertEqual(decoder.programmingMode, True)

        buf = checksum_loconet_buffer(start_module_LNCV_programming(10001, address - 1))
        self.assertIsNone(decoder.checkMsg(buf))
        self.assertEqual(decoder.programmingMode, True)

        buf = checksum_loconet_buffer(stop_module_LNCV_programming(10001, address - 1))
        self.assertIsNone(decoder.checkMsg(buf))
        self.assertEqual(decoder.programmingMode, True)

        buf = checksum_loconet_buffer(stop_module_LNCV_programming(10001, address))
        self.assertIsNone(decoder.checkMsg(buf))
        self.assertEqual(decoder.programmingMode, False)

    def test_dummy_decoder_read_write(self):
        address = 50
        decoder = DummyDecoder('')
        self.assertEqual(decoder.CVs[1], 0)
        self.assertEqual(decoder.programmingMode, False)
        decoder.CVs[1] = address
        self.assertEqual(decoder.CVs[1], address)

        buf = checksum_loconet_buffer(start_module_LNCV_programming(10001, address))
        decoder.checkMsg(buf)
        self.assertEqual(decoder.programmingMode, True)

        buf = checksum_loconet_buffer(read_module_LNCV(10001, 1))
        reply = decoder.checkMsg(buf)
        expected_reply = make_LNCV_response(10001, 1, 50, 0x00, src=Ln.LNCV_SRC_MODULE)
        self.assertEqual(reply, expected_reply)
        msg = parse_LNCV_message(reply)
        self.assertEqual(msg['lncvValue'], 50)

        buf = checksum_loconet_buffer(write_module_LNCV(10001, 1, 51))
        reply = decoder.checkMsg(buf)
        expected_reply = checksum_loconet_buffer(bytearray.fromhex("b46d7f00"))
        self.assertEqual(reply, expected_reply)
        self.assertEqual(decoder.CVs[1], 51)


    def test_dummy_decoder_discover(self):
        address = 50
        decoder = DummyDecoder('')
        decoder.CVs[1] = address

        buf = make_LNCV_response(0xFFFF, 0, 0xFFFF, 0, opc=Ln.OPC_IMM_PACKET, src=Ln.LNCV_SRC_KPU,
                                 req=Ln.LNCV_REQID_CFGREQUEST)
        reply = decoder.checkMsg(buf)
        expected_reply = checksum_loconet_buffer(
            compute_PXCT_from_bytes(bytearray.fromhex("E50F0505001f00112700003200000D")))
        self.assertEqual(reply, expected_reply)


if __name__ == '__main__':
    unittest.main()
