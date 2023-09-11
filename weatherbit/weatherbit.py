import json

import serial
import time


def compass_dir_to_deg(compass_dir):
    if compass_dir == "N":
        return 0
    elif compass_dir == "NE":
        return 45
    elif compass_dir == "E":
        return 90
    elif compass_dir == "SE":
        return 135
    elif compass_dir == "S":
        return 180
    elif compass_dir == "SW":
        return 225
    elif compass_dir == "W":
        return 270
    elif compass_dir == "NW":
        return 315
    else:
        return -1


class DataPoint:

    def __init__(self, do_init=False, ser_data=None, prev_ts=0):
        self.timestamp = 0
        self.millis = 0
        self.weatherbit_temperature = 0
        self.microbit_temperature = 0
        self.humidity = 0
        self.pressure = 0
        self.wind_speed = 0
        self.wind_gust = 0
        self.wind_direction = 0
        self.rainfall = 0
        self.light = 0
        if do_init:
            self.ingest_serial(ser_data, prev_ts)

    def ingest_serial(self, ser_data, prev_ts):
        try:
            ser_data = ser_data.strip().split(',')
            ts = int(ser_data[0])
            if ts == prev_ts:
                self.is_valid = False
                return
            self.millis = ts
            self.weatherbit_temperature = float(ser_data[1]) / 100
            self.microbit_temperature = float(ser_data[7])
            self.humidity = float(ser_data[2]) / 1000
            self.pressure = float(ser_data[3]) / 1000 + 173  # 173 is offset due to elevation (5100ft)
            self.wind_speed = float(ser_data[4])
            self.wind_direction = float(compass_dir_to_deg(ser_data[5]))
            self.rainfall = float(ser_data[6])
            self.light = float(ser_data[8])
            self.is_valid = True
        except Exception as e:
            print(e)
            self.is_valid = False
        self.timestamp = time.time()

    def to_json(self):
        return {
            "timestamp": self.timestamp,
            "millis": self.millis,
            "weatherbit_temperature": self.weatherbit_temperature,
            "microbit_temperature": self.microbit_temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "wind_speed": self.wind_speed,
            "wind_gust": self.wind_gust,
            "wind_direction": self.wind_direction,
            "rainfall": self.rainfall,
            "light": self.light
        }


class SensorData:

    def __init__(self, fname="/mnt/metrics/weatherbit.json", queue_size=60):
        self.fname = fname
        self.queue_size = queue_size
        self.data_points = []

    def update(self, data_point):
        self.data_points.append(data_point)
        if len(self.data_points) > 60:
            self.data_points.pop(0)

    def get_avg(self):
        avg_data = DataPoint()
        n = len(self.data_points)
        if n == 0:
            return avg_data
        max_wind_speed = 0
        for data_point in self.data_points:
            avg_data.weatherbit_temperature += data_point.weatherbit_temperature
            avg_data.microbit_temperature += data_point.microbit_temperature
            avg_data.humidity += data_point.humidity
            avg_data.pressure += data_point.pressure
            avg_data.wind_speed += data_point.wind_speed
            avg_data.wind_direction += data_point.wind_direction
            avg_data.rainfall += data_point.rainfall
            avg_data.light += data_point.light
            if data_point.wind_speed > max_wind_speed:
                max_wind_speed = data_point.wind_speed
        avg_data.timestamp = time.time()
        avg_data.weatherbit_temperature /= n
        avg_data.microbit_temperature /= n
        avg_data.humidity /= n
        avg_data.pressure /= n
        avg_data.wind_speed /= n
        avg_data.wind_direction /= n
        avg_data.rainfall /= n
        avg_data.light /= n
        avg_data.wind_gust = max_wind_speed
        return avg_data

    def get_rolling_avg(self, last_sec):
        now = time.time()
        avg_data = DataPoint()
        n = len(self.data_points)
        if n == 0:
            return avg_data
        max_wind_speed = 0
        num_points = 0
        for data_point in self.data_points:
            if now - data_point.timestamp < last_sec:
                avg_data.weatherbit_temperature += data_point.weatherbit_temperature
                avg_data.microbit_temperature += data_point.microbit_temperature
                avg_data.humidity += data_point.humidity
                avg_data.pressure += data_point.pressure
                avg_data.wind_speed += data_point.wind_speed
                avg_data.wind_direction += data_point.wind_direction
                avg_data.rainfall += data_point.rainfall
                avg_data.light += data_point.light
                if data_point.wind_speed > max_wind_speed:
                    max_wind_speed = data_point.wind_speed
                num_points += 1
        if num_points == 0:
            return avg_data
        avg_data.timestamp = now
        avg_data.weatherbit_temperature /= num_points
        avg_data.microbit_temperature /= num_points
        avg_data.humidity /= num_points
        avg_data.pressure /= num_points
        avg_data.wind_speed /= num_points
        avg_data.wind_direction /= num_points
        avg_data.rainfall /= num_points
        avg_data.light /= num_points
        avg_data.wind_gust = max_wind_speed
        return avg_data

    def persist(self):
        if len(self.data_points) == 0:
            return
        avg_data = self.get_avg()
        avg_15s_data = self.get_rolling_avg(15)  # for Mimir
        last_data = self.data_points[-1]
        with open(self.fname, 'w') as f:
            json.dump({
                "last": last_data.to_json(),
                "avg": avg_data.to_json(),
                "avg_15s": avg_15s_data.to_json()
            }, f, indent=4)


def main():
    ser = serial.Serial('/dev/ttyACM0', 115200)
    sensor_data = SensorData()
    last_time = 0
    while True:
        ser_data = ser.readline().decode('utf-8')
        data = DataPoint(True, ser_data, last_time)
        if data.is_valid:
            last_time = data.millis
            sensor_data.update(data)
            sensor_data.persist()
        time.sleep(0.5)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
