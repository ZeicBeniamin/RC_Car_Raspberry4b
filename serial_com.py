import serial
import threading
import time

delay = 0.001
n = 100

port = '/dev/ttyACM0'
baud = 115200

ser = serial.Serial(port, baud)

# # Send n times 8-bit strings to the STM via UART to test the robustness of the connection
# for i in range(n):
#     ser.write("test1234".encode())
#     time.sleep(delay)
# ser.write("123fdval".encode())
 
def ser_write(ser):
    while True:

        reading = ser.read(8).decode()
        print(reading)

thread = threading.Thread(target=ser_write, args=(ser,))
thread.start()

while True:
    time.sleep(1)
    print("One second delay")

ser.close()
