from homeassistant import loader
from homeassistant.components.binary_sensor.mqtt import MqttBinarySensor
from itertools import chain
import json

DEPENDENCIES = ['mqtt']


def with_family(family):
    def set_family(device):
        device['family'] = family
        return device

    return set_family


def read_only(switch):
    return switch['access'] == 'readonly'


def setup_platform(hass, config, add_devices, discovery_info=None):
    registered_boards = {}

    def connected(topic, payload, qos):
        serial = topic[0:topic.find('/')]
        if serial in registered_boards:
            if registered_boards[serial] != payload:
                hass.services.call('homeassistant', 'restart')
        else:
            board_config = json.loads(payload)
            devices = chain(map(with_family('switches'), filter(read_only, board_config['switches'])),
                            map(with_family('sensors'), board_config['sensors']))
            add_devices(MqttBinarySensor(
                hass=hass,
                name=device['name'],
                state_topic='{}/{}/{}'.format(serial, device['family'], device['topic']),
                sensor_class=device['type'] if device['type'] != 'generic' else None,
                qos=0,
                payload_on='ON',
                payload_off='OFF',
                value_template=None
            ) for device in devices)
            registered_boards[serial] = payload

    loader.get_component('mqtt').subscribe(hass, '+/config', connected)
