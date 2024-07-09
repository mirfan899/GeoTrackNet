import csv
import os.path
from datetime import datetime

dataset_path = "./data/csvs/"


def generate_csvs(tracks: list):
    with open(os.path.join(dataset_path, 'api.csv'), 'w') as f:
        writer = csv.writer(f)

        writer.writerow(["LAT", "LON", "SOG", "COG", "HEADING", "ROT", "NAV_STT", "TIMESTAMP", "MMSI"])
        for track in tracks:
            dt = datetime.utcfromtimestamp(int(track[7]))
            # utc_time = datetime.strptime(datetime.strftime(dt, '%Y-%m-%dT%H:%M:%fZ'), '%Y-%m-%dT%H:%M:%fZ')
            utc_time = datetime.strftime(dt, '%Y-%m-%dT%H:%M:%fZ')
            track[7] = utc_time
            writer.writerow(track)
