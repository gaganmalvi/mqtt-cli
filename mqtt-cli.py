'''
MQTT client to publish and subscribe to topics and view messages
Store config in a file and read from it
Usage:
    mqtt-cli.py set-mqtt-server <server> <port>
    mqtt-cli.py set-credentials <username> <password>
    mqtt-cli.py publish <topic> <message>
    mqtt-cli.py subscribe <topic>
    mqtt-cli.py view-messages <topic>
    mqtt-cli.py (-h | --help)
'''

from io import DEFAULT_BUFFER_SIZE
import os
import paho.mqtt.client as mqtt
import sys
import time
import json

from docopt import docopt

def pr_inf(msg: str): print(f'\033[94m[INF]: {msg}\033[0m')
def pr_err(msg: str): print(f'\033[91m[ERR]: {msg}\033[0m')
def pr_war(msg: str): print(f'\033[93m[WAR]: {msg}\033[0m')

CONFIG_FILE = '.mqtt-cli-config.json'

DEFAULT_CONFIG_SCHEMA = {
    'server': 'localhost',
    'port': 1883,
    'client_id': 'mqtt-cli',
    'clean_session': True,
    'userdata': None,
    'username': None,
    'password': None,
    'protocol': mqtt.MQTTv311,
    'transport': 'tcp'
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        pr_err(f"Couldn't find config file, creating config file {CONFIG_FILE}")
        json.dump(DEFAULT_CONFIG_SCHEMA, f)
else:
    with open(CONFIG_FILE, 'r') as f:
        pr_inf(f"Config file {CONFIG_FILE} found, loading config")
        DEFAULT_CONFIG_SCHEMA = json.load(f)

class MqttClient:
    def __init__(self):
        self.client = mqtt.Client(DEFAULT_CONFIG_SCHEMA['client_id'], protocol=DEFAULT_CONFIG_SCHEMA['protocol'], transport=DEFAULT_CONFIG_SCHEMA['transport'], userdata=DEFAULT_CONFIG_SCHEMA['userdata'], clean_session=DEFAULT_CONFIG_SCHEMA['clean_session'])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_log = self.on_log
        if DEFAULT_CONFIG_SCHEMA['username'] and DEFAULT_CONFIG_SCHEMA['password']:
            self.client.username_pw_set(DEFAULT_CONFIG_SCHEMA['username'], DEFAULT_CONFIG_SCHEMA['password'])

    def set_mqtt_server(self, server: str, port: int):
        pr_inf(f"Setting MQTT server to {server}:{port}")
        DEFAULT_CONFIG_SCHEMA['server'] = server
        DEFAULT_CONFIG_SCHEMA['port'] = port
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG_SCHEMA, f)

    def set_credentials(self, username: str, password: str):
        pr_inf(f"Setting credentials to {username}:{password}")
        DEFAULT_CONFIG_SCHEMA['username'] = username
        DEFAULT_CONFIG_SCHEMA['password'] = password
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG_SCHEMA, f)

    def publish(self, topic: str, message: str, qos: int = 0, retain: bool = False):
        pr_inf(f'Connecting to MQTT server {DEFAULT_CONFIG_SCHEMA["server"]}:{DEFAULT_CONFIG_SCHEMA["port"]}')
        self.client.connect(DEFAULT_CONFIG_SCHEMA['server'], DEFAULT_CONFIG_SCHEMA['port'])
        pr_inf(f"Publishing message {message} to topic {topic}")
        self.client.publish(topic, message, qos=qos, retain=retain)

    def subscribe(self, topic: str):
        pr_inf(f'Connecting to MQTT server {DEFAULT_CONFIG_SCHEMA["server"]}:{DEFAULT_CONFIG_SCHEMA["port"]}')
        self.client.connect(DEFAULT_CONFIG_SCHEMA['server'], DEFAULT_CONFIG_SCHEMA['port'])
        pr_inf(f"Subscribing to topic {topic}")
        self.client.subscribe(topic)

    def view_messages(self, topic: str):
        pr_inf(f'Connecting to MQTT server {DEFAULT_CONFIG_SCHEMA["server"]}:{DEFAULT_CONFIG_SCHEMA["port"]}')
        self.client.connect(DEFAULT_CONFIG_SCHEMA['server'], DEFAULT_CONFIG_SCHEMA['port'])
        try:
            pr_inf(f"Viewing messages from topic {topic}")
            pr_inf("Press Ctrl+C to exit")
            self.client.subscribe(topic)
            self.client.loop_start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()
            pr_inf("Exiting view messages")

    def on_connect(self, client, userdata, flags, rc):
        pr_inf(f"Connected with result code {rc}")

    def on_message(self, client, userdata, message):
        pr_inf(f"Message received on topic {message.topic}: {message.payload.decode()}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        pr_inf(f"Subscribed to topic with mid {mid} and granted qos {granted_qos}")

    def on_log(self, client, userdata, level, buf):
        pr_inf(f"Log: {buf}")

class MqttCli:
    def __init__(self):
        self.client = MqttClient()

    def run(self, args):
        if args['set-mqtt-server']:
            self.client.set_mqtt_server(args['<server>'], int(args['<port>']))
        elif args['set-credentials']:
            self.client.set_credentials(args['<username>'], args['<password>'])
        elif args['publish']:
            self.client.publish(args['<topic>'], args['<message>'])
        elif args['subscribe']:
            self.client.subscribe(args['<topic>'])
        elif args['view-messages']:
            self.client.view_messages(args['<topic>'])
        else:
            pr_err("Invalid command")

if __name__ == '__main__':
    MqttCli().run(docopt(__doc__))
