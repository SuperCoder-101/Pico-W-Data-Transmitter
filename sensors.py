# sensors.py
# Environmental sensor reader
# MicroPython / Raspberry Pi Pico W
#
# Copyright (c) 2026 Sophia J Anderson
#
# Reads temperature and humidity data from HDC302x sensors
# and a BME280 sensor over I2C. Applies humidity calibration
# offsets, prints formatted sensor readings, and returns data
# for logging.
#
# This file is part of Sophia J Anderson's & Nolan Hoffs environmental monitoring project.

import time
from machine import Pin, I2C

import adafruit_hdc302x
import qwiic_bme280
from qwiic_bme280 import QwiicBme280


def prints():
    #Initialize sensors and buses

    # I2C bus 0
    i2c0 = I2C(0,scl=Pin(1),sda=Pin(0),freq=100000)
    # I2C bus 1
    i2c1 = I2C(1,scl=Pin(7),sda=Pin(6),freq=100000)

    bme280 = qwiic_bme280.QwiicBme280(address=i2c0)
    bme280.begin()


    # Humidity calibration offsets
    HUMIDITY_OFFSETS = [-6.8,-5.5,-7.6]
    
    # HDC320x List
    temperatures0 = []
    humidities0 = []
    
    # BME280 List
    get_temperature_celsius1 = []
    get_humidity1 = []


    # Sensor list
    sensors0 = [

        # Bus 1 sensors
        ("Sensor 1","0x44",adafruit_hdc302x.HDC302X(i2c1,address=0x44)),
        ("Sensor 2","0x45",adafruit_hdc302x.HDC302X(i2c1,address=0x45)),
        ("Sensor 4","0x47",adafruit_hdc302x.HDC302X(i2c1,address=0x47)),

    ]

    sensors1 = [
        
        # Bus 0 sensor
        ("Sensor 4","0x77", bme280)
        
    ]
    
    # HDC320x Index
    for index, (sensor_name, sensor_address, sensor) in enumerate(sensors0):

            try:
                temperature = sensor.temperature
                humidity = (sensor.relative_humidity + HUMIDITY_OFFSETS[index])

                temperatures0.append(temperature)
                humidities0.append(humidity)

            except Exception as e:
                print("[SENSOR ERROR]", sensor_name, e)

                temperatures0.append(0.0)
                humidities0.append(0.0)
                
    # BME280 Index
    for index, (sensor_name1, sensor_address1, sensor1) in enumerate(sensors1):

            try:
                temperature_celsius = sensor1.get_temperature_celsius()
                humidity = (sensor1.get_humidity())

                get_temperature_celsius1.append(temperature_celsius)
                get_humidity1.append(humidity)

            except Exception as e:
                print("[SENSOR ERROR]", sensor_name1, e)

                get_temperature_celsius1.append(0.0)
                get_humidity1.append(0.0)

    # Timestamps
    now = time.localtime()

    timestamp = ("{:04d}-{:02d}-{:02d}  {:02d}:{:02d}:{:02d}").format(now[0],now[1],now[2],now[3],now[4],now[5])

    # Print statements
    print()
    print("=============== TEMPERATURE LOG ROW ==============")
    print("Timestamp	     | Sensor 1 | Sensor 2 | Sensor 3 |")
    print("{} |  {:.2f}°C |  {:.2f}°C |  {:.2f}°C |".format(timestamp,temperatures0[0],temperatures0[1],temperatures0[2]))

    print()
    print("=============== HUMIDITY LOG ROW ==============")
    print("Timestamp	     | Sensor 1 | Sensor 2 | Sensor 3 |")
    print("{} |  {:.2f}%  |  {:.2f}%  |  {:.2f}%  |".format(timestamp,humidities0[0],humidities0[1],humidities0[2]))

    print("=================================================")
        
    print()
    print("====TEMP & HUMD====")
    print("Timestamp	     | BME280 TEMP| BME280 HUMD |")
    print("{} |   {:.2f}°C  |   {:.2f}%    |".format(timestamp, get_temperature_celsius1[0], get_humidity1[0]))
    print()
    
    return (timestamp, temperatures0, humidities0, get_temperature_celsius1[0], get_humidity1[0])
