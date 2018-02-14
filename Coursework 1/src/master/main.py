from algorithms.exceptions import EmptyDataError, EmptyCentroidsError
from algorithms.kmeans import KMeans
from algorithms.postprocessing import PostProcessing, encapsulate_data
from algorithms.log import log_event, check_on_field
from www.web import create_app

import random
import time
import sys
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import _thread
import json

# Define static variables
N_PLAYERS = 20
MODEL_NAME =  "kmeans" + "1.0"
SENSOR_STATES = [0 for i in range(20)]

def encrypt(val):

    temp = int(0)

    temp = temp | (val << 0  & 0x000F)
    temp = temp | (val << 16 & 0x00F0)
    temp = temp | (val << 0  & 0x0F00)
    temp = temp | (val >> 16 & 0xF000)
    
    return temp



if __name__ == '__main__':
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    BROKET_HOST = sys.argv[3]
    BROKET_PORT = int(sys.argv[4])
    print("Initializing the web server & MQTT broker")
    print("BROKER HOST {}".format(BROKET_HOST))
    print("BROKER PORT {}".format(BROKET_PORT))
    print("HOST {}".format(HOST))
    print("PORT {}".format(PORT))

    # Initialization of data postprocessing and ML algorithm
    kmeans = KMeans(k=4)
    kmeans.load('algorithms/model/{}.pickle'.format(MODEL_NAME))

    # Calibrate the sensors
    sensor = PostProcessing()
    sensor.load_gyro_calibration(file_path="algorithms/calibration/calibration_values.txt")


    ### Establishing code for the broker
    # Establish the broker service
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("esys/HeadAid/sensor")

    def on_message(client, userdata, msg):
        # Get the raw data
        temp = {}

        #TODO: check if this is actually a list
        data = list(msg.payload.decode("utf-8"))

        temp['PLAYER']          = data[3]
        temp['DEVICE ADDRESS']  = data[4]
        # Manipulate the data to reflect the compression of the sent data
        temp['DATA'] = []
        temp['DATA'].append(data[0]     & 0xFF)
        temp['DATA'].append(data[0]>>16 & 0xFF)
        temp['DATA'].append(data[1]     & 0xFF)
        temp['DATA'].append(0)
        temp['DATA'].append(data[1]>>16 & 0xFF)
        temp['DATA'].append(data[2]     & 0xFF)
        temp['DATA'].append(data[2]>>16 & 0xFF)

        data = temp

        print(data)

        #Encapsulate the data into dictionary format
        data = encapsulate_data(data)

        processed_data = sensor.postprocess_data(data)
        label = kmeans.classify(processed_data)

        # The condition has been classified as bad
        if label >= 2:
            log_event(data=data, label=label)

    ####### MQTT #######
    #Establish connection with the MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    def con_thread():
        client.loop_start()
        client.connect(BROKET_HOST, BROKET_PORT, 60)
    _thread.start_new_thread(con_thread,())


    ####### FLASK #######
    ### Establishing code for the web server
    app = create_app('dev')
    def web_thread():
        app.run(debug=False, host=HOST,port=PORT, threaded=True, use_reloader=False)
    _thread.start_new_thread(web_thread,())

    def turn_sensor(value,sensor):
        client.publish("esys/HeadAid/on_field_status{}".format(sensor), str(value))

    # Necessary while loop for the code to keep on executing
    while True:
        # Delay to reduce the checking if the players are on the field, selected by the coach
        time.sleep(1)
        players_on_field = check_on_field()
        for i in range(N_PLAYERS):
            if players_on_field[i] != SENSOR_STATES[i]:
                SENSOR_STATES[i] = players_on_field[i]
                # Turn on or off the sensor in case player state has been changed to conserve power
                turn_sensor(SENSOR_STATES[i],i)
