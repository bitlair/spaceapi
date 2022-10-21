#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import tornado.ioloop
import tornado.web


PORT      = 8888
BASE_URL  = 'https://bitlair.nl/state'
MQTT_HOST = 'bitlair.nl'


current_state        = False
current_state_change = time.time()

class StatejsonHandler(tornado.web.RequestHandler):
    def get(self):
        global current_state, current_state_change
        state = {
            'api':   '0.13',
            'space': 'Bitlair',
            'logo':   BASE_URL+'/logo.png',
            'url':    'https://bitlair.nl/',
            'contact': {
                'phone':   '+31337114666',
                'irc':     'irc://irc.smurfnet.ch/bitlair',
                'twitter': '@bitlair',
                'email':   'info@bitlair.nl',
                'ml':      'general@list.bitlair.nl',
            },
            'spacefed': {
                'spacenet':   True,
                'spacesaml':  True,
                'spacephone': False,
            },
            'location': {
                'address': 'Computerweg 20A, 3821 AB Amersfoort, The Netherlands',
                'lat': 52.177323,
                'lon': 5.414782,
            },
            'state': {
                'open':       current_state,
                'lastchange': int(current_state_change),
                'icon': {
                    'open':   BASE_URL+'/open.png',
                    'closed': BASE_URL+'/closed.png',
                },
                'mqtt': {
                    'host': 'bitlair.nl',
                    'port': 1883,
                    'tls': False,
                    'topic': 'bitlair/state',
                    'closed': 'closed',
                    'open': 'open'
                },
            },
            'issue_report_channels': [ 'twitter' ],
        }
        self.write(state)

def make_app():
    return tornado.web.Application([
        (r'/statejson', StatejsonHandler),
    ])

def on_message(client, userdata, message):
    global current_state, current_state_change
    if message.topic == 'bitlair/state':
        current_state        = message.payload == b'open'
        current_state_change = time.time()

def on_connect(client, userdata, flags, rc):
    client.subscribe('bitlair/state', qos=2)

if __name__ == '__main__':
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect

    mqttc.connect(MQTT_HOST)
    mqttc.loop_start()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
