import logging
import time

import smbus

# from submodules import telemetry
# from submodules import aprs

# from core.mode import Mode
# from core.threadhandler import ThreadHandler
# from functools import partial

import core

import time
try:
    import struct
except ImportError:
    import ustruct as struct

import adafruit_bus_device.spi_device as spi_device
from micropython import const


import board
import busio
import digitalio


spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
xgcs = digitalio.DigitalInOut(board.D5) # Pin connected to XGCS (accel/gyro chip
mcs = digitalio.DigitalInOut(board.D6) # Pin connected to MCS (magnetometer chip
# Internal constants and register values:
# pylint: disable=bad-whitespace
LSM9DS1_ADDRESS_ACCELGYRO       = const(0x6B)
LSM9DS1_ADDRESS_MAG             = const(0x1E)
LSM9DS1_XG_ID                   = const(0b01101000)
LSM9DS1_MAG_ID                  = const(0b00111101)
LSM9DS1_ACCEL_MG_LSB_2G         = 0.061
LSM9DS1_ACCEL_MG_LSB_4G         = 0.122
LSM9DS1_ACCEL_MG_LSB_8G         = 0.244
LSM9DS1_ACCEL_MG_LSB_16G        = 0.732
LSM9DS1_MAG_MGAUSS_4GAUSS       = 0.14
LSM9DS1_MAG_MGAUSS_8GAUSS       = 0.29
LSM9DS1_MAG_MGAUSS_12GAUSS      = 0.43
LSM9DS1_MAG_MGAUSS_16GAUSS      = 0.58
LSM9DS1_GYRO_DPS_DIGIT_245DPS   = 0.00875
LSM9DS1_GYRO_DPS_DIGIT_500DPS   = 0.01750
LSM9DS1_GYRO_DPS_DIGIT_2000DPS  = 0.07000
LSM9DS1_TEMP_LSB_DEGREE_CELSIUS = 8 # 1°C = 8, 25° = 200, etc.
LSM9DS1_REGISTER_WHO_AM_I_XG    = const(0x0F)
LSM9DS1_REGISTER_CTRL_REG1_G    = const(0x10)
LSM9DS1_REGISTER_CTRL_REG2_G    = const(0x11)
LSM9DS1_REGISTER_CTRL_REG3_G    = const(0x12)
LSM9DS1_REGISTER_TEMP_OUT_L     = const(0x15)
LSM9DS1_REGISTER_TEMP_OUT_H     = const(0x16)
LSM9DS1_REGISTER_STATUS_REG     = const(0x17)
LSM9DS1_REGISTER_OUT_X_L_G      = const(0x18)
LSM9DS1_REGISTER_OUT_X_H_G      = const(0x19)
LSM9DS1_REGISTER_OUT_Y_L_G      = const(0x1A)
LSM9DS1_REGISTER_OUT_Y_H_G      = const(0x1B)
LSM9DS1_REGISTER_OUT_Z_L_G      = const(0x1C)
LSM9DS1_REGISTER_OUT_Z_H_G      = const(0x1D)
LSM9DS1_REGISTER_CTRL_REG4      = const(0x1E)
LSM9DS1_REGISTER_CTRL_REG5_XL   = const(0x1F)
LSM9DS1_REGISTER_CTRL_REG6_XL   = const(0x20)
LSM9DS1_REGISTER_CTRL_REG7_XL   = const(0x21)
LSM9DS1_REGISTER_CTRL_REG8      = const(0x22)
LSM9DS1_REGISTER_CTRL_REG9      = const(0x23)
LSM9DS1_REGISTER_CTRL_REG10     = const(0x24)
LSM9DS1_REGISTER_OUT_X_L_XL     = const(0x28)
LSM9DS1_REGISTER_OUT_X_H_XL     = const(0x29)
LSM9DS1_REGISTER_OUT_Y_L_XL     = const(0x2A)
LSM9DS1_REGISTER_OUT_Y_H_XL     = const(0x2B)
LSM9DS1_REGISTER_OUT_Z_L_XL     = const(0x2C)
LSM9DS1_REGISTER_OUT_Z_H_XL     = const(0x2D)
LSM9DS1_REGISTER_WHO_AM_I_M     = const(0x0F)
LSM9DS1_REGISTER_CTRL_REG1_M    = const(0x20)
LSM9DS1_REGISTER_CTRL_REG2_M    = const(0x21)
LSM9DS1_REGISTER_CTRL_REG3_M    = const(0x22)
LSM9DS1_REGISTER_CTRL_REG4_M    = const(0x23)
LSM9DS1_REGISTER_CTRL_REG5_M    = const(0x24)
LSM9DS1_REGISTER_STATUS_REG_M   = const(0x27)
LSM9DS1_REGISTER_OUT_X_L_M      = const(0x28)
LSM9DS1_REGISTER_OUT_X_H_M      = const(0x29)
LSM9DS1_REGISTER_OUT_Y_L_M      = const(0x2A)
LSM9DS1_REGISTER_OUT_Y_H_M      = const(0x2B)
LSM9DS1_REGISTER_OUT_Z_L_M      = const(0x2C)
LSM9DS1_REGISTER_OUT_Z_H_M      = const(0x2D)
LSM9DS1_REGISTER_CFG_M          = const(0x30)
LSM9DS1_REGISTER_INT_SRC_M      = const(0x31)
MAGTYPE                         = True
XGTYPE                          = False
SENSORS_GRAVITY_STANDARD        = 9.80665

