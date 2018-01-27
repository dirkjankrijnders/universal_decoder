#!/usr/bin/env python3

import argparse
import queue
from time import sleep

from decconf.interfaces.locobuffer import LocoBuffer
from decconf.interfaces.dummy_serial import DummySerial
import serial.tools.list_ports

from decconf.protocols.loconet import *


class CSVWriter(object):
    def __init__(self, fid, ncv):
        super(CSVWriter, self).__init__()
        self.ncv = ncv
        self.fid = fid

    def message_confirmed(self, msg, reply):
        lncv = parse_LNCV_message(bytearray(reply))
        print("{}, {}".format(lncv['lncvNumber'], lncv['lncvValue']), file=self.fid)
        self.ncv -= 1


class CSVReader(object):
    def __init__(self, fid, ncv):
        super(CSVReader, self).__init__()
        self.ncv = 0
        self.fid = fid

    def message_confirmed(self, msg, reply):
        # lncv = parse_LNCV_message(bytearray(reply))
        # print("{}, {}".format(lncv['lncvNumber'], lncv['lncvValue']), file=self.fid)
        self.ncv += 1


class StatsPrinter(object):
    def __init__(self, fid, ncv):
        super(StatsPrinter, self).__init__()
        self.ncv = 0
        self.fid = fid

    def message_confirmed(self, msg, reply):
        lncv = parse_LNCV_message(bytearray(reply))
        print("{}, {}".format(lncv['lncvNumber'], lncv['lncvValue']))
        self.ncv -= 1


def main():
    """docstring for main"""
    parser = argparse.ArgumentParser(description='Bulk read/write LNCVs')
    parser.add_argument('command', choices=['read', 'write', 'stats'], metavar='command', type=str, nargs=1,
                        help='read or write')
    parser.add_argument('--moduleclass', type=int, nargs=1, required=True, help='Article number')
    parser.add_argument('--address', type=int, nargs=1, required=True, help='Module address')
    parser.add_argument('--cs', type=str, nargs=1, required=True,
                        help='Dummy, or port name of serial port for locobuffer')
    parser.add_argument('filename', type=str, nargs=1, help='CSV file to write to/read from')
    args = parser.parse_args()

    logger = logging.getLogger('decconf')
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

    logger = logging.getLogger('decconf.bulkLNCVAccess')
    logger.info('Bulk LNCV Access version 1.0.')
    logger.debug('Config: {}'.format(args))

    n_cv = 320

    reader = None
    writer = None
    printer = None

    if args.command[0] == 'write':
        fid = open(args.filename[0], 'r')
        reader = CSVReader(fid, n_cv - 1)
    elif args.command[0] == 'read':
        fid = open(args.filename[0], 'w')
        writer = CSVWriter(fid, n_cv - 1)
    else:
        fid = None
        printer = StatsPrinter(None, 0)

    recieve_queue = queue.Queue()
    send_queue = queue.Queue()
    _serial = serial.Serial(None, 57600)
    if args.cs[0] == 'Dummy':
        logger.info("Connecting to {} _serial device".format("Dummy"))
        _serial = DummySerial()
    else:
        _serial.port = args.cs[0]
        _serial.open()

    while not _serial.is_open:
        pass

    lb = LocoBuffer(_serial, send_queue, recieve_queue)

    # lb.add_to_queue(LNCVWriteMessage(start_module_LNCV_programming(args.moduleclass[0], args.address[0]), reader))
    lb.write(start_module_LNCV_programming(args.moduleclass[0], args.address[0]))
    # lb.add_to_queue(LNCVWriteMessage(start_module_LNCV_programming(args.moduleclass[0], args.address[0]), reader))
    # lb.add_to_queue(LNCVWriteMessage(start_module_LNCV_programming(args.moduleclass[0], args.address[0]), reader))
    sleep(1)
    lb.write(start_module_LNCV_programming(args.moduleclass[0], args.address[0]))
    sleep(1)
    lb.write(start_module_LNCV_programming(args.moduleclass[0], args.address[0]))
    sleep(1)
    lb.write(start_module_LNCV_programming(args.moduleclass[0], args.address[0]))

    try:
        if args.command[0] == 'read':

            for cv in range(1, n_cv):
                lb.add_to_queue(LNCVReadMessage(read_module_LNCV(args.moduleclass[0], cv), writer))
            while writer.ncv > 0:
                pass

        if args.command[0] == 'write':
            ncv = 0
            for line in fid:
                vals = line.split(',')
                if vals[1] == '':
                    vals[1] = 0
                lb.add_to_queue(
                    LNCVWriteMessage(write_module_LNCV(args.moduleclass[0], int(vals[0]), int(vals[1])),
                                     reader))
                ncv += 1
            while reader.ncv < ncv:
                pass

        if args.command[0] == 'stats':
            printer.ncv = 9
            for cv in range(1024, 1033):
                lb.add_to_queue(LNCVReadMessage(read_module_LNCV(args.moduleclass[0], cv), printer))
            while printer.ncv > 0:
                pass
    except KeyboardInterrupt:
        pass

    lb.write(stop_module_LNCV_programming(args.moduleclass[0], args.address[0]))
    sleep(1)
    lb.write(stop_module_LNCV_programming(args.moduleclass[0], args.address[0]))

    sleep(1)
    if fid is not None:
        fid.close()


if __name__ == '__main__':
    main()
