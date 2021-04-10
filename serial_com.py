import serial
import threading
import time

delay = 0.001
n = 100

port0 = '/dev/ttyACM0'
port1 = '/dev/ttyACM1'
baud = 115200


# # Send n times 8-bit strings to the STM via UART to test the robustness of the connection
# for i in range(n):
#     ser.write("test1234".encode())
#     time.sleep(delay)
# ser.write("123fdval".encode())
 

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

def ser_read(ser):
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
            parsed = parse(reading)
    # Print message received from UART and the processed message
    # TODO: Remove after completing tests
            print (reading)
            print(parsed)
        except:
            print("exception gen")

def ser_write(ser):
    """ Write 8 bytes at a time to the UART serial port in an infinite
        loop

        Parameters
        ----------
        ser : Serial
            Serial port to write to
    """
    i = 0
    test = "pi.><ras"
    while True:
        # i += 1
        ser.write(test.encode())
        print("send " + str(i))
        time.sleep(1)
        
# Open the serial port that connects to STM32. It may be connected on 
# ACM0 or ACM1
try:
    ser = serial.Serial(port1, baud)
except:
    ser = serial.Serial(port0, baud)

# Start two other threads for reading and writing to UART
thread_read = threading.Thread(target=ser_read, args=(ser,))
thread_write = threading.Thread(target=ser_write, args=(ser,))

thread_read.start()
thread_write.start()

# Print a message from main as an indication that the program is 
# running
while True:
    print("Alive - one second delay")
    time.sleep(1)

# Close the serial port after using it
ser.close()
