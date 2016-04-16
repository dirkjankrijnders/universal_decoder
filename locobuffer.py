import threading
import collections

from loconet import recvLnMsg, checksumLnBuf

class LocoBuffer(object):
	def __init__(self, serial, inputQueue, outputQueue):
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
		print(self.mq)
		if len(self.mq) == 1:
			self.iq.put(self.mq[0].msg);
	
	def read(self):
		buf = b"";
		while self.running:
			buf += self.serial.read(1);

			if recvLnMsg(buf):
				print("Recv LN Msg: 0x", " ".join("{:02x}".format(b) for b in buf));
				if (len(self.mq) > 0):
					print(self.mq)
				if (len(self.mq) > 0) and self.mq[0].match(buf):
					self.mq.popleft();
					print(self.mq)
					if (len(self.mq) > 0):
						self.iq.put(self.mq[0].msg);

				else:
					self.oq.put(bytearray(buf));
				buf = b"";
			
	def write(self, buf):
		#self.iq.push(buf);
		buf = bytes(buf)
		buf = checksumLnBuf(buf);
		print("Push to send Queue: ", buf)
		self.iq.put(buf)
		
	def writet(self):
		while self.running:
			buf = self.iq.get();
			print("Sending to serial: ", buf)
			self.serial.write(buf);
			self.iq.task_done();