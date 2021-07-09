'''
    cpu_temp.py

    version 1.0 - 16.03.2020

    Programm liest die CPU-Temperatur des Chips aus
'''

# Imports
from gpiozero import CPUTemperature

# Globale Variablen
cpu = CPUTemperature()
version_nr = 1.0


def get_cpu_temp():
    return cpu.temperature


def print_cpu_temp():
    print('CPU temperature: {}C'.format(cpu.temperature))


if __name__ == '__main__':
    print("CPU-Temp Version", version_nr)
    print_cpu_temp()
