#!/usr/bin/env python3

import unittest

from decconf.protocols.loconet import *

class TestLocoNet(unittest.TestCase):
	def testRecvLnMsg(self):
		buf = bytes.fromhex('B0510F11');
		
		self.assertEqual(buf, recieve_loconet_bytes(buf))
	
	def testComputeBytesFromPXCT(self):
		buf = bytearray.fromhex('ED0F0105002150112700007F000021');
		buf_data = compute_bytes_from_PXCT(buf);
		self.assertEqual(buf_data[0:5], buf[0:5]);
		self.assertEqual(buf_data[-1], buf[-1]);
		self.assertEqual(buf_data[6], 0x00);
		self.assertEqual(buf_data[7:14], bytes.fromhex('11270000FF0080'));
		
	def testComputePXCTFromBytes(self):
		buf = bytearray.fromhex('ED0F010500210011270000FF008021');
		buf_data = compute_PXCT_from_bytes(buf);
		self.assertEqual(buf_data[0:5], buf[0:5]);
		self.assertEqual(buf_data[-1], buf[-1]);
		self.assertEqual(buf_data[6], 0x50);
		self.assertEqual(buf_data[7:14], bytes.fromhex('112700007F0000'));
		
	def testParseLNCVmsg(self):
		buf = bytearray.fromhex('ED0F0105002150112700007F000021');
		pkt = parse_LNCV_message(buf)
		self.assertNotEqual(pkt, None)
		self.assertEqual(pkt['deviceClass'], 10001)
		self.assertEqual(pkt['lncvValue'], 255)
	
	def testMakeLNCVresponse(self):
		buf = makeLNCVresponse(1,1,1,1);
		self.assertEqual(buf[0], LocoNet.OPC_PEER_XFER)
		buf = makeLNCVresponse(10001,1,255, 0, opc = LocoNet.OPC_IMM_PACKET, src = LocoNet.LNCV_SRC_KPU, req = LocoNet.LNCV_REQID_CFGREQUEST);
		#print("Recv LN Msg: 0x", " ".join("{:02x}".format(b) for b in buf));
		#print("Recv LN Msg: 0x", " ".join("{:02x}".format(b) for b in bytes.fromhex('ED0F0105002110112701007F000060')));
		self.assertEqual(buf, bytes.fromhex('ED0F0105002110112701007F000060'))
		
if __name__ == '__main__':
    unittest.main()
