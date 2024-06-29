import ubinascii              # Conversions between binary data and various encodings
import machine                # To Generate a unique id from processor

# Wireless network
WIFI_SSID = 'jancat4'
WIFI_PASS = 'Dragsviken11'

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "elinandlun"
AIO_KEY = "aio_yLtl48QfY2LgTKG6eisN6zoDCQVN"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_LIGHTS_FEED = "elinandlun/feeds/lights"
AIO_RANDOMS_FEED = "elinandlun/feeds/randoms"