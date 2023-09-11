import json
import time

from prometheus_client import start_http_server, Gauge

class WeatherPi:

    def __init__(self, fname="/mnt/metrics/weatherbit.json", interval=15.0):
        self.polling_interval = interval

        # Get data from file
        self.fname = fname
        self.data = {}
        with open(self.fname, 'r') as f:
            self.data = json.load(f)
            self.data = self.data['avg_15s']

        # Metrics to collect
        self.weatherbit_temperature = Gauge('weatherbit_temperature', 'Temperature from Weatherbit sensor')
        self.microbit_temperature = Gauge('microbit_temperature', 'Temperature from Microbit sensor')
        self.weatherbit_humidity = Gauge('weatherbit_humidity', 'Humidity from Weatherbit sensor')
        self.weatherbit_pressure = Gauge('weatherbit_pressure', 'Pressure from Weatherbit sensor')
        self.weatherbit_wind_speed = Gauge('weatherbit_wind_speed', 'Wind speed from Weatherbit sensor')
        self.weatherbit_wind_gust = Gauge('weatherbit_wind_gust', 'Wind gust from Weatherbit sensor')
        self.weatherbit_wind_direction = Gauge('weatherbit_wind_direction', 'Wind direction from Weatherbit sensor')
        self.weatherbit_rainfall = Gauge('weatherbit_rainfall', 'Rainfall from Weatherbit sensor')
        self.microbit_light = Gauge('microbit_light', 'Light from Microbit sensor')

    def update(self, interval=5.0):
        with open(self.fname, 'r') as f:
            data = json.load(f)
            self.data = data['avg_15s']
        self.weatherbit_temperature.set(self.data['weatherbit_temperature'])
        self.microbit_temperature.set(self.data['microbit_temperature'])
        self.weatherbit_humidity.set(self.data['humidity'])
        self.weatherbit_pressure.set(self.data['pressure'])
        self.weatherbit_wind_speed.set(self.data['wind_speed'])
        self.weatherbit_wind_gust.set(self.data['wind_gust'])
        self.weatherbit_wind_direction.set(self.data['wind_direction'])
        self.weatherbit_rainfall.set(self.data['rainfall'])
        self.microbit_light.set(self.data['light'])


    def run_loop(self):
        while True:
            self.update(self.polling_interval)
            time.sleep(self.polling_interval)


def main():
    polling_interval = 15.0
    weatherpi = WeatherPi("/mnt/metrics/weatherbit.json", polling_interval)
    start_http_server(9109)
    weatherpi.run_loop()


if __name__ == '__main__':
    main()
