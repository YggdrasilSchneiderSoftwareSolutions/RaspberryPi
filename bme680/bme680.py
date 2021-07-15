import time
import board
import adafruit_bme680
import database
import statistics
import log
import sys

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)

# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1012.0

# for altitude (here not used)
#bme680.seaLevelhPa = 1014.5

# You will usually have to add an offset to account for the temperature of
# the sensor. This is usually around 5 degrees but varies by use. Use a
# separate temperature sensor to calibrate this one.
temperature_offset = -5

# Interval for sending average measurements to database in seconds (min * 60sec)
T_SEND_DB = 300  # 5 min
# Interval for each measurement in seconds
T_MEASUREMENT = 5  # 5 sec
# List for all measurements
data = []
# Counter for passed seconds until sending to database
sec_passed = 0

# Object for holding measurement data
class BME680_Data:
    def __init__(self, temperature, gas, humidity, pressure):
        self.temperature = temperature
        self.gas = gas
        self.humidity = humidity
        self.pressure = pressure


try:
    while True:
        data.append(
            BME680_Data(
                bme680.temperature + temperature_offset,
                bme680.gas,
                bme680.relative_humidity,
                bme680.pressure
                # bme680.altitude
            )
        )

        '''
        print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
        print("Gas: %d ohm" % bme680.gas)
        print("Humidity: %0.1f %%" % bme680.relative_humidity)
        print("Pressure: %0.3f hPa" % bme680.pressure)
        print("Altitude = %0.2f meters" % bme680.altitude)
        '''

        sec_passed += T_MEASUREMENT
        time.sleep(T_MEASUREMENT)

        if sec_passed >= T_SEND_DB:
            # calculate averages
            temperatures = []
            gases = []
            humidities = []
            pressures = []
            for bme_data in data:
                temperatures.append(bme_data.temperature)
                gases.append(bme_data.gas)
                humidities.append(bme_data.humidity)
                pressures.append(bme_data.pressure)

            avg_temperature = statistics.mean(temperatures)
            avg_gas = statistics.mean(gases)
            avg_humidity = statistics.mean(humidities)
            avg_pressure = statistics.mean(pressures)

            database.insert("INSERT INTO BME680 (temperature, gas, humidity, pressure) values (%s, %s, %s, %s)",
                            (avg_temperature, avg_gas, avg_humidity, avg_pressure))
            # reset counter
            sec_passed = 0

except:
    log.error(sys.exc_info()[0])
