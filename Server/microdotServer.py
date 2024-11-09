from microdot import Microdot
from microdot.websocket import with_websocket
from microdot.cors import CORS
from machine import Pin, PWM
import asyncio 
import network
import time

# Initialize PWM and direction pins
PWM1 = PWM(Pin(3, Pin.OUT), freq=1000)
Motor1_in1, Motor1_in2 = Pin(0, Pin.OUT), Pin(10, Pin.OUT)

PWM2 = PWM(Pin(11, Pin.OUT), freq=1000)
Motor2_in1, Motor2_in2 = Pin(5, Pin.OUT), Pin(9, Pin.OUT)

PWM3 = PWM(Pin(27, Pin.OUT), freq=1000)
Motor3_in1, Motor3_in2 = Pin(26, Pin.OUT), Pin(22, Pin.OUT)

PWM4 = PWM(Pin(19, Pin.OUT), freq=1000)
Motor4_in1, Motor4_in2 = Pin(20, Pin.OUT), Pin(21, Pin.OUT)
 

'''
Motor Testing
PWM1.duty_u16(65536)
Motor1_in1.value(0)
Motor1_in2.value(1)

PWM2.duty_u16(65536)
Motor2_in1.value(0)
Motor2_in2.value(1)

PWM3.duty_u16(65536)
Motor3_in1.value(0)
Motor3_in2.value(1)

PWM4.duty_u16(65536)
Motor4_in1.value(0)
Motor4_in2.value(1)
'''

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SBRT", "Robotic$3")
time.sleep(5)

# Wait for connection
max_attempts = 10
attempt = 0

while not wlan.isconnected() and attempt < max_attempts:
    print(f"Trying to connect to (Attempt {attempt + 1}/{max_attempts})...")
    time.sleep(10)
    attempt += 1

if wlan.isconnected():
    print("Connected to IP:", wlan.ifconfig()[0])
else:
    print("Failed to connect to Wi-Fi. Please check your SSID and password.")

app = Microdot()
CORS(app, allowed_origins = '*', allow_credentials = True)

@app.get('/test')
def index(requsst):
    return "hello world"

# Custom function to set motor power
def setMotorPower(power, PWM, in1, in2):
    PWM.duty_u16(int(abs(power)*65535))
    
    # Changing motor direction, based on sign
    if power > 0:
        in1.value(1)
        in2.value(0)
    else:
        in1.value(0)
        in2.value(1)


print("Im here")
    
@app.get('/direction')
@with_websocket
async def index(request, ws): 
    try:
        while True:
            # Access controller values
            x = int(round(float(await ws.receive())))
            y = int(round(float(await ws.receive())))
            
            print(x,y)
            
            # Normalize controller values
            x = x/100
            y = y/100
            
            # Calculate motor powers, component-wise
            fLeft = y - x
            fRight = y + x
            bLeft = y - x
            bRight = y + x
            
            print("Motor Powers")
            print(fLeft)
            print(fRight)
            print(bLeft)
            print(bRight)

            # Set power to motors using custom function
            setMotorPower(fLeft, PWM2, Motor2_in1, Motor2_in2)
            setMotorPower(fRight, PWM4, Motor4_in1, Motor4_in2)
            setMotorPower(bLeft, PWM1, Motor1_in1, Motor1_in2)
            setMotorPower(bRight, PWM3, Motor3_in1, Motor3_in2)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket connection closed")

app.run(port=80)