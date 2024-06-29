import time
from machine import Pin


# Set the led and sensor pin 
led = Pin("LED", Pin.OUT)
sensor = Pin(16, Pin.IN)
relay = Pin(27, Pin.OUT)
sangria = 10 # how much sangria we are starting with
flowrate = 0.3 # set liters pers second for the pump flow rate
pumptime = 3 # how many seconds the pump is on

state = True

def update_sangria(time):
    global sangria
    sangria = sangria - (0.3*time)

def pump():
    relay.value(1)
    update_sangria(pumptime)
    time.sleep(pumptime)
    relay.value(0) 
 
while True:
    state = sensor.value() 
    if state == False:
        led.on() 
        print("Detected...")
        pump()
    else:
        led.off()
        relay.value(0)
        print("Safe to go...")
        
