import serial
from datetime import datetime
from os import path, mkdir, getpid
from utilities import convert_to_array
import numpy as np


class SerialPort:

    """"Serial port object that works with multiprocessing"""

    def __init__(self, port, foldername, filename="trial.txt",
                 baudrate=115200, buffersize=100, nchannels=3, delimiter=","):

        """
        :param port: string, The string referencing the serial port name as
        seen in the device manager or in the /dev/ directory of a linux filesystem.
        Is named starting with "COM" on windows and "usbtty" or "usbACM" on linux
        :param foldername: string, Folder to save the data captured from the serial port
        :param filename: string, filename to save the data in
        :param baudrate: int, baudrate of the serial communication device
        :param delimiter: string, Expected delimiter in serial data
        """
        self.port = port

        self.baudrate = baudrate
        self.buffersize = buffersize
        self.nchannels = nchannels

        self.serial_port = None

        self.foldername = foldername
        self.filename = path.join(self.foldername, filename)
        self.delimiter = delimiter

        self.running = False

        self.total_lines = 0

        self.data_buffer = np.zeros([self.buffersize, self.nchannels], dtype=float)

    def read_port(self) -> bytearray | None:
        """
        Read serial port and return the bytes object. If unable to return,
        return None
        :return: Bytes array or None
        """
        try:
            ln = self.serial_port.readline()
            return ln
        except serial.SerialException:
            self.running = False
            return None

    def close(self) -> None:
        """
        Wrapper function to close the serial port
        """
        self.serial_port.close()

    def isOpen(self) -> bool:
        """
        Wrapper to check if serial port is open
        :return: bool
        """
        if self.serial_port is not None:
            return self.serial_port.isOpen()
        else:
            return False

    def open_port(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=1)
        except serial.SerialException:
            print("Port %s not connected or busy" % self.port)
            print("Port %s was stopped in process %d" % (self.port, getpid()))
            raise serial.SerialException

    def fill_buffer(self):

        i = 0
        while i < self.buffersize:
            try:
                raw = self.read_port()
                ln = raw.decode('utf-8')
                data = convert_to_array(ln, self.delimiter)
                self.data_buffer[i] = data
                i += 1
            except ValueError:
                continue


if __name__ == "__main__":
    print("Object definition file for handling serial ports")
