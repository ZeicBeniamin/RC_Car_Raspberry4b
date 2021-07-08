from enum import Enum
from time import sleep
import serial
import threading
import time
import datetime
import traceback
from uart_utils import *

delay = 0.001
n = 100

port0 = '/dev/ttyACM0'
port1 = '/dev/ttyACM1'
baud = 115200


def ser_read(ser, uart_msg_handler, uart_io_handler):
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
            reading = uart_io_handler.read()
            # Store raw message in uart handling class
            uart_msg_handler.receive_msg(reading)
            write_string = "Received: " + uart_msg_handler.read_msg() + "\n"
            print("Received: " + uart_msg_handler.read_msg())
    except:
        print("Read - Exception generated")
        traceback.print_exc()
    finally:
        print("Ended reading")


def ser_write(ser, count, uart_writer):
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
            
def open_log_file():
    """ Opens the file to which logs are written"""

    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d__%H:%M:%S")
    print(date)

    f = open("./logs/rpi_log_{}.txt".format(date), "w")
    return f

# Open the log file into which logging data will be written
f = open_log_file()

# Open the serial port that connects to STM32. It may be connected on
# ACM0 or ACM1
try:
    ser = serial.Serial(port1, baud)
except:
    ser = serial.Serial(port0, baud)

# Initialize message handler and I/O handler
uart_message_handler = UartMessageHandler()
uart_io_handler = UartIOHandler(ser)
# Set the file that will be used for logs
uart_io_handler.set_log_file(f)

# Start two other threads for reading and writing to UART
thread_read = threading.Thread(
    target=ser_read, args=(ser, uart_message_handler, uart_io_handler))
thread_write = threading.Thread(
    target=ser_write, args=(ser, 20, uart_io_handler))

# Start the reading and writing threads
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
