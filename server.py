#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import tornado.ioloop
import tornado.web


PORT      = 8888
BASE_URL  = 'https://bitlair.nl/state'
MQTT_HOST = 'mqtt.bitlair.nl'


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
                'address': 'Heiligenbergerweg 144b, 3816 AN Amersfoort, The Netherlands',
                'lat':     52.146196,
                'lon':     5.405488,
            },
            'state': {
                'open':       current_state,
                'lastchange': int(current_state_change),
                'icon': {
                    'open':   BASE_URL+'/open.png',
                    'closed': BASE_URL+'/closed.png',
                }
            },
            'issue_report_channels': [ 'twitter' ],
        }
        self.write(state)

def make_app():
    return tornado.web.Application([
        (r'/statejson', StatejsonHandler),
    ])

if __name__ == '__main__':
    mqttc = mqtt.Client()
    mqttc.connect(MQTT_HOST)
    mqttc.loop_start()

    def on_message(client, userdata, message):
        global current_state, current_state_change
        if message.topic == 'bitlair/state':
            current_state        = message.payload == b'open'
            current_state_change = time.time()
    mqttc.on_message = on_message
    mqttc.subscribe('bitlair/state')

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
