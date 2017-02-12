import logging
import threading
import collections
from queue import Queue

from decconf.protocols.loconet import recvLnMsg, checksumLnBuf, LNMessage

class LocoBuffer(object):
	IDLE = 0;
	WAITING = 1;
	
	def __init__(self, serial, inputQueue, outputQueue):
		self.logger = logging.getLogger('decconf.LocoBuffer')
		self.serial = serial;
		self.iq = inputQueue;
		self.oq = outputQueue;
		self.mq = Queue(); #collections.deque();
		self.running = True;
		self.lastsend = b'';
		
		self.reader = threading.Thread(None, self.read);
		self.reader.daemon = True
		self.reader.start();

		self.writer = threading.Thread(None, self.writet);
		self.writer.daemon = True
		self.writer.start();
		
		self.expectCondition = threading.Condition();
		self.expectMessage = None;
		
	def addToQueue(self, msg):
		self.mq.put(msg);
		#if len(self.mq) == 1:
		#	self.iq.put(self.mq[0].msg);
	
	def read(self):
		buf = b""
		while self.running:
			buf += self.serial.read(1);
			if recvLnMsg(buf):
				if buf == self.lastsend:
					pass
				else:
					self.logger.debug("Recv LN Msg: 0x {}".format( " ".join("{:02x}".format(b) for b in buf)));
					#if not self.mq.empty() and self.mq[0].match(buf): # We have a expected reply, pop the message
					if self.expectMessage is not None and self.expectMessage.match(buf):
						self.expectCondition.acquire();
						self.expectCondition.notify_all();
						self.logger.debug("Matched! Match queue: {}".format(self.mq))
						self.expectCondition.release();	
					else: # Not a matched msg, so put it on the incoming queue for someone else to deal with it.
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
		self.mq.put(LNMessage(buf));
		
	def writet(self):
		while self.running:
			msg = self.mq.get();
			self.logger.debug("Sending to serial: 0x {}".format( " ".join("{:02x}".format(b) for b in msg.msg)))
			self.serial.write(msg.msg);
			self.lastsend = msg.msg;
			if msg.expectReply:
				self.expectCondition.acquire();
				self.expectMessage = msg;
				if not self.expectCondition.wait(1): # Got a time-out, put the message back on the queue
					self.mq.put(msg);
				self.expectCondition.release();
			#self.iq.task_done();