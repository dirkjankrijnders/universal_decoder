import logging
import threading
from queue import Queue

from decconf.protocols.loconet import recieve_loconet_bytes, LNMessage


class LocoBuffer(object):
    IDLE = 0
    WAITING = 1

    def __init__(self, serial, input_queue, output_queue):
        self.logger = logging.getLogger('decconf.LocoBuffer')
        self.serial = serial
        self.iq = input_queue
        self.oq = output_queue
        self.mq = Queue()  # collections.deque()
        self.running = True
        self.last_send = b''

        self.reader = threading.Thread(None, self.read)
        self.reader.daemon = True
        self.reader.start()

        self.writer = threading.Thread(None, self.write_thread)
        self.writer.daemon = True
        self.writer.start()

        self.expectCondition = threading.Condition()
        self.expectMessage = None

    def add_to_queue(self, msg):
        self.mq.put(msg)

    def read(self):
        buf = b""
        while self.running:
            buf += self.serial.read(1)
            if recieve_loconet_bytes(buf):
                if buf == self.last_send:
                    pass
                else:
                    self.logger.debug("Received LN Msg: 0x {}".format(" ".join("{:02x}".format(b) for b in buf)))
                    # if not self.mq.empty() and self.mq[0].match(buf): # We have a expected reply, pop the message
                    if self.expectMessage is not None and self.expectMessage.match(buf):
                        self.expectCondition.acquire()
                        self.expectCondition.notify_all()
                        self.logger.debug("Matched! Match queue: {}".format(self.mq))
                        self.expectCondition.release()
                    else:  # Not a matched msg, so put it on the incoming queue for someone else to deal with it.
                        self.oq.put(bytearray(buf))
                buf = b""

    def write(self, buf):
        # self.iq.push(buf)
        # buf = bytearray(buf)
        # buf = checksum_loconet_buffer(buf)
        if recieve_loconet_bytes(buf) is None:
            self.logger.warning("Tried to send invalid packet: 0x {}".format(" ".join("{:02x}".format(b) for b in buf)))
            return
        self.logger.debug("Push to send Queue: 0x {}".format(" ".join("{:02x}".format(b) for b in buf)))
        self.mq.put(LNMessage(buf))

    def write_thread(self):
        while self.running:
            msg = self.mq.get()
            self.logger.debug("Sending to serial: 0x {}".format(" ".join("{:02x}".format(b) for b in msg.msg)))
            self.serial.write(msg.msg)
            self.last_send = msg.msg
            if msg.expectReply:
                self.expectCondition.acquire()
                self.expectMessage = msg
                if not self.expectCondition.wait(1):  # Got a time-out, put the message back on the queue
                    self.mq.put(msg)
                self.expectCondition.release()
                # self.iq.task_done()
