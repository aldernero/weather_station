import json
import time

from prometheus_client import start_http_server, Gauge

class Weatherino:

    def __init__(self, fname="/mnt/metrics/weatherino.json", interval=15.0):
        self.polling_interval = interval

        # Get data from file
        self.fname = fname
        self.data = {}
        with open(self.fname, 'r') as f:
            self.data = json.load(f)
            self.data = self.data['avg_15s']

        # Metrics to collect
        self.weatherino_signal_disturber = Gauge('weatherino_signal_disturber', 'Signal disturber from lightning detector')
        self.weatherino_signal_noise = Gauge('weatherino_signal_noise', 'Signal noise from lightning detector')
        self.weatherino_signal_unknown = Gauge('weatherino_signal_unknown', 'Signal unknown from lightning detector')
        self.weatherino_signal_lightning = Gauge('weatherino_signal_lightning', 'Signal lightning from lightning detector')
        self.weatherino_lightning_distance = Gauge('weatherino_lightning_distance', 'Lightning distance from lightning detector')
        self.weatherino_pm10_standard = Gauge('weatherino_pm10_standard', 'PM10 standard from particulate matter sensor')
        self.weatherino_pm25_standard = Gauge('weatherino_pm25_standard', 'PM25 standard from particulate matter sensor')
        self.weatherino_pm100_standard = Gauge('weatherino_pm100_standard', 'PM100 standard from particulate matter sensor')
        self.weatherino_pm10_env = Gauge('weatherino_pm10_env', 'PM10 env from particulate matter sensor')
        self.weatherino_pm25_env = Gauge('weatherino_pm25_env', 'PM25 env from particulate matter sensor')
        self.weatherino_pm100_env = Gauge('weatherino_pm100_env', 'PM100 env from particulate matter sensor')
        self.weatherino_particles_03um = Gauge('weatherino_particles_03um', 'Particles 0.3um from particulate matter sensor')
        self.weatherino_particles_05um = Gauge('weatherino_particles_05um', 'Particles 0.5um from particulate matter sensor')
        self.weatherino_particles_10um = Gauge('weatherino_particles_10um', 'Particles 1.0um from particulate matter sensor')
        self.weatherino_particles_25um = Gauge('weatherino_particles_25um', 'Particles 2.5um from particulate matter sensor')
        self.weatherino_particles_50um = Gauge('weatherino_particles_50um', 'Particles 5.0um from particulate matter sensor')
        self.weatherino_particles_100um = Gauge('weatherino_particles_100um', 'Particles 10um from particulate matter sensor')

    def update(self, interval=5.0):
        with open(self.fname, 'r') as f:
            data = json.load(f)
            self.data = data['avg_15s']
        self.weatherino_signal_disturber.set(self.data['signal_disturber'])
        self.weatherino_signal_noise.set(self.data['signal_noise'])
        self.weatherino_signal_unknown.set(self.data['signal_unknown'])
        self.weatherino_signal_lightning.set(self.data['signal_lightning'])
        self.weatherino_lightning_distance.set(self.data['lightning_distance'])
        self.weatherino_pm10_standard.set(self.data['pm10_standard'])
        self.weatherino_pm25_standard.set(self.data['pm25_standard'])
        self.weatherino_pm100_standard.set(self.data['pm100_standard'])
        self.weatherino_pm10_env.set(self.data['pm10_env'])
        self.weatherino_pm25_env.set(self.data['pm25_env'])
        self.weatherino_pm100_env.set(self.data['pm100_env'])
        self.weatherino_particles_03um.set(self.data['particles_03um'])
        self.weatherino_particles_05um.set(self.data['particles_05um'])
        self.weatherino_particles_10um.set(self.data['particles_10um'])
        self.weatherino_particles_25um.set(self.data['particles_25um'])
        self.weatherino_particles_50um.set(self.data['particles_50um'])
        self.weatherino_particles_100um.set(self.data['particles_100um'])


    def run_loop(self):
        while True:
            self.update(self.polling_interval)
            time.sleep(self.polling_interval)


def main():
    polling_interval = 15.0
    weatherpi = Weatherino("/mnt/metrics/weatherino.json", polling_interval)
    start_http_server(9108)
    weatherpi.run_loop()


if __name__ == '__main__':
    main()
