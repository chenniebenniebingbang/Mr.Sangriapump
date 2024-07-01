import time  # Allows use of time.sleep() for delays
from mqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import machine  # Interfaces with hardware components
import micropython  # Needed to run any MicroPython code
import random  # Random number generator
from machine import Pin  # Define pin
import keys  # Contain all keys used here
import wifiConnection  # Contains functions to connect/disconnect from WiFi

# BEGIN SETTINGS
# These need to be change to suit your environment
DATA_INTERVAL = 20000  # milliseconds
last_sent_ticks = 0  # milliseconds

led = Pin("LED", Pin.OUT)
sensor = Pin(16, Pin.IN)
relay = Pin(27, Pin.OUT)
sangria = 10  # how much sangria we are starting with
flowrate = 0.3  # set liters per second for the pump flow rate
pumptime = 1  # how many seconds the pump is on
status = False 
 
# Callback Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):  # sub_cb means "callback subroutine"
    print((topic, msg))  # Outputs the message that was received. Debugging use.
    global status
    global sangria

    if topic == bytes(keys.AIO_LIGHTS_FEED, 'utf-8'):
        if msg == b"ON":  # If message says "ON" ...
            status = True  # ... then LED on
        elif msg == b"OFF":  # If message says "OFF" ...
            status = False  # ... then LED off
        else:  # If any other message is received ...
            print("Unknown message")  # ... do nothing but output that it happened.
    
    elif topic == bytes(keys.AIO_SANGRIA_FEED, 'utf-8'):
        try:
            sangria = float(msg)
            print(f"Sangria level set to {sangria}")
        except ValueError:
            print("Invalid sangria level received")

# Function to generate a random number between 0 and the upper_bound
def getsangrialevel():
    global sangria
    return sangria

# Function to publish random number to Adafruit IO MQTT server at fixed interval
def send_level():
    global last_sent_ticks
    global DATA_INTERVAL

    if (time.ticks_ms() - last_sent_ticks) < DATA_INTERVAL:
        return  # Too soon since last one sent.

    some_number = getsangrialevel()
    print(
        "Publishing: {0} to {1} ... ".format(some_number, keys.AIO_RANDOMS_FEED), end=""
    )
    try:
        client.publish(topic=keys.AIO_RANDOMS_FEED, msg=str(some_number))
        print("DONE")
    except Exception as e:
        print("FAILED")
    finally:
        last_sent_ticks = time.ticks_ms()

def update_sangria(time):
    global sangria
    sangria -= (flowrate * time)

def pump():
    relay.value(1)
    update_sangria(pumptime)
    time.sleep(pumptime)
    relay.value(0)

# Try WiFi Connection
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(  
    keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY
)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(keys.AIO_LIGHTS_FEED)
client.subscribe(keys.AIO_SANGRIA_FEED)  # Subscribe to the sangria level feed
print("Connected and subscribed to feeds")

try:  # Code between try: and finally: may cause an error
    while True:  # Repeat this loop forever
        client.check_msg()  # Action a message if one is received. Non-blocking.
        send_level()  # Send a random number to Adafruit IO if it's time.
        
        sensorstate = sensor.value()
        if status:
            if sensorstate == 0:
                led.on()
                pump()
            else:
                led.off()
                relay.value(0)

finally:  # If an exception is thrown ...
    client.disconnect()  # ... disconnect the client and clean up.
    client = None
    wifiConnection.disconnect()
    print("Disconnected from Adafruit IO.")
