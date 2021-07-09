'''
    control.py

    version 1.0 - 17.03.2020

    Programm ueber das alle Services gesteuert werden koennen
'''

# Imports
import led_pir
import cpu_temp
import disk
import datetime
import time
import os

# Globale Variablen
version_nr = 1.0


def start_cpu_temp_interval(sec):
    if not sec.isdigit():
        print("Interval nicht numerisch, default = 5")
        sec = 5
    else:
        sec = int(sec)

    for i in range(sec):
        cpu_temp.print_cpu_temp()
        time.sleep(1)


def start_led_pir():
    os.popen("sudo python3 led_pir.py&")
    print("led_pir.py gestartet")


def stop_led_pir():
    os.popen("sudo pkill -9 -f led_pir.py")
    print("led_pir.py gestoppt")


def start_disk():
    disk.print_disk_usage()


def show_python_processes():
    cmd_stream = os.popen("sudo ps -ef | grep python")
    output = cmd_stream.read()
    print(output)


def get_user_input():
    userinput = ""
    while not userinput.isdigit():
        userinput = input("~: ")

        if not userinput.isdigit():
            print("Ungültige Eingabe")

    return userinput


def test_pir():
    led_pir.check_sensor()


def main_menu():
    print("Bitte Funktion wählen")
    print("\t1  - led_pir.py starten")
    print("\t2  - led_pir.py stoppen")
    print("\t3  - cpu_temp.py für x Sekunden starten")
    print("\t4  - disk.py starten")
    print("\t5  - Python-Prozesse anzeigen")
    print()
    print("\t91 - Test PIR")
    print("\t99 - Beenden")

    option = get_user_input()
    if option == "1":
        start_led_pir()
    elif option == "2":
        stop_led_pir()
    elif option == "3":
        print("Bitte Interval in Sekunden angeben")
        interval = input("~: ")
        start_cpu_temp_interval(interval)
    elif option == "4":
        start_disk()
    elif option == "5":
        show_python_processes()
    elif option == "91":
        test_pir()
    elif option == "99":
        exit(0)
    else:
        raise Exception("Programmfehler bei Benutzereingabe")


def startup():
    today = datetime.datetime.now()
    print("###########################################################")
    print("#               Raspberry Pi Control Panel                #")
    print("#                                                         #")
    print("#       Version {}                                       #".format(version_nr))
    print("#                                              {} #".format(today.strftime("%Y-%m-%d")))
    print("###########################################################")


if __name__ == '__main__':
    print("Starte Hauptprogramm")
    try:
        startup()
        while True:
            main_menu()
    except Exception as e:
        print("Fehler in Hauptprogramm:", str(e))
    finally:
        exit(1)
