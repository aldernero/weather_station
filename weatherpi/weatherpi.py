import time

import bme680
import bme680.constants

from prometheus_client import start_http_server, Gauge

from bme680IAQ import *

class WeatherPi:
    TEMPERATURE_OFFSET_BME680 = -2.6

    def __init__(self, interval=15.0):
        self.polling_interval = interval

        # Configure sensor
        self.sensor_bme680 = bme680.BME680(0x77)
        self.sensor_bme680.set_temp_offset(self.TEMPERATURE_OFFSET_BME680)
        self.sensor_bme680.set_gas_status(bme680.constants.ENABLE_GAS_MEAS)
        self.sensor_bme680.set_gas_heater_temperature(320)  # middle of range (200 - 400)
        self.sensor_bme680.set_gas_heater_duration(150)     # half a second
        self.sensor_bme680.set_humidity_oversample(bme680.constants.OS_2X)
        self.sensor_bme680.set_pressure_oversample(bme680.constants.OS_4X)
        self.sensor_bme680.set_temperature_oversample(bme680.constants.OS_8X)
        self.sensor_bme680.set_filter(bme680.constants.FILTER_SIZE_3)
        # Air quality tracking
        self.iaq_tracker = IAQTracker(300 / self.polling_interval, 3600 / self.polling_interval)

        # Metrics to collect
        self.bme680_temperature = Gauge('bme680_temperature', 'Temperature from BME680 sensor')
        self.bme680_pressure = Gauge('bme680_pressure', 'Pressure from BME680 sensor')
        self.bme680_humidity = Gauge('bme680_humidity', 'Humidity from BME680 sensor')
        self.bme680_gas_resistance = Gauge('bme680_gas_resistance', 'Gas resistance from BME680 sensor')
        self.bme680_head_stable = Gauge('bme680_head_stable', 'Heat stable from BME680 sensor')
        self.bme680_iaq = Gauge('bme680_iaq', 'IAQ from BME680 sensor')
        self.bme680_aqi = Gauge('bme680_aqi', 'AQI from BME680 sensor')

    def update(self, interval=5.0):
        # Read sensors
        self.sensor_bme680.get_sensor_data()
        iaq = self.iaq_tracker.getIAQ(self.sensor_bme680.data)
        aqi = 0
        if iaq is not None:
            aqi = 500 * (1 - iaq/100)
        else:
            iaq = 0
        # Update metrics
        self.bme680_temperature.set(self.sensor_bme680.data.temperature)
        self.bme680_pressure.set(self.sensor_bme680.data.pressure)
        self.bme680_humidity.set(self.sensor_bme680.data.humidity)
        self.bme680_gas_resistance.set(self.sensor_bme680.data.gas_resistance)
        self.bme680_head_stable.set(1 if self.sensor_bme680.data.heat_stable else 0)
        self.bme680_iaq.set(iaq)
        self.bme680_aqi.set(aqi)

    def run_loop(self):
        while True:
            self.update(self.polling_interval)
            time.sleep(self.polling_interval)


def main():
    polling_interval = 15.0
    weatherpi = WeatherPi(polling_interval)
    start_http_server(9107)
    weatherpi.run_loop()


if __name__ == '__main__':
    main()
