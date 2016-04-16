#!/usr/bin/env python3

import argparse
import logging
import queue
from time import sleep

from locobuffer import LocoBuffer
from dummy_serial import dummySerial
from loconet import *

class CSVWriter(object):
	def __init__(self, fid, ncv):
		super(CSVWriter, self).__init__();
		self.ncv = ncv;
		self.fid = fid;
		
		
	def messageConfirmed(self, msg, reply):
		lncv = parseLNCVmsg(bytearray(reply));
		print("{}, {}".format(lncv['lncvNumber'], lncv['lncvValue']), file=self.fid);
		self.ncv -=1;

class CSVReader(object):
	def __init__(self, fid, ncv):
		super(CSVReader, self).__init__();
		self.ncv = 0;
		self.fid = fid;
		
		
	def messageConfirmed(self, msg, reply):
		#lncv = parseLNCVmsg(bytearray(reply));
		#print("{}, {}".format(lncv['lncvNumber'], lncv['lncvValue']), file=self.fid);
		self.ncv += 1;
		
def main():
	"""docstring for main"""
	parser = argparse.ArgumentParser(description='Bulk read/write LNCVs')
	parser.add_argument('command', choices=['read', 'write'], metavar='command', type=str, nargs=1,
	                   help='read or write')
	parser.add_argument('--moduleclass',  type=int, nargs=1, required=True, help='Article number');
	parser.add_argument('--address',  type=int, nargs=1, required=True, help='Module address');
	parser.add_argument('--cs', type=str, nargs=1, required=True, help='Dummy, or port name of serial port for locobuffer')
	parser.add_argument('filename', type=str, nargs = 1, help='CSV file to write to/read from')
	args = parser.parse_args();
	
	logger = logging.getLogger('decconf');
	logger.setLevel(logging.DEBUG)
	
	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	# create formatter
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# add formatter to ch
	ch.setFormatter(formatter)

	# add ch to logger
	logger.addHandler(ch)
	
	logger = logging.getLogger('decconf.bulkLNCVAccess');
	logger.info('Bulk LNCV Access version 1.0.');
	logger.debug('Config: {}'.format(args));
	fid = None;
	if args.command[0] == 'read':
		fid = open(args.filename[0], 'w');
	else:
		fid = open(args.filename[0], 'r');

	nCV = 100;
	lb = None;
	writer = CSVWriter(fid, nCV - 1);
	reader = CSVReader(fid, nCV - 1);
	recvQueue = queue.Queue();
	sendQueue = queue.Queue();
	serial = None
	if args.cs[0] == 'Dummy':
		logger.info("Connecting to {} serial device".format("Dummy"))
		serial = dummySerial();

	lb = LocoBuffer(serial, sendQueue, recvQueue);
	
	lb.write(startModuleLNCVProgramming(args.moduleclass[0], args.address[0]));

	if args.command[0] == 'read':
		
		for cv in range(1,nCV):
			lb.addToQueue(LNCVReadMessage(readModuleLNCV(args.moduleclass[0], args.address[0], cv), writer))
		while writer.ncv > 0:
			pass
		
	if args.command[0] == 'write':
		ncv = 0;
		for line in fid:
			vals = line.split(',');
			lb.addToQueue(LNCVWriteMessage(writeModuleLNCV(args.moduleclass[0], args.address[0], int(vals[0]), int(vals[1])), reader))
			ncv += 1;
		while reader.ncv < ncv:
			pass

	lb.write(stopModuleLNCVProgramming(args.moduleclass[0], args.address[0]));

	sleep(1)
	fid.close();
	
if __name__ == '__main__':
	main()