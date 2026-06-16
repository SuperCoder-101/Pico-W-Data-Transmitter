# SD_Card.py
# Simple MicroPython SD card manager
# Raspberry Pi Pico W
#
# Copyright (c) 2026 Sophia J Anderson
#
# Handles SD card SPI setup, card detection, mounting,
# unmounting, safe file writes, and shared SD access state.
#
# This file is part of Sophia J Anderson's & Nolan Hoffs environmental monitoring project.

from machine import Pin, SPI
import sdcard
import os
import time

# SD detect pin
det = Pin(8, Pin.IN, Pin.PULL_UP)

# SPI setup
spi = SPI(
    1,
    baudrate=1_000_000,  #This is not baudrate the library just calls this baudrate... this is actually freq
    polarity=0,
    phase=0,
    bits=8,
    firstbit=SPI.MSB,
    sck=Pin(10),
    mosi=Pin(11),
    miso=Pin(12)
)

# CS pin
cs = Pin(13, Pin.OUT)

# Global SD state
sd_safe = True
sd_mounted = False

sd = None
vfs = None

# Simple software lock
_sd_lock = False

# Compatibility export
sd_busy = False


# Try to acquire SD lock
def _try_lock():

    global _sd_lock

    if _sd_lock:
        return False

    _sd_lock = True

    return True


# Release SD lock
def _unlock():

    global _sd_lock

    _sd_lock = False


# Check if SD operations active
def is_writing():

    return _sd_lock


# Block SD activity
def sd_block():

    global sd_safe

    sd_safe = False


# Unblock SD activity
def sd_unblock():

    global sd_safe

    sd_safe = True


# Check if SD card inserted
def card_inserted():

    # DET goes HIGH when card inserted
    return det.value() == 1


# Placeholder LED updater
def update_led():

    pass


# Reset SPI bus
def reset_spi():

    global spi

    try:

        spi = SPI(
            1,
            baudrate=1_000_000, #This is not baudrate the library just calls this baudrate... this is actually freq
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SPI.MSB,
            sck=Pin(10),
            mosi=Pin(11),
            miso=Pin(12)
        )

        time.sleep(0.1)

    except Exception as e:

        print("[SD] SPI reset failed:", e)


# Mount SD card
def mount_sd():

    global sd_mounted
    global sd
    global vfs

    if not sd_safe:
        return False

    if sd_mounted:
        return True

    if not card_inserted():

        print("[SD] No SD card detected")

        return False

    if not _try_lock():
        return False

    try:

        reset_spi()

        time.sleep(0.2)

        # Initialize SD card
        sd = sdcard.SDCard(spi, cs)

        # Mount filesystem
        vfs = os.VfsFat(sd)

        os.mount(vfs, "/sd")

        sd_mounted = True

        print("[SD] Mounted successfully")

    except Exception as e:

        print("[SD] Mount failed:", e)

        sd_mounted = False

        return False

    finally:

        _unlock()

    return sd_mounted


# Unmount SD card
def unmount_sd():

    global sd_mounted
    global sd
    global vfs

    if not sd_mounted:
        return

    if not _try_lock():
        return

    try:

        try:

            os.umount("/sd")

            print("[SD] Unmounted")

        except Exception as e:

            print("[SD] Unmount failed:", e)

        sd_mounted = False

        sd = None
        vfs = None

    finally:

        _unlock()


# Auto monitor
def update():

    if not sd_safe:
        return

    if not sd_mounted:

        mount_sd()


# Initialize SD system
def init():

    update()


# Fallback error logger
def log_error_fallback(msg):

    if not sd_mounted:
        return False

    if not _try_lock():
        return False

    try:

        with open(
            "/sd/error_fallback.txt", "a") as f:

            f.write(msg + "\n")

            f.flush()

        return True

    except Exception as e:

        print("[SD] Fallback log failed:", e)

        return False

    finally:

        _unlock()


# Safe log writer
def write_log_line(filepath, line, header=None, timestamp=None):

    global sd_mounted

    if not sd_safe:
        return False

    if not sd_mounted:

        update()

        if not sd_mounted:
            return False

    if not _try_lock():
        return False

    try:

        write_header = False

        try:

            st = os.stat(filepath)

            if st[6] == 0:
                write_header = True

        except OSError:

            write_header = True

        with open(filepath, "a") as f:

            # Write CSV header
            if header and write_header:

                f.write(header + "\n")

            # Write log line
            if timestamp is not None:

                f.write("[{}] {}\n".format(timestamp, line))

            else:

                f.write(line + "\n")

            f.flush()

        return True

    except Exception as e:

        print("[SD] Write failed:", e)

        return False

    finally:

        _unlock()


# Public exports
__all__ = [

    "init",
    "update",
    "mount_sd",
    "unmount_sd",
    "write_log_line",
    "log_error_fallback",
    "sd_block",
    "sd_unblock",
    "sd_mounted",
    "is_writing",
    "sd_busy",
    "spi",
    "cs"
]

