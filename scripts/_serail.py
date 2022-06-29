# -*- coding: UTF-8 -*-
import serial
import serial.tools.list_ports
import time


class _Serail(object):
    def __init__(self):
        self.ser = None

    def _get_port_list(self):
        port_list = list(serial.tools.list_ports.comports())
        return port_list

    def _open_serial_port(self, port, baud):
        try:
            self.ser = serial.Serial(port, baud, timeout=0.3, interCharTimeout = 0.05)
        except Exception as e:
            self.ser =None
            raise Exception(e)

    def _close_serial_port(self):
        if self.ser == None:
            raise Exception('no selected serial')
        try:
            self.ser.close()
            self.ser = None
        except Exception as e:
            raise Exception(e)

    def _write(self, cmd):
        if self.ser == None:
            raise Exception('no selected serial')
        try:
            self.ser.write(cmd)
            self.ser.flush()
        except Exception as e:
            raise Exception(e)

    def _read(self):
        if self.ser == None:
            raise Exception('no selected serial')
        try:
            time.sleep(0.1)
            return self.ser.read(self.ser.in_waiting)
        except Exception as e:
            raise Exception(e)

    def _is_active(self):
        return self.ser
