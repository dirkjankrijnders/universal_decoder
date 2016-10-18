#!/usr/bin/env python3
import logging
import unittest
from decconf.protocols.loconet import LNCVConfirmedMessage, LNCVWriteMessage, writeModuleLNCV, readModuleLNCV, startModuleLNCVProgramming, stopModuleLNCVProgramming, makeLNCVresponse, checksumLnBuf

class TestLNCV(unittest.TestCase):
	def setUp(self):
		self.okCalled = False
	
	def messageConfirmed(self, msg,reply):
		self.okCalled = True;
		
	def testConfirmedMessage(self):
		msg = writeModuleLNCV(10001, 127, 0 , 2);
		reply = bytes.fromhex('ed2634df');
		mask = bytes.fromhex('ffffff00');
		
		cmsg = LNCVConfirmedMessage(msg, reply, mask, self);
		self.assertFalse(cmsg.match(bytes.fromhex('ed2734ff')));
		self.assertFalse(self.okCalled);
		self.assertTrue(cmsg.match(bytes.fromhex('ed2634ff')));
		self.assertTrue(self.okCalled);
		
	def testWriteCV(self):
		msg = writeModuleLNCV(10001, 127, 0 , 2);
		cmsg = LNCVWriteMessage(msg, self);
		self.assertFalse(cmsg.match(bytes.fromhex('ed2734ff')));
		self.assertFalse(self.okCalled);
		self.assertTrue(cmsg.match(bytes.fromhex('b46d34ff')));
		self.assertTrue(self.okCalled);
	
	def testStartModuleLNCVProgramming(self):
		self.assertEqual(bytes.fromhex('ED0F0105002150112700007F000021'), startModuleLNCVProgramming(10001, 255));

	def testStopModuleLNCVProgramming(self):
		self.assertEqual(bytes.fromhex('ED0F0105002110112700007F004021'), stopModuleLNCVProgramming(10001, 255));
	
	def testMakeLNCVMessage(self):
		buf = bytearray.fromhex('e50f05494b1f8011270402650002DA');
		self.assertEqual(buf, checksumLnBuf(buf))
		#self.assertEqual(bytes.fromhex('e50f05494b1f8011270402650002DA'), makeLNCVresponse(10001,0x0204,101,0x02))
		#msg = readModuleLNCV(10001, 127, 1);
		#reply = bytes.fromhex('ED 0F 01 05 00 21 10 11 27 01 00 7F 00 00 60');
		#mask  = bytes.fromhex('')
	
if __name__ == '__main__':
	logger = logging.getLogger('decconf');
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
	
	logger = logging.getLogger('decconf.testLNCV');
	logger.info('Test LNCV version 1.0.');
	
	unittest.main()
	