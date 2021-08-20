import time
import board
import adafruit_bme680
import requests
import statistics
import log
import sys
import configparser
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont

# setup config
config = configparser.ConfigParser()
config.read('config.ini')

# Backend-URL for database service
DB_SERVICE_URL = 'http://' \
                 + config["production.server"].get("host")\
                 + '/'\
                 + config["production.server"].get("serviceLocation")

# Switch for sending data to database on server
send_to_db = config["DEFAULT"].getboolean("sendDb")

# Counter for scrolling screens
num_screen = 0

# IAQ-Index Integer (oHm)
iaq_index = 0
# IAQ Text
iaq = "..."
# Gas baseline
avg_gas = 0

# BME680
# Create sensor object, communicating over the board's default SPI bus
cs = digitalio.DigitalInOut(board.D25)
spi = board.SPI()
bme680 = adafruit_bme680.Adafruit_BME680_SPI(spi, cs)

# change this to match the location's pressure (hPa) at sea level (possibly for altitude only)
bme680.sea_level_pressure = 1012.0

# for altitude (here not used)
#bme680.seaLevelhPa = 1014.5

# You will usually have to add an offset to account for the temperature of
# the sensor. This is usually around 5 degrees but varies by use. Use a
# separate temperature sensor to calibrate this one.
temperature_offset = -1.5

# Interval for calculating average measurements, gas baseline and sending to database in seconds (min * 60sec)
T_BASE_INTERVAL = 300  # 5 min
# Interval for each measurement in seconds
T_MEASUREMENT = 5  # 5 sec
# List for all measurements
data = []
# Counter for passed seconds until sending to database
sec_passed = 0
# Set the humidity baseline to 40%, an optimal indoor humidity.
hum_baseline = 40.0
# This sets the balance between humidity and gas reading in the
# calculation of air_quality_score (25:75, humidity:gas)
hum_weighting = 0.25

# SSD1306
# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D17)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64  # Change to 32 if needed

# Use for I2C.
i2c = board.I2C()
disp = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c, reset=oled_reset)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (disp.width, disp.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load default font.
#font = ImageFont.load_default()
font = ImageFont.truetype('Minecraftia-Regular.ttf', 10)
font_value = ImageFont.truetype('Minecraftia-Regular.ttf', 23)
font_iaq = ImageFont.truetype('Minecraftia-Regular.ttf', 16)

# Display image
disp.image(image)
disp.show()


# Object for holding measurement data
class BME680_Data:
    def __init__(self, temperature, gas, humidity, pressure):
        self.temperature = temperature
        self.gas = gas
        self.humidity = humidity
        self.pressure = pressure


def get_indoor_air_quality_index(humidity, gas, gas_baseline):
    # references: https://github.com/pimoroni/bme680-python/blob/master/examples/indoor-air-quality.py
    #             https://github.com/G6EJD/BME680-Example
    #             https://forum.iot-usergroup.de/t/indoor-air-quality-index/416/2
    hum_offset = humidity - hum_baseline
    gas_offset = gas_baseline - gas

    # Calculate hum_score as the distance from the hum_baseline.
    if hum_offset > 0:
        hum_score = (100 - hum_baseline - hum_offset)
        hum_score /= (100 - hum_baseline)
        hum_score *= (hum_weighting * 100)

    else:
        hum_score = (hum_baseline + hum_offset)
        hum_score /= hum_baseline
        hum_score *= (hum_weighting * 100)

    # Calculate gas_score as the distance from the gas_baseline.
    if gas_offset > 0:
        gas_score = (gas / gas_baseline)
        gas_score *= (100 - (hum_weighting * 100))

    else:
        gas_score = 100 - (hum_weighting * 100)

    # Calculate air quality in % (100 is best)
    air_quality_index = hum_score + gas_score

    # Calculate air_quality_score (0 is best, 500 worst).
    air_quality_score = (100 - air_quality_index) * 5

    # define air quality
    if air_quality_score >= 301:
        iaq_text = "giftig"
    elif air_quality_score >= 201 and air_quality_score <= 300:
        iaq_text = "sau ungsund"
    elif air_quality_score >= 176 and air_quality_score <= 200:
        iaq_text = "ungsund"
    elif air_quality_score >= 151 and air_quality_score <= 175:
        iaq_text = "bissl schlecht"
    elif air_quality_score >= 51 and air_quality_score <= 150:
        iaq_text = "moderat"
    elif air_quality_score >= 0 and air_quality_score <= 50:
        iaq_text = "guad"
    else:
        iaq_text = ""

    return air_quality_score, iaq_text


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

        last_data = data[-1]
        if avg_gas != 0:
            iaq_index, iaq = get_indoor_air_quality_index(last_data.humidity, last_data.gas, avg_gas)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)

        if num_screen == 0:
            draw.text((2, 0), "Temp:", font=font, fill=255)
            draw.text((32, 4), "%0.1f C" % last_data.temperature, font=font_value, fill=255)
            draw.text((2, 30), "Luftf.:", font=font, fill=255)
            draw.text((32, 38), "%0.1f %%" % last_data.humidity, font=font_value, fill=255)
        elif num_screen == 1:
            draw.text((2, 0), "Druck:", font=font, fill=255)
            draw.text((10, 8), "%0.2f" % last_data.pressure, font=font_value, fill=255)
            draw.text((105, 12), "hPa", font=font, fill=255)
            draw.text((2, 38), "D'Luft is", font=font, fill=255)
            if len(iaq) <= 7:
                draw.text((32, 44), iaq, font=font_iaq, fill=255)
            else:
                draw.text((2, 44), iaq, font=font_iaq, fill=255)

        # TODO binary
        if num_screen == 0:
            num_screen = 1
        elif num_screen == 1:
            num_screen = 0

        # Display image.
        disp.image(image)
        disp.show()

        '''
        print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
        print("Gas: %d ohm" % bme680.gas)
        print("Humidity: %0.1f %%" % bme680.relative_humidity)
        print("Pressure: %0.3f hPa" % bme680.pressure)
        print("Altitude = %0.2f meters" % bme680.altitude)
        '''

        sec_passed += T_MEASUREMENT
        time.sleep(T_MEASUREMENT)

        if sec_passed >= T_BASE_INTERVAL:
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

            iaq_index, iaq = get_indoor_air_quality_index(last_data.humidity, last_data.gas, avg_gas)

            # send to backend
            if send_to_db:
                dataObj = {
                    'temperature': avg_temperature,
                    'gas': avg_gas,
                    'humidity': avg_humidity,
                    'pressure': avg_pressure,
                    'iaq_index': iaq_index,
                    'iaq': iaq
                }

                try:
                    response = requests.post(DB_SERVICE_URL, data=dataObj,
                                             headers={'Content-type': 'application/x-www-form-urlencoded'})

                # Sometimes Raspberry has problems with DNS...
                except requests.exceptions.ConnectionError:
                    log.info('ConnectionError. Possibly problem with DNS')
                    continue

                if response.text != 'success':
                    raise Exception('Error in Backend. Http-status {}, {}'.format(response.status_code, response.text))

            # reset counter
            sec_passed = 0
            # reset data-list
            data = []

except KeyboardInterrupt:  # normal when stopping script
    # Clear display.
    disp.fill(0)
    disp.show()
    pass
except (MemoryError, OSError):  # possible if DNS-Error occurs and we're running out of memory
    log.error(sys.exc_info()[0:2])
    # Clear display.
    disp.fill(0)
    disp.show()
except:
    log.error(sys.exc_info()[0:2])
    # Clear display.
    disp.fill(0)
    disp.show()
