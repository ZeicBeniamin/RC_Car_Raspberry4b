from enum import Enum
import traceback
import os

class SwapFlag(Enum):
    SWP_BUFFER_READY = 1
    SWP_BUFFER_REQUEST_SWAP = 2

class RxFlag(Enum):
    RX_BUFFER_READY = 1 
    RX_BUFFER_BUSY_READING = 2

class UartMessageHandler:
    """ Stores messages received through UART; returns them on-demand

        The messages are received from threads responsible with reading
        from UART. The messages are stored in this class and forwarded
        to every function that calls the read_msg() method on an object
        of this class.
        NOTE: Alternatively, this class could be implemented using an
        Observer pattern, in which this class keeps a list of all
        "subscribers" and notifies them upon receiving a message from
        UART.

        We use a double buffer system for data reception and forwarding
        We do this in order to avoid situations where a repeated buffer
        read operation hinders the buffer write operation. 
        A buffer handling mechanism was implemented, that ensures that,
        the last or second-to-last message received from 
        UART is passed forward. Of course, this assumption is valid 
        only if the read and write operations, performed on objects of
        this class, have similar execution times (i.e. the functions
        receive_msg() and read_msg() have similar execution times). 

        Attributes
        ----------
        _rx_buffer1 : str
            First buffer to be used for message forwarding from UART
        _rx_buffer2 : str
            Second buffer to be used for message forwarding from UART
        _swap_flag : SwapFlag(Enum)
            Stores the state of the buffer swap requests. 
        _rx_state : RxFlag(Enum)
            Acts as a lock on the rx buffers. If a buffer is used for
            reading, this flag is triggered. The receiving function
            must check this flag before writing in the buffer
        

    """
    def __init__(self):
        """ Initialize the variables of the class
        """
        self._rx_buffer1 = ""
        self._rx_buffer2 = ""

        self._swap_flag = SwapFlag(SwapFlag.SWP_BUFFER_READY)
    
        self._rx_state = RxFlag(RxFlag.RX_BUFFER_READY)

        # _in_use_buffer indicates the currently used buffer
        self._in_use_buffer = self._rx_buffer1
        return

    def receive_msg(self, rx_string):
        """ Receive UART message from reading thread 

            UART message is stored in the active buffer, which can be
            found by checking the value of _in_use_buffer. The inactive
            buffer might be used in the read_msg() method, so 
            receive_msg() will use the active one, in order not to 
            interfere with the message forwarding operation.
            Before writing in the buffer, a check is performed on the 
            _swap_flag, in order to find if the previous swap requests 
            made by receive_msg() were satisfied. If this is not the 
            case, it means that the read_msg() operation that was 
            executing during previous calls of receive_msg() has not 
            finished yet. In this case, we don't want write operations
            to occur. We want to wait until the read_msg() operation
            finishes, to ensure a proper message forwarding, without
            external interference.

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
        """ Read UART message stored in this class

            UART message is stored in one of the two internal buffers.
            This method retrieves the message from the buffer which
            is not currently used by write operations. The message is
            parsed before being returned. (For more details on the
            parsing operation, see the documentation of parse().)

            This method is also responsible for swapping the active and
            inactive buffers, in case the method receive_msg() raised
            the flag for this operation. THe flag is raised only when
            receive_msg() returns before an ongoing read_msg() call
            terminates execution.

            Returns
            -------
            parsed : str
                Message stored in this classed, after parsing was
                applied on it.
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

        # If there was any swap request, execute it now
        if (self._swap_flag == SwapFlag.SWP_BUFFER_REQUEST_SWAP):
            if (self._in_use_buffer == self._rx_buffer1):
                self._in_use_buffer = self._rx_buffer2
            else: 
                self._in_use_buffer = self._rx_buffer1
            self._swap_flag = SwapFlag.SWP_BUFFER_READY
        # TODO: Test that message parsing works correctly            
        parsed = parse(aux)
        return parsed


class UartIOHandler:
    """ Sends messages through an UART port

        Messages are sent through the already opoened UART port that is
        stored in the object "ser".

        Attributes
        ----------
        _ser : Serial
            Object created with the help of the PySerial library. 
            Facilitates communication through the port that it manages.
        Methods
        -------
        TODO: Write method comments
    """

    def __init__(self, serial_port=None):
        """
        """
        self._ser = serial_port
        self._log = False

    def set_serial_port(self, serial_port):
        """ Set the serial port for UART communication

            Parameters
            ----------
            serial_port : Serial
                Serial object with already opened port to communicate through
        """
        self._ser = serial_port

    def set_log_file(self, log_file):
        """ Sets the file to be used for log messages

        Parameters
        ----------
        log_file : file object
            Already opened log file for writing log messages.
        """
        self._log = True
        self._log_file = log_file

    def write(self, message):
        """ Writes message to UART port

            If a log file was set in this class, after writing message to
            UART it will also write the message to the log file.

            Parameters
            ----------
            message : str
                Message to write to UART port.
        """
        try:
            self._ser.write(message.encode())
        except:
            print("UartWriter.write: serial write exception occured")
            traceback.print_exc()
        try:
            if (self._log):
                self._log_file.write(
                    "UartIOHandler.write: write message to UART: " + message)
                self._log_file.flush()
                os.fsync(self._log_file.fileno())
        except:
            print("UartWriter.write: file writing exception")
            traceback.print_exc()

    def read(self):
        """ Reads and decodes message from UART port

            If a log file was set in this class, after reading the 
            message from UART it will also write the message to the 
            log file.

            Returns
            -------
            message : str
                The decoded message received through the UART port
        """
        message = None
        try:
            message = self._ser.read(8).decode()
            # print("message is : ", message)
        except:
            print("UartWriter.read: serial read exception")
            traceback.print_exc()
        try:
            if (self._log):
                self._log_file.write(
                    "UartIOHandler.read: read message from UART: " + message)
                self._log_file.flush()
                os.fsync(self._log_file.fileno())
        except:
            print("UartIOHandler.read: file write exception")
            traceback.print_exc()
        return message


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
    
    # Check that the stop byte exists - if not, return an error message 
    if rearranged[7] != '>':
        rearranged = "MINVALID"

    return rearranged