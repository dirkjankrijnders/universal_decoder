import copy
import logging
import os
import queue

import numpy as np

from decconf.protocols.loconet import start_module_LNCV_programming, stop_module_LNCV_programming, \
    checksum_loconet_buffer, parse_LNCV_message, make_LNCV_response
from decconf.protocols.loconet import LocoNet as LN


class DummySerial(object):
    def __init__(self):
        self.stream = queue.Queue()
        self.port = ''
        self.clients = []
        self.logger = logging.getLogger('decconf.dummySerial')
        self.clients.append(DummyDecoder(cvfile='dummydecoder1.npz'))
        self.clients.append(DummyDecoder(cvfile='dummydecoder2.npz'))

    def open(self):
        pass

    def close(self):
        pass

    def read(self, n):
        return self.stream.get()

    def write(self, buf):
        self.stream.put(bytes(buf))
        for c in self.clients:
            resp = c.check_msg(buf)
            if resp is not None:
                self.logger.debug('DS Sending: {}'.format(" ".join("{:02x}".format(b) for b in resp)))
                for b in resp:
                    self.stream.put(bytes([b]))


class DummyDecoder(object):
    def __init__(self, cvfile):
        super(DummyDecoder, self).__init__()
        self.programmingMode = False
        self.logger = logging.getLogger('decconf.dummyDecoder')

        self.CVs = np.zeros((1100,), dtype=int)
        self.cvfile = cvfile

        if os.path.exists(self.cvfile):
            # with open(self.cvfile, 'rb') as fid:
            with np.load(self.cvfile) as data:
                self.CVs = data['CVs']
        else:
            self.logger.info('Created empty dummy decoder')

        self.CVs[1018] = 19.75*16
        self.CVs[1019] = 0x1f1f
        self.CVs[1020] = 0x2f2f
        self.CVs[1021] = 0x3f3f
        self.CVs[1022] = 0x4f4f
        self.CVs[1023] = '010301'

        self.logger.info('Created dummy decoder with address {}'.format(str(self.CVs[1])))

    def check_msg(self, buf):
        resp = None
        self.logger.debug('Checking message against dummy decoder with address {}'.format(str(self.CVs[1])))
        if buf == make_LNCV_response(0xFFFF, 0, 0xFFFF, 0, opc=LN.OPC_IMM_PACKET, src=LN.LNCV_SRC_KPU,
                                     req=LN.LNCV_REQID_CFGREQUEST):
            resp = make_LNCV_response(10001, 0, self.CVs[1], 0x00,
                                      src=LN.LNCV_SRC_MODULE)
            return resp

        elif buf == checksum_loconet_buffer(start_module_LNCV_programming(10001, self.CVs[1])):
            self.logger.info("Decoder programming start, decoder address {}".format(self.CVs[1]))
            self.programmingMode = True
            resp = make_LNCV_response(10001, 0, self.CVs[1], 0x80, src=LN.LNCV_SRC_MODULE)
            return resp

        if buf == checksum_loconet_buffer(stop_module_LNCV_programming(10001, self.CVs[1])):
            self.logger.info("Decoder programming stop, decoder address {}".format(self.CVs[1]))
            self.programmingMode = False
            np.savez(self.cvfile, CVs=self.CVs)
            return resp

        lncv_msg = parse_LNCV_message(copy.deepcopy(buf))
        if lncv_msg is None:
            return None
        if self.programmingMode is not True:
            return None
        if lncv_msg['deviceClass'] != 10001:
            return None

        if lncv_msg is not None:
            if lncv_msg['ReqId'] == LN.LNCV_REQID_CFGREQUEST and lncv_msg['flags'] == 0:
                cv = lncv_msg['lncvNumber']
                self.logger.info("Reading CV {}".format(cv))
                resp = make_LNCV_response(10001, cv, self.CVs[cv], 0x00, src=LN.LNCV_SRC_MODULE)

        if lncv_msg is not None:
            if lncv_msg['ReqId'] == LN.LNCV_REQID_CFGWRITE:
                self.logger.info("Setting CV {} to {}".format(lncv_msg['lncvNumber'], lncv_msg['lncvValue']))
                self.CVs[lncv_msg['lncvNumber']] = lncv_msg['lncvValue']
                resp = bytearray.fromhex('b4ff7f00')
                resp[1] = lncv_msg['OPC'] & 0x7f
                resp = checksum_loconet_buffer(resp)

        return resp
