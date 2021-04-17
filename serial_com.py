from enum import Enum
from time import sleep
import serial
import threading
import time


class SwapFlag(Enum):
    SWP_BUFFER_READY = 1
    SWP_BUFFER_REQUEST_SWAP = 2

class RxFlag(Enum):
    RX_BUFFER_READY = 1 
    RX_BUFFER_BUSY_READING = 2

# -------------------------- IMPORTANT TODO ---------------------------

# TODO: Complete the TODO's in this file before proceding to anything
#        else

# -------------------------- IMPORTANT TODO - END ---------------------


# TODO: Document the UartMessageHandler class better
#       Add docstring to class and to each of the methods

class UartMessageHandler:
    """ Stores messages received through UART; returns them on-demand

        The messages are received from threads responsible with UART
        reading
    """
    def __init__(self):
        """ Initialize the variables of the class
        """
        self._rx_buffer1 = ""
        self._rx_buffer2 = ""

        self._swap_flag = None
        self._swap_flag = SwapFlag(SwapFlag.SWP_BUFFER_READY)
    
        self._rx_state = RxFlag(RxFlag.RX_BUFFER_READY)

        # _in_use_buffer indicates the currently used buffer
        self._in_use_buffer = self._rx_buffer1
        return

    def receive_msg(self, rx_string):
        """ Receive UART message from reading thread 

            UART message is stored in the attributes of the class. We use a
            double buffer system for storing data

            Parameters
            ----------
            rx_string : str
                String received through the UART channel
        """

        # Check if a swap request was previously made by this method
        if (self._swap_flag == SwapFlag.SWP_BUFFER_READY):
            # Check the active buffer (the buffer to write to)
            if (self._in_use_buffer == self._rx_buffer1):
                # Write received string to buffer
                self._rx_buffer1 = rx_string
                # Change the active buffer, or request a swap, if the 
                # buffer is not currently available
                if (self._rx_state == RxFlag.RX_BUFFER_READY):
                    self._in_use_buffer = self._rx_buffer2
                else:
                    self._swap_flag = SwapFlag.SWP_BUFFER_REQUEST_SWAP
            # Repeat the  structure used for writing in _rx_buffer1
            # for writing in _rx_buffer2
            elif (self._in_use_buffer == self._rx_buffer2):
                self._rx_buffer2 = rx_string
                if (self._rx_state == RxFlag.RX_BUFFER_READY):
                    self._in_use_buffer = self._rx_buffer1
                else:
                    self._swap_flag = SwapFlag.SWP_BUFFER_REQUEST_SWAP
        
        return

    def read_msg(self):
        """ Read UART message stored in the inactive buffer

            UART message is stored in one of the two internal buffers.
            This function retrieves the message from the buffer which
            is not currently in use.
        """

        aux = ""
        # Lock the resource by flagging it as busy
        self._rx_state = RxFlag.RX_BUFFER_BUSY_READING
        if (self._in_use_buffer == self._rx_buffer1):
            aux = self._rx_buffer2
        else:
            aux = self._rx_buffer1
        # Unlock the resource after reading its content
        self._rx_state = RxFlag.RX_BUFFER_READY

        # If there was any swap request, perform it now
        if (self._swap_flag == SwapFlag.SWP_BUFFER_REQUEST_SWAP):
            if (self._in_use_buffer == self._rx_buffer1):
                self._in_use_buffer = self._rx_buffer2
                self._swap_flag = SwapFlag.SWP_BUFFER_READY
            else: 
                self._in_use_buffer = self._rx_buffer1
                self._swap_flag = SwapFlag.SWP_BUFFER_READY
        # TODO: Test that message parsing works correctly            
        return parse(aux)

delay = 0.001
n = 100

port0 = '/dev/ttyACM0'
port1 = '/dev/ttyACM1'
baud = 115200

def parse(message):
    """ Rearrange the message received through UART
    
        Received data is 8 bytes long. We receive the bytes in the 
        correct order, but we are not sure about the location of the
        first byte of the message in the array.
        Thus, we set up the following convention: every message starts
        with a '<' character (called heading byte), and ends with a '>'
        character (called stop byte). By having this convention, we can
        easily rearrange the message in the correct form.
        
        Example: We were sent the message "<234567>" through UART,
        but we received the string "67><2345". We can see that the
        message suffered a circular shift with 3 positions to the right
        To rearrange the message, we first search for the heading byte
        '<' and then we start reordering the message. If we do not
        encounter the stop byte '>', we dismiss the message and return
        an appropriate string to signal this event to the caller 
        function.        
        
        Parameters
        ----------
        message : str
            String received through UART

        Returns
        -------
        rearranged : str
            Rearranged message string, 
    """
    # Position of the heading byte
    heading_pos = 0

    # Find the heading byte '<'
    for i, c in enumerate(message):
        if c == '<':
            heading_pos = i

    rearranged = ""
    # Reconstruct the message in the correct order
    for i in range(len(message)):
        rearranged = rearranged + message[(i+heading_pos) % 8]
    
    # Check that the stop byte exists - if not, return a corresponding 
    # message
    if rearranged[7] != '>':
        rearranged = "MINVALID"

    return rearranged

def ser_read(ser, uart_msg_handler):
    """ Read 8 bytes at a time from the UART serial port in an infinite
        loop

        Parameters
        ----------
        ser : Serial
            Serial port to read from
    """
    
    while True:
        try:
            reading = ser.read(8).decode()
            # Store raw message in uart handling class
            uart_msg_handler.receive_msg(reading)
        except:
            print("exception gen")

def ser_write(ser, uart_message_handler):
    """ Write 8 bytes at a time to the UART serial port in an infinite
        loop

        Parameters
        ----------
        ser : Serial
            Serial port to write to
    """
    test = "pi.><ras"
    test = "<CONACC>"
    while True:
        # i += 1
        try:
            ser.write(test.encode())
        except:
            print ("Write killed")
        time.sleep(0.5)
        print("send; sleep = 0.5")
        

# Open the serial port that connects to STM32. It may be connected on 
# ACM0 or ACM1
try:
    ser = serial.Serial(port1, baud)
except:
    ser = serial.Serial(port0, baud)

uart_message_handler = UartMessageHandler()

# Start two other threads for reading and writing to UART
thread_read = threading.Thread(target=ser_read, args=(ser, uart_message_handler))
thread_write = threading.Thread(target=ser_write, args=(ser, uart_message_handler))

thread_read.start()
thread_write.start()


# Print a message from main as an indication that the program is 
# running
while True:
    
    pass

# TODO: Detail the print statements below - useful for debugging

print ("Working")
print ("Sending and receiving messages at the following frequencies:")
print ("TODO: Show frequency of tx and rx operations")


# Close the serial port after using it
ser.close()
