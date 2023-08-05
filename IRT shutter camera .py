#!/usr/bin/python
import cv2
from pyzbar.pyzbar import decode
import socket
import RPi.GPIO as GPIO

# QR code data corresponding to door positions from 0 to 10
qr_codes = ['qr0', 'qr1', 'qr2', 'qr3', 'qr4', 'qr5', 'qr6', 'qr7', 'qr8', 'qr9', 'qr10']

# GPIO setup
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
LED_PIN = 12  # Adjust as needed
GPIO.setup(LED_PIN, GPIO.OUT)

# initialize the camera
cap = cv2.VideoCapture(0)

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define the IP address and port of the computer you want to send data to
host = '192.168.1.100'  # The server's hostname or IP address
port = 65432  # The port used by the server

try:
    # connect to the server
    s.connect((host, port))
    
    while True:
        # capture frame-by-frame
        ret, frame = cap.read()

        # our operations on the frame come here
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            print("Type:", obj.type)
            print("Data:", obj.data)

            # compare detected QR code data with known codes
            if obj.data.decode("utf-8") in qr_codes:
                # convert data to feet
                door_position = qr_codes.index(obj.data.decode("utf-8"))
                print("Door position:", door_position)

                # here you would send `door_position` to your control system
                # send the door position over TCP
                try:
                    s.sendall(str(door_position).encode())
                except socket.error:
                    print("TCP connection lost, illuminating LED")
                    GPIO.output(LED_PIN, GPIO.HIGH)

        # display the resulting frame
        cv2.imshow('frame', frame)

        # condition to break the loop (press 'q' to quit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # when everything done, release the capture, destroy windows, and close the socket
    cap.release()
    cv2.destroyAllWindows()
    s.close()
    GPIO.cleanup()  # clean up GPIO

