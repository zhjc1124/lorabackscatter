#! /usr/bin/env python3
#-*- coding: utf-8 -*-
import serial
from serial.tools import list_ports
import time
import platform
import os
import requests
import platform
import logging

logger = logging.getLogger()
logger.setLevel('DEBUG')
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel('INFO')  # 也可以不设置，不设置就默认用logger的level
fhlr = logging.FileHandler('/home/pi/my.log') # 输出到文件的handler
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)

real_path = os.path.dirname(os.path.realpath(__file__)) + os.sep

def check_device():    
    active_device = None
    passive_device = None
    nbiot_device = None
    ports = list_ports.comports()
    for i in ports:
        if not i.location:
            continue
        if i.location.startswith('1-1.1'):
            nbiot_device = i.device
        elif i.location.startswith('1-1.2'):
            active_device = i.device
        elif i.location.startswith('1-1.4'):
            passive_device = i.device
    if not nbiot_device:
        logging.error('Nb-IoT not detected')
        os._exit(0)
    else:
        logging.info('Nb-IoT detected: {}'.format(nbiot_device))
    if not active_device and not passive_device:
        logging.error('Reciever not detected')
        os._exit(0)
    logging.info('{} active reciever detected'.format(active_device))
    logging.info('{} passive reciever detected'.format(passive_device))
    return active_device, passive_device, nbiot_device

def display(w_string):
    try:
        w_string = w_string.decode()
    except:
        return
    t, id, *sensors = w_string.split(',')
    logging.info('Time: {}'.format(t))
    logging.info("Device ID: {}".format(id))
    logging.info('Door status: {}'.format(sensors[0]))
    logging.info('Water status: {}'.format(sensors[1]))
    logging.info('Alarm status: {}'.format(sensors[2]))
    logging.info('Shock status: {}'.format(sensors[3]))
    

def pi_work(active_device, passive_device, nbiot_device):

    while True:
        try:
            requests.get('http://www.baidu.com')
            flag = 1
        except:
            time.sleep(2)
            flag = 2
        if platform.system == 'Linux' and flag == 1:
            os.system('ntpdate -u 0.debian.pool.ntp.org')
            # os.system('date -s "$(wget -qSO- --max-redirect=0 www.baidu.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"')
            # os.system('systemctl stop serial-getty@ttyACM0.service')
            # os.system('systemctl stop serial-getty@ttyUSB0.service')
            logging.info('Time synced')
        elif flag == 2:
            l = nbiot_ser.readline()
            print(l)
            os._exit(0)
        break
    nbiot_ser = serial.Serial(nbiot_device, 9600)
    active_device = serial.Serial(active_device, 9600)
    passive_device = serial.Serial(passive_device, 9600)
    logging.info('Open seial')
    filename = None
    current_time = time.time()
    rx_sers = [active_device, passive_device]
    rx_counts = {}
    while True:
        for index, rx_ser in enumerate(rx_sers):
            
            wait = rx_ser.in_waiting
            # print(wait)
            if wait < 6:
                continue
            # print(wait)
            # print(rx_ser)
            line = rx_ser.readline()
            # print(line)
            logging.info('{}'.format(line))
            
            if line in rx_counts:
                rx_counts[line] += 1
            else:
                rx_counts[line] = 1

            stamp = time.time()
            if not (line.startswith(b'txtest')) and not (line.endswith(b'\r\n') and len(line) == 8):
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
            # w_string += b'\r\n'
            # f_string += b'\r\n'
            w_string += b',' + line
            f_string += b',' + line
            if platform.system() == 'Linux':
                if not filename:
                    filename = t.decode() + '.log'
                with open(real_path + filename, 'ab+') as f:
                    f.write(f_string)
            if index == 1:
                nbiot_ser.write(w_string)
            elif rx_counts[line] > 10:
                nbiot_ser.write(w_string)
                rx_counts[line] = 0
                
            display(w_string)


if __name__ == '__main__':
    logging.info('Start!!!!!!')
    devices = check_device()
    pi_work(*devices)
