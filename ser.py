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

valid_sn = ['01E19977', '01DF2461']

def check_device():    
    isPi = False
    fsk_device = None
    back_device = None
    ports = list_ports.comports()
    for i in ports:
        if i.vid == 1155:
            fsk_device = i.device
        if i.vid == 6790:
            back_device = i.device
    if not back_device:
        print('WH-NB73 not detected')
        os._exit(0)
    if not fsk_device:
        print('Reciever not detected')
        os._exit(0)
    return fsk_device, back_device

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

def pi_work(fsk_device, back_device):
    while True:
        try:
            requests.get('http://www.baidu.com')
        except:
            time.sleep(2)
            continue
        if platform.system == 'Linux':
            # os.system('ntpdate -u 0.debian.pool.ntp.org')
            os.system('date -s "$(wget -qSO- --max-redirect=0 www.baidu.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"')
            os.system('systemctl stop serial-getty@ttyACM0.service')
            os.system('systemctl stop serial-getty@ttyUSB0.service')
        break
    fsk_ser = serial.Serial(fsk_device, 9600)
    back_ser = serial.Serial(back_device, 9600, timeout=20e-3)
    filename = None
    while True:
        line = fsk_ser.readline()
        stamp = time.time()
        if not (line.endswith(b'\r\n') and len(line) == 8):
            continue
        t = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(stamp)).encode()
        id = line[:5]
        sensors = ~(line[5])
        sensor = []
        for i in range(4):
            sensor.append(sensors & 0x01)
            sensors = sensors >> 1
        sensor = sensor[::-1]
        w_string = t + b',' + id
        for s in sensor:
            w_string += b',' + str(s).encode()
        if platform.system() == 'Linux':
            if not filename:
                filename = t.decode() + '.log'
            with open(real_path + filename, 'wb+') as f:
                f.write(w_string)
        back_ser.write(w_string)
        display(w_string)


if __name__ == '__main__':
    devices = check_device()
    pi_work(*devices)
