import copy
import logging
import os
import queue

import numpy as np

from decconf.protocols.loconet import startModuleLNCVProgramming, stopModuleLNCVProgramming, readModuleLNCV, writeModuleLNCV, checksumLnBuf, LNCVReadMessage, parseLNCVmsg, LNCVWriteMessage, makeLNCVresponse
from decconf.protocols.loconet import LocoNet as LN

class dummySerial(object):
	def __init__(self):
		self.stream = queue.Queue();
		self.port = ''
		self.clients = [];
		self.logger = logging.getLogger('decconf.dummySerial');
		self.clients.append(dummyDecoder(cvfile = 'dummydecoder1.npz'))
		self.clients.append(dummyDecoder(cvfile = 'dummydecoder2.npz'))
		
	def open(self):
		pass
	
	def close(self):
		pass
		
	def read(self, n):
		return self.stream.get();
	
	def write(self, buf):
		self.stream.put(bytes(buf));
		for c in self.clients:
			resp = c.checkMsg(buf);
			if resp is not None:
				self.logger.debug('DS Sending: {}'.format( " ".join("{:02x}".format(b) for b in resp)));
				for b in resp:
					self.stream.put(bytes([b]));

class dummyDecoder(object):
	def __init__(self, cvfile):
		super(dummyDecoder, self).__init__()
		self.programmingMode = False
		
		self.CVs = np.zeros((1100,), dtype=int);
		self.cvfile = cvfile
		
		if os.path.exists(self.cvfile):
			#with open(self.cvfile, 'rb') as fid:
			with np.load(self.cvfile) as data:
				self.CVs = data['CVs'];
		self.logger = logging.getLogger('decconf.dummyDecoder');
		
		self.logger.info('Created dummy decoder with address {}'.format(str(self.CVs[1])))
		
	def checkMsg(self, buf):
		resp = None;
		self.logger.debug('Checking message against dummy decoder with address {}'.format(str(self.CVs[1])))
		#print(buf)
		if buf == makeLNCVresponse(0xFFFF,0,0xFFFF, 0, opc = LN.OPC_IMM_PACKET, src = LN.LNCV_SRC_KPU, req = LN.LNCV_REQID_CFGREQUEST):
			
			resp = makeLNCVresponse(10001, 0, self.CVs[1], 0x00, src = LN.LNCV_SRC_MODULE); #bytes.fromhex("E50F05494B1F037F7F00007F000071")

		elif buf == checksumLnBuf(startModuleLNCVProgramming(10001, self.CVs[1])):
			self.logger.info("Decoder programming start, decoder address {}".format(self.CVs[1]));
			self.programmingMode = True;
			resp = makeLNCVresponse(10001, 0, self.CVs[1], 0x80, src = LN.LNCV_SRC_MODULE);

		if buf == checksumLnBuf(stopModuleLNCVProgramming(10001, self.CVs[1])):
			self.logger.info("Decoder programming stop, decoder address {}".format(self.CVs[1]));
			self.programmingMode = False;
			np.savez(self.cvfile, CVs=self.CVs);
			
			#resp = makeLNCVresponse(10001, 0, 121, 0x80, src = LN.LNCV_SRC_MODULE);
		lncvMsg = parseLNCVmsg(copy.deepcopy(buf));
		if resp is None:
			if lncvMsg is None:
				return None
			if self.programmingMode != True:
				return None
			if lncvMsg['deviceClass'] != 10001:
				return None
		else:
			return resp

		if lncvMsg is not None:
			if lncvMsg['ReqId'] == LN.LNCV_REQID_CFGREQUEST:
				cv = lncvMsg['lncvNumber'];
				self.logger.info("Reading CV {}".format(cv));
				resp = makeLNCVresponse(10001, cv, self.CVs[cv], 0x00, src = LN.LNCV_SRC_MODULE);
				
		"""if buf == (readModuleLNCV(10001, self.CVs[1], 1)):
				
		if buf == (readModuleLNCV(10001, self.CVs[1], 6)):
			resp = makeLNCVresponse(10001, 6, self.CVs[6], 0x00, src = LN.LNCV_SRC_MODULE);

		if buf == (readModuleLNCV(10001, self.CVs[1], 7)):
			resp = makeLNCVresponse(10001, 7, self.CVs[7], 0x00, src = LN.LNCV_SRC_MODULE);
		"""	
		if lncvMsg is not None:
			if lncvMsg['ReqId'] == LN.LNCV_REQID_CFGWRITE:
				self.logger.info("Setting CV {} to {}".format(lncvMsg['lncvNumber'], lncvMsg['lncvValue']))
				self.CVs[lncvMsg['lncvNumber']] = lncvMsg['lncvValue'];
				resp  = bytearray.fromhex('b4ff7f00');
				returnCode = LN.LNCV_LACK_OK
				resp[1] = lncvMsg['OPC'] & 0x7f
				resp = checksumLnBuf(resp);
				
		return resp;