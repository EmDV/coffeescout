import requests
import picamera
import base64
import time
import RPi.GPIO as GPIO
from pyonep import onep

import netifaces as net
net.ifaddresses('eth0')
ip = net.ifaddresses('eth0')[2][0]['addr']
# print(ip)

# Var setup

cik = "31bb26c318d42448181bce5405b9c8546f532b8f"

ob = onep.OnepV1()
aliases = ['ip', 'picture']

sensor = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

previous_state = False
current_state = False



if __name__ == '__main__':

    # write IP address to dataport
    ob.write(cik, {"alias": aliases[0]}, str(ip), {})
    isok, response = ob.read(cik, {"alias": aliases[0]}, {'limit': 1, 'sort': 'desc', 'selection': 'all'})
    if isok:
        print("Read back %s" % response)
    else:
        print("Read failed: %s" % response)

    # Begin loop to evaluate GPIO pin HI/LO and take a picture on HI.
    while True:
        time.sleep(0.2)
        previous_state = current_state
        current_state = GPIO.input(sensor)
        if current_state != previous_state:
            if current_state:
                print("GPIO pin %s is %s, now taking a picture" % (sensor, current_state))

                with picamera.PiCamera() as camera:

                    camera.resolution = (100, 100)
                    camera.start_preview()
                    time.sleep(1)
                    camera.capture("sample.jpg")

                # take captured file, encode it, and send it to Exosite.
                with open("sample.jpg", "rb") as f:
                    encodedF = base64.b64encode(f.read()).decode()

                    isok, response = ob.write(cik, {"alias": aliases[1]}, encodedF, {})

                    if isok:
                        # expect Read back [[1374522992, 1]]
                        print("write %s" % response)
                    else:
                        print("write failed: %s" % response)

                f.close()

