#! /usr/bin/env python3 
###
# mqtt_json parser
# a middleware for BirdNET-Pi 
# https://github.com/yjeanrenaud/BirdNET-Pi-influxdb/
# 2025, Yves Jeanrenaud
###

import paho.mqtt.client as mqtt
import json
import re
import datetime

# Configuration with authentication
MQTT_BROKER = "hostname"
MQTT_PORT = 1883
MQTT_USERNAME = "username"  # Replace with your MQTT username
MQTT_PASSWORD = "password"  # Replace with your MQTT password
MQTT_SOURCE_TOPIC = "birdnet/bird"
MQTT_DEST_TOPIC = "birdnet/bird_json"

def parse_mqtt_message(message):
    """
    Extracts the key-value pairs from the MQTT message.
    Expected format:
    New BirdNET-Pi Detection
     A Blässhuhn \(Fulica atra\) was just detected with a confidence of 0.95805514. VALUES: comname=Blässhuhn,sciname=Fulica atra,confidence=0.95805514,date=2025-02-24,time=20:41:36,week=8
    """
    pattern = (
        r"comname=(?P<comname>[^,]+),"
        r"sciname=(?P<sciname>[^,]+),"
        r"confidence=(?P<confidence>[^,]+),"
        r"date=(?P<date>[^,]+),"
        r"time=(?P<time>[^,]+),"
        r"week=(?P<week>\d+)"
    )
    
    match = re.search(pattern, message)
    if not match:
        return None

    data = match.groupdict()
    # Convert fields to appropriate types
    try:
        data["confidence"] = float(data["confidence"])
    except ValueError:
        pass

    try:
        data["week"] = int(data["week"])
    except ValueError:
        pass

    # Combine date and time into a single string
    datetime_str = f"{data['date']} {data['time']}"
    # Parse the string into a datetime object
    dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    # Convert the datetime object to a Unix timestamp (in seconds)
    unix_timestamp = int(dt.timestamp())
    data["timestamp"] = unix_timestamp

    print("debug {}".format(data))

    return data

def on_connect(client, userdata, flags, rc):
    print("Connected with result code:", rc)
    # Subscribe to the topic where BirdNET messages are published
    client.subscribe(MQTT_SOURCE_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8").strip()
    print("Received message on topic {}: {}".format(msg.topic, message.strip()))
    
    parsed_data = parse_mqtt_message(message)
    if parsed_data:
        json_payload = json.dumps(parsed_data)
        # Publish the JSON-formatted message to birdnet/bird_json
        client.publish(MQTT_DEST_TOPIC, json_payload)
        print("Published JSON message to {}: {}".format(MQTT_DEST_TOPIC.strip(), json_payload.strip()))
    else:
        print("Failed to parse the message.\nSent no new topic PUBLISH to MQTT broker")

def main():
    client = mqtt.Client(client_id="mqttJson")

    # Set the MQTT username and password for authentication
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("connected to mqtt broker {}:{} and listening to {}".format(MQTT_BROKER,MQTT_PORT,MQTT_SOURCE_TOPIC))
    # Loop forever to listen for messages
    client.loop_forever()

if __name__ == "__main__":
    main()

