from enum import Enum
from time import sleep
import serial
import threading
import time
import datetime
import os
import traceback
from uart_messsage_handler import UartMessageHandler
# Testing purposes only
# TODO: Remove import after testing
import argparse


class UartIOHandler:
    """ Sends messages through an UART port

        Messages are sent through the already opoened UART port that is
        stored in the object "ser".

        Attributes
        ----------
        _ser : Serial
            Object created with the help of the PySerial library. 
            Facilitates communication through the port that it manages.

    """

    def __init__(self, serial_port=None):
        self._ser = serial_port
        self._log = False

    """ Set the serial port for UART communication

        Parameters
        ----------
        serial_port : Serial
            Serial object with already opened port to communicate through
    """

    def set_serial_port(self, serial_port):
        self._ser = serial_port

    """ Sets the file to be used for log messages
        
        Parameters
        ----------
        log_file : file object
            Already opened log file for writing log messages.
    """

    def set_log_file(self, log_file):
        self._log = True
        self._log_file = log_file

    """ Writes message to UART port

        If a log file was set in this class, after writing message to
        UART it will also write the message to the log file.
        
        Parameters
        ----------
        message : str
            Message to write to UART port.
    """

    def write(self, message):
        try:
            self._ser.write(message.encode())
        except:
            print("UartWriter.write: serial write exception occured")
            traceback.print_exc()
        try:
            if (self._log):
                self._log_file.write("UartIOHandler.write: write message to UART: " + message)
                self._log_file.flush()
                os.fsync(self._log_file.fileno())
        except:
            print("UartWriter.write: file writing exception")
            traceback.print_exc()

    def read(self):
        message = None
        try:
            message = self._ser.read(8).decode()
            # print("message is : ", message)
        except:
            print("UartWriter.read: serial read exception")
            traceback.print_exc()
        try:
            if (self._log):
                self._log_file.write("UartIOHandler.read: read message from UART: " + message)
                self._log_file.flush()
                os.fsync(self._log_file.fileno())
        except:
            print("UartIOHandler.read: file write exception")
            traceback.print_exc()
        return message


delay = 0.001
n = 100

port0 = '/dev/ttyACM0'
port1 = '/dev/ttyACM1'
baud = 115200

def ser_read(ser, uart_msg_handler, log_file, uart_io_handler):
    """ Read 8 bytes at a time from the UART serial port in an infinite
        loop

        Parameters
        ----------
        ser : Serial
            Serial port to read from
        uart_msg : UartMessageHandler
            Stores message received through UART. Makes uart messages
            visible to other threads/functions
    """
    try:
        while True:
            reading = uart_writer.read()
            # print("reading = ", reading)
            # Store raw message in uart handling class
            uart_msg_handler.receive_msg(reading)
            write_string = "Received: " + uart_msg_handler.read_msg() + "\n"
            log_file.write(write_string)
            log_file.flush()
            os.fsync(log_file.fileno())
            print("Received: " + uart_msg_handler.read_msg())
    except:
        print("Read - Exception generated")
        traceback.print_exc()
    finally:
        print("Ended reading")


def ser_write(ser, uart_message_handler, count, log_file, uart_writer):
    """ Write 8 bytes at a time to the UART serial port in an infinite
        loop

        Parameters
        ----------
        ser : Serial
            Serial port to write to
        uart_message_handler : UartMessageHandler
            Not used for the moment. Can be used as a communication
            bridge to other threads.
    """
    test = "pi.><ras"
    test = "<M15S80>"

    while True:
        try:
            count += 1
            if count <= 10:
                ser.write("<CONACC>".encode())
                print("<CONNACC>")
            else:
                # Bug fix: count is now padded with zeros to form a number of at least two digits
                test = f"<M00S{count%100:02}>"
                uart_writer.write(test)
                write_string = "send; sleep = 0.1; " + \
                    test + " " + str(count) + "\n"
                print(write_string)
            time.sleep(0.05)
        except:
            print("Write - inner while error")
            log_file.write("write error")
            log_file.flush()
            os.fsync(log_file.fileno())


def open_log_file():
    global f
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d__%H:%M:%S")
    print(date)

    f = open("./logs/rpi_log_{}.txt".format(date), "w")


f = None
g = None
g = open("./logs/Dummy_file", "w")

# Open the serial port that connects to STM32. It may be connected on
# ACM0 or ACM1
try:
    ser = serial.Serial(port1, baud)
except:
    ser = serial.Serial(port0, baud)

open_log_file()

uart_message_handler = UartMessageHandler()
uart_writer = UartIOHandler(ser)
uart_writer.set_log_file(f)

# Start two other threads for reading and writing to UART
thread_read = threading.Thread(
    target=ser_read, args=(ser, uart_message_handler, f, uart_writer))
thread_write = threading.Thread(
    target=ser_write, args=(ser, uart_message_handler, 20, f, uart_writer))

thread_read.start()
thread_write.start()


# TODO: Detail the print statements below - useful for debugging

print("Working")
print("Sending and receiving messages at the following frequencies:")
print("TODO: Show frequency of tx and rx operations")

while True:
    pass

f.close()

# Close the serial port after using it
ser.close()
