# FYI I personally changed the csv2pkl file to the below and ran this to get my pkl files instead:
import csv
import os
import pickle
from collections import defaultdict
from datetime import datetime

from tqdm import tqdm

# PARAMETERS AND GLOBAL SETTINGS
# ======================================
LAT_MIN, LAT_MAX = 4.7, 20.5
LON_MIN, LON_MAX = 116.8, 126.6
SOG_MAX = 30.0
dataset_path = "/home/iffi/PycharmProjects/GeoTrackNet/data/clean_csvs1"
l_csv_filename = [filename for filename in os.listdir(dataset_path) if filename.endswith('.csv')]

# Time conversion
timeframes = {
    'train': ("01/12/2023", "15/01/2024"),
    'valid': ("16/01/2024", "15/02/2024"),
    'test': ("16/02/2024", "01/03/2024")
}
for k, (start, end) in timeframes.items():
    timeframes[k] = (datetime.strptime(start, "%d/%m/%Y"), datetime.strptime(end, "%d/%m/%Y"))


# DATA PROCESSING AND FILTERING
# ======================================
def to_timestamp(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")


def process_and_filter(filenames, path):
    data = defaultdict(list)
    for csv_filename in filenames:
        filepath = os.path.join(path, csv_filename)
        print(f"Reading {csv_filename}...")
        with open(filepath, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Extract header
            for row in tqdm(csv_reader, desc="Processing rows"):
                try:
                    # Convert first eight fields to float, last field to int, and convert timestamp
                    numeric_data = list(map(float, row[: -2]))  # Convert numeric fields
                    timestamp = to_timestamp(row[-2])  # Convert timestamp
                    mmsi = int(row[-1])  # Convert MMSI
                    # Append all together
                    processed_row = numeric_data + [timestamp, mmsi]
                    # Apply geographic and SOG filters
                    if LAT_MIN <= processed_row[0] <= LAT_MAX and LON_MIN <= processed_row[1] <= LON_MAX and 0 <= processed_row[
                        2] <= SOG_MAX:
                        data[mmsi].append(processed_row)
                except Exception as e:
                    print(f"Error processing row: {row}, Exception: {e}")
                    continue
            # Sort each vessel's messages by timestamp
            for mmsi in data:
                data[mmsi].sort(key=lambda x: x[7])  # Assuming timestamp is at index 7
            return data


# Split data into training, validation, and test sets based on timestamps
def split_data(data, timeframes):
    datasets = {'train': defaultdict(list), 'valid': defaultdict(list), 'test': defaultdict(list)}
    for mmsi, tracks in data.items():
        for record in tracks:
            timestamp = record[7]
            for phase, (start, end) in timeframes.items():
                if start <= timestamp < end:
                    datasets[phase][mmsi].append(record)
            break
    return {k: dict(v) for k, v in datasets.items()}


# Process CSV files
data = process_and_filter(l_csv_filename, dataset_path)
datasets = split_data(data, timeframes)

# PICKLING
# ======================================
for phase, ds in datasets.items():
    filename = os.path.join(dataset_path, f"{phase}_tracks.pkl")
    with open(filename, "wb") as f:
        pickle.dump(ds, f)
    print(f"Saved {len(ds)} tracks to {filename}")
