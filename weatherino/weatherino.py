import json

import serial
import time

class DataPoint:

    def __init__(self, do_init=False, ser_data=None, prev_ts=0):
        self.timestamp = 0
        self.millis = 0
        self.lightning_signal = 0
        self.lightning_distance = 0
        self.num_disturber = 0
        self.num_noise = 0
        self.num_unknown = 0
        self.num_lightning = 0
        self.pm10_standard = 0
        self.pm25_standard = 0
        self.pm100_standard = 0
        self.pm10_env = 0
        self.pm25_env = 0
        self.pm100_env = 0
        self.particles_03um = 0
        self.particles_05um = 0
        self.particles_10um = 0
        self.particles_25um = 0
        self.particles_50um = 0
        self.particles_100um = 0
        if do_init:
            self.ingest_serial(ser_data, prev_ts)

    def ingest_serial(self, ser_data, prev_ts):
        try:
            ser_data = ser_data.strip().split(',')
            id_field = ser_data[0]
            ts = int(ser_data[1])
            if id_field != "data" or ts == prev_ts:
                self.is_valid = False
                return
            self.millis = ts
            self.lightning_signal = int(ser_data[2])
            self.lightning_distance = int(ser_data[3])
            self.pm10_standard = int(ser_data[4])
            self.pm25_standard = int(ser_data[5])
            self.pm100_standard = int(ser_data[6])
            self.pm10_env = int(ser_data[7])
            self.pm25_env = int(ser_data[8])
            self.pm100_env = int(ser_data[9])
            self.particles_03um = int(ser_data[10])
            self.particles_05um = int(ser_data[11])
            self.particles_10um = int(ser_data[12])
            self.particles_25um = int(ser_data[13])
            self.particles_50um = int(ser_data[14])
            self.particles_100um = int(ser_data[15])
            self.is_valid = True
        except Exception as e:
            print(e)
            self.is_valid = False
        self.timestamp = time.time()

    def to_json(self):
        return {
            "timestamp": self.timestamp,
            "lightning_distance": self.lightning_distance,
            "signal_disturber": self.num_disturber,
            "signal_noise": self.num_noise,
            "signal_unknown": self.num_unknown,
            "signal_lightning": self.num_lightning,
            "pm10_standard": self.pm10_standard,
            "pm25_standard": self.pm25_standard,
            "pm100_standard": self.pm100_standard,
            "pm10_env": self.pm10_env,
            "pm25_env": self.pm25_env,
            "pm100_env": self.pm100_env,
            "particles_03um": self.particles_03um,
            "particles_05um": self.particles_05um,
            "particles_10um": self.particles_10um,
            "particles_25um": self.particles_25um,
            "particles_50um": self.particles_50um,
            "particles_100um": self.particles_100um
        }


class SensorData:

    def __init__(self, fname="/mnt/metrics/weatherino.json", queue_size=60):
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
        num_lightning = 0
        for data_point in self.data_points:
            if data_point.lightning_signal == 8:
                num_lightning += 1
                avg_data.lightning_distance += data_point.lightning_distance
            elif data_point.lightning_signal == 4:
                avg_data.num_disturber += 1
            elif data_point.lightning_signal == 1:
                avg_data.num_noise += 1
            else:
                avg_data.num_unknown += 1
            avg_data.pm10_standard += data_point.pm10_standard
            avg_data.pm25_standard += data_point.pm25_standard
            avg_data.pm100_standard += data_point.pm100_standard
            avg_data.pm10_env += data_point.pm10_env
            avg_data.pm25_env += data_point.pm25_env
            avg_data.pm100_env += data_point.pm100_env
            avg_data.particles_03um += data_point.particles_03um
            avg_data.particles_05um += data_point.particles_05um
            avg_data.particles_10um += data_point.particles_10um
            avg_data.particles_25um += data_point.particles_25um
            avg_data.particles_50um += data_point.particles_50um
            avg_data.particles_100um += data_point.particles_100um
        avg_data.timestamp = time.time()
        avg_data.num_lightning = num_lightning
        if num_lightning > 0:
            avg_data.lightning_distance /= num_lightning
        avg_data.pm10_standard /= n
        avg_data.pm25_standard /= n
        avg_data.pm100_standard /= n
        avg_data.pm10_env /= n
        avg_data.pm25_env /= n
        avg_data.pm100_env /= n
        avg_data.particles_03um /= n
        avg_data.particles_05um /= n
        avg_data.particles_10um /= n
        avg_data.particles_25um /= n
        avg_data.particles_50um /= n
        avg_data.particles_100um /= n
        return avg_data

    def get_rolling_avg(self, last_sec):
        now = time.time()
        avg_data = DataPoint()
        n = len(self.data_points)
        if n == 0:
            return avg_data
        num_lightning = 0
        num_points = 0
        for data_point in self.data_points:
            if now - data_point.timestamp < last_sec:
                if data_point.lightning_signal == 8:
                    num_lightning += 1
                    avg_data.lightning_distance += data_point.lightning_distance
                elif data_point.lightning_signal == 4:
                    avg_data.num_disturber += 1
                elif data_point.lightning_signal == 1:
                    avg_data.num_noise += 1
                else:
                    avg_data.num_unknown += 1
                avg_data.pm10_standard += data_point.pm10_standard
                avg_data.pm25_standard += data_point.pm25_standard
                avg_data.pm100_standard += data_point.pm100_standard
                avg_data.pm10_env += data_point.pm10_env
                avg_data.pm25_env += data_point.pm25_env
                avg_data.pm100_env += data_point.pm100_env
                avg_data.particles_03um += data_point.particles_03um
                avg_data.particles_05um += data_point.particles_05um
                avg_data.particles_10um += data_point.particles_10um
                avg_data.particles_25um += data_point.particles_25um
                avg_data.particles_50um += data_point.particles_50um
                avg_data.particles_100um += data_point.particles_100um
                num_points += 1
        if num_points == 0:
            return avg_data
        avg_data.num_lightning = num_lightning
        if num_lightning > 0:
            avg_data.lightning_distance /= num_lightning
        avg_data.pm10_standard /= num_points
        avg_data.pm25_standard /= num_points
        avg_data.pm100_standard /= num_points
        avg_data.pm10_env /= num_points
        avg_data.pm25_env /= num_points
        avg_data.pm100_env /= num_points
        avg_data.particles_03um /= num_points
        avg_data.particles_05um /= num_points
        avg_data.particles_10um /= num_points
        avg_data.particles_25um /= num_points
        avg_data.particles_50um /= num_points
        avg_data.particles_100um /= num_points
        avg_data.timestamp = now
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
    ser = serial.Serial('/dev/ttyUSB0', 115200)
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
