#!/usr/bin/env bash

mkdir ~/.homeassistant/custom_components/switch -p
cp esp_board_switch.py ~/.homeassistant/custom_components/switch

mkdir ~/.homeassistant/custom_components/binary_sensor -p
cp esp_board_binary_sensor.py ~/.homeassistant/custom_components/binary_sensor