# User facing constants/module globals.
ACCELRANGE_2G                = (0b00 << 3)
ACCELRANGE_16G               = (0b01 << 3)
ACCELRANGE_4G                = (0b10 << 3)
ACCELRANGE_8G                = (0b11 << 3)
MAGGAIN_4GAUSS               = (0b00 << 5)  # +/- 4 gauss
MAGGAIN_8GAUSS               = (0b01 << 5)  # +/- 8 gauss
MAGGAIN_12GAUSS              = (0b10 << 5)  # +/- 12 gauss
MAGGAIN_16GAUSS              = (0b11 << 5)  # +/- 16 gauss
GYROSCALE_245DPS             = (0b00 << 3)  # +/- 245 degrees/s rotation
GYROSCALE_500DPS             = (0b01 << 3)  # +/- 500 degrees/s rotation
GYROSCALE_2000DPS            = (0b11 << 3)  # +/- 2000 degrees/s rotation
# pylint: enable=bad-whitespace
BUFFER = bytearray(6)


def twos_comp(val, bits):
    # Convert an unsigned integer in 2's compliment form of the specified bit
    # length to its signed integer value and return it.
    if val & (1 << (bits - 1)) != 0:
        return val - (1 << bits)
    return val
    
def start():
    # soft reset & reboot accel/gyro
    write_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG8, 0x05)
    # soft reset & reboot magnetometer
    write_u8(MAGTYPE, LSM9DS1_REGISTER_CTRL_REG2_M, 0x0C)
    time.sleep(0.01)
    # Check ID registers.
    if read_u8(XGTYPE, LSM9DS1_REGISTER_WHO_AM_I_XG) != LSM9DS1_XG_ID or \
        read_u8(MAGTYPE, LSM9DS1_REGISTER_WHO_AM_I_M) != LSM9DS1_MAG_ID:
        raise RuntimeError('Could not find LSM9DS1, check wiring!')
    # enable gyro continuous
    write_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG1_G, 0xC0) # on XYZ
    # Enable the accelerometer continous
    write_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG5_XL, 0x38)
    write_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG6_XL, 0xC0)
    # enable mag continuous
    write_u8(MAGTYPE, LSM9DS1_REGISTER_CTRL_REG3_M, 0x00)
    # Set default ranges for the various sensors
    accel_mg_lsb = None
    mag_mgauss_lsb = None
    gyro_dps_digit = None
    accel_range = ACCELRANGE_2G
    mag_gain = MAGGAIN_4GAUSS
    gyro_scale = GYROSCALE_245DPS
    mag_device = spi_device.SPIDevice(spi, mcs, baudrate=200000, phase=1, polarity=1)
    xg_device = spi_device.SPIDevice(spi, xgcs, baudrate=200000, phase=1, polarity=1)

#getter
def accel_range():
    """The accelerometer range.  Must be a value of:
        - ACCELRANGE_2G
        - ACCELRANGE_4G
        - ACCELRANGE_8G
        - ACCELRANGE_16G
    """
    reg = read_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG6_XL)
    return (reg & 0b00011000) & 0xFF

#setter
def accel_range(val):
    assert val in (ACCELRANGE_2G, ACCELRANGE_4G, ACCELRANGE_8G,
                    ACCELRANGE_16G)
    reg = read_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG6_XL)
    reg = (reg & ~(0b00011000)) & 0xFF
    reg |= val
    write_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG6_XL, reg)
    if val == ACCELRANGE_2G:
        _accel_mg_lsb = LSM9DS1_ACCEL_MG_LSB_2G
    elif val == ACCELRANGE_4G:
        _accel_mg_lsb = LSM9DS1_ACCEL_MG_LSB_4G
    elif val == ACCELRANGE_8G:
        _accel_mg_lsb = LSM9DS1_ACCEL_MG_LSB_8G
    elif val == ACCELRANGE_16G:
        _accel_mg_lsb = LSM9DS1_ACCEL_MG_LSB_16G

#getter
def mag_gain():
    """The magnetometer gain.  Must be a value of:
        - MAGGAIN_4GAUSS
        - MAGGAIN_8GAUSS
        - MAGGAIN_12GAUSS
        - MAGGAIN_16GAUSS
    """
    reg = read_u8(MAGTYPE, LSM9DS1_REGISTER_CTRL_REG2_M)
    return (reg & 0b01100000) & 0xFF

