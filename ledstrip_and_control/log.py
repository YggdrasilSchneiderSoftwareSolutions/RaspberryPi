'''
    log.py

    version 1.0 - 18.03.2020

    Logging fuer mehrere Szenarien
'''

# Imports
import datetime

# Globale Variablen
ERROR_FILE = "error.log"
LOG_FILE = "application.log"


def error(msg):
    __log_internal(ERROR_FILE, msg)


def info(msg):
    __log_internal(LOG_FILE, msg)


def __log_internal(filename, msg):
    now = datetime.datetime.now()
    f = open(filename, "a+")
    f.write("{} : {}\n".format(now.strftime("%Y-%m-%d %H:%M:%S"), msg))
    f.close()


if __name__ == '__main__':
    print("Erstelle Testfiles")
    info("Test")
    error("Test")
