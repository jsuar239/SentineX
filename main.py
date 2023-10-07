import time
from AlarmController import *
time.sleep(0.1) # Wait for USB to become ready

print("Hello, Pi Pico!")

myAlarm = AlarmController()
myAlarm.run()