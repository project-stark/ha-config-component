from homeassistant import loader
from homeassistant.components.switch.mqtt import MqttSwitch
from itertools import chain
import json

DEPENDENCIES = ['mqtt']


def with_family(family):
    def set_family(device):
        device['family'] = family
        return device

    return set_family


def read_write(switch):
    return switch['access'] == 'readwrite'


def setup_platform(hass, config, add_devices, discovery_info=None):
    registered_boards = {}

    def connected(topic, payload, qos):
        serial = topic[0:topic.find('/')]
        if serial in registered_boards:
            if registered_boards[serial] != payload:
                hass.services.call('homeassistant', 'restart')
        else:
            board_config = json.loads(payload)
            devices = chain(map(with_family('switches'), filter(read_write, board_config['switches'])),
                            map(with_family('actuators'), board_config['actuators']))
            add_devices(MqttSwitch(
                hass=hass,
                name=device['name'],
                state_topic='{}/{}/{}'.format(serial, device['family'], device['topic']),
                command_topic='{}/{}/{}/set'.format(serial, device['family'], device['topic']),
                qos=0,
                retain=True,
                payload_on='ON',
                payload_off='OFF',
                optimistic=False,
                value_template=None
            ) for device in devices)
            registered_boards[serial] = payload

    loader.get_component('mqtt').subscribe(hass, '+/config', connected)
