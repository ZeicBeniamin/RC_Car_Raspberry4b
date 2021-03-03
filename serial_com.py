import serial
import time

delay = 0.4
n = 4

ser = serial.Serial('/dev/ttyACM0', 115200)

# Send 4 bit strings to the STM via UART to test the robustness of the connection
for i in range(n):
    ser.write("test".encode())
    time.sleep(delay)
 

ser.close()
