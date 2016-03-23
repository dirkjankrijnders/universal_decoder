#!/usr/bin/env python3

import unittest
from loconet import LNCVConfirmedMessage, LNCVWriteMessage, writeModuleLNCV, readModuleLNCV

class TestLNCV(unittest.TestCase):
	def setUp(self):
		self.okCalled = False
	
	def messageConfirmed(self, msg):
		self.okCalled = True;
		
	def testConfirmedMessage(self):
		msg = writeModuleLNCV(10001, 127, 0 , 2);
		reply = bytes.fromhex('ed2634');
		mask = bytes.fromhex('ffff00');
		
		cmsg = LNCVConfirmedMessage(msg, reply, mask, self);
		self.assertFalse(cmsg.match(bytes.fromhex('ed2734')));
		self.assertFalse(self.okCalled);
		self.assertTrue(cmsg.match(bytes.fromhex('ed2634')));
		self.assertTrue(self.okCalled);
		
	def testWriteCV(self):
		msg = writeModuleLNCV(10001, 127, 0 , 2);
		cmsg = LNCVWriteMessage(msg, self);
		self.assertFalse(cmsg.match(bytes.fromhex('ed2734')));
		self.assertFalse(self.okCalled);
		self.assertTrue(cmsg.match(bytes.fromhex('7f6d34')));
		self.assertTrue(self.okCalled);
		
		#msg = readModuleLNCV(10001, 127, 1);
		#reply = bytes.fromhex('ED 0F 01 05 00 21 10 11 27 01 00 7F 00 00 60');
		#mask  = bytes.fromhex('')
	
if __name__ == '__main__':
	unittest.main()
	