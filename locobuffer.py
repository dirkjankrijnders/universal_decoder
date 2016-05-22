import logging
import threading
import collections

from loconet import recvLnMsg, checksumLnBuf

class LocoBuffer(object):
	def __init__(self, serial, inputQueue, outputQueue):
		self.logger = logging.getLogger('decconf.LocoBuffer')
		self.serial = serial;
		self.iq = inputQueue;
		self.oq = outputQueue;
		self.mq = collections.deque();
		self.running = True;
			
		self.reader = threading.Thread(None, self.read);
		self.reader.daemon = True
		self.reader.start();

		self.writer = threading.Thread(None, self.writet);
		self.writer.daemon = True
		self.writer.start();
		
		
	def addToQueue(self, msg):
		self.mq.append(msg);
		if len(self.mq) == 1:
			self.iq.put(self.mq[0].msg);
	
	def read(self):
		buf = b""
		while self.running:
			buf += self.serial.read(1);
			if recvLnMsg(buf):
				self.logger.debug("Recv LN Msg: 0x {}".format( " ".join("{:02x}".format(b) for b in buf)));
				if (len(self.mq) > 0):
					self.logger.debug("Match queue: {}".format(self.mq))
				if (len(self.mq) > 0) and self.mq[0].match(buf):
					self.mq.popleft();
					self.logger.debug("Match queue: {}".format(self.mq))
					if (len(self.mq) > 0):
						self.iq.put(self.mq[0].msg);

				else:
					self.oq.put(bytearray(buf));
				buf = b"";
			
	def write(self, buf):
		#self.iq.push(buf);
		#buf = bytearray(buf)
		#buf = checksumLnBuf(buf);
		if recvLnMsg(buf) is None:
			self.logger.warn("Tried to send invalid packet: 0x {}".format( " ".join("{:02x}".format(b) for b in buf)));
			return
		self.logger.debug("Push to send Queue: 0x {}".format( " ".join("{:02x}".format(b) for b in buf)))
		self.iq.put(buf)
		
	def writet(self):
		while self.running:
			buf = self.iq.get();
			self.logger.debug("Sending to serial: 0x {}".format( " ".join("{:02x}".format(b) for b in buf)))
			self.serial.write(buf);
			self.iq.task_done();