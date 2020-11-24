#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import serial
from serial.tools import list_ports
import time
import platform
import os
import requests
import platform


real_path = os.path.dirname(os.path.realpath(__file__)) + os.sep

def check_device():    
    rx_device = []
    nbiot_device = None
    ports = list_ports.comports()
    for i in ports:
        if i.location in ['1-1.2', '1-1.4']:
            rx_device.append(i.device)
        if i.location in ['1-1.1', '1-1.3']:
            nbiot_device = i.device

    if not nbiot_device:
        print('Nb-IoT not detected')
        os._exit(0)
    else:
        print('Nb-IoT detected')
    if not rx_device:
        print('Reciever not detected')
        os._exit(0)
    elif len(rx_device) == 1:
        print('One reciever detected')
    elif len(rx_device) == 2:
        print('Two reciever detected')
    return rx_device, nbiot_device

def display(w_string):
    w_string = w_string.decode()
    t, id, *sensors = w_string.split(',')
    print('Time: ', t)
    print("Device ID: {}".format(id))
    print('Door status: ', sensors[0])
    print('Water status: ', sensors[1])
    print('Alarm status: ', sensors[2])
    print('Shock status: ', sensors[3])
    print()

def pi_work(rx_device, nbiot_device):
    while True:
        try:
            requests.get('http://www.baidu.com')
        except:
            time.sleep(2)
            continue
        if platform.system == 'Linux':
            os.system('ntpdate -u 0.debian.pool.ntp.org')
            # os.system('date -s "$(wget -qSO- --max-redirect=0 www.baidu.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"')
            # os.system('systemctl stop serial-getty@ttyACM0.service')
            # os.system('systemctl stop serial-getty@ttyUSB0.service')
            print('Time synced')
        break
    rx_sers = []
    for i in rx_device:
        rx_sers.append(serial.Serial(i, 115200))
    nbiot_ser = serial.Serial(nbiot_device, 9600)
    print('Open seial')
    filename = None
    while True:
        for rx_ser in rx_sers:
            line = rx_ser.readline()
            stamp = time.time()
            if not (line.endswith(b'\r\n') and len(line) == 8):
                continue
            t = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(stamp)).encode()
            id = line[:5]
            sensors = line[5]
            sensor = []
            for i in range(4):
                sensor.append(sensors & 0x01)
                sensors = sensors >> 1
            sensor = sensor[::-1]
            w_string = t + b',' + id
            f_string = str(stamp).encode() + b',' + id
            for s in sensor:
                w_string += b',' + str(s).encode()
                f_string += b',' + str(s).encode()
            w_string += b'\r\n'
            f_string += b'\r\n'
            if platform.system() == 'Linux':
                if not filename:
                    filename = t.decode() + '.log'
                with open(real_path + filename, 'ab+') as f:
                    f.write(f_string)
            nbiot_ser.write(w_string)
            display(w_string)


if __name__ == '__main__':
    devices = check_device()
    pi_work(*devices)
