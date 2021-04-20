
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from sense_hat import SenseHat
import time as t
import json
import datetime
import RPi.GPIO as GPIO
import time

sense = SenseHat()

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a25jpsro0ddnpn-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERT = "certificates/382dc9e2e4-certificate.pem.crt"
PATH_TO_KEY = "certificates/382dc9e2e4-private.pem.key"
PATH_TO_ROOT = "certificates/root.pem"
DEVICE_ID = "60"
TOPIC = "device/ " +DEVICE_ID +"/data"
POLL_TIME = 600
TANK_HEIGHT = 20

def getTemperature():
    temp = sense.get_temperature()
    return(temp)

def getHumidity():
    humidity = sense.get_humidity()
    return (humidity)


def getOrientation():
    acceleration = sense.get_accelerometer_raw()
    z = acceleration['z']
    z=round(z, 0)

    if z == 1:
        piUpright = True
    else:
        piUpright = False
    return (piUpright)


#Code from https://pimylifeup.com/raspberry-pi-distance-sensor/
def getWaterLevel():
    try:
        GPIO.setmode(GPIO.BOARD)

        PIN_TRIGGER = 7
        PIN_ECHO = 11

        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        print("Waiting for sensor to settle")

        t.sleep(2)

        print("Calculating distance")

        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        t.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        while GPIO.input(PIN_ECHO)==0 :
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1 :
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        print("Distance:",distance,"cm ")


    finally:
        GPIO.cleanup()
        return ((TANK_HEIGHT - int(distance))/TANK_HEIGHT)*100




#Loop to send data to AWS


def sendData(data):
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=PATH_TO_CERT,
        pri_key_filepath=PATH_TO_KEY,
        client_bootstrap=client_bootstrap,
        ca_filepath=PATH_TO_ROOT,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=6
    )
    print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")
    # Publish message to server desired number of times.
    print('Begin Publish')
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(data), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(data) + "' to the topic: " + TOPIC)
    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()


#main loop gets data and sends, need to do water level, toilet paper level and usage sensors.
while True:
    temperature = int(getTemperature())
    humidity = int(getHumidity())
    orientation = getOrientation()
    waterLevel = getWaterLevel()
    toiletPaperLevel = 50
    usage =50
    sampleTime = datetime.datetime.now().isoformat()
    sendData({"sampleTime": sampleTime, "waterLevel": waterLevel, "toiletPaperLevel": toiletPaperLevel, "usage": usage,
              "temperature": temperature, "humidity": humidity, "orientation": orientation})
    t.sleep(POLL_TIME)
