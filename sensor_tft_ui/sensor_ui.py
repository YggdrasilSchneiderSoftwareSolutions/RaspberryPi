# Displaying sensor data on a 3.5" (480x320) TFT

# Import and initialize the pygame library and MQTT
import pygame
import os
import paho.mqtt.client as mqtt
import json


MQTT_SERVER = "127.0.0.1"
MQTT_PATH = "bme680_channel"

WIDTH = 480
HEIGHT = 320
MID_SCREEN = WIDTH // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (144, 238, 144)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
MAROON = (128, 0, 0)

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.mouse.set_visible(False)

clock = pygame.time.Clock()

# Fonts
font_label = pygame.font.SysFont("Arial", 30)
font_data = pygame.font.SysFont("Arial", 64, True)
font_long_data = pygame.font.SysFont("Arial", 50, True)

# Labels
label_temp = font_label.render("Temperatur", True, WHITE)
label_pressure = font_label.render("Luftdruck", True, WHITE)
label_humidity = font_label.render("Luftfeuchtigkeit", True, WHITE)
label_iaq = font_label.render("IAQ", True, WHITE)
label_co2 = font_label.render("CO2-Gehalt", True, WHITE)

received_temperature = 0.0
received_pressure = 0.0
received_humidity = 0.0
received_iaq = 450
received_co2 = 2000


def get_indoor_air_quality_text(air_quality_score):
    # Define air quality. Reference: https://forum.iot-usergroup.de/t/indoor-air-quality-index/416/2
    if air_quality_score >= 301:
        iaq_text = "Sehr schlecht"
        iaq_color = MAROON
    elif 201 <= air_quality_score <= 300:
        iaq_text = "Sehr ungesund"
        iaq_color = PURPLE
    elif 176 <= air_quality_score <= 200:
        iaq_text = "Ungesund"
        iaq_color = RED
    elif 151 <= air_quality_score <= 175:
        iaq_text = "Schlecht"
        iaq_color = ORANGE
    elif 51 <= air_quality_score <= 150:
        iaq_text = "Mittelmäßig"
        iaq_color = YELLOW
    elif 0 <= air_quality_score <= 50:
        iaq_text = "Gut"
        iaq_color = GREEN
    else:
        iaq_text = ""
        iaq_color = BLACK

    return iaq_text, iaq_color


def get_co2_quality_level_text(co2_ppm):
    # Define CO2 level. Reference: https://www.cik-solutions.com/anwendungen/co2-im-innenraum/
    if co2_ppm < 800:
        co2_level_text = "Niedrig"
        co2_level_color = GREEN
    elif 800 > co2_ppm <= 1000:
        co2_level_text = "Mittel"
        co2_level_color = LIGHT_GREEN
    elif 1000 > co2_ppm <= 1400:
        co2_level_text = "Mäßig"
        co2_level_color = YELLOW
    else:
        co2_level_text = "Hoch"
        co2_level_color = RED

    return co2_level_text, co2_level_color


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # more callbacks, etc
    # '{"temperature":"23.5","pressure":"945.6","humidity":"43.5","iaq":"34","co2":"200"}'
    payload = msg.payload
    json_data = json.loads(payload)
    global received_temperature
    global received_pressure
    global received_humidity
    global received_iaq
    global received_co2
    received_temperature = float(json_data['temperature'])
    received_pressure = float(json_data['pressure'])
    received_humidity = float(json_data['humidity'])
    received_iaq = int(json_data['iaq'])
    received_co2 = int(json_data['co2'])


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_SERVER, 1883, 60)

# Non-blocking
mqtt_client.loop_start()


# Run until the user asks to quit
running = True
while running:
    try:
        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background with white
        screen.fill((0, 0, 0))

        # Draw labels
        screen.blit(label_temp, (15, 20))
        screen.blit(label_pressure, (15, 75))
        screen.blit(label_humidity, (15, 130))
        screen.blit(label_iaq, (15, 185))
        screen.blit(label_co2, (15, 240))

        # Draw data
        data_label_temp = font_data.render("%0.1f C" % received_temperature, True, WHITE)
        data_label_pressure = font_data.render("%0.2f hPa" % received_pressure, True, WHITE)
        data_label_humidity = font_data.render("%0.1f %%" % received_humidity, True, WHITE)

        _label_iaq, _label_iaq_color = get_indoor_air_quality_text(received_iaq)
        if len(_label_iaq) > 8:
            data_label_iaq = font_long_data.render(_label_iaq, True, _label_iaq_color)
        else:
            data_label_iaq = font_data.render(_label_iaq, True, _label_iaq_color)

        _label_co2, _label_co2_color = get_co2_quality_level_text(received_co2)
        data_label_co2 = font_data.render(_label_co2, True, _label_co2_color)

        screen.blit(data_label_temp, (MID_SCREEN, 15))
        screen.blit(data_label_pressure, (MID_SCREEN, 75))
        screen.blit(data_label_humidity, (MID_SCREEN, 135))
        screen.blit(data_label_iaq, (MID_SCREEN, 195))
        screen.blit(data_label_co2, (MID_SCREEN, 255))

        # Flip the display
        pygame.display.update()

        clock.tick(30)

    except KeyboardInterrupt:
        running = False

pygame.quit()
mqtt_client.loop_stop()
exit(0)
