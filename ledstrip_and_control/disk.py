'''
    disk.py

    version 1.0 - 16.03.2020

    Programm liefert Informationen zum Speicher
'''

# Imports
from gpiozero import DiskUsage

# Globale Variablen
disk = DiskUsage()
version_nr = 1.0


def get_disk_usage():
    return disk.usage


def print_disk_usage():
    print('Current disk usage: {}%'.format(disk.usage))


if __name__ == '__main__':
    print("Disk Version", version_nr)
    print_disk_usage()
