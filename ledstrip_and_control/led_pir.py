'''
    led_pir.py

    version 1.1 - 20.03.2020: Wechsel von os auf subprocess
    version 1.0 - 14.03.2020

    Programm lauscht via PIR-Sensor auf Bewegung und schaltet LED-Streifen durch
    De-/ Aktivierung des USB-Hubs
'''

# Imports
from gpiozero import MotionSensor
import time
import subprocess
import log
import sys
import shlex

# Globale Variablen
pir = MotionSensor(4)
usb_is_active = False
version_nr = 1.0


def usb_power_on():
    cmd = shlex.split("sudo uhubctl/./uhubctl -p 2 -a 1 -l 1-1")
    out = subprocess.call(cmd)
    print(out)


def usb_power_off():
    cmd = shlex.split("sudo uhubctl/./uhubctl -p 2 -a 0 -l 1-1")
    out = subprocess.call(cmd)
    print(out)


def usb_hub_info():
    cmd = shlex.split("sudo uhubctl/./uhubctl")
    out = subprocess.call(cmd)
    print(out)


def on_motion_detected():
    global usb_is_active
    if usb_is_active is True:
        return

    # USB-Hub power on
    usb_is_active = True
    usb_power_on()

    # 30 Sekunden LED anlassen
    print("LED aktiviert fuer 30 Sekunden")
    time.sleep(30)

    # USB-Hub power off
    usb_is_active = False
    usb_power_off()


def check_sensor():
    print("PIR wait_for_motion")
    pir.wait_for_motion()
    print("motion detected")


if __name__ == '__main__':
    try:
        print("LED-PIR Version", version_nr)
        print("Initialisiere Programm...USB-Hub power off")
        usb_power_off()
        usb_hub_info()
        print("LED-PIR Detector gestartet")
        log.info("LED-PIR gestartet")

        while True:
            print("PIR lauscht...")
            pir.wait_for_motion()
            # pir.when_motion = on_motion_detected
            on_motion_detected()
    except:
        exctype, value = sys.exc_info()[:2]
        print("Fehler in Hauptprogramm: {} {}".format(exctype, value))
        log.error("{} {}".format(exctype, value))