#setter
def mag_gain(val):
    assert val in (MAGGAIN_4GAUSS, MAGGAIN_8GAUSS, MAGGAIN_12GAUSS,
                    MAGGAIN_16GAUSS)
    reg = read_u8(MAGTYPE, LSM9DS1_REGISTER_CTRL_REG2_M)
    reg = (reg & ~(0b01100000)) & 0xFF
    reg |= val
    write_u8(MAGTYPE, LSM9DS1_REGISTER_CTRL_REG2_M, reg)
    if val == MAGGAIN_4GAUSS:
       mag_mgauss_lsb = LSM9DS1_MAG_MGAUSS_4GAUSS
    elif val == MAGGAIN_8GAUSS:
       mag_mgauss_lsb = LSM9DS1_MAG_MGAUSS_8GAUSS
    elif val == MAGGAIN_12GAUSS:
       mag_mgauss_lsb = LSM9DS1_MAG_MGAUSS_12GAUSS
    elif val == MAGGAIN_16GAUSS:
       mag_mgauss_lsb = LSM9DS1_MAG_MGAUSS_16GAUSS

#getter
def gyro_scale():
    """The gyroscope scale.  Must be a value of:
        - GYROSCALE_245DPS
        - GYROSCALE_500DPS
        - GYROSCALE_2000DPS
    """
    reg = read_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG1_G)
    return (reg & 0b00011000) & 0xFF

#setter
def gyro_scale(val):
    assert val in (GYROSCALE_245DPS, GYROSCALE_500DPS, GYROSCALE_2000DPS)
    reg = read_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG1_G)
    reg = (reg & ~(0b00011000)) & 0xFF
    reg |= val
    write_u8(XGTYPE, LSM9DS1_REGISTER_CTRL_REG1_G, reg)
    if val == GYROSCALE_245DPS:
        _gyro_dps_digit = LSM9DS1_GYRO_DPS_DIGIT_245DPS
    elif val == GYROSCALE_500DPS:
        _gyro_dps_digit = LSM9DS1_GYRO_DPS_DIGIT_500DPS
    elif val == GYROSCALE_2000DPS:
        _gyro_dps_digit = LSM9DS1_GYRO_DPS_DIGIT_2000DPS

def read_accel_raw():
    read_bytes(XGTYPE, 0x80 | LSM9DS1_REGISTER_OUT_X_L_XL, 6,
                        BUFFER)
    raw_x, raw_y, raw_z = struct.unpack_from('<hhh', BUFFER[0:6])
    return (raw_x, raw_y, raw_z)

def acceleration():
    raw = read_accel_raw()
    return map(lambda x: x * _accel_mg_lsb / 1000.0 * SENSORS_GRAVITY_STANDARD,
                raw)

def read_mag_raw():
    read_bytes(MAGTYPE, 0x80 | LSM9DS1_REGISTER_OUT_X_L_M, 6,
                        BUFFER)
    raw_x, raw_y, raw_z = struct.unpack_from('<hhh', BUFFER[0:6])
    return (raw_x, raw_y, raw_z)


def magnetic():
    raw = read_mag_raw()
    return map(lambda x: x *mag_mgauss_lsb / 1000.0, raw)

def read_gyro_raw():
    read_bytes(XGTYPE, 0x80 | LSM9DS1_REGISTER_OUT_X_L_G, 6,
                        BUFFER)
    raw_x, raw_y, raw_z = struct.unpack_from('<hhh', BUFFER[0:6])
    return (raw_x, raw_y, raw_z)

@property
def gyro():
    raw = read_gyro_raw()
    return map(lambda x: x * _gyro_dps_digit, raw)

def read_temp_raw():
    read_bytes(XGTYPE, 0x80 | LSM9DS1_REGISTER_TEMP_OUT_L, 2,
                        BUFFER)
    temp = ((BUFFER[1] << 8) | BUFFER[0]) >> 4
    return twos_comp(temp, 12)

def temperature():

    temp = read_temp_raw()
    temp = 27.5 + temp/16
    return temp

def read_u8(sensor_type, address):
    if sensor_type = MAGTYPE:
        device =mag_device
    else:
        device = xg_device
    with device as spi:
        BUFFER[0] = (address | 0x80) & 0xFF
        spi.write(BUFFER, end=1)
        spi.readinto(BUFFER, end=1)
    return BUFFER[0]

def read_bytes(sensor_type, address, count, buf):
    if sensor_type ==MAGTYPE:
        device =mag_device
    else:
        device = xg_device
    with device as spi:
        buf[0] = (address | 0x80) & 0xFF
        spi.write(buf, end=1)
        spi.readinto(buf, end=count)

def write_u8(sensor_type, address, val):
    if sensor_type ==MAGTYPE:
        device =mag_device
    else:
        device = xg_device
    with device as spi:
        BUFFER[0] = (address & 0x7F) & 0xFF
        BUFFER[1] = val & 0xFF
        spi.write(BUFFER, end=2)


if __name__ == '__main__':
    start()